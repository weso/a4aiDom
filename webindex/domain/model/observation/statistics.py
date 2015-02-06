__author__ = 'Herminio'


class Statistics(object):
    DEVELOPING = "Developing"
    EMERGING = "Emerging"

    def __init__(self, observations):
        self._observations = observations

    @property
    def average(self):
        values = self._observations_values()
        return self._average(values)

    @property
    def median(self):
        values = self._observations_values()
        return self._median(values)

    @property
    def average_developing(self):
        return self._average(self._filter_observations_values_by_area_type(self.DEVELOPING))

    @property
    def median_developing(self):
        return self._median(self._filter_observations_values_by_area_type(self.DEVELOPING))

    @property
    def average_emerging(self):
        return self._average(self._filter_observations_values_by_area_type(self.EMERGING))

    @property
    def median_emerging(self):
        return self._median(self._filter_observations_values_by_area_type(self.EMERGING))

    def _average(self, values):
        if len(values) == 0:
            return 0
        return reduce(lambda sum, value: sum + value, values, 0) / float(len(values))

    def _median(self, values):
        values.sort()
        half = len(values) / 2
        if len(values) == 0:
            return 0
        if len(values) % 2 == 0:
            return self._average([values[half - 1], values[half]])
        else:
            return values[half]

    def _get_observations_without_unknown_values(self):
        return [obs for obs in self._observations if obs.value != ""]  # avoids unknown values

    def _observations_values(self):
        observations = self._get_observations_without_unknown_values()
        return [obs.value for obs in observations]

    def _filter_observations_values_by_area_type(self, area_type):
        observations = self._get_observations_without_unknown_values()
        return [obs.value for obs in observations if obs.area_type == area_type]

    def to_dict(self):
        return {
            'average': self.average,
            'median': self.median,
            'average_developing': self.average_developing,
            'median_developing': self.median_developing,
            'average_emerging': self.average_emerging,
            'median_emerging': self.median_emerging
        }
