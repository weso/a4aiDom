__author__ = 'Herminio'

from webindex.domain.model.observation.visualisation import Visualisation


class GroupedByAreaVisualisation(object):
    """
    GroupedByAreaVisualisation entity
    """

    def __init__(self, area_codes, observations):
        """
        Constructor for GroupedByAreaVisualisation

        Args:
            area_codes (list of str): Iso3 codes for the areas to group by
            observations (list of Observation): Observations to filter by area
        """
        self._area_codes = area_codes
        self._observations = observations

    def observation_by_area(self, area_code):
        """
        Returns observations of a area code

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
        dict = {}
        if self._area_codes is None or len(self._area_codes) == 0:
            dict['ALL'] = \
                    Visualisation(observations=self._observations).to_dict()
        else:
            for area_code in self._area_codes:
                dict[area_code] = \
                    Visualisation(observations=self.observation_by_area(area_code)).to_dict()
        return dict
