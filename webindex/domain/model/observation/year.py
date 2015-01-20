__author__ = 'guillermo'
import itertools


class Year(object):
    """An observation year"""
    def __init__(self, value):
        self._name = '_'.join(['year', str(value)])
        self._value = value

    def __str__(self):
        return self._value

    def __repr__(self):
        return "Year(name={n!r}, value={v!r}".format(n=self._name, v=self._value)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(tuple(itertools.chain(self.__dict__.items(), [type(self)])))

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value
