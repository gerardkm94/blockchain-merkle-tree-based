import time
import json

from blocklibs.chain.block import Block
from blocklibs.crypto.hashing import Hashing
from blocklibs.chain.errors import BlockChainError


class Blockchain:
    """
    Class to handle blockchain structure and its methods. This class will handle all
    the structured data regarding a Blockchain instance.

    This class should be instantiated as soon as the node is set up since it will be
    the core of the applications, storing and managing all the blockchain operations.

    Parameters:
    # TODO Explain better.
    difficulty (int): Difficulty level of the blockchain.
    """

    def __init__(self):
        """
        Parameters:

        unconfirmed_transactions (list): Transactions stored, but pending to confirm.
        chain (list): List of blocks (Block) objects, conforming the whole chain.
        nodes (set): Contains all the nodes that are contributing to the blockchain.
        """
        self._difficulty = 2
        self._unconfirmed_transactions = []
        self._chain = []
        self._nodes = set()
        self.get_genesis_block()

    def get_genesis_block(self):
        """
        This method creates a genesis block (First block to be stored into the chain)
        and appends it into the block chain.
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = Hashing.compute_sha256_hash(
            genesis_block.get_block)
        self._chain.append(genesis_block)

    def proof_of_work(self, block):

        block.nonce = 0

        hashed_block = Hashing.compute_sha256_hash(block)
        while not hashed_block.startswith('0' * self._difficulty):
            block.nonce += 1
            hashed_block = Hashing.compute_sha256_hash(block)

        return hashed_block

    def is_valid_proof_of_work(self, block, block_hash):

        return (block_hash.startswith('0' * self._difficulty)
                and block_hash == Hashing.compute_sha256_hash(block))

    def add_block(self, block, proof_of_work):
        """
        Adds the block to the chain if verification is okay
        """
        previous_hash = self.chain_last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof_of_work(block, proof_of_work):
            return False

        block.hash = proof_of_work
        self._chain.append(block)
        return True

    def compute_transactions(self):
        """
        Add unconfirmed transactions to the blockchain
        """
        if not self._unconfirmed_transactions:
            raise BlockChainError("Not pending transactions to confirm")

        last_block = self.chain_last_block
        new_block = Block(index=last_block.index,
                          transactions=self._unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof_of_work = self.proof_of_work(new_block)
        self.add_block(new_block, proof_of_work)
        self.unconfirmed_transactions = []
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

        for node in self._nodes:
            remote_chain = node.get_remote_chain()
            chain_len = remote_chain.get("length")
            chain_data = remote_chain.get("chain")

            if chain_len > current_len and self.check_chain_validity(chain_data):
                current_len = chain_len
                longest_chain = chain_data

        if longest_chain:
            self._chain = longest_chain
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
                block_data.get("previous_hash")
            )
            proof = block_data.get("hash")

            if block_data.get("index") > 0:
                is_block_added = block_chain.add_block(block, proof)
                if not is_block_added:
                    raise BlockChainError(
                        "The chain is tampered, can be added")

        return block_chain

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
        """
        return len(self.chain)

    @chain.getter
    def chain_last_block(self):
        """
        Property to get the last block of the blockchain 
        """
        return self.chain.pop()

    @chain.getter
    def chain_local_info(self):
        """
        Property to get the whole blockchain of this node
        """
        node_data = [block.get_block for block in self._chain]
        return {
            "length": len(node_data),
            "chain": node_data,
            "nodes": list(self.nodes)
        }

    @property
    def nodes(self):
        """
        Property to get all the nodes
        """
        return self._nodes

    @nodes.setter
    def nodes(self, node):
        """
        Add a new node to the chain
        """
        self.nodes.add(node)

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
