__author__ = 'Herminio'


class AreaShortInfo(object):

    def __init__(self, area_code, value, year):
        self._area_code = area_code
        self._value = value
        self._year = year

    @property
    def area_code(self):
        return self._area_code

    @area_code.setter
    def area_code(self, area_code):
        self._area_code = area_code

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
        return {
            'value': self.value,
            'year': self.year
        }
