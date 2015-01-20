__author__ = 'guillermo'
import itertools


class Organization(object):
    """An indicator organization"""
    def __init__(self, label):
        self._label = label
        self._type = "Organization"

    def __str__(self):
        return ' '.join([self._type, self._label])

    def __repr__(self):
        return "Organization(label={o._label!r}, type={o._type!r}".format(o=self)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(tuple(itertools.chain(self.__dict__.items(), [type(self)])))

    @property
    def label(self):
        return self._label

