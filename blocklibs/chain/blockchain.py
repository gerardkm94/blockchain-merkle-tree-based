import time
import json

from blocklibs.chain.block import Block
from blocklibs.crypto.hashing import Hashing


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
        peers (set): Contains all the peers that are contributing to the blockchain.
        """
        self._difficulty = 2
        self._unconfirmed_transactions = []
        self._chain = []
        self._peers = set()
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
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof_of_work(block, proof_of_work):
            return False

        block.hash = proof_of_work
        self._chain.append(block)
        return True

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def compute_transactions(self):
        """
        Add pending transactions to the blockchain
        """
        if not self._unconfirmed_transactions:
            print("Not transactions to add")
            return False

        last_block = self.last_block
        new_block = Block(index=last_block.index,
                          transactions=self._unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof_of_work = self.proof_of_work(new_block)
        self.add_block(new_block, proof_of_work)
        self.unconfirmed_transactions = []
        return new_block.index

    @property
    def get_chain(self):
        """
        Property to get the whole blockchain of this node
        """
        node_data = [block.get_block for block in self.chain]
        return json.dumps({"length": len(node_data),
                           "chain": node_data})

    @property
    def last_block(self):
        """
        Property to get the last block of the blockchain 
        """
        return self.chain[-1]
