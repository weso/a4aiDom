
__author__ = 'guillermo'


from webindex.domain.model.area.area import Area
from webindex.domain.model.entity import Entity
import uuid
from ..events import DomainEvent, publish
from utility.mutators import when, mutate


class Region(Area):
    """
    Region aggregate root entity

    Attributes:
        countries (list of Country): List of countries that belong to this region
    """
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class CountryRelated(DomainEvent):
        pass

    def __init__(self, event):
        """
        Constructor for Region

        Note:
            New regions should be created by create_region factory function

        Args:
            event: Event with the required attributes
        """
        super(Region, self).__init__(event)
        self._countries = event.countries

    def __repr__(self):
        return "{d}Region(id={s._id}, type={s._type}, label={s._label}, " \
               "countries=[0..{n}])".format(d="*Discarded* " if self._discarded else "",
                                            s=self, n=len(self._countries))

    def to_dict(self):
        dictionary = super(Region, self).to_dict()
        dictionary['countries'] = [country.to_dict() for country in self._countries]
        return dictionary

# =======================================================================================
# Properties
# =======================================================================================
    @property
    def countries(self):
        return self._countries

    @countries.setter
    def countries(self, countries):
        self._countries = countries
        self.increment_version()

    def add_country(self, country):
        """
        Add a country to this region

        Args:
            country (Country): country to be added to this region
        """
        self._countries.append(country)
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
def create_region(name=None, short_name=None, area=None, countries=[],
                  uri=None, iso3=None, iso2=None, iso_num=None, id=None, search=None):
    """
    This function creates new regions and acts as a factory

    Args:
        name (str, optional): Name for the region
        short_name (str, optional): Short name for the region, could be the same as name
        area (str, optional): Area where this region belongs to, e.g.: Europe and Asia for Europe
        countries (list of Country, optional): List of countries that belong to this region
        uri (str, optional): URI that identifies this unique resource, normally composed depending on deployment address
        iso3 (str, optional): ISO 3166-1 alpha-3 code for the country
        iso2 (str, optional): ISO 3166-1 alpha-2 code for the country
        iso_num (str, optional): ISO 3166-1 number code for the country
        id (optional): Id code for the country
        search (str, optional): Search names separated by ';' with the name of the country in various languages
    """
    region_id = uuid.uuid4().hex[:24]
    event = Region.Created(originator_id=region_id, originator_version=0,
                           name=name, short_name=short_name, area=area,
                           countries=countries, uri=uri, iso3=iso3, iso2=iso2,
                           iso_num=iso_num, id=id, search=search)
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

