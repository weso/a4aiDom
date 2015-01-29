
__author__ = 'Herminio'


class RepositoryError(Exception):
    def __init__(self, message, custom_header=""):
        self._message = message
        self._custom_header = custom_header

    @property
    def message(self):
        return self._custom_header + " " + self._message


class AreaRepositoryError(RepositoryError):
    def __init__(self, message):
        super(AreaRepositoryError, self).__init__(message=message, custom_header="Area Error:")


class IndicatorRepositoryError(RepositoryError):
    def __init__(self, message):
        super(IndicatorRepositoryError, self).__init__(message=message, custom_header="Indicator Error:")


class ObservationRepositoryError(RepositoryError):
    def __init__(self, message):
        super(ObservationRepositoryError, self).__init__(message=message, custom_header="Observation Error:")