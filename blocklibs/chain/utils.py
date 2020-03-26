

class Utils:
    """
    Class to handle all the util operations
    """

    @staticmethod
    def is_power_of_two(number):
        """
        Returns true if a number is power of 2
        """
        return number != 0 and ((number & (number - 1)) == 0)
