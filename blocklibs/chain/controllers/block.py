import json


class Block:

    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0, merkle_root=0):
        """
        Block Structure
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = merkle_root

    def get_block(self):
        """
        This method returns a Json Object with the block data 
        """
        return json.dumps(self.__dict__, sort_keys=True)
