from a4ai.domain.model.area.area_info import AreaInfo

__author__ = 'guillermo'

from infrastructure.errors.errors import AreaRepositoryError
from a4ai.domain.model.area import area
from a4ai.domain.model.area.country import create_country
from a4ai.domain.model.area.region import create_region
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import uri


class AreaRepository(area.Repository):
    """
    Concrete mongodb repository for Areas.
    """

    def __init__(self, url_root):
        """
        Constructor for AreaRepository

        Args:
            url_root (str): URL root where service is deployed, it will be used to compose URIs on areas
        """
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root

    def find_by_name(self, area_name):
        """
        Finds one area by its name

        Args:
            area_name (str): Name of the area to query, case insensitive

        Returns:
            Area: The first area with the given name

        Raises:
            AreaRepositoryError: If there is not an area with the given name
        """
        area = self._db['areas'].find_one({"$or": [
            {"name": area_name},
            {"name": area_name.upper()},
            {"name": area_name.title()},
            {"name": area_name.lower()},
        ]})
        if area is None:
            raise AreaRepositoryError("No area with name " + area_name)
        self.area_uri(area)
        return AreaDocumentAdapter().transform_to_area(area)

    def find_countries_by_code_or_income(self, area_code_or_income):
        """
        Finds countries by code or income if no area is found it will search by income

        Args:
            area_code_or_income (str): iso3, iso2, name or income(for a list of countries)

        Returns:
            Region with the given countries appended or a list of countries

        Raises:
            AreaRepositoryError: If not countries nor areas are found

        """
        area_code_or_income_upper = area_code_or_income.upper()
        area = self._db['areas'].find_one({"$or": [
            {"iso3": area_code_or_income},
            {"iso3": area_code_or_income_upper},
            {"iso2": area_code_or_income},
            {"iso2": area_code_or_income_upper},
            {"name": area_code_or_income}]})

        if area is None:
            # Find if code is an income code
            # TODO: This is not working, order by is needed on method call
            countries = self.find_countries_by_continent_or_income_or_type(area_code_or_income_upper)
            if countries is None:
                raise AreaRepositoryError("No countries for code " + area_code_or_income)
            else:
                return countries

        self.set_continent_countries(area)
        self.area_uri(area)
        area["short_name"] = area["name"]

        return AreaDocumentAdapter().transform_to_area(area)

    def find_countries_by_continent_or_income_or_type(self, continent_or_income_or_type, order="iso3"):
        """
        Finds a list of countries by its continent, income or type

        Args:
            continent_or_income_or_type (str): Code for continent, income or type
            order (str, optional): Attribute key to sort, default to iso3

        Returns:
            list of Country: countries with the given continent, income or type

        Raises:
            AreaRepositoryCountry: If no countries are found
        """
        order = "name" if order is None else order
        continent_or_income_or_type_upper = continent_or_income_or_type.upper()
        continent_or_income_or_type_title = continent_or_income_or_type.title()  # Nowadays, this is the way it
                                                                                 # is stored
        countries = self._db['areas'].find({"$or": [
            {"area": continent_or_income_or_type},
            {"income": continent_or_income_or_type_upper},
            {"type": continent_or_income_or_type_title}]},).sort(order, 1)

        if countries.count() == 0:
            raise AreaRepositoryError("No countries for code " + continent_or_income_or_type)

        country_list = []

        for country in countries:
            self.set_continent_countries(country)
            self.area_uri(country)
            country_list.append(country)

        return CountryDocumentAdapter().transform_to_country_list(country_list)

    def find_areas(self, order):
        """
        Finds all areas in the repository

        Args:
            order (str): Attribute of Area to sort by

        Returns:
            list of Area: All regions and countries
        """
        order = "name" if order is None else order
        continents = self.find_continents(order)
        countries = self.find_countries(order)

        return continents + countries

    def find_continents(self, order):
        """
        Finds all regions in the repository

        Args:
            order (str): Attribute of Region to sort by

        Returns:
            list of Region: All regions
        """
        order = "name" if order is None else order
        areas = self._db['areas'].find({"area": None}).sort(order, 1)
        continents = []

        for continent in areas:
            continent["short_name"] = continent["name"]
            self.set_continent_countries(continent)

            self.area_uri(continent)
            continents.append(continent)

        return RegionDocumentAdapter().transform_to_region_list(continents)

    def find_countries(self, order):
        """
        Finds all countries in the repository

        Args:
            order (str): Attribute of Country to sort by

        Returns:
            list of Country: All countries
        """
        order = "name" if order is None else order
        countries = self._db['areas'].find({"area": {"$ne": None}}).sort(order, 1)
        country_list = []

        for country in countries:
            self.area_uri(country)
            country_list.append(country)

        return CountryDocumentAdapter().transform_to_country_list(country_list)

    def set_continent_countries(self, area):
        """
        Sets the countries that belong to a region

        Args:
            area (str): Area name

        Returns:

        """
        iso3 = area["iso3"]
        countries = self._db['areas'].find({"area": iso3}).sort("name", 1)
        country_list = []

        for country in countries:
            self.area_uri(country)
            country_list.append(country)

        if countries.count() > 0:
            area["countries"] = country_list

    def area_uri(self, area):
        """
        Sets the URI to the given area

        Args:
            area (Area): Area to set the URI
        """
        field = "iso3" if area["iso3"] is not None else "name"
        uri(url_root=self._url_root, element=area, element_code=field,
            level="areas")

    def enrich_country(self, iso3, indicator_list):
        """
        Enriches country data with indicator info

        Note:
            The input indicator_list must contain the following attributes: indicator_code, year, value,
            provider_name and provider_value
        Args:
            iso3 (str): Iso3 of the country for which data is going to be appended.
            indicator_list (list of Indicator): Indicator list with the attributes in the note.
        """
        info_dict = {}
        for indicator in indicator_list:
            info_dict[indicator.indicator_code] = {
                "year": indicator.year,
                "value": indicator.value,
                "provider": {
                    "name": indicator.provider_name,
                    "url": indicator.provider_url
                }
            }

        self._db["areas"].update({"iso3": iso3}, {"$set": {"info": info_dict}})


class CountryDocumentAdapter(object):
    """
    Adapter class to transform countries from PyMongo format to Domain country objects
    """
    def transform_to_country(self, country_document):
        """
        Transforms one single country

        Args:
            country_document (dict): Country document in PyMongo format

        Returns:
            Country: A country object with the data in country_document
        """
        info=AreaInfoDocumentAdapter().transform_to_area_info_list(country_document['info'])\
                if 'info' in country_document else []
        return create_country(name=country_document['name'], short_name=country_document['short_name'],
                              area=country_document['area'], uri=country_document['uri'],
                              iso3=country_document['iso3'], iso2=country_document['iso2'],
                              iso_num=country_document['iso_num'], income=country_document['income'],
                              id=country_document['_id'], type=country_document['type'],
                              search=country_document['search'],
                              info=info)

    def transform_to_country_list(self, country_document_list):
        """
        Transforms a list of countries

        Args:
            country_document_list (list): Country document list in PyMongo format

        Returns:
            list of Country: A list of countries with the data in country_document_list
        """
        return [self.transform_to_country(country_document) for country_document in country_document_list]


class RegionDocumentAdapter(object):
    """
    Adapter class to transform regions from PyMongo format to Domain region objects
    """
    def transform_to_region(self, region_document):
        """
        Transforms one single region

        Args:
            region_document (dict): Region document in PyMongo format

        Returns:
            Region: A region object with the data in region_document
        """
        info=AreaInfoDocumentAdapter().transform_to_area_info_list(region_document['info'])\
                if 'info' in region_document else []
        return create_region(name=region_document['name'], short_name=region_document['short_name'],
                             area=region_document['area'], uri=region_document['uri'],
                             iso3=region_document['iso3'], iso2=region_document['iso2'],
                             iso_num=region_document['iso_num'], id=region_document['_id'],
                             search=region_document['search'],
                             countries=CountryDocumentAdapter().transform_to_country_list(region_document['countries']),
                             info=info)

    def transform_to_region_list(self, region_document_list):
        """
        Transforms a list of regions

        Args:
            region_document_list (list): Region document list in PyMongo format

        Returns:
            list of Region: A list of regions with the data in region_document_list
        """
        return [self.transform_to_region(region_document) for region_document in region_document_list]


class AreaDocumentAdapter(object):
    """
    Adapter class to transform areas from PyMongo format to Domain region or country objects
    """
    def transform_to_area(self, area_document):
        """
        Transforms one single area

        Args:
            area_document (dict): Area document in PyMongo format

        Returns:
            A region or country object, depending on the type
        """
        if 'countries' in area_document:
            return RegionDocumentAdapter().transform_to_region(area_document)
        else:
            return CountryDocumentAdapter().transform_to_country(area_document)

    def transform_to_area_list(self, area_document_list):
        """
        Transforms a list of areas

        Args:
            area_document_list (list): Area document list in PyMongo format

        Returns:
            A list of regions or countries, depending on the type
        """
        return [self.transform_to_area(area_document) for area_document in area_document_list]


class AreaInfoDocumentAdapter(object):
    """
    Adapter class to transform area info from PyMongo format to Domain area info objects
    """
    def transform_to_area_info_list(self, area_info_document_dict):
        """
        Transforms a dict with area infos

        Args:
            area_info_document_dict (dict): Area info document dict in PyMongo format

        Returns:
            A list of area infos
        """
        return [AreaInfo(indicator_code=area_info_key,
                         provider_name=area_info_document_dict[area_info_key]['provider']['name'],
                         provider_url=area_info_document_dict[area_info_key]['provider']['url'],
                         value=area_info_document_dict[area_info_key]['value'],
                         year=area_info_document_dict[area_info_key]['year'])
                for area_info_key in area_info_document_dict.keys()]

