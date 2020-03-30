""" 
Custom Class to manage all the API errors
"""


class Errors(Exception):
    """
    Base class for exceptions
    """
    pass


class HttpErrors(Errors):
    """
    Class to handle all the HTTP Related errors
    """


class BlockChainError(Errors):
    """
    Class to handle all the errors inside Blockchain module
    """


class NodeError(Errors):
    """
    Class to handle all the errors inside Node's Module
    """

    def __init__(self, message):
        self.message = message

    def invalid_node(self):
        return {'message': str(self.message)}

    def existent_node(self):
        return {'message': str(self.message)}


class SerializeNodeError(Errors):
    """
    Class to handle all the Node Serialize Errors
    """


class ApiResponse():
    """
    Class to normalize the raised errors
    """
    @classmethod
    def raise_response(cls, message, code):
        return {'message': str(message)}, code
