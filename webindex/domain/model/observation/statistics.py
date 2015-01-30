__author__ = 'Herminio'


class Statistics(object):
    def __init__(self, observations):
        self._observations = observations

    @property
    def average(self):
        values = self._observations_values()
        return self._average(values)

    @property
    def median(self):
        values = self._observations_values()
        values.sort()
        half = len(values) / 2
        if len(values) % 2 == 0:
            return self._average([values[half - 1], values[half]])
        else:
            return values[half]

    def _average(self, values):
        return reduce(lambda sum, value: sum + value, values, 0) / float(len(values))

    def _observations_values(self):
        return [obs.value for obs in self._observations]

    def to_dict(self):
        return {
            'average': self.average,
            'median': self.median
        }
