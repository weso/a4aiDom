__author__ = 'guillermo'
from webindex.domain.model.area import region
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import error, success, uri


class AreaRepository(region.Repository):
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
            countries = self.find_countries_by_continent_or_income(
                area_code_or_income_upper)
            if countries is None:
                return self.area_error(area_code_or_income)
            else:
                return success(countries)

        self.set_continent_countries(area)
        self.area_uri(area)

        return success(area)

    def find_countries_by_continent_or_income(self, continent_or_income, order):
        order = "name" if order is None else order
        continent_or_income_upper = continent_or_income.upper()
        countries = self._db['areas'].find({"$or": [
            {"area": continent_or_income},
            {"income": continent_or_income_upper}]}).sort(order, 1)

        if countries.count() == 0:
            return self.area_error(continent_or_income)

        country_list = []

        for country in countries:
            self.set_continent_countries(country)
            self.area_uri(country)
            country_list.append(country)

        return success(country_list)

    def find_areas(self, order):
        order = "name" if order is None else order
        continents = self.find_continents(order)["data"]
        countries = self.find_countries(order)["data"]

        return success(continents + countries)

    def find_continents(self, order):
        order = "name" if order is None else order
        areas = self._db['areas'].find({"area": None}).sort(order, 1)
        continents = []

        for continent in areas:
            continent["short_name"] = continent["name"]
            self.set_continent_countries(continent)

            self.area_uri(continent)
            continents.append(continent)

        return success(continents)

    def find_countries(self, order):
        order = "name" if order is None else order
        countries = self._db['areas'].find({"area": {"$ne": None}}).sort(order, 1)
        country_list = []

        for country in countries:
            self.area_uri(country)
            country_list.append(country)

        return success(country_list)

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
