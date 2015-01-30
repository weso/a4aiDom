__author__ = 'guillermo'


from webindex.domain.model.observation.observation import Repository, create_observation
from webindex.domain.model.observation.year import Year
from infrastructure.errors.errors import IndicatorRepositoryError, AreaRepositoryError
from config import port, db_name, host
from .mongo_connection import connect_to_db
from .indicator_repository import IndicatorRepository
from .area_repository import AreaRepository
from utils import success, normalize_group_name
from .visualization_repository import VisualizationRepository
from .ranking_repository import RankingRepository
import random


class ObservationRepository(Repository):
    def __init__(self, url_root):
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._indicator = IndicatorRepository(url_root=url_root)
        self._area = AreaRepository(url_root=url_root)
        self._visualization = VisualizationRepository(url_root=url_root)
        self._ranking = RankingRepository(url_root=url_root)
        self._url_root = url_root

    def find_visualisations(self, indicator_code=None, area_code=None, year=None, max_bars=7):
        observations = self.find_observations(indicator_code, area_code, year)

        # Ranking bar chart and general (ALL) map
        barChart = self.find_observations(indicator_code, "ALL", year)

        # Get list of countries
        queryCountries = "ALL"

        if observations["success"] and area_code is not None and area_code != "ALL":
            areas = self.get_countries_by_code_name_or_income(area_code)

            queryCountries = areas["countries"]

        aux_data = self.get_visualisations(observations, indicator_code, area_code, year, max_bars)

        byCountry = aux_data["byCountry"]
        secondVisualisation = aux_data["visualisations"]
        countries = aux_data["countries"]
        selectedRegion = aux_data["region"]
        years = self.get_year_array()
        full_observations = self.find_observations(indicator_code, selectedRegion, year)

        years = years["data"] if years["success"] else []

        statistics = self.get_statistic_values(observations)
        globalStatistics = self.get_statistic_values(barChart)

        # continents
        continents = self._area.find_continents(None)

        if continents["success"]:
            data = continents["data"]
            continents = {}

            for datum in data:
                code = datum["iso3"]
                name = datum["name"]

                continents[code] = name

        if barChart["success"] and observations["success"]:
            # set selected countries
            for observation in barChart["data"]:
                if queryCountries == "ALL":
                   observation["selected"] = True
                else:
                    code = observation["code"]
                    observation["selected"] = code in queryCountries

            rankings = self._ranking.find_rankings(year)
            self.set_observation_rankings(observations["data"], rankings)
            self.set_observation_rankings(full_observations["data"], rankings)

            observations["data"] = {
                "observations": observations["data"],
                "observationsByCountry": self.set_observations_by_country(observations["data"]),
                "bars": barChart["data"],
                "secondVisualisation": secondVisualisation,
                "statistics": statistics,
                "globalStatistics": globalStatistics,
                "byCountry": byCountry,
                "years": reversed(years),
                "continents": continents,
                "countries": countries,
                "region": selectedRegion,
                "fullObservations": full_observations["data"]
            }

        return observations

    def get_statistic_values(self, observations):
         # mean and median
        mean = 0
        median = []

        for observation in observations["data"]:
            value = observation["values"][0]

            mean += value
            median.append(value)

        length = len(observations["data"])
        mean = 0 if length <= 0 else mean * 1.0 / length
        median = self.getMedian(median)

        mean = round(mean, 2)
        median = round(median, 2)

        # higher and lower
        higher = observations["data"][0] if length > 0 else ""
        lower = observations["data"][length - 1] if length > 0 else ""

        return {
            "mean": mean,
            "median": median,
            "higher": higher,
            "lower": lower
        }

    def set_observations_by_country(self, observations):
        obj = {}

        for observation in observations:
            area = observation["area"]
            obj[area] = observation

        return obj

    def set_observation_rankings(self, observations, rankings):
        rankings = rankings["values"]
        rankingList = {}

        for ranking in rankings:
            area = ranking["area"]
            rankingList[area] = ranking

        for observation in observations:
            area = observation["area"]
            extra = rankingList[area]

            observation["extra"] = extra

    def get_visualisations(self, observations, indicator_code, area_code, year, max_bars):
        region = "ALL"

        if observations["success"] and area_code is not None and area_code != "ALL":
            areas = self.get_countries_by_code_name_or_income(area_code)

            queryCountries = areas["countries"]
            areas = areas["areas"]

            if areas is None:
                return self._area.area_error(area_code)

            previousRegion = areas[0]
            sameRegion = True

            for area in areas:
                if area != previousRegion:
                    sameRegion = False
                    break
                previousRegion = area

            region = previousRegion if sameRegion else "ALL"

        regionObservations = self.find_observations(indicator_code, region, year)

        # Several countries bar chart
        if regionObservations["success"]:
            data1 = observations["data"]
            data2 = regionObservations["data"]

            #if len(data2) < max_bars - len(data1):
            #    data2 = data2 + self.find_observations(indicator_code, "ALL", year)["data"]

            processedCountries = []

            # Set selected field
            for observation in data1:
                observation["selected"] = True
                processedCountries.append(observation["code"])

            index = 0
            right = 0
            left = 0
            top = len(data2) - 1

            right_stopped = False
            left_stopped = False

            # data is completed with countries of the region (higher and lower)
            while len(data1) < max_bars:
                if right_stopped and left_stopped:
                    break

                if index % 2 == 0:
                    if right < len(data2):
                        if data2[right]["code"] not in processedCountries:
                            data1.append(data2[right])
                            processedCountries.append(data2[right]["code"])
                        right += 1
                    else:
                        right_stopped = True
                else:
                    pos = top - left
                    if pos >= 0 and pos < len(data2):
                        if data2[pos]["code"] not in processedCountries:
                            data1.append(data2[pos])
                            processedCountries.append(data2[pos]["code"])
                        left += 1
                    else:
                        left_stopped = True

                index += 1

            def sort_by_value(a, b):
                a_rank = a["ranked"]
                b_rank = b["ranked"]

                return cmp(a_rank, b_rank)

            data1.sort(sort_by_value)

            for observation in data1:
                value = observation["value"]
                scored = observation["scored"]
                normalized = observation["normalized"]

                if value is not None:
                    observation["value"] = round(value, 2)

                if scored is not None:
                    observation["scored"] = round(scored, 2)

                if normalized is not None:
                    observation["normalized"] = round(normalized, 2)

            # Several countries line chart

            # Get selected countries from previous query
            selectedCountries = []
            selectedCountriesString = ""
            countries = {}

            for observation in data1:
                country = observation["area"]
                selectedCountries.append(country)

                if selectedCountriesString != "":
                    selectedCountriesString += ","

                selectedCountriesString += country

                country_object = self._area.find_countries_by_code_or_income(country)
                countries[country] = country_object["data"]

            byCountry = self._visualization.get_visualizations_in_object(indicator_code, selectedCountries)

            if area_code == "ALL":
                visualisations = self.find_observations(indicator_code, selectedCountriesString, year)
                visualisations = visualisations["data"] if visualisations["success"] else []

                # Set continent info
                for observation in visualisations:
                    area = observation["area"]
                    area = self._db["areas"].find({ "iso3": area })

                    for element in area:
                        observation["continent"] = element["area"]
            else:
                visualisations = self._visualization.get_visualizations(indicator_code, selectedCountries)

            return {
                "byCountry": byCountry,
                "visualisations": visualisations,
                "countries": countries,
                "region": region
            }

        return {
            "byCountry": {},
            "visualisations": [],
            "countries": [],
            "region": "ALL"
        }

    def find_observations(self, indicator_code=None, area_code=None, year=None):
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

        #return success(observation_list)
        return ObservationDocumentAdapter().transform_to_observation_list(observation_list)

    def find_linked_observations(self):
        return success([obs for obs in self._db['linked_observations'].find()])

    def get_indicators_by_code(self, code):
        codes = code.upper().strip().split(",")

        for code in codes:
            # Check that the indicator exists
            indicator = self._db['indicators'].find_one({"indicator": code})

            if indicator is None:
                return None

        return {"indicator": {"$in": codes}}

    def get_countries_by_code_name_or_income(self, code):
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
        if year is None:
            return None

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
        years = self._db['observations'].distinct("year")
        years.sort(reverse = True)

        year_list = []

        for year in years:
            year_list.append({
                "value": year
            })

        #return success(year_list)
        return YearDocumentAdapter().transform_to_year_list(year_list)

    def get_year_array(self):
        years = self._db['observations'].distinct("year")
        years.sort(reverse=True)

        return success(years)

    # def observation_uri(self, observation):
    #     indicator_code = observation["indicator"]
    #     area_code = observation["area"]
    #     year = observation["year"]
    #     observation["uri"] = "%sobservations/%s/%s/%s" % (self._url_root,
    #                                                       indicator_code, area_code, year)

    def set_observation_country_and_indicator_name(self, observation):
        indicator_code = observation["indicator"]
        area_code = observation["area"]

        indicator = self._db["indicators"].find_one({"indicator": indicator_code})
        area = self._db["areas"].find_one({"iso3": area_code})

        observation["indicator_name"] = indicator["name"]
        observation["area_name"] = area["name"]

    def insert_observation(self, observation, observation_uri=None, area_iso3_code=None, indicator_code=None,
                           year_literal=None, area_name=None, area_code=None, indicator_name=None, previous_value=None,
                           year_of_previous_value=None, republish=True, provider_name="WF (Web Foundation)",
                           provider_url="http://webfoundation.org/", short_name=None,
                           area_type=None, tendency=1):  # Refactor please...
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
        observation_dict['indicator'] = normalize_group_name(indicator_code)
        observation_dict['indicator_name'] = indicator_name
        observation_dict['value'] = observation.value
        observation_dict['year'] = str(observation.year.value)
        observation_dict['uri'] = observation_uri
        # observation_dict['previous_value'] = self._build_previous_value_object(previous_value,
        #                                                                        year_of_previous_value,
        #                                                                        propper_values_content)
        observation_dict['republish'] = republish
        observation_dict['continent'] = area_code
        observation_dict['short_name'] = short_name
        observation_dict['provider_name'] = provider_name
        observation_dict['provider_url'] = provider_url
        observation_dict['tendency'] = tendency
        observation_dict['area_type'] = area_type



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



    def normalize_plain_observation(self, area_iso3_code=None, indicator_code=None, year_literal=None,
                                    normalized_value=None, computation_type=None):
        observation = self.find_observations(indicator_code=indicator_code, area_code=area_iso3_code, year=year_literal)
        if observation["success"] and len(observation["data"]) > 0:
            observation = observation["data"][0]
            if computation_type is None:
                computation_type = "normalized"
            observation[computation_type] = normalized_value
            if computation_type == 'scored':
                observation['values'] = [round(normalized_value, 2)]
            self._db['observations'].update({'_id': observation["_id"]}, {"$set": observation}, upsert=False)


    # @staticmethod
    # def _build_previous_value_object(value_previous_year, year, value_current_year):
    #     if value_previous_year is None or year is None:
    #         return None
    #     else:
    #         # tendency = -1  # Case the values are equal
    #         # if value_current_year < value_previous_year:  # Case current is lower
    #         #     tendency = -1
    #         # elif value_current_year > value_previous_year:  # Case current is higher
    #         #     tendency = 1
    #         return {'value': value_previous_year, 'year': str(year)}
    #         # return {'value': value_previous_year, 'year': str(year), 'tendency': tendency}


    # def update_previous_value_object(self, indicator_code, area_code, current_year,
    #                                  previous_year, previous_value):
    #     observation = self.find_observations(indicator_code=normalize_group_name(indicator_code),
    #                                          area_code=area_code,
    #                                          year=current_year)
    #     if observation["success"] and len(observation["data"]) > 0:
    #         observation = observation["data"][0]
    #         # observation['previous_value'] = {'value': previous_value, 'year': str(previous_year),'tendency': tendency}
    #         observation['previous_value'] = {'value': previous_value, 'year': str(previous_year)}
    #         self._db['observations'].update({'_id': observation["_id"]}, {"$set": observation}, upsert=False)
    #     else:
    #         raise ValueError("Unable to actualize previous value of "
    #                          "observation: Obs not found. {},{},{}".format(indicator_code,
    #                                                                        area_code,
    #                                                                        current_year))


    @staticmethod
    def _look_for_computation(comp_type, observation):
        if observation.obs_type == comp_type:
            return observation.value
        for comp in observation.computations:
            if comp.comp_type == comp_type:
                return comp.value
        return None


    # def group_observations_by_country(self, observations):
    #     years = []
    #
    #     grouped_by_country = {}
    #
    #     for observation in observations:
    #         country = observation["area"]
    #         country_name = observation["area_name"]
    #         year = observation["year"]
    #
    #         if year not in years:
    #             years.append(year)
    #
    #         if country not in grouped_by_country:
    #             grouped_by_country[country] = {
    #                 "name": country_name,
    #                 "code": country,
    #                 "observations": {}
    #             }
    #
    #         grouped_by_country[country]["observations"][year] = observation
    #
    #     years.sort()
    #     series = []
    #     byCountry = {}
    #
    #     for country in grouped_by_country:
    #         values = []
    #
    #         for year in years:
    #             observation = grouped_by_country[country]["observations"][year] if grouped_by_country[country]["observations"][year] else None
    #             value = observation["value"] if observation else None
    #             value = round(value, 2) if value else None
    #             values.append(value)
    #
    #         code = grouped_by_country[country]["code"]
    #
    #         serie = {
    #             "name": grouped_by_country[country]["name"],
    #             "code": code,
    #             "values": values
    #         }
    #
    #         series.append(serie)
    #
    #         byCountry[code] = serie
    #
    #     return {
    #         "series": series,
    #         "years": years,
    #         "byCountry": byCountry
    #     }

    def getMedian(self, numericValues):
        theValues = sorted(numericValues)

        if len(theValues) == 0:
            return 0
        elif len(theValues) % 2 == 1:
            return theValues[(len(theValues)+1)/2 - 1]
        else:
            lower = theValues[len(theValues)/2 - 1]
            upper = theValues[len(theValues)/2]
            return (float(lower + upper)) / 2

    # def get_previous_value(self, observation):
    #     country = observation["area"]
    #     indicator = observation["indicator"]
    #     year = observation["year"]
    #     value = float(observation["value"])
    #     previousYear = str(int(year) - 1)
    #
    #     filter = { "$and": [
    #         {
    #             "area": country
    #         },
    #         {
    #             "indicator": indicator
    #         },
    #         {
    #             "year": previousYear
    #         }
    #     ]}
    #
    #     previousObservation = indicator = self._db["observations"].find_one(filter)
    #
    #     if previousObservation:
    #         previousValue = float(previousObservation["value"])
    #
    #         tendency = 0
    #
    #         if value > previousValue:
    #             tendency = 1
    #
    #         if value < previousValue:
    #             tendency = -1
    #
    #         return {
    #             "value": previousObservation["value"],
    #             "tendency": tendency
    #         }
    #
    #     return None


class ObservationDocumentAdapter(object):
    def transform_to_observation(self, observation_document):
        return create_observation(provider_url=observation_document['provider_url'],
                                  indicator=observation_document['indicator'],
                                  indicator_name=observation_document['indicator_name'],
                                  short_name=observation_document['short_name'],
                                  area=observation_document['area'],
                                  area_name=observation_document['area_name'],
                                  uri=observation_document['uri'],
                                  value=observation_document['value'],
                                  year=observation_document['year'],
                                  provider_name=observation_document['provider_name'],
                                  id=observation_document['_id'],
                                  continent=observation_document['continent'],
                                  tendency=observation_document['tendency'],
                                  republish=observation_document['republish'],
                                  area_type=observation_document['area_type'],)

    def transform_to_observation_list(self, observation_document_list):
        return [self.transform_to_observation(observation_document)
                for observation_document in observation_document_list]


class YearDocumentAdapter(object):
    def transform_to_year(self, year_document):
        return Year(value=year_document['value'])

    def transform_to_year_list(self, year_document_list):
        return [self.transform_to_year(year_document) for year_document in year_document_list]