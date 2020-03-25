import time
import json
import requests

from blocklibs.chain.block import Block
from blocklibs.crypto.hashing import Hashing
from blocklibs.chain.errors import BlockChainError, NodeError


class Blockchain:
    """
    Class to handle blockchain structure and its methods. This class will handle all
    the structured data regarding a Blockchain instance.

    This class should be instantiated as soon as the node is set up since it will be
    the core of the applications, storing and managing all the blockchain operations.

    Parameters:
    difficulty (int): Difficulty level of the blockchain.
    """

    def __init__(self):
        """
        Attributes:
        difficulty (int): Mine blockchain difficulty.
        unconfirmed_transactions (list): Transactions stored, but pending to confirm.
        chain (list): List of blocks (Block) objects, conforming the whole chain.
        nodes (set): Contains all the nodes that are contributing to the blockchain.


        """
        self._difficulty = 2
        self._unconfirmed_transactions = []
        self._chain = []
        self._nodes = set()
        self._self_node_identifier = None
        self.get_genesis_block()

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

        return (block_hash.startswith('0' * self._difficulty)
                and block_hash == Hashing.compute_sha256_hash(block.get_block()))

    def add_block(self, block, proof_of_work):
        """
        Adds the block to the chain if verification is okay.

        Parameters: 
        block (Block): Block trying to be added.
        proof_of_work (str): Hash of the block.

        Returns: 
        Boolean, True if the bloock meets the conditions to be added. False if not.
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
        Add unconfirmed transactions to the blockchain

        Returns: 
        new_block.index (int): The Index of the added block.
        """
        if not self._unconfirmed_transactions:
            raise BlockChainError("Not pending transactions to confirm")

        unconfirmed_transactions_serialized = [
            json.loads(unconfirmed.transaction) for unconfirmed in self.unconfirmed_transactions]

        last_block = self.chain_last_block
        # pylint: disable=maybe-no-member
        new_block = Block(index=last_block.index + 1,
                          transactions=unconfirmed_transactions_serialized,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof_of_work = self.proof_of_work(new_block)
        self.add_block(new_block, proof_of_work)
        self.unconfirmed_transactions_reset
        return new_block.index

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
        Consensus Algorithm. If a longer chain is found, it will be replaced with it.
        """

        longest_chain = None
        current_len = self.chain_len

        for node in self.nodes:
            remote_chain = node.get_remote_chain()
            chain_len = remote_chain.get("length")
            chain_data = remote_chain.get("chain")

            if chain_len > current_len and self.check_chain_validity(chain_data):
                current_len = chain_len
                longest_chain = chain_data

        if longest_chain is not None:
            self.chain = longest_chain
            print("Consensus achieved, longer chain found")
            return True

        return False

    @classmethod
    def chain_builder(cls, new_chain):
        """
        This method creates a new Blockchain instance from a 
        remote instance or dump.
        """
        block_chain = Blockchain()

        for block_data in new_chain:
            block_data = json.loads(block_data)
            block = Block(
                block_data.get("index"),
                block_data.get("transactions"),
                block_data.get("timestamp"),
                block_data.get("previous_hash"),
                block_data.get("nonce")
            )
            proof = block_data.get("hash")

            if block_data.get("index") > 0:
                is_block_added = block_chain.add_block(block, proof)
                if not is_block_added:
                    raise BlockChainError(
                        "The chain is tampered, can't be added")

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

                raise NodeError("Already Registered")

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
