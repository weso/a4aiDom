__author__ = 'Herminio'


class IndicatorInfo(object):

    def __init__(self, indicator_code, provider_name, provider_url):
        self._indicator_code = indicator_code
        self._provider_name = provider_name
        self._provider_url = provider_url
        self._values = []

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
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values

    def add_value(self, value):
        self._values.append(value)

    def to_dict(self):
        return {
            'provider': {
                'provider_name': self.provider_name,
                'provider_url': self.provider_url,
            },
            'values': {
                value.area_code: value.to_dict()
                for value in self.values
            }
        }


class IndicatorInfoList(object):

    def __init__(self):
        self._indicator_infos = []

    @property
    def indicator_infos(self):
        return self._indicator_infos

    @indicator_infos.setter
    def indicator_infos(self, indicator_infos):
        self._indicator_infos = indicator_infos

    def add_indicator_info(self, indicator_info):
        self._indicator_infos.append(indicator_info)

    def to_dict(self):
        return {
            indicator_info.indicator_code: indicator_info.to_dict()
            for indicator_info in self.indicator_infos
        }