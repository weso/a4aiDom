__author__ = 'guillermo'

from webindex.domain.model.entity import Entity
import uuid
from .events import DomainEvent, publish
from utility.mutators import when, mutate
from ..exceptions import ConstraintError, DiscardedEntityError


class Slice(Entity):
    """ Slice aggregate root entity"""
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class ObservationAdded(DomainEvent):
        pass

    def __init__(self, event):
        super(Slice, self).__init__(event.originator_id, event.originator_version)
        self._type = event.type
        self._year = event.year
        self._indicator = None
        self._observation_ids = []

    def __repr__(self):
        return "{d}Slice(id={s._id}, type={s._type}, year={s._year}, " \
               "indicator={s._indicator}, observations=[0..{n}])".\
            format(d="*Discarded* " if self._discarded else "", s=self,
                   n=len(self._observation_ids))

    def __contains__(self, observation):
        """Determine whether a particular observation is present in this Slice.
        """
        self._check_not_discarded()
        return observation.id in self._observation_ids

# =======================================================================================
# Properties
# =======================================================================================
    @property
    def type(self):
        self._check_not_discarded()
        return self._type

    @type.setter
    def type(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Slice type cannot be empty")
        self._type = value
        self.increment_version()

    @property
    def year(self):
        self._check_not_discarded()
        return self._year

    @year.setter
    def year(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Slice year cannot be empty")
        self._type = value
        self.increment_version()

# =======================================================================================
# Commands
# =======================================================================================
    def discard(self):
        """Discard this slice.

        After a call to this method, the slice can no longer be used.
        """
        self._check_not_discarded()
        event = Slice.Discarded(originator_id=self.id, originator_version=self.version)

        self._apply(event)
        publish(event)

    def _apply(self, event):
        mutate(self, event)

    def observation_ids(self):
        """Obtain an iterator over the identifiers of observations in this slice.

        Returns:
            An iterator over a series of observation ids.

        Raises:
            DiscardedEntityError: If this slice has been discarded.
        """
        self._check_not_discarded()
        return iter(self._observation_ids)

    def add_observation(self, observation):
        """Add an observation to this slice.

        Args:
            observation: The Observation to be added to this slice.

        Raises:
            DiscardedEntityError: If this slice or the observation has been discarded.
            ConstraintError: If this observation has already been added to this slice.
        """
        self._check_not_discarded()

        if observation.discarded:
            raise DiscardedEntityError("Cannot add {!r}".format(observation))

        if observation in self:
            raise ConstraintError("{!r} is already added".format(observation))

        event = Slice.ObservationAdded(originator_id=self.id,
                                       originator_version=self.version,
                                       observation_id=observation.id)
        self._apply(event)
        publish(event)


# =======================================================================================
# DataSet aggregate root factory
# =======================================================================================
def create_slice(_type=None, year=None, indicator=None):
    slice_id = uuid.uuid4().hex[:24]
    event = Slice.Created(originator_id=slice_id, originator_version=0, type=_type,
                          year=year)
    _slice = when(event)
    publish(event)
    return _slice


# =======================================================================================
# Mutators
# =======================================================================================
@when.register(Slice.Created)
def _(event):
    """Create a new aggregate root"""
    _slice = Slice(event)
    _slice.increment_version()
    return _slice


@when.register(Slice.Discarded)
def _(event, _slice):
    _slice.validate_event_originator(event)
    _slice._discarded = True
    _slice.increment_version()
    return _slice


@when.register(Slice.ObservationAdded)
def _(event, _slice):
    _slice.validate_event_originator(event)
    _slice._observation_ids.append(event.observation_id)
    _slice.increment_version()
    return _slice
