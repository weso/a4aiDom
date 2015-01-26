__author__ = 'Herminio'

from webindex.domain.model.entity import Entity
import uuid
from ..events import DomainEvent, publish
from utility.mutators import when, mutate
from abc import ABCMeta, abstractmethod


class Area(Entity):
    """ Region aggregate root entity"""
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class CountryRelated(DomainEvent):
        pass

    def __init__(self, event):
        super(Area, self).__init__(event.originator_id, event.originator_version)
        self._name = event.name
        self._short_name = event.short_name
        self._area = event.area
        self._uri = event.uri
        self._iso3 = event.iso3
        self._iso2 = event.iso2
        self._iso_num = event.iso_num
        self._id = event.id

    def __repr__(self):
        return "{d}Region(id={s._id}, type={s._type}, label={s._label}, " \
               "countries=[0..{n}])".format(d="*Discarded* " if self._discarded else "",
                                            s=self, n=len(self._countries))

    def to_dict(self):
        return {
            'name': self._name, 'short_name': self._short_name, 'area': self._area,
            'uri': self._uri, 'iso3': self._iso3, 'iso2': self._iso2,
            'iso_num': self._iso_num, 'id': self._id
        }

# =======================================================================================
# Properties
# =======================================================================================
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.increment_version()

    @property
    def short_name(self):
        return self._short_name

    @short_name.setter
    def short_name(self, short_name):
        self._short_name = short_name
        self.increment_version()

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, area):
        self._area = area
        self.increment_version()

    @property
    def countries(self):
        return self._countries

    @countries.setter
    def countries(self, countries):
        self._countries = countries
        self.increment_version()

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, uri):
        self._uri = uri
        self.increment_version()

    @property
    def iso3(self):
        return self._iso3

    @iso3.setter
    def iso3(self, iso3):
        self._iso3 = iso3
        self.increment_version()

    @property
    def iso2(self):
        return self._iso2

    @iso2.setter
    def iso2(self, iso2):
        self._iso2 = iso2
        self.increment_version()

    @property
    def iso_num(self):
        return self._iso_num

    @iso_num.setter
    def iso_num(self, iso_num):
        self._iso_num = iso_num
        self.increment_version()

    @property
    def id(self):
        return self._id

# =======================================================================================
# Commands
# =======================================================================================
    def discard(self):
        """Discard this region.

        After a call to this method, the region can no longer be used.
        """
        self._check_not_discarded()
        event = Area.Discarded(originator_id=self.id, originator_version=self.version)

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
        event = Area.CountryRelated(originator_id=self.id,
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
# Mutators
# =======================================================================================
@when.register(Area.Created)
def _(event):
    """Create a new aggregate root"""
    region = Area(event)
    region.increment_version()
    return region


@when.register(Area.Discarded)
def _(event, region):
    region.validate_event_originator(event)
    region._discarded = True
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

    def find_countries_by_continent_or_income_or_type(self, continent_or_income):
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