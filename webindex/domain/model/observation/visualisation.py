__author__ = 'Herminio'

from webindex.domain.model.observation.statistics import Statistics


class Visualisation(object):
    """
    Visualisations entity

    Attributes:
        observations (list of Observations): Observations for the visualization
        statistics (Statistics): Statistics for the visualization
    """

    def __init__(self, observations):
        """
        Constructor for Visualization

        Args:
            observations (list of Observation): Observation to store and calculate statistics
        """
        self._observations = observations
        self._statistics = Statistics(observations)

    @property
    def observations(self):
        return self._observations

    @property
    def statistics(self):
        return self._statistics

    def to_dict(self):
        """
        Converts self object to dictionary

        Returns:
            dict: Dictionary representation of self object
        """
        return {
            'observations': [obs.to_dict() for obs in self.observations],
            'statistics': self.statistics.to_dict()
        }