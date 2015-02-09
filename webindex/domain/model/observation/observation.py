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
    """
    Observation aggregate root entity

    Attributes:
        provider_url (str): URL of the provider
        indicator (str): Indicator indicator attribute value
        indicator_name (str): Indicator name for this observation
        short_name (str): Short name of the area
        area (str): Area area attribute value
        area_name (str): Name of the area
        uri (str): URI for this observation
        value (float or string): Value for this observation, could be blank if there is no valid value
        year (str): Year for this observation
        provider_name (str): Name of the observation provider
        id (str): Id for this observations
        continent (str): Continent for the area
        tendency (int): Tendency regarding previous years, -1 decreasing, 0 equal, +1 increasing
        republish (bool): True if republish is allowed, otherwise False
        area_type (str): Area type, i.g.: EMERGING or DEVELOPING
        ranking (int): Ranking for this observation
        ranking_type (int): Ranking type for this observation
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
        """
        Constructor for Observation, creation of new objects should be done by create_observation factory function

        Note:
            New observations should be created by create_observation function

        Args:
            event: The event with the required attributes
        """
        super(Observation, self).__init__(event.originator_id, event.originator_version)
        self._provider_url = event.provider_url
        self._indicator = event.indicator
        self._indicator_name = event.indicator_name
        self._short_name = event.short_name
        self._area = event.area
        self._area_name = event.area_name
        self._uri = event.uri
        self._value = event.value
        self._year = event.year
        self._provider_name = event.provider_name
        self._id = event.id
        self._continent = event.continent
        self._tendency = event.tendency
        self._republish = event.republish
        self._area_type = event.area_type
        self._ranking = event.ranking
        self._ranking_type = event.ranking_type

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
        """
        Converts self object to dictionary

        Returns:
            dict: Dictionary representation of self object
        """
        return {
            'provider_url': self.provider_url, 'indicator': self.indicator, 'indicator_name': self.indicator_name,
            'short_name': self.short_name, 'area': self.area, 'area_name': self.area_name, 'uri': self.uri,
            'value': self.value, 'year': self.year, 'provider_name': self.provider_name, 'id': self.id,
            'continent': self.continent, 'tendency': self.tendency, 'republish': self.republish,
            'area_type': self.area_type, 'ranking': self.ranking, 'ranking_type': self.ranking_type
        }

    # =======================================================================================
    # Properties
    # =======================================================================================

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
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
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

    @property
    def tendency(self):
        return self._tendency

    @tendency.setter
    def tendency(self, tendency):
        self._tendency = tendency
        self.increment_version()

    @property
    def republish(self):
        return self._republish

    @republish.setter
    def republish(self, republish):
        self._republish = republish
        self.increment_version()

    @property
    def area_type(self):
        return self._area_type

    @area_type.setter
    def area_type(self, area_type):
        self._area_type = area_type
        self.increment_version()

    @property
    def ranking(self):
        return self._ranking

    @ranking.setter
    def ranking(self, ranking):
        self._ranking = ranking
        self.increment_version()

    @property
    def ranking_type(self):
        return self._ranking_type

    @ranking_type.setter
    def ranking_type(self, ranking_type):
        self._ranking_type = ranking_type
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
def create_observation(provider_url=None, indicator=None, indicator_name=None,
                       short_name=None, area=None, area_name=None, uri=None, value=0,
                       year="1970", provider_name=None, id=None, continent=None,
                       tendency=0, republish=False, area_type=None, ranking=None, ranking_type=None):
    """
    This function creates new observations and acts as a factory

    Args:
        provider_url (str, optional): URL of the provider
        indicator (str, optional): Indicator indicator attribute value
        indicator_name (str, optional): Indicator name for this observation
        short_name (str, optional): Short name of the area
        area (str, optional): Area area attribute value
        area_name (str, optional): Name of the area
        uri (str, optional): URI for this observation
        value (float or string, optional): Value for this observation, could be blank if there is no valid value
        year (str, optional): Year for this observation
        provider_name (str, optional): Name of the observation provider
        id (str, optional): Id for this observations
        continent (str, optional): Continent for the area
        tendency (int, optional): Tendency regarding previous years, -1 decreasing, 0 equal, +1 increasing
        republish (bool, optional): True if republish is allowed, otherwise False
        area_type (str, optional): Area type, i.g.: EMERGING or DEVELOPING
        ranking (int, optional): Ranking for this observation
        ranking_type (int, optional): Ranking type for this observation

    Returns:
        Observation: Created observation
    """
    obs_id = uuid.uuid4().hex[:24]
    event = Observation.Created(originator_id=obs_id, originator_version=0,
                                provider_url=provider_url, indicator=indicator, indicator_name=indicator_name,
                                short_name=short_name, area=area, area_name=area_name,
                                uri=uri, value=value, year=year, provider_name=provider_name, id=id,
                                continent=continent, tendency=tendency, republish=republish, area_type=area_type,
                                ranking=ranking, ranking_type=ranking_type)
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