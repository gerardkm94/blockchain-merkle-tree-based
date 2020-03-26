from hashlib import sha256
from merkletools import MerkleTools


class Hashing:
    """
    This class will manage all related hashing methods. Blocks and transactions
    will be hashed using this Class. Several hashing methods with different purposes
    will be declared here.
    """
    @staticmethod
    def compute_sha256_hash(block_or_trans):
        """
        @args: "block_or_trans" JsonString formatted object, containing
        a block/transaction information.
        @return "hashedOutput" Hashed value of block/trans object passed as
        argument
        """
        hashed_output = sha256(block_or_trans.encode()).hexdigest()

        return hashed_output

    @classmethod
    def build_merkle_tree(cls, unconfirmed_transactions):
        """
        Returns a Merkle tree Object with all the MT information regarding the
        transactions passed as a parameter.

        For this implementation, we are considering ^2 transactions for performance, with a limit
        of 8 for each tree.
        """
        # Settign Tree Hashing Type Internal
        m_tree = MerkleTools(hash_type="SHA256")
        # Passing as list all the elements to hash
        m_tree.add_leaf(unconfirmed_transactions, True)
        # Merkle tree building
        m_tree.make_tree()

        return m_tree
