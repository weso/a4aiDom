__author__ = 'guillermo'

import uuid
from utility.mutators import mutate, when
from webindex.domain.model.area.area import Area
from webindex.domain.model.area.region import Region
from webindex.domain.model.events import publish
from webindex.domain.model.entity import Entity


class Country(Area):
    """ Country entity """
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    def __init__(self, event):
        super(Country, self).__init__(event)
        self._income = event.income
        self._type = event.type

    def __repr__(self):
        return "{d}Country(id={id!r}, region_id={c._region.id!r}, " \
               "iso2_code={c._iso2_code}, iso3_code={c._iso3_code}, label={c._label!r})".\
                format(d="Discarded" if self.discarded else "", id=self._id, c=self,
                       type=self._type)



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
def create_country(name=None, short_name=None, area=None, income=[],
                   uri=None, iso3=None, iso2=None, iso_num=None, id=None, type=None, search=None):
    country_id = uuid.uuid4().hex[:24]
    event = Country.Created(originator_id=country_id, originator_version=0,
                            name=name, short_name=short_name, area=area,
                            income=income, uri=uri, iso3=iso3, iso2=iso2,
                            iso_num=iso_num, id=id, type=type, search=search)
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


