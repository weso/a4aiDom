__author__ = 'Herminio'


class AreaInfo(object):
    """
    Area info entity

    Attributes:
        indicator_code (str): Indicator code for this area info
        provider_name (str): Provider name of the indicator
        provider_url (str): Provider url of the indicator
        value (float or string): Value for this area and the indicator, could be blank if there is no valid value
        year (str): Year when value was observed
    """

    def __init__(self, indicator_code, provider_name, provider_url, value, year):
        """
        Constructor for AreaInfo

        Args:
            indicator_code (str): Indicator code for this area info
            provider_name (str): Provider name of the indicator
            provider_url (str): Provider url of the indicator
            value (float): Value for this area and the indicator
            year (str): Year when value was observed
        """
        self._indicator_code = indicator_code
        self._provider_name = provider_name
        self._provider_url = provider_url
        self._value = value
        self._year = year

    @property
    def indicator_code(self):
        return self._indicator_code

    @indicator_code.setter
    def indicator_code(self, indicator_code):
        self._indicator_code = indicator_code

    @property
    def provider_name(self):
        return self._provider_name

    @provider_name.setter
    def provider_name(self, provider_name):
        self._provider_name = provider_name

    @property
    def provider_url(self):
        return self._provider_url

    @provider_url.setter
    def provider_url(self, provider_url):
        self._provider_url = provider_url

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        self._year = year

    def to_dict(self):
        """
        Converts self object to dictionary

        Returns:
            dict: Dictionary representation of self object
        """
        return {
            "provider": {
                "url": self.provider_url,
                "name": self.provider_name
            },
            "year": self.year,
            "value": self.value
        }
