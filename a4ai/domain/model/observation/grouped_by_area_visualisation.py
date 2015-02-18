from a4ai.domain.model.observation.statistics import Statistics

__author__ = 'Herminio'

from a4ai.domain.model.observation.visualisation import Visualisation


class GroupedByAreaVisualisation(object):
    """
    GroupedByAreaVisualisation entity
    """

    def __init__(self, area_codes, observations, observations_all_areas):
        """
        Constructor for GroupedByAreaVisualisation

        Args:
            area_codes (list of str): Iso3 codes for the areas to group by
            observations (list of Observation): Observations to filter by area
            observations_all_areas (list of Observation): All observations without area filters
        """
        self._area_codes = area_codes
        self._observations = observations
        self._observations_all_areas = observations_all_areas
        self._statistics_all_areas = Statistics(observations_all_areas)

    def observation_by_area(self, area_code):
        """
        Returns observations of an area code

        Args:
            area_code (str): Iso3 code for the area to filter

        Returns:
            list of Observations: Filtered observations by area iso3 code
        """
        return [obs for obs in self._observations
                if obs.area == area_code or obs.continent == area_code]

    def to_dict(self):
        """
        Converts self object to dictionary

        Returns:
            dict: Dictionary representation of self object
        """
        dict = {
            'statistics_all_areas': self._statistics_all_areas.to_dict()
        }
        for area_code in self._area_codes:
            dict[area_code] = \
                Visualisation(observations=self.observation_by_area(area_code)).to_dict_without_all_areas()
        return dict
