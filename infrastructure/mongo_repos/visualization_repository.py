__author__ = 'Dani'

from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import normalize_group_name


class VisualizationRepository(object):
    """
    It does not have inheritance relationships.
    It does not represent an entity, but an abstract group of data handy only for visualizations.
    """


    def __init__(self, url_root):
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root
        self._FIRST_YEAR, self._LAST_YEAR = self.get_first_and_last_year()

    def get_visualizations_in_object(self, indicator_code, countries):
        visualizations = self.get_visualizations(indicator_code, countries)

        obj = {}

        for observation in visualizations:
            area = observation["area"]
            obj[area] = observation

        return obj

    def get_visualizations(self, indicator_code, countries):
        filter = {
            "$and": [
                {
                    "indicator": indicator_code
                },
                {
                    "area": {
                        "$in": countries
                    }
                }
            ]
        }

        return self._db['visualizations'].find(filter)

    @staticmethod
    def get_first_and_last_year():
        # I am still thinking if im going to consume an API method to discover this data
        # or config, or constants, or params or what...
        return 2007, 2013

    def insert_visualization(self, observations, area_iso3_code, area_name, indicator_code, indicator_name,
                             provider_name, provider_url, short_name, continent, republish, tendency):
        visualization_dict = {}
        visualization_dict['area'] = area_iso3_code
        visualization_dict['area_name'] = area_name
        visualization_dict['indicator'] = normalize_group_name(indicator_code)
        visualization_dict['indicator_name'] = indicator_name
        visualization_dict['values'] = self._build_values_object(observations)
        visualization_dict['provider_name'] = provider_name
        visualization_dict['provider_url'] = provider_url
        visualization_dict['short_name'] = short_name
        visualization_dict['continent'] = continent
        visualization_dict['republish'] = republish
        visualization_dict['tendency'] = tendency

        self._db['visualizations'].insert(visualization_dict)

    def insert_built_visualization(self, array_values, area_iso3_code, area_name, indicator_code, indicator_name,
                                   provider_name, provider_url, short_name, continent, republish, tendency):
        """
        Handy for inserting in mongo a visualization document by directly receiving the array "values" built.


        :param array_values:
        :param area_iso3_code:
        :param area_name:
        :param indicator_code:
        :param indicator_name:
        :return:
        """
        visualization_dict = {}
        visualization_dict['area'] = area_iso3_code
        visualization_dict['area_name'] = area_name
        visualization_dict['indicator'] = normalize_group_name(indicator_code)
        visualization_dict['indicator_name'] = indicator_name
        visualization_dict['values'] = array_values
        visualization_dict['provider_name'] = provider_name
        visualization_dict['provider_url'] = provider_url
        visualization_dict['short_name'] = short_name
        visualization_dict['continent'] = continent
        visualization_dict['republish'] = republish
        visualization_dict['tendency'] = tendency
        self._db['visualizations'].insert(visualization_dict)


    def _build_values_object(self, observations):
        """
        It receives a list of observations and return an array with as many positions as the total number
        of available years stored in the system. Each position of the array will represent the value of a year.
        Example: if we had 2002, 2003, 2004, 2005 and 2006 as available years and we receive and array of 3
        observations with years and values as follows: 2003 --> 3, 2004 --> 4, 2006 --> 6, then the method
         will return an array such as: [None, 3, 4, None, 6]

        :param observations:
        :return:
        """
        type_of_obs_desirable = self._look_for_type_of_obs_desirable(observations)
        result = []
        for i in range(self._FIRST_YEAR, self._LAST_YEAR + 1):
            # The next method could return None. NP =)
            value = self._look_for_a_value_for_a_year(i, observations, type_of_obs_desirable)
            if value is not None:
                value = round(value, 2)
            result.append(value)
        return result

    @staticmethod
    def _look_for_type_of_obs_desirable(observations):
        if len(observations) == 0:
            return None
        for comp in observations[0].computations:
            if comp.comp_type == "scored":
                return "scored"
        for comp in observations[0].computations:
            if comp.comp_type == "normalized":
                return "normalized"
        else:
            return None

    @staticmethod
    def _look_for_a_value_for_a_year(year_target, observations, desired_type):
        for obs in observations:
            year_obs = obs.ref_year.value
            if str(year_obs) == str(year_target):
                if desired_type is None:
                    return obs.value
                elif desired_type in ['scored', 'normalized']:
                    for comp in obs.computations:
                        if comp.comp_type == desired_type:
                            return comp.value
                    raise ValueError("Not found but expected computation {} for an obs".format(desired_type))


        return None  # No observation found for target_year in this list
