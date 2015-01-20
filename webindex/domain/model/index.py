__author__ = 'guillermo'

from webindex.domain.model.entity import Entity
import uuid
from webindex.domain.model.events import publish, DomainEvent
from ..exceptions import ConstraintError, DiscardedEntityError
from utility.mutators import mutate, when
from abc import ABCMeta


# =======================================================================================
# SubIndex aggregate
# =======================================================================================
class Index(Entity):
    """ Index aggregate root entity
    """
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class SubIndexAdded(DomainEvent):
        pass

    def __init__(self, event):
        super(Index, self).__init__(event.originator_id, event.originator_version)
        self._order = event.order
        self._colour = event.colour
        self._type = "Index"
        self._label = event.label
        self._comment = event.comment
        self._notation = event.notation
        self._sub_index_ids = []

    def __repr__(self):
        return "{d}Index(id={c._id}, order={c._order}, " \
               "colour={c._colour}, type={c._type}, label={c._label}, " \
               "notation={c._notation}), component_ids=[0..{n}]".\
            format(d="*Discarded*" if self.discarded else "", id=self._id, c=self,
                   n=len(self._sub_index_ids))

    def __contains__(self, component):
        """Determine whether a particular sub_index is present in this Index.
        """
        self._check_not_discarded()
        return component.id in self._sub_index_ids

# =======================================================================================
# Properties
# =======================================================================================
    @property
    def order(self):
        self._check_not_discarded()
        return self._order

    @order.setter
    def order(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Index order cannot be empty")
        self._order = value
        self.increment_version()

    @property
    def colour(self):
        self._check_not_discarded()
        return self._colour

    @colour.setter
    def colour(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Index colour cannot be empty")
        self._colour = value
        self.increment_version()

    @property
    def type(self):
        self._check_not_discarded()
        return self._type

    @type.setter
    def type(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Index type cannot be empty")
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
            raise ValueError("Index label cannot be empty")
        self._label = value
        self.increment_version()

    @property
    def comment(self):
        self._check_not_discarded()
        return self._comment

    @comment.setter
    def comment(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Index comment cannot be empty")
        self._comment = value
        self.increment_version()

    @property
    def notation(self):
        self._check_not_discarded()
        return self._notation

    @notation.setter
    def notation(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Index notation cannot be empty")
        self._notation = value
        self.increment_version()

# =======================================================================================
# Commands
# =======================================================================================
    def discard(self):
        """Discard this index.

        After a call to this method, the index can no longer be used.
        """
        self._check_not_discarded()
        event = Index.Discarded(originator_id=self.id, originator_version=self.version)

        self._apply(event)
        publish(event)

    def _apply(self, event):
        mutate(self, event)

    def sub_index_ids(self):
        """Obtain an iterator over the identifiers of sub_indexes in this index.

        Returns:
            An iterator over a series of sub_index ids.

        Raises:
            DiscardedEntityError: If this index has been discarded.
        """
        self._check_not_discarded()
        return iter(self._sub_index_ids)

    def add_sub_index(self, sub_index):
        """Add a sub_index to this index.

        Args:
            sub_index: The SubIndex to be added to this index.

        Raises:
            DiscardedEntityError: If this index or the sub_index has been discarded.
            ConstraintError: If this sub_index has already been added to this index.
        """
        self._check_not_discarded()

        if sub_index.discarded:
            raise DiscardedEntityError("Cannot add {!r}".format(sub_index))

        if sub_index in self:
            raise ConstraintError("{!r} is already added".format(sub_index))

        event = Index.SubIndexAdded(originator_id=self.id,
                                    originator_version=self.version,
                                    sub_index_id=sub_index.id)
        self._apply(event)
        publish(event)


# =======================================================================================
# Index aggregate factory
# =======================================================================================
def create_index(order=None, colour=None, label=None, notation=None, comment=None):
    index_id = uuid.uuid4().hex[:24]
    event = Index.Created(originator_id=index_id, originator_version=0,
                          order=order, colour=colour, label=label, notation=notation, comment=comment)
    index = when(event)
    publish(event)
    return index


# =======================================================================================
# Mutators
# =======================================================================================
@when.register(Index.Created)
def _(event):
    """Create a new aggregate"""
    index = Index(event)
    index.increment_version()
    return index


@when.register(Index.Discarded)
def _(event, index):
    index.validate_event_originator(event)
    index._discarded = True
    index.increment_version()
    return index


@when.register(Index.SubIndexAdded)
def _(event, index):
    index.validate_event_originator(event)
    index._sub_index_ids.append(event.sub_index_id)
    index.increment_version()
    return index

# =======================================================================================
# Index Repository
# =======================================================================================

class Repository(object):

    """Abstract implementation of generic queries for managing Index."""
    __metaclass__ = ABCMeta

    def insert_index(self, index, index_uri=None, provider_name=None, provider_url=None):
        pass

