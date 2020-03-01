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


class ApiResponse():
    """
    Class to normalize the raised errors
    """

    def raise_response(self, message, code):
        return {'message': str(message)}, code
