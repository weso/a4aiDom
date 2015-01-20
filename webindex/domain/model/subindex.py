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
class SubIndex(Entity):
    """ SubIndex aggregate root entity
    """
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class ComponentAdded(DomainEvent):
        pass

    def __init__(self, event):
        super(SubIndex, self).__init__(event.originator_id, event.originator_version)
        self._order = event.order
        self._colour = event.colour
        self._type = "Subindex"
        self._label = event.label
        self._notation = event.notation
        self._component_ids = []
        self._comment = event.comment

    def __repr__(self):
        return "{d}SubIndex(id={c._id}, order={c._order}, " \
               "colour={c._colour}, type={c._type}, label={c._label}, " \
               "notation={c._notation}), component_ids=[0..{n}]".\
            format(d="*Discarded*" if self.discarded else "", id=self._id, c=self,
                   n=len(self._component_ids))

    def __contains__(self, component):
        """Determine whether a particular component is present in this SubIndex.
        """
        self._check_not_discarded()
        return component.id in self._component_ids

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
            raise ValueError("SubIndex order cannot be empty")
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
            raise ValueError("SubIndex colour cannot be empty")
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
            raise ValueError("SubIndex type cannot be empty")
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
            raise ValueError("SubIndex label cannot be empty")
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
            raise ValueError("SubIndex comment cannot be empty")
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
            raise ValueError("SubIndex notation cannot be empty")
        self._notation = value
        self.increment_version()

# =======================================================================================
# Commands
# =======================================================================================
    def discard(self):
        """Discard this subindex.

        After a call to this method, the subindex can no longer be used.
        """
        self._check_not_discarded()
        event = SubIndex.Discarded(originator_id=self.id, originator_version=self.version)

        self._apply(event)
        publish(event)

    def _apply(self, event):
        mutate(self, event)

    def component_ids(self):
        """Obtain an iterator over the identifiers of components in this subindex.

        Returns:
            An iterator over a series of component ids.

        Raises:
            DiscardedEntityError: If this subindex has been discarded.
        """
        self._check_not_discarded()
        return iter(self._component_ids)

    def add_component(self, component):
        """Add a component to this subindex.

        Args:
            component: The Component to be added to this subindex.

        Raises:
            DiscardedEntityError: If this subindex or the component has been discarded.
            ConstraintError: If this component has already been added to this subindex.
        """
        self._check_not_discarded()

        if component.discarded:
            raise DiscardedEntityError("Cannot add {!r}".format(component))

        if component in self:
            raise ConstraintError("{!r} is already added".format(component))

        event = SubIndex.ComponentAdded(originator_id=self.id,
                                        originator_version=self.version,
                                        component_id=component.id)
        self._apply(event)
        publish(event)


# =======================================================================================
# SubIndex aggregate factory
# =======================================================================================
def create_sub_index(order=None, colour=None, label=None, notation=None, comment=None):
    sub_index_id = uuid.uuid4().hex[:24]
    event = SubIndex.Created(originator_id=sub_index_id, originator_version=0,
                             order=order, colour=colour, label=label, notation=notation,
                             comment=comment)
    sub_index = when(event)
    publish(event)
    return sub_index


# =======================================================================================
# Mutators
# =======================================================================================
@when.register(SubIndex.Created)
def _(event):
    """Create a new aggregate"""
    index = SubIndex(event)
    index.increment_version()
    return index


@when.register(SubIndex.Discarded)
def _(event, sub_index):
    sub_index.validate_event_originator(event)
    sub_index._discarded = True
    sub_index.increment_version()
    return sub_index


@when.register(SubIndex.ComponentAdded)
def _(event, sub_index):
    sub_index.validate_event_originator(event)
    sub_index._component_ids.append(event.component_id)
    sub_index.increment_version()
    return sub_index


# =======================================================================================
# Subindex Repository
# =======================================================================================

class Repository(object):

    """Abstract implementation of generic queries for managing subindexes."""
    __metaclass__ = ABCMeta

    def insert_subindex(self, subindex, subindex_uri=None, index_name=None, weight=None,
                        provider_name=None, provider_url=None):
        pass

