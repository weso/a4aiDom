__author__ = 'guillermo'

from webindex.domain.model.entity import Entity
import uuid
from ..events import DomainEvent, publish
from utility.mutators import when, mutate
from .country import Country
from abc import ABCMeta, abstractmethod


class Region(Entity):
    """ Region aggregate root entity"""
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class CountryRelated(DomainEvent):
        pass

    def __init__(self, event):
        super(Region, self).__init__(event.originator_id, event.originator_version)
        self._type = "Region"
        self._label = event.label
        self._countries = []

    def __repr__(self):
        return "{d}Region(id={s._id}, type={s._type}, label={s._label}, " \
               "countries=[0..{n}])".format(d="*Discarded* " if self._discarded else "",
                                            s=self, n=len(self._countries))

# =======================================================================================
# Properties
# =======================================================================================
    @property
    def label(self):
        self._check_not_discarded()
        return self._label

    @label.setter
    def label(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Region label cannot be empty")
        self._label = value
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

    def country_with_iso3(self, iso3_code):
        """Obtain a country by iso3 code.

        Args:
            iso3_code: The iso3 code of the country to return.

        Returns:
            The country with the specified iso3 code.

        Raises:
            DiscardedEntityError: If this region has been discarded.
            ValueError: If there is no country with the specified iso3 code.
        """
        self._check_not_discarded()
        for country in self._countries:
            if country.iso3_code == iso3_code:
                return country
        raise ValueError("No country with iso3 code '{}'".format(iso3_code))

    def relate_country(self, _type="Country", iso2_code=None, iso3_code=None, label=None):
        self._check_not_discarded()
        event = Region.CountryRelated(originator_id=self.id,
                                      originator_version=self.version,
                                      country_id=uuid.uuid4().hex[:24],
                                      country_version=0, type=_type, iso2_code=iso2_code,
                                      iso3_code=iso3_code, label=label)

        self._apply(event)
        publish(event)
        return self.country_with_iso3(iso3_code)

    def _apply(self, event):
        mutate(self, event)


# =======================================================================================
# Region aggregate root factory
# =======================================================================================
def create_region(label=None):
    region_id = uuid.uuid4().hex[:24]
    event = Region.Created(originator_id=region_id, originator_version=0, label=label)
    region = when(event)
    publish(event)
    return region


# =======================================================================================
# Mutators
# =======================================================================================
@when.register(Region.Created)
def _(event):
    """Create a new aggregate root"""
    region = Region(event)
    region.increment_version()
    return region


@when.register(Region.Discarded)
def _(event, region):
    region.validate_event_originator(event)
    region._discarded = True
    region.increment_version()
    return region


@when.register(Region.CountryRelated)
def _(event, region):
    region.validate_event_originator(event)
    country = Country(event, region)
    region._countries.append(country)
    region.increment_version()
    return region


# =======================================================================================
# Area Repository
# =======================================================================================
class Repository(object):
    """
    Abstract implementation of generic queries for managing areas.
    This will be sub-classed with an infrastructure specific implementation
    which will customize all the queries
    """
    __metaclass__ = ABCMeta

    def find_countries_by_code_or_income(self, area_code_or_income):
        pass

    def find_countries_by_continent_or_income(self, continent_or_income):
        pass

    def find_continents(self):
        pass

    def find_countries(self):
        pass

    def set_continent_countries(self, area):
        pass

    def area_error(self, area_code):
        pass

    def area_uri(self, area):
        pass