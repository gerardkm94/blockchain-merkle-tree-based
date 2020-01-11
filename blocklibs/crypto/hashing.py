from hashlib import sha256


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
