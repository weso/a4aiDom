__author__ = 'guillermo'

from webindex.domain.model.entity import Entity
from webindex.domain.model.events import DomainEvent, publish
import uuid
from .computation import Computation
from utility.mutators import mutate, when
from ...exceptions import DiscardedEntityError
from abc import ABCMeta


# =======================================================================================
# Observation aggregate root entity
# =======================================================================================
class Observation(Entity):
    """ Observation aggregate root entity
    """

    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class ComputationAdded(DomainEvent):
        pass

    class ReferencedArea(DomainEvent):
        pass

    class ReferencedIndicator(DomainEvent):
        pass

    def __init__(self, event):
        super(Observation, self).__init__(event.originator_id, event.originator_version)
        self._scored = event.scored
        self._provider_url = event.provider_url
        self._indicator = event.indicator
        self._code = event.code
        self._indicator_name = event.indicator_name
        self._short_name = event.short_name
        self._area = event.area
        self._area_name = event.area_name
        self._uri = event.uri
        self._value = event.value
        self._name = event.name
        self._ranked = event.ranked
        self._values = event.values
        self._normalized = event.normalized
        self._year = event.year
        self._provider_name = event.provider_name
        self._id = event.id
        self._continent = event.continent
        #self._tendency = event.tendency
        self._republish = event.republish

    def __repr__(self):
        return "{d}Observation(id={id!r}, " \
               "issued={issued!r}, " \
               "publisher={publisher!r}, type={obs_type!r}, label={label!r}, " \
               "status={status!r}, " \
               "ref_indicator={ref_indicator!r}, value={value!r}, " \
               "ref_area={ref_area!r}, ref_year={ref_year!r}) ". \
            format(d="*Discarded* " if self.discarded else "", id=self._id,
                   issued=self._issued, publisher=self._publisher,
                   obs_type=self._type, label=self._label,
                   status=self._status, ref_indicator=self._ref_indicator_id,
                   value=self._value, ref_area=self._ref_area_id,
                   ref_year=self._ref_year)

    def to_dict(self):
        return {
            'scored': self._scored, 'provider_url': self._provider_url, 'indicator': self._indicator,
            'code': self._code, 'indicator_name': self._indicator_name, 'short_name': self._short_name,
            'area': self._area, 'area_name': self._area_name, 'uri': self._uri, 'value': self._value,
            'name': self._name, 'ranked': self._ranked, 'values': self._values, 'normalized': self._normalized,
            'year': self._year, 'provider_name': self.provider_name, 'id': self._id, 'continent': self._continent,
            #'tendency': self.tendency,
            'republish': self.republish
        }

    # =======================================================================================
    # Properties
    # =======================================================================================
    @property
    def scored(self):
        return self._scored

    @scored.setter
    def scored(self, scored):
        self._scored = scored
        self.increment_version()

    @property
    def provider_url(self):
        return self._provider_url

    @provider_url.setter
    def provider_url(self, provider_url):
        self._provider_url = provider_url
        self.increment_version()

    @property
    def indicator(self):
        return self._indicator

    @indicator.setter
    def indicator(self, indicator):
        self._indicator = indicator
        self.increment_version()

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        self._code = code
        self.increment_version()

    @property
    def indicator_name(self):
        return self._indicator_name

    @indicator_name.setter
    def indicator_name(self, indicator_name):
        self._indicator_name = indicator_name
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
    def area_name(self):
        return self._area_name

    @area_name.setter
    def area_name(self, area_name):
        self._area_name = area_name
        self.increment_version()

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, uri):
        self._uri = uri
        self.increment_version()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.increment_version()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.increment_version()

    @property
    def ranked(self):
        return self._ranked

    @ranked.setter
    def ranked(self, ranked):
        self._ranked = ranked
        self.increment_version()

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values
        self.increment_version()

    @property
    def normalized(self):
        return self._normalized

    @normalized.setter
    def normalized(self, normalized):
        self._normalized = normalized
        self.increment_version()

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        self._year = year
        self.increment_version()

    @property
    def provider_name(self):
        return self._provider_name

    @provider_name.setter
    def provider_name(self, provider_name):
        self._provider_name = provider_name
        self.increment_version()

    @property
    def id(self):
        return self._id

    @property
    def continent(self):
        return self._continent

    @continent.setter
    def continent(self, continent):
        self._continent = continent
        self.increment_version()

    # @property
    # def tendency(self):
    #     return self._tendency
    #
    # @tendency.setter
    # def tendency(self, tendency):
    #     self._tendency = tendency
    #     self.increment_version()

    @property
    def republish(self):
        return self._republish

    @republish.setter
    def republish(self, republish):
        self._republish = republish
        self.increment_version()

    def add_value(self, value):
        # TODO: use event system
        self._values.append(value)
        self.increment_version()


    # =======================================================================================
    # Commands
    # =======================================================================================
    def discard(self):
        """Discard this observation.

        After a call to this method, the observation can no longer be used.
        """
        self._check_not_discarded()
        event = Observation.Discarded(originator_id=self.id,
                                      originator_version=self.version)

        self._apply(event)
        publish(event)





    def reference_indicator(self, indicator):
        """Reference an indicator from this observation.

        Args:
            indicator: The Indicator to be referenced from this observation.

        Raises:
            DiscardedEntityError: If this observation or the indicator has been discarded.
            """
        self._check_not_discarded()

        if indicator.discarded:
            raise DiscardedEntityError("Cannot reference {!r}".format(indicator))

        event = Observation.ReferencedIndicator(originator_id=self.id,
                                                originator_version=self.version,
                                                indicator_id=indicator.id)
        self._apply(event)
        publish(event)

    def reference_area(self, area):
        """Reference an area from this observation.

        Args:
            area: The area (Region or Country) to be referenced from this observation.

        Raises:
            DiscardedEntityError: If this observation or the area has been discarded.
            """

        self._check_not_discarded()
        if area.discarded:
            raise DiscardedEntityError("Cannot reference {!r}".format(area))

        event = Observation.ReferencedArea(originator_id=self.id,
                                           originator_version=self.version,
                                           area_id=area.id)
        self._apply(event)
        publish(event)

    def _apply(self, event):
        mutate(self, event)


# =======================================================================================
# Observation aggregate root factory
# =======================================================================================
def create_observation(scored=0, provider_url=None, indicator=None, code=None, indicator_name=None,
                       short_name=None, area=None, area_name=None, uri=None, value=0, name=None, ranked=0,
                       values=[], normalized=0, year="1970", provider_name=None, id=None, continent=None,
                       #tendency=0,
                       republish=False):
    obs_id = uuid.uuid4().hex[:24]
    event = Observation.Created(originator_id=obs_id, originator_version=0,
                                scored=scored, provider_url=provider_url, indicator=indicator, code=code,
                                indicator_name=indicator_name, short_name=short_name, area=area, area_name=area_name,
                                uri=uri, value=value, name=name, ranked=ranked, values=values, normalized=normalized,
                                year=year, provider_name=provider_name, id=id, continent=continent,
                                #tendency=tendency,
                                republish=republish)
    obs = when(event)
    publish(event)
    return obs


# =======================================================================================
# Mutators
# =======================================================================================
@when.register(Observation.Created)
def _(event):
    """Create a new aggregate root"""
    obs = Observation(event)
    obs.increment_version()
    return obs


@when.register(Observation.Discarded)
def _(event, obs):
    obs.validate_event_originator(event)
    obs._discarded = True
    obs.increment_version()
    return obs


@when.register(Observation.ReferencedIndicator)
def _(event, obs):
    obs.validate_event_originator(event)
    obs._ref_indicator_id = event.indicator_id
    obs.increment_version()
    return obs


@when.register(Observation.ReferencedArea)
def _(event, obs):
    obs.validate_event_originator(event)
    obs._ref_area_id = event.area_id
    obs.increment_version()
    return obs


# =======================================================================================
# Observations Repository
# =======================================================================================
class Repository(object):
    """Abstract implementation of generic queries for managing observations."""
    __metaclass__ = ABCMeta

    def find_observations(self, indicator_code=None, area_code=None, year=None):
        pass

    def get_indicators_by_code(self, code):
        pass

    def get_countries_by_code_name_or_income(self, code):
        pass

    def get_years(self, year):
        pass

    def observation_uri(self, observation):
        pass

    def set_observation_country_and_indicator_name(self, observation):
        pass

    def insert_observation(self, observation, observation_uri=None, area_iso3_code=None, indicator_code=None,
                           year_literal=None, area_name=None, indicator_name=None, previous_value=None,
                           year_of_previous_value=None, republish=None, provider_name=None, provider_url=None,
                           tendency=None):
        """
        The info related to area, indicator and year could be provided using the observation
        object internal fields or, in some context, directly using the parameters
        area_iso3_code, indicator_code and year literal. Each implementation will choose
        :param observation: observation object of the model
        :param uri: uri generated according to some parameters that represents the entity
        :param area_iso3_code:  iso3_code of a country
        :param indicator_code: code of an indicator (not id)
        :param year_literal: inst/string year, not an object year of the model
        :param area_name: String containing the name of the country
        :param indicator_name: String containing the name of the indicator
        :param previous_value: numeric value of previous observation in time registered
        :param year_of_previous_value: year of the previous observation registered
        :return:
        """
        pass