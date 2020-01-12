import time
from blocklibs.chain.block import Block
from blocklibs.crypto.hashing import Hashing


class Blockchain:

    difficulty = 2

    def __init__(self):

        self.unconfirmed_transactions = []
        self.chain = []
        self.get_genesis_block()

    def get_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = Hashing.compute_sha256_hash(
            genesis_block.get_block)
        self.chain.append(genesis_block)

    @staticmethod
    def proof_of_work(block):

        block.nonce = 0

        hashed_block = Hashing.compute_sha256_hash(block)
        while not hashed_block.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            hashed_block = Hashing.compute_sha256_hash(block)

        return hashed_block

    @staticmethod
    def is_valid_proof_of_work(block, block_hash):

        return (block_hash.startswith('0' * Blockchain.difficulty)
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
        self.chain.append(block)
        return True

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def compute_transactions(self):
        """
        Add pending transactions to the blockchain
        """
        if not self.unconfirmed_transactions:
            print("Not transactions to add")
            return False

        last_block = self.last_block
        new_block = Block(index=last_block.index,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof_of_work = self.proof_of_work(new_block)
        self.add_block(new_block, proof_of_work)
        self.unconfirmed_transactions = []
        return new_block.index

    @property
    def last_block(self):
        return self.chain[-1]
