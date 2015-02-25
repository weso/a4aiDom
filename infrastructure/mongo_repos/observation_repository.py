from a4ai.domain.model.observation.grouped_by_area_visualisation import GroupedByAreaVisualisation
from a4ai.domain.model.observation.visualisation import Visualisation

__author__ = 'guillermo'


from a4ai.domain.model.observation.observation import Repository, create_observation
from a4ai.domain.model.observation.year import Year
from infrastructure.errors.errors import IndicatorRepositoryError, AreaRepositoryError
from config import port, db_name, host
from .mongo_connection import connect_to_db
from .indicator_repository import IndicatorRepository
from .area_repository import AreaRepository
from utils import success
from a4ai.domain.model.observation.statistics import Statistics


class ObservationRepository(Repository):
    """
    Concrete mongodb repository for Observations.
    """

    def __init__(self, url_root):
        """
        Constructor for ObservationRepository

        Args:
            url_root (str): URL root where service is deployed, it will be used to compose URIs on areas
        """
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._indicator = IndicatorRepository(url_root=url_root)
        self._area = AreaRepository(url_root=url_root)
        self._url_root = url_root

    def find_observations(self, indicator_code=None, area_code=None, year=None, area_type=None):
        """
        Returns all observations that satisfy the given filters

        Args:
            indicator_code (str, optional): The indicator code (indicator attribute in Indicator)
            area_code (str, optional): The area code for the observation
            year (str, optional): The year when observation was observed
            area_type (str, optional): The area type for the observation area
        Returns:
            list of Observation: Observation that satisfy the given filters
        """
        filters = []

        if indicator_code is not None:
            # Check that the indicator exists
            indicator_filter = self.get_indicators_by_code(indicator_code)

            if indicator_filter is None:
                raise IndicatorRepositoryError("No indicator with code " + indicator_code)

            filters.append(indicator_filter)

        if area_code is not None and area_code != "ALL":
            area_filter = self.get_countries_by_code_name_or_income(area_code)

            if area_filter is not None:
                area_filter = area_filter["area_filter"]

            if area_filter is None:
                raise AreaRepositoryError("No area with code " + area_code)

            filters.append(area_filter)

        year_filter = self.get_years(year)

        if year_filter is not None:
            filters.append(year_filter)

        if area_type is not None:
            filters.append({"$or": [
                {"area_type": area_type},
                {"area_type": area_type.upper()},
                {"area_type": area_type.title()}
            ]})

        search = {}

        if len(filters) > 0:
            search = {"$and": filters}

        observations = self._db["observations"].find(search).sort([("ranked", 1)])
        observation_list = []

        for observation in observations:
            # self.observation_uri(observation)
            self.set_observation_country_and_indicator_name(observation)
            observation_list.append(observation)
            # Extra info
            observation["code"] = observation["area"]
            observation["name"] = observation["area_name"]
            #observation["values"] = [ round(observation["value"], 2) ]
            #observation["previous-value"] = self.get_previous_value(observation)

        observations = ObservationDocumentAdapter().transform_to_observation_list(observation_list)
        return sorted(observations, key=lambda obs: obs.ranking)  # returning the observations in ranking order

    def find_linked_observations(self):
        return success([obs for obs in self._db['linked_observations'].find()])

    def get_all_indicators(self):
        """
        Returns all indicators mongodb filter to use in other queries

        Returns:
            dict: The filter for mongodb queries
        """

    def get_indicators_by_code(self, code):
        """
        Returns an indicator mongodb filter to use in other queries

        Args:
            code (str): Indicator code or codes, for many indicator codes, divide them using a ','

        Returns:
            dict: The filter for mongodb queries
        """
        if code.lower() == 'ALL'.lower():  # case does not matter
            return {}

        codes = code.upper().strip().split(",")

        for code in codes:
            # Check that the indicator exists
            indicator = self._db['indicators'].find_one({"indicator": code})

            if indicator is None:
                return None

        return {"indicator": {"$in": codes}}

    def get_countries_by_code_name_or_income(self, code):
        """
        Returns an area mongodb filter to use in other queries

        Args:
            code (str): Area code or area codes, divide them using a ','

        Returns:
            dict: The filter for mongodb queries
        """
        codes = code.split(",")

        country_codes = []
        areas = []

        for code in codes:
            code_upper = code.upper()

            # by ISO3
            countries = self._db["areas"].find({ "$and": [{"iso3": code_upper}, { "area": { "$ne": None } }] })

            # by ISO2
            if countries is None or countries.count() == 0:
                countries = self._db["areas"].find({"iso2": code_upper})

            # by name
            if countries is None or countries.count() == 0:
                countries = self._db["areas"].find({"name": code})

            # by Continent

            if countries is None or countries.count() == 0:
                countries = self._db["areas"].find({"area": code})

            # by Income
            if countries is None or countries.count() == 0:
                countries = self._db["areas"].find({"income": code_upper})

            if countries is None or countries.count() == 0:
                return None

            for country in countries:
                iso3 = country["iso3"]
                country_codes.append(iso3)
                area = country["area"]
                areas.append(area)

        return {
            "area_filter": {"area": {"$in": country_codes}},
            "areas": areas,
            "countries": country_codes
        }

    def get_years(self, year):
        """
        Returns a year mongodb filter to use in other queries

        Args:
            year (str): Year, years or LATEST (last year with observations), divide them using a ','

        Returns:
            dict: The filter for mongodb queries
        """
        if year is None:
            return None

        if year == 'LATEST':
            last_year = self.get_year_list()[0].value
            return {"year": last_year}

        years = year.strip().split(",")

        year_list = []

        for year in years:
            interval = year.split("-")

            if len(interval) == 1 and interval[0].isdigit():
                year_list.append(interval[0])
            elif len(interval) == 2 and interval[0].isdigit() and interval[
                1].isdigit():
                for i in range(int(interval[0]), int(interval[1]) + 1):
                    year_list.append(str(i))

        return {"year": {"$in": year_list}}

    def get_year_list(self):
        """
        Returns all years with observations

        Returns:
            list of Year: All years with observations
        """
        years = self._db['observations'].distinct("year")
        years.sort(reverse = True)

        year_list = []

        for year in years:
            year_list.append({
                "value": year
            })

        return YearDocumentAdapter().transform_to_year_list(year_list)

    def get_year_array(self):
        years = self._db['observations'].distinct("year")
        years.sort(reverse=True)

        return success(years)

    def set_observation_country_and_indicator_name(self, observation):
        """
        Sets country an indicator name to the given observation

        Args:
            observation (dict): Observation in pymongo format
        """
        indicator_code = observation["indicator"]
        area_code = observation["area"]

        indicator = self._db["indicators"].find_one({"indicator": indicator_code})
        area = self._db["areas"].find_one({"iso3": area_code})

        observation["indicator_name"] = indicator["name"]
        observation["area_name"] = area["name"]

    def insert_observation(self, observation, observation_uri=None, area_iso3_code=None, indicator_code=None,
                           year_literal=None, area_name=None, area_code=None, indicator_name=None, previous_value=None,
                           year_of_previous_value=None, republish=True, provider_name="WF (Web Foundation)",
                           provider_url="http://webfoundation.org/", short_name=None, area_type=None,
                           ranking=None, ranking_type=None, indicator_type=None):  # Refactor please...
        """
        It takes the info of indicator and area through the optional params area_iso3_code,
        indicator_code and year_literal
        :param observation:
        :param area_iso3_code:
        :param indicator_code:
        :param year_literal:
        :return:
        """

        observation_dict = {}
        observation_dict['area'] = area_iso3_code
        observation_dict['area_name'] = area_name
        observation_dict['indicator'] = indicator_code
        observation_dict['indicator_name'] = indicator_name
        observation_dict['indicator_type'] = indicator_type
        observation_dict['value'] = observation.value
        observation_dict['year'] = str(observation.year.value)
        observation_dict['uri'] = observation_uri
        observation_dict['republish'] = republish
        observation_dict['continent'] = area_code
        observation_dict['short_name'] = short_name
        observation_dict['provider_name'] = provider_name
        observation_dict['provider_url'] = provider_url
        observation_dict['area_type'] = area_type
        observation_dict['ranking'] = ranking
        observation_dict['ranking_type'] = ranking_type

        self._db['observations'].insert(observation_dict)

    def _look_for_continent_iso3(self, area_iso3_code):
        if 'local_areas_dict' not in self.__dict__:   # Lazy initialization and just one query
            self.local_areas_dict = self._build_local_areas_dict()
        return self.local_areas_dict[area_iso3_code]['area']

    def _look_for_short_name(self, area_iso3_code):
        if 'local_areas_dict' not in self.__dict__:   # Lazy initialization and just one query
            self.local_areas_dict = self._build_local_areas_dict()
        return self.local_areas_dict[area_iso3_code]['short_name']

    def _build_local_areas_dict(self):
        result = {}
        for country in self._area.find_countries(None)['data']:
            result[country['iso3']] = country
        return result

    def update_observation_ranking_type(self, obs, ranking_type):
        self._db['observations'].update({'_id': obs.id}, {"$set": {'ranking_type': ranking_type}}, upsert=False)

    def update_observation_ranking(self, obs, ranking):
        self._db['observations'].update({'_id': obs.id}, {"$set": {'ranking': ranking}}, upsert=False)

    @staticmethod
    def _look_for_computation(comp_type, observation):
        if observation.obs_type == comp_type:
            return observation.value
        for comp in observation.computations:
            if comp.comp_type == comp_type:
                return comp.value
        return None

    def find_observations_statistics(self, indicator_code=None, area_code=None, year=None):
        """
        Returns statitics for observations that satisfy the given filters

        Args:
            indicator_code (str, optional): The indicator code (indicator attribute in Indicator)
            area_code (str, optional): The area code for the observation
            year (str, optional): The year when observation was observed
        Returns:
            list of Statistics: Observations statistics that satisfy the filters
        """
        return StatisticsDocumentAdapter().transform_to_statistics(
            self.find_observations(indicator_code=indicator_code, area_code=area_code, year=year))

    def find_observations_visualisation(self, indicator_code=None, area_code=None, year=None):
        """
        Returns visualisation for observations that satisfy the given filters

        Args:
            indicator_code (str, optional): The indicator code (indicator attribute in Indicator)
            area_code (str, optional): The area code for the observation
            year (str, optional): The year when observation was observed
        Returns:
            Visualisation: Observations visualisation that satisfy the filters
        """
        observations = self.find_observations(indicator_code=indicator_code, area_code=area_code, year=year)
        observations_all_areas = self.find_observations(indicator_code=indicator_code, area_code='ALL', year=year)

        return VisualisationDocumentAdapter().transform_to_visualisation(observations, observations_all_areas)

    def find_observations_grouped_by_area_visualisation(self, indicator_code=None, area_code=None, year=None):
        """
        Returns grouped by area visualisation for observations that satisfy the given filters

        Args:
            indicator_code (str, optional): The indicator code (indicator attribute in Indicator)
            area_code (str, optional): The area code for the observation
            year (str, optional): The year when observation was observed
        Returns:
            GroupedByAreaVisualisation: Observations grouped by area visualisation that satisfy the filters
        """
        area_code_splitted = area_code.split(',') if area_code is not None else None
        observations = self.find_observations(indicator_code=indicator_code, area_code=area_code, year=year)
        observations_all_areas = self.find_observations(indicator_code=indicator_code, area_code='ALL', year=year)
        if area_code_splitted is None or len(area_code_splitted) == 0 or area_code == 'ALL':
            areas = AreaRepository(url_root=self._url_root).find_countries(order="iso3")
            area_code_splitted = [area.iso3 for area in areas]

        return GroupedByAreaVisualisationDocumentAdapter().transform_to_grouped_by_area_visualisation(
            area_codes=area_code_splitted,
            observations=observations,
            observations_all_areas=observations_all_areas
        )


class ObservationDocumentAdapter(object):
    """
    Adapter class to transform observations from PyMongo format to Domain observations objects
    """
    def transform_to_observation(self, observation_document):
        """
        Transforms one single observation

        Args:
            observation_document (dict): Observation document in PyMongo format

        Returns:
            Observation: Observation object with the data in observation_document
        """
        return create_observation(provider_url=observation_document['provider_url'],
                                  indicator=observation_document['indicator'],
                                  indicator_name=observation_document['indicator_name'],
                                  indicator_type=observation_document['indicator_type'],
                                  short_name=observation_document['short_name'],
                                  area=observation_document['area'],
                                  area_name=observation_document['area_name'],
                                  uri=observation_document['uri'],
                                  value=observation_document['value'],
                                  year=observation_document['year'],
                                  provider_name=observation_document['provider_name'],
                                  id=observation_document['_id'],
                                  continent=observation_document['continent'],
                                  republish=observation_document['republish'],
                                  area_type=observation_document['area_type'],
                                  ranking=observation_document['ranking'],
                                  ranking_type=observation_document['ranking_type'])

    def transform_to_observation_list(self, observation_document_list):
        """
        Transforms a list observations

        Args:
            observation_document_list (list): Observation document list in PyMongo format

        Returns:
            Observation: A list of observations with the data in observation_document_list
        """
        return [self.transform_to_observation(observation_document)
                for observation_document in observation_document_list]


class YearDocumentAdapter(object):
    """
    Adapter class to transform years from PyMongo format to Domain Year objects
    """
    def transform_to_year(self, year_document):
        """
        Transforms one single year

        Args:
            year_document (dict): Year document in PyMongo format

        Returns:
            Year: Year object with the data in year_document
        """
        return Year(value=year_document['value'])

    def transform_to_year_list(self, year_document_list):
        """
        Transforms a list of years

        Args:
            year_document_list (list): Year document list in PyMongo format

        Returns:
            list of Year: A list of years with the data in year_document_list
        """
        return [self.transform_to_year(year_document) for year_document in year_document_list]


class StatisticsDocumentAdapter(object):
    """
    Adapter class to transform observations from PyMongo format to Domain Statistics objects
    """
    def transform_to_statistics(self, observations):
        """
        Transforms a list of observations into statistics

        Args:
            observations (list): Observation document list in PyMongo format

        Returns:
            Statistics: Statistics object with statistics data for the given observations
        """
        return Statistics(observations)


class VisualisationDocumentAdapter(object):
    """
    Adapter class to transform observations from PyMongo format to Domain Visualisation objects
    """
    def transform_to_visualisation(self, observations, observations_all_areas):
        """
        Transforms a list of observations into visualisation

        Args:
            observations (list of Observation): Observation list
            observations_all_areas (list of Observation): Observations list with all areas without filter applied

        Returns:
            Visualisation: Visualisation object for the given observations
        """
        return Visualisation(observations, observations_all_areas)


class GroupedByAreaVisualisationDocumentAdapter(object):
    """
    Adapter class to transform observations from PyMongo format to Domain GroupedByAreaVisualisation objects
    """
    def transform_to_grouped_by_area_visualisation(self, area_codes, observations, observations_all_areas):
        """
        Transforms a list of observations into GroupedByAreaVisualisation

        Args:
            area_codes (list of str): Iso3 codes for the area to group by
            observations (list of Observation): Observation list
            observations_all_areas (list of Observation): Observations list with all areas without filter applied

        Returns:
            GroupedByAreaVisualisation: GroupedByAreaVisualisation object for the given observations
        """
        return GroupedByAreaVisualisation(area_codes, observations, observations_all_areas)