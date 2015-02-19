
__author__ = 'Herminio'


class RepositoryError(Exception):
    """
    Exception parent class for all repositories, this class could be subclassed for custom behaviour

    Attributes:
        message (str): Error message for this exception
    """

    def __init__(self, message, custom_header=""):
        """
        Constructor for RepositoryError

        Args:
            message (str): Error message for this exception
            custom_header (str): Title to introduce the error message
        """
        self._message = message
        self._custom_header = custom_header

    @property
    def message(self):
        return self._custom_header + " " + self._message


class AreaRepositoryError(RepositoryError):
    """
    Exception for Area Repository, it will print 'Area Error:' as title
    """
    def __init__(self, message):
        """
        Constructor for AreaRepositoryError

        Args:
            message (str): Error message for this exception
        """
        super(AreaRepositoryError, self).__init__(message=message, custom_header="Area Error:")


class IndicatorRepositoryError(RepositoryError):
    """
    Exception for Indicator Repository, it will print 'Indicator Error:' as title
    """
    def __init__(self, message):
        """
        Constructor for IndicatorRepositoryError

        Args:
            message (str): Error message for this exception
        """
        super(IndicatorRepositoryError, self).__init__(message=message, custom_header="Indicator Error:")


class ObservationRepositoryError(RepositoryError):
    """
    Exception for Observation Repository, it will print 'Observation Error:' as title
    """
    def __init__(self, message):
        """
        Constructor for ObservationRepositoryError

        Args:
            message (str): Error message for this exception
        """
        super(ObservationRepositoryError, self).__init__(message=message, custom_header="Observation Error:")