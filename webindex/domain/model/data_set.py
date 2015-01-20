__author__ = 'guillermo'
from webindex.domain.model.entity import Entity
import uuid
from .events import DomainEvent, publish
from utility.mutators import when, mutate
from ..exceptions import ConstraintError, DiscardedEntityError


class DataSet(Entity):
    """ DataSet aggregate root entity"""
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class SliceAdded(DomainEvent):
        pass

    def __init__(self, event):
        super(DataSet, self).__init__(event.originator_id, event.originator_version)
        self._title = event.title
        self._type = event.type
        self._computation = None
        self._structure = event.structure
        self._contributor = event.contributor
        self._unit_measure = event.unit_measure
        self._label = event.label
        self._comment = event.comment
        self._publisher = event.publisher
        self._subject = event.subject
        self._slice_ids = []
        self._component = None

    def __repr__(self):
        return "{d}DataSet(id={s._id}, title={s._title}, type={s._type}, " \
               "computation={s._computation}, structure={s._structure}, " \
               "contributor={s._contributor}, unit_measure={s._unit_measure}," \
               "label={s._label}, comment={s._comment}, publisher={s._publisher}, " \
               "subject={s._subject}, slices=[0..{n}], component={s._component})".\
            format(d="*Discarded* " if self._discarded else "", s=self,
                   n=len(self._slice_ids))

    def __contains__(self, _slice):
        """Determine whether a particular slice is present in this DataSet.
        """
        self._check_not_discarded()
        return _slice.id in self._slice_ids

# =======================================================================================
# Properties
# =======================================================================================
    @property
    def title(self):
        self._check_not_discarded()
        return self._title

    @title.setter
    def title(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("DataSet title cannot be empty")
        self._title = value
        self.increment_version()

    @property
    def type(self):
        self._check_not_discarded()
        return self._type

    @type.setter
    def type(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("DataSet type cannot be empty")
        self._type = value
        self.increment_version()

    # TODO Complete properties
# =======================================================================================
# Commands
# =======================================================================================
    def discard(self):
        """Discard this data_set.

        After a call to this method, the data_set can no longer be used.
        """
        self._check_not_discarded()
        event = DataSet.Discarded(originator_id=self.id, originator_version=self.version)

        self._apply(event)
        publish(event)

    def _apply(self, event):
        mutate(self, event)

    def slice_ids(self):
        """Obtain an iterator over the identifiers of slices in this data_set.

        Returns:
            An iterator over a series of slice ids.

        Raises:
            DiscardedEntityError: If this data_set has been discarded.
        """
        self._check_not_discarded()
        return iter(self._slice_ids)

    def add_slice(self, _slice):
        """Add an slice to this data_set.

        Args:
            slice: The Slice to be added to this data_set.

        Raises:
            DiscardedEntityError: If this data_set or the slice has been discarded.
            ConstraintError: If this slice has already been added to this data_set.
        """
        self._check_not_discarded()

        if _slice.discarded:
            raise DiscardedEntityError("Cannot add {!r}".format(_slice))

        if _slice in self:
            raise ConstraintError("{!r} is already added".format(_slice))

        event = DataSet.SliceAdded(originator_id=self.id, originator_version=self.version,
                                   slice_id=_slice.id)
        self._apply(event)
        publish(event)


# =======================================================================================
# DataSet aggregate root factory
# =======================================================================================
def create_data_set(title=None, _type=None, computation=None, structure=None,
                    contributor=None, unit_measure=None, label=None,
                    comment=None, publisher=None, subject=None, component=None):
    data_set_id = uuid.uuid4().hex[:24]
    event = DataSet.Created(originator_id=data_set_id, originator_version=0, title=title,
                            type=_type, computation=computation, structure=structure,
                            contributor=contributor, unit_measure=unit_measure,
                            label=label, comment=comment, publisher=publisher,
                            subject=subject, component=component)
    data_set = when(event)
    publish(event)
    return data_set


# =======================================================================================
# Mutators
# =======================================================================================
@when.register(DataSet.Created)
def _(event):
    """Create a new aggregate root"""
    data_set = DataSet(event)
    data_set.increment_version()
    return data_set


@when.register(DataSet.Discarded)
def _(event, data_set):
    data_set.validate_event_originator(event)
    data_set._discarded = True
    data_set.increment_version()
    return data_set


@when.register(DataSet.SliceAdded)
def _(event, data_set):
    data_set.validate_event_originator(event)
    data_set._slice_ids.append(event.slice_id)
    data_set.increment_version()
    return data_set
