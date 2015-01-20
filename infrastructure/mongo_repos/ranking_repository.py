__author__ = 'Dani'

from config import port, db_name, host
from .mongo_connection import connect_to_db


class RankingRepository(object):
    """
    It does not have inheritance relationships.
    It does not represent an entity, but an abstract group of data handy only for visualizations.
    """


    def __init__(self, url_root):
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root

    def find_rankings(self, year):
        rankings = self._db['rankings'].find({"year": year})

        result = None

        for ranking in rankings:
            result = ranking
            ranking["values"].sort(key = lambda x: x["rank"])

        return result

    def insert_ranking(self, groups_of_observations):
        """
        It expects in groups_of_observations a list of list of dictionaries:
        The higher list contains list of 5 dictionaries, and each dictionary represents an observation.
        The observations should be referred to the same year and the same country, and they should
        be 5 because their respective indicators should be Index and the 4 suindexes.

        We should check that every observation is referred to the same iso and year,
        but we will assume that

        """
        ranking_dict = {}
        ranking_dict['year'] = self._get_rank_year(groups_of_observations[0][0])
        indicators = self._build_indicators_list(groups_of_observations[0])
        ranking_dict['indicators'] = self._build_indicators_list(groups_of_observations[0])
        ranking_dict['values'] = self._build_values_list(groups_of_observations, indicators)

        self._db['rankings'].insert(ranking_dict)


    @staticmethod
    def _get_rank_year(observation_dict):
        """
        It is expecting a dictionary with the form of an observation dict
        :param observation_dict:
        :return:
        """
        return str(observation_dict['year'])

    @staticmethod
    def _build_indicators_list(group_of_observations):
        if len(group_of_observations) != 5:
            raise ValueError("Unexpected number of observations while "
                             "building a ranking document: {}".format(len(group_of_observations)))
        result = []
        for observation_dict in group_of_observations:
            ind_dict = {}
            ind_dict['code'] = observation_dict['indicator']
            ind_dict['name'] = observation_dict['indicator_name']
            result.append(ind_dict)
        return result

    def _build_values_list(self, group_of_observations, indicators_dicts):
        result = []
        for a_group in group_of_observations:
            result.append(self._build_ranking_dict_for_a_country(a_group, indicators_dicts))
        return result

    def _build_ranking_dict_for_a_country(self, country_obs_dicts_group, indicators_dicts):
        result = {}
        result['area'] = country_obs_dicts_group[0]['area']
        result['name'] = country_obs_dicts_group[0]['area_name']
        result['rank'] = self._look_for_country_rank_in_obs_group(country_obs_dicts_group)
        for indicator in indicators_dicts:
            indicator_code = indicator['code']
            result[indicator_code] = round(self._look_the_scored_of_a_concrete_indicator(indicator_code,
                                                                                         country_obs_dicts_group), 2)
        return result

    @staticmethod
    def _look_the_scored_of_a_concrete_indicator(indicator_code, country_obs_dicts_groups):
        for obs_dict in country_obs_dicts_groups:
            if obs_dict['indicator'] == indicator_code:
                if obs_dict['scored'] is not None:
                    return obs_dict['scored']
                else:
                    return obs_dict['value']
        raise ValueError("Unable to find {} scored value"
                         " for {} while building ranking".format(indicator_code,
                                                                 country_obs_dicts_groups[0]['area_name']))


    @staticmethod
    def _look_for_country_rank_in_obs_group(list_of_obs_dicts):
        for obs_dict in list_of_obs_dicts:
            print obs_dict['indicator']
            if obs_dict['indicator'] == "INDEX":  # TODO: Dangerous hard-coded value
                if obs_dict['ranked'] is not None:
                    return obs_dict['ranked']
        raise ValueError("Unable to find index rank while building a ranking document. ")




