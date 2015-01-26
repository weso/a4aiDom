__author__ = 'guillermo'

from webindex.domain.model.area import area
from webindex.domain.model.area.country import create_country
from webindex.domain.model.area.region import create_region
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import error, success, uri


class AreaRepository(area.Repository):
    """Concrete mongodb repository for Areas.
    """

    def __init__(self, url_root):
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root

    def find_countries_by_code_or_income(self, area_code_or_income):
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
                return self.area_error(area_code_or_income)
            else:
                return countries

        self.set_continent_countries(area)
        self.area_uri(area)
        area["short_name"] = area["name"]

        return AreaDocumentAdapter().transform_to_area(area)

    def find_countries_by_continent_or_income_or_type(self, continent_or_income_or_type, order="iso3"):
        order = "name" if order is None else order
        continent_or_income_or_type_upper = continent_or_income_or_type.upper()
        continent_or_income_or_type_title = continent_or_income_or_type.title()  # Nowadays this is the way it
                                                                                 # is stored
        countries = self._db['areas'].find({"$or": [
            {"area": continent_or_income_or_type},
            {"income": continent_or_income_or_type_upper},
            {"type": continent_or_income_or_type_title}]},).sort(order, 1)

        if countries.count() == 0:
            return self.area_error(continent_or_income_or_type)

        country_list = []

        for country in countries:
            self.set_continent_countries(country)
            self.area_uri(country)
            country_list.append(country)

        #return success(country_list)
        return CountryDocumentAdapter().transform_to_country_list(country_list)

    def find_areas(self, order):
        order = "name" if order is None else order
        continents = self.find_continents(order)
        countries = self.find_countries(order)

        return continents + countries

    def find_continents(self, order):
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
        order = "name" if order is None else order
        countries = self._db['areas'].find({"area": {"$ne": None}}).sort(order, 1)
        country_list = []

        for country in countries:
            self.area_uri(country)
            country_list.append(country)

        #return success(country_list)
        return CountryDocumentAdapter().transform_to_country_list(country_list)

    def set_continent_countries(self, area):
        iso3 = area["iso3"]
        countries = self._db['areas'].find({"area": iso3}).sort("name", 1)
        country_list = []

        for country in countries:
            self.area_uri(country)
            country_list.append(country)

        if countries.count() > 0:
            area["countries"] = country_list

    def area_error(self, area_code):
        return error("Invalid Area Code: %s" % area_code)

    def area_uri(self, area):
        field = "iso3" if area["iso3"] is not None else "name"
        uri(url_root=self._url_root, element=area, element_code=field,
            level="areas")


class CountryDocumentAdapter(object):
    def transform_to_country(self, country_document):
        return create_country(name=country_document['name'], short_name=country_document['short_name'],
                              area=country_document['area'], uri=country_document['uri'],
                              iso3=country_document['iso3'], iso2=country_document['iso2'],
                              iso_num=country_document['iso_num'], income=country_document['income'],
                              id=country_document['_id'], type=country_document['type'])

    def transform_to_country_list(self, country_document_list):
        return [self.transform_to_country(country_document) for country_document in country_document_list]


class RegionDocumentAdapter(object):
    def transform_to_region(self, region_document):
        return create_region(name=region_document['name'], short_name=region_document['short_name'],
                             area=region_document['area'], uri=region_document['uri'],
                             iso3=region_document['iso3'], iso2=region_document['iso2'],
                             iso_num=region_document['iso_num'], id=region_document['_id'],
                             countries=CountryDocumentAdapter().transform_to_country_list(region_document['countries']))

    def transform_to_region_list(self, region_document_list):
        return [self.transform_to_region(region_document) for region_document in region_document_list]


class AreaDocumentAdapter(object):
    def transform_to_area(self, area_document):
        if 'countries' in area_document:
            return RegionDocumentAdapter().transform_to_region(area_document)
        else:
            return CountryDocumentAdapter().transform_to_country(area_document)

    def transform_to_area_list(self, area_document_list):
        return [self.transform_to_area(area_document) for area_document in area_document_list]