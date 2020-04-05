import copy
import json
import time
from http import HTTPStatus as code

import requests
from flask import request
from merkletools import MerkleTools

from blocklibs.chain.controllers.block import Block
from blocklibs.chain.controllers.node import Node
from blocklibs.chain.errors import (ApiResponse, BlockChainError, HttpErrors,
                                    NodeError)
from blocklibs.chain.utils import Utils
from blocklibs.crypto.hashing import Hashing

max_request_retry = 3


class Blockchain:
    """
    Class to handle blockchain structure and its methods. This class will handle all
    the structured data regarding a Blockchain instance.

    This class should be instantiated as soon as the node is set up since it will be
    the core of the application, storing and managing all the blockchain operations for a 
    single node.
    """

    def __init__(self):
        """
        Attributes:
        difficulty (int): Mine blockchain difficulty.
        unconfirmed_transactions (list): Transactions stored, but pending to confirm.
        chain (list): List of blocks (Block) objects, conforming the whole chain.
        nodes (set): Contains all the nodes that are contributing to the blockchain.
        self_node_identifier (Node): Own node identifier information.
        trustable(Boolean): Determine if a node is trustable or not.
        votes(int): Received votes to determine if a node is not trustable.


        """
        self._difficulty = 2
        self._unconfirmed_transactions = []
        self._chain = []
        self._nodes = set()
        self._self_node_identifier = None
        self.get_genesis_block()

        self._trustable = True
        self._votes = 0

    def get_genesis_block(self):
        """
        This method creates a genesis block (First block to be stored into the chain)
        and appends it into the block chain.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = Hashing.compute_sha256_hash(
            genesis_block.get_block())
        self._chain.append(genesis_block)

    def proof_of_work(self, block):
        """
        Calculates the hash for a given block until the criteria its accomplished.
        The difficulty of the proof of work will set the difficulty level to achieve the hash.

        Parameters:
        block (Block): Block instance.

        Returns:
        hashed_block (str): The result of hashing the input Block meeting the criteria.
        """

        block.nonce = 0
        hashed_block = Hashing.compute_sha256_hash(block.get_block())

        while not hashed_block.startswith('0' * self._difficulty):
            block.nonce += 1
            hashed_block = Hashing.compute_sha256_hash(block.get_block())

        return hashed_block

    def is_valid_proof_of_work(self, block, block_hash):
        """
        Check if a given block_hash meets the difficulty criteria and if the computed hash
        of the given block is equal to the calculated in the chain and it's not tampered.

        Parameters:
        block (Block): Block instance.
        block_hash (str): Hash of the given block

        Returns:
        Boolean, True if all conditions are met.
        """
        hash_start_with = block_hash.startswith('0' * self._difficulty)
        new_hash = Hashing.compute_sha256_hash(block.get_block())

        return (hash_start_with and block_hash == new_hash)

    def add_block(self, block, proof_of_work):
        """
        Adds the block to the chain if verification is okay.

        Parameters:
        block (Block): Block trying to be added.
        proof_of_work (str): Hash of the block.

        Returns:
        Boolean, True if the block meets the conditions to be added. False if not.
        """
        # pylint: disable=maybe-no-member
        previous_hash = self.chain_last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof_of_work(block, proof_of_work):
            return False

        block.hash = proof_of_work
        self.chain.append(block)

        return True

    def compute_transactions(self):
        """
        Add unconfirmed transactions to the blockchain. Only Power of 2 transactions are allowed
        to meet Merkle Tree efficiency requirements.

        Returns:
        new_block.index (int): The Index of the added block.
        """
        if not self._unconfirmed_transactions:
            raise BlockChainError("Not pending transactions to confirm")

        if Utils.is_power_of_two(len(self.unconfirmed_transactions)):
            pass

        elif Utils.is_power_of_two(len(self.unconfirmed_transactions) + 1):
            # Append a copy of last transaction to make it power of 2
            self.unconfirmed_transactions = self.unconfirmed_transactions[-1]

        else:
            raise BlockChainError(
                "Unconfirmed transactions are not power of 2")

        unconfirmed_transactions_serialized = [
            json.loads(unconfirmed.transaction) for unconfirmed in self.unconfirmed_transactions]

        computed_merkle_tree = Hashing.build_merkle_tree(
            unconfirmed_transactions_serialized)

        last_block = self.chain_last_block
        last_block_no_hash = copy.deepcopy(last_block)
        delattr(last_block_no_hash, "hash")

        # pylint: disable=maybe-no-member
        new_block = Block(index=last_block.index + 1,
                          transactions=unconfirmed_transactions_serialized,
                          timestamp=time.time(),
                          previous_hash=Hashing.compute_sha256_hash(
                              last_block_no_hash.get_block()),
                          merkle_root=computed_merkle_tree.get_merkle_root()
                          )

        proof_of_work = self.proof_of_work(new_block)
        self.add_block(new_block, proof_of_work)
        self.unconfirmed_transactions_reset

        return new_block.index

    def check_invalid_transactions(self, merkle_root, transactions, remote_node):
        """
        Find for a detected list of invalid transactions which of them are not valid, and
        which have been tampered. 

        To do so, ask to every node in the network for the merkle proof of the suspicious
        transactions. When the merkle proof is received, check if is valid validating it 
        against the merkle_root of the own node.

        Returns a list containing this invalid transactions.
        """
        invalid_transactions = []

        for index_transaction, transaction in enumerate(transactions):

            merkle_proof = self.validate_transaction(
                index_transaction, merkle_root, remote_node)

            if merkle_proof:
                # Agree, all the chains returned the same!
                m_tree = MerkleTools(hash_type="SHA256")
                is_valid = m_tree.validate_proof(
                    merkle_proof,
                    Hashing.compute_sha256_hash(json.dumps(transaction)),
                    merkle_root)

                if not is_valid:
                    invalid_transactions.append(
                        {
                            "transaction": json.dumps(transaction),
                            "index_transaction": index_transaction,
                            "merkle_root_block": merkle_root
                        }
                    )

        return invalid_transactions

    def validate_transaction(self, index_transaction, merkle_root, remote_node):
        """
        For a given transaction, ask to all the available nodes for its merkle proof. 
        This merkle proof is not requested to the node which has been triggered this request.

        Returns: 
        merkle_proof: Object containing the requested merkle proof for a given transaction.

        """
        remote_node = Node(remote_node.get('_node_address'),
                           remote_node.get('_node_name'))

        nodes = [node for node in self.nodes if node.node_address !=
                 remote_node.node_address]

        for node in nodes:

            url = f"{node.node_address}/Transactions/validator"
            # pylint: disable=maybe-no-member
            data = {
                "transaction_index": index_transaction,
                "merkle_root": merkle_root
            }
            headers = {'Content-Type': "application/json"}

            try:
                for _ in range(0, 3):
                    response = requests.post(
                        url,
                        data=json.dumps(data),
                        headers=headers)

                    if response.status_code == 201:
                        break

            except:
                return "Can't validate, no nodes available"

            merkle_proof = json.loads(json.loads(
                response.content).get('message'))

            return merkle_proof

    def check_chain_validity(self, chain):
        """
        A helper method to check if the blockchain is valid.          
        """
        result = True
        previous_hash = "0"

        # Iterate through every block
        for block in chain:
            block_hash = block.hash
            # remove has attribute
            delattr(block, "hash")

            if not self.is_valid_proof_of_work(block=block, block_hash=block.hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def consensus(self):
        """
        Consensus Algorithm. If a longer chain is found, it will be replaced with it. This method
        should be called when a new operation to the node (adding blocks) want to be performed.

        This will ensure that the node is updated to the last chain version regarding the
        rest of the nodes of the network. If a biggest and consisten chain is found, the node
        will be updated and then, operations could be executed to keep growing the chain.
        """

        longest_chain = None
        current_len = self.chain_len

        for node in self.nodes:
            remote_chain = node.get_remote_chain()
            chain_len = remote_chain.get("length")
            chain_data = remote_chain.get("chain")

            # Calculate chain integrity
            if chain_len > current_len:

                if self.check_chain_validity(chain_data):
                    # TODO REPLACE FOR CHAIN BUILDER??
                    current_len = chain_len
                    longest_chain = chain_data

                else:
                    # This remote chain is tempered, should notify and force a re_sync for remote
                    # or add to non trusted nodes (nop)
                    # TODO CREATE METHOD to vote for a bad request. Notify here if for this node
                    # the chain couldn't not be validated!

                    pass

        if longest_chain is not None:
            self.chain = longest_chain
            print("Consensus achieved, longer chain found")
            return True

        return False

    def chain_builder(self, chain_info):
        """
        This method creates a new Blockchain instance from a 
        remote instance or dump.
        """
        block_chain = Blockchain()
        new_chain = chain_info.get('chain')
        remote_node = json.loads(chain_info.get('node_identifier'))

        for block_data in new_chain:
            block_data = json.loads(block_data)
            block = Block(
                block_data.get("index"),
                block_data.get("transactions"),
                block_data.get("timestamp"),
                block_data.get("previous_hash"),
                block_data.get("nonce"),
                block_data.get("merkle_root")
            )
            proof = block_data.get("hash")

            if block_data.get("index") > 0:
                is_block_added = block_chain.add_block(block, proof)

                if not is_block_added:
                    tampered_transactions = []
                    transactions = block.transactions
                    tampered_transactions = self.check_invalid_transactions(
                        block.merkle_root, transactions, remote_node)

                    if not tampered_transactions:
                        raise BlockChainError(
                            "The chain is tampered, can't be added, previous hash differ")
                    else:
                        message = f"""Te chain is tampered, the following transactions 
                            couldn't be validated: {str(tampered_transactions)}"""
                        raise BlockChainError(message)

        return block_chain

    def publish_new_block(self):
        """
        Publish a new block on remote nodes. In this implementations, the number of calls
        is set to 1000 to give time to remote nodes to be released if they're performing operations.

        IMPROVEMENT: Make this operations through threads and status.
        """
        failed_nodes = []

        for node in self.nodes:
            url = f"{node.node_address}Block/add"
            # pylint: disable=maybe-no-member
            data = self.chain_last_block.get_block()
            headers = {'Content-Type': "application/json"}

            try:
                for _ in range(0, 100):
                    response = requests.post(
                        url,
                        data=data,
                        headers=headers)

                    if response.status_code == 201:
                        break

                if response.status_code != 201:
                    # If after X attempts status_code is not 201, error:
                    failed_nodes.append(
                        {'node': node.get_node_info(),
                         'error_code': response.status_code,
                         'error_message': response.content,
                         }
                    )

            except Exception as add_node_error:
                failed_nodes.append(
                    {'node': node.get_node_info(),
                        'error_message': str(add_node_error)
                     }
                )

        return failed_nodes

    def register_node(self, node_address):
        """
        This method publish _self_node to the specified node address list.
        """
        post_data = {
            'node_address': request.host_url.rstrip('/'),
            'node_name': self.self_node_identifier.node_name
        }
        headers = {'Content-Type': "application/json"}

        for _ in range(0, max_request_retry):

            response = requests.post(
                f"{node_address}/Nodes/register_node",
                data=json.dumps(post_data),
                headers=headers
            )

            if response.status_code == code.CREATED:
                return response

            else:
                message = response.reason
                raise HttpErrors(message)

    def get_transactions_by_merkle_root(self, merkle_root):
        """
        Check if a transaction is valid, sending it to remote nodes and validating
        through a merkle_proof validation process.
        """
        for block in self.chain:

            if block.merkle_root == merkle_root:
                return block.transactions

        return False

    @property
    def chain(self):
        """
        Property to get the current chain
        """
        return self._chain

    @chain.setter
    def chain(self, received_chain):
        """
        Property to set a new chain when a longer one is received
        """
        self._chain = received_chain

    @chain.getter
    def chain_len(self):
        """
        Property to get the len of the chain

        Returns: 
        The len of the chain.
        """
        return len(self.chain)

    @chain.getter
    def chain_last_block(self):
        """
        Property to get the last block of the blockchain 

        Returns: 
        last_added_block (Block): Last added block to the chain.

        """
        last_added_block = self.chain[-1]

        return last_added_block

    @chain.getter
    def chain_local_info(self):
        """
        Property to get the whole blockchain of this node
        """
        node_chain_data = [block.get_block() for block in self.chain]
        node_data = [node.get_node_info() for node in self.nodes]
        try:
            self_node_identifier = self.self_node_identifier.get_node_info()
        except:
            raise NodeError("Please, set first the Node's Name")

        return {
            "length": len(node_chain_data),
            "chain": node_chain_data,
            "nodes": node_data,
            "node_identifier": self_node_identifier,
        }

    @property
    def nodes(self):
        """
        Property to get all the nodes
        """
        return self._nodes

    @nodes.setter
    def nodes(self, new_node):
        """
        Add a new node to the chain
        """
        for registered_node in self.nodes:

            if registered_node.get_node_info() == new_node.get_node_info():
                return None

        self.nodes.add(new_node)

    @nodes.setter
    def nodes_update(self, received_nodes):
        """
        Property to sync the nodes within remote origins
        """

        self.nodes.update(received_nodes)

    @property
    def unconfirmed_transactions(self):
        """
        Retrieve all the pending transactions
        """
        return self._unconfirmed_transactions

    @unconfirmed_transactions.setter
    def unconfirmed_transactions(self, transaction):
        self._unconfirmed_transactions.append(transaction)

    @property
    def unconfirmed_transactions_reset(self):
        self._unconfirmed_transactions = []

    @property
    def self_node_identifier(self):
        return self._self_node_identifier

    @self_node_identifier.setter
    def self_node_identifier(self, node):
        self._self_node_identifier = node

    @property
    def votes(self):
        return self._votes

    @votes.setter
    def votes(self, vote):
        self._votes = self._votes + 1

    def is_trustable(self):
        """
        Return either the chain is trustable if more than the 50% of the nodes
        agree on that. 
        """
        if len(self.nodes) > 0:

            if (self._votes * 100) / len(self.nodes) >= 50:
                return False
            else:
                return True
        else:
            return "I don't know, add nodes to compare with!"
