__author__ = 'guillermo'

import uuid
from utility.mutators import mutate, when
from webindex.domain.model.area.area import Area
from webindex.domain.model.area.region import Region
from webindex.domain.model.events import publish
from webindex.domain.model.entity import Entity


class Country(Area):
    """
    Country entity

    Attributes:
        income (str): Income level, e.g.: LIC(Low income), LMC(Lower middle income), OEC(High income, OECD)
        type (str): Type of development for the country e.g.: Developing, Emerging
    """
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    def __init__(self, event):
        """
        Constructor for Country

        Note:
            New countries should be created by create_country factory function

        Args:
            event: Event with the required attributes
        """
        super(Country, self).__init__(event)
        self._income = event.income
        self._type = event.type

    def __repr__(self):
        return "{d}Country(id={id!r}, region_id={c._region.id!r}, " \
               "iso2_code={c._iso2_code}, iso3_code={c._iso3_code}, label={c._label!r})".\
                format(d="Discarded" if self.discarded else "", id=self._id, c=self,
                       type=self._type)

    def to_dict(self):
        """
        Converts self object to dictionary

        Returns:
            dict: Dictionary representation of self object
        """
        dictionary = super(Country, self).to_dict()
        dictionary['income'] = self.income
        dictionary['type'] = self.type
        return dictionary



# =======================================================================================
# Properties
# =======================================================================================
    @property
    def income(self):
        return self._income

    @income.setter
    def income(self, income):
        self._income = income
        self.increment_version()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type
        self.increment_version()

# =======================================================================================
# Commands
# =======================================================================================
    def discard(self):
        """Discard this region.

        After a call to this method, the region can no longer be used.
        """
        self._check_not_discarded()
        event = Region.Discarded(originator_id=self.id, originator_version=self.version)

        self._apply(event)
        publish(event)

    def _apply(self, event):
        mutate(self, event)


# =======================================================================================
# Region aggregate root factory
# =======================================================================================
def create_country(name=None, short_name=None, area=None, income=None,
                   uri=None, iso3=None, iso2=None, iso_num=None, id=None, type=None, search=None,
                   info=[]):
    """
    This function creates new countries and acts as a factory

    Args:
        name (str, optional): Name for the country
        short_name (str, optional): Short name for the country, could be the same as name
        area (str, optional): Area where this country belongs to, e.g.: Europe for Spain
        income (str, optional): Income level, e.g.: LIC(Low income), LMC(Lower middle income), OEC(High income, OECD)
        uri (str, optional): URI that identifies this unique resource, normally composed depending on deployment address
        iso3 (str, optional): ISO 3166-1 alpha-3 code for the country
        iso2 (str, optional): ISO 3166-1 alpha-2 code for the country
        iso_num (str, optional): ISO 3166-1 number code for the country
        id (optional): Id code for the country
        type (str, optional): Type of development for the country e.g.: Developing, Emerging
        search (str, optional): Search names separated by ';' with the name of the country in various languages
        info (list of AreaInfo): List of area info for this area

    Returns:
        Country: Created country
    """
    country_id = uuid.uuid4().hex[:24]
    event = Country.Created(originator_id=country_id, originator_version=0,
                            name=name, short_name=short_name, area=area,
                            income=income, uri=uri, iso3=iso3, iso2=iso2,
                            iso_num=iso_num, id=id, type=type, search=search,
                            info=info)
    country = when(event)
    publish(event)
    return country


# =======================================================================================
# Mutators
# =======================================================================================
@when.register(Country.Created)
def _(event):
    """Create a new aggregate root"""
    country = Country(event)
    country.increment_version()
    return country


@when.register(Country.Discarded)
def _(event, country):
    country.validate_event_originator(event)
    country._discarded = True
    country.increment_version()
    return country


