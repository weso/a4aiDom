__author__ = 'Herminio'


class Statistics(object):
    """
    Statistics entity

    Attributes:
        average (float): Average value for given observations
        median (float): Median value for given observations
        average_developing (float): Average value for developing areas observations
        average_emerging (float): Average value for emerging areas observations
        median_developing (float): Median value for developing areas observations
        median_emerging (float): Median value for emerging areas observations
        max (float): Max value for given observations
        min (float): Min value for given observations
    """
    DEVELOPING = "Developing"
    EMERGING = "Emerging"

    def __init__(self, observations):
        """
        Constructor for Statistics, in order to calculate the statistics a set of observations is needed

        Args:
            observations (list of Observation): list of Observations to calculate the statistics
        """
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

    @property
    def max(self):
        return max(self._observations_values())

    @property
    def min(self):
        return min(self._observations_values())

    def _average(self, values):
        """
        Calculates the average of a set of values

        Args:
            values (list of float): Values to calculate average
        Returns:
            float: Average of the given values
        """
        if len(values) == 0:
            return 0
        return reduce(lambda sum, value: sum + value, values, 0) / float(len(values))

    def _median(self, values):
        """
        Calculates the median of a set of values

        Args:
            values (list of float): Values to calculate average

        Returns:
            float: Median of the given values
        """
        values.sort()
        half = len(values) / 2
        if len(values) == 0:
            return 0
        if len(values) % 2 == 0:
            return self._average([values[half - 1], values[half]])
        else:
            return values[half]

    def _get_observations_without_unknown_values(self):
        """
        Filters observations with blank value, they are not considered in calculation

        Note:
            The reason why these observations are discarded is because there is not a value known
            for the observation's area and indicator. So actually, they are not useful in these
            calculations. Equalize to zero is not a solution because: there are already another
            observations with value zero and they modify the resulting value

        Returns:
            list of Observation: Filtered observations without blank values
        """
        return [obs for obs in self._observations if obs.value != ""]  # avoids unknown values

    def _observations_values(self):
        """
        Extract values from Observation entity

        Returns:
            list of float: Values of the observations in self
        """
        observations = self._get_observations_without_unknown_values()
        return [obs.value for obs in observations]

    def _filter_observations_values_by_area_type(self, area_type):
        """
        Filters values by a given area type

        Args:
            area_type (str): Area type to filter observations
        """
        observations = self._get_observations_without_unknown_values()
        return [obs.value for obs in observations if obs.area_type == area_type]

    def to_dict(self):
        """
        Converts self object to dictionary

        Returns:
            dict: Dictionary representation of self object
        """
        return {
            'average': self.average,
            'median': self.median,
            'average_developing': self.average_developing,
            'median_developing': self.median_developing,
            'average_emerging': self.average_emerging,
            'median_emerging': self.median_emerging,
            'max': self.max,
            'min': self.min
        }
