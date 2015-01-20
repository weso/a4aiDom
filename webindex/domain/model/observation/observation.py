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
        self._computations = []
        self._issued = event.issued
        self._publisher = event.publisher
        self._type = event.obs_type
        self._label = event.label
        self._status = event.status
        self._ref_indicator_id = None
        self._ref_area_id = None
        self._value = event.value
        self._ref_year = None

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

    # =======================================================================================
    # Properties
    # =======================================================================================
    @property
    def computations(self):
        self._check_not_discarded()
        return self._computations


    @property
    def issued(self):
        self._check_not_discarded()
        return self._issued

    @issued.setter
    def issued(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Observation's issue date cannot be empty")
        self._issued = value
        self.increment_version()

    @property
    def publisher(self):
        self._check_not_discarded()
        return self._publisher

    @publisher.setter
    def publisher(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Observation's publisher cannot be empty")
        self._issued = value
        self.increment_version()

    @property
    def obs_type(self):
        self._check_not_discarded()
        return self._type

    @obs_type.setter
    def obs_type(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Observation's type cannot be empty")
        self._type = value
        self.increment_version()

    @property
    def label(self):
        self._check_not_discarded()
        return self._label

    @label.setter
    def label(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Observation's label cannot be empty")
        self._label = value
        self.increment_version()

    @property
    def status(self):
        self._check_not_discarded()
        return self._status

    @status.setter
    def status(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Observation's status cannot be empty")
        self._status = value
        self.increment_version()

    @property
    def value(self):
        self._check_not_discarded()
        return self._value

    @value.setter
    def value(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Observation's value cannot be empty")
        self._value = value
        self.increment_version()

    @property
    def ref_area(self):
        self._check_not_discarded()
        return self._ref_area_id

    @property
    def ref_indicator(self):
        self._check_not_discarded()
        return self._ref_indicator_id

    @property
    def ref_year(self):
        """
        Checks for object's properties
        """
        self._check_not_discarded()
        return self._ref_year

    @ref_year.setter
    def ref_year(self, value):
        self._check_not_discarded()
        self._ref_year = value
        self.increment_version()

    def add_computation(self, comp_type, value):
        computation = Computation(comp_type=comp_type, value=value)
        self._computations.append(computation)
        self.increment_version()
        return computation


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
def create_observation(issued=None, publisher=None, data_set=None, obs_type=None,
                       label=None, status=None, ref_indicator=None, value=None,
                       ref_area=None, ref_year=None):
    obs_id = uuid.uuid4().hex[:24]
    event = Observation.Created(originator_id=obs_id, originator_version=0, issued=issued,
                                publisher=publisher, data_set=data_set, obs_type=obs_type,
                                label=label, status=status, ref_indicator=ref_indicator,
                                value=value, ref_area=ref_area, ref_year=ref_year)
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