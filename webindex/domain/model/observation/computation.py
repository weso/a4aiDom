__author__ = 'Dani'

import itertools


class Computation(object):
    """ Computation entity """

    def __init__(self, comp_type, value):
        self._type = self._validate_computation_type(comp_type)
        self._value = value

    def __str__(self):
        return self._value

    def __repr__(self):
        return "Computation(type{n!r}, value{v!r}".format(n=self._type, r=self._value)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(tuple(itertools.chain(self.__dict__.items(), [type(self)])))


    @property
    def comp_type(self):
        return self._type


    @property
    def value(self):
        return self._value


    @staticmethod
    def _validate_computation_type(_type):
        if _type not in ["raw", "normalized", "ranked", "scored", "grouped"]:
            raise ValueError("There is no {} computation type".format(_type))
        return _type








