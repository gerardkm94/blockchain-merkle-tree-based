from blocklibs.chain.blockchain import Blockchain
from blocklibs.chain.block import Block
from blocklibs.chain.errors import BlockChainError


class Utils():
    """
    Class to handle all the util operations
    """
    @classmethod
    def create_chain(cls, new_chain):
        """
        This method creates a new Blockchain instance from a 
        remote instance or dump.
        """
        block_chain = Blockchain()

        for block_data in new_chain:
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
