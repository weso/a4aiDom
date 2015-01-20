__author__ = 'guillermo'

from webindex.domain.model.entity import Entity
import uuid
from webindex.domain.model.events import publish, DomainEvent
from ..exceptions import ConstraintError, DiscardedEntityError
from utility.mutators import mutate, when
from abc import ABCMeta


# =======================================================================================
# Component aggregate root entity
# =======================================================================================
class Component(Entity):
    """ Component aggregate root entity
    """
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class IndicatorAdded(DomainEvent):
        pass

    def __init__(self, event):
        super(Component, self).__init__(event.originator_id, event.originator_version)
        self._order = event.order
        self._contributor = event.contributor
        self._issued = event.issued
        self._type = "Component"
        self._label = event.label
        self._notation = event.notation
        self._indicator_ids = []
        self._comment = event.comment

    def __repr__(self):
        return "{d}Component(id={c._id}, order={c._order}, " \
               "contributor={c._contributor}," \
               "issued={c._issued}, type={c._type}, label={c._label}, " \
               "notation={c._notation}), indicator_ids=[0..{n}]".\
            format(d="*Discarded*" if self.discarded else "", id=self._id, c=self,
                   n=len(self._indicator_ids))

    def __contains__(self, indicator):
        """Determine whether a particular indicator is present in this Component.
        """
        self._check_not_discarded()
        return indicator.id in self._indicator_ids

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
            raise ValueError("Component's order cannot be empty")
        self._order = value
        self.increment_version()

    @property
    def contributor(self):
        self._check_not_discarded()
        return self._contributor

    @contributor.setter
    def contributor(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Component's contributor cannot be empty")
        self._contributor = value
        self.increment_version()

    @property
    def issued(self):
        self._check_not_discarded()
        return self._issued

    @issued.setter
    def issued(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Component's issued date cannot be empty")
        self._issued = value
        self.increment_version()

    @property
    def type(self):
        self._check_not_discarded()
        return self._type

    @type.setter
    def type(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Component's type cannot be empty")
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
            raise ValueError("Component's label cannot be empty")
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
            raise ValueError("Component's comment cannot be empty")
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
            raise ValueError("Component's notation cannot be empty")
        self._notation = value
        self.increment_version()

# =======================================================================================
# Commands
# =======================================================================================
    def discard(self):
        """Discard this component.

        After a call to this method, the component can no longer be used.
        """
        self._check_not_discarded()
        event = Component.Discarded(originator_id=self.id, originator_version=self.version)

        self._apply(event)
        publish(event)

    def _apply(self, event):
        mutate(self, event)

    def indicator_ids(self):
        """Obtain an iterator over the identifiers of indicators in this component.

        Returns:
            An iterator over a series of indicator ids.

        Raises:
            DiscardedEntityError: If this component has been discarded.
        """
        self._check_not_discarded()
        return iter(self._indicator_ids)

    def add_indicator(self, indicator):
        """Add an indicator to this component.

        Args:
            indicator: The Indicator to be added to this component.

        Raises:
            DiscardedEntityError: If this component or the indicator has been discarded.
            ConstraintError: If this indicator has already been added to this component.
        """
        self._check_not_discarded()

        if indicator.discarded:
            raise DiscardedEntityError("Cannot add {!r}".format(indicator))

        if indicator in self:
            raise ConstraintError("{!r} is already added".format(indicator))

        event = Component.IndicatorAdded(originator_id=self.id,
                                         originator_version=self.version,
                                         indicator_id=indicator.id)
        self._apply(event)
        publish(event)


# =======================================================================================
# Component aggregate factory
# =======================================================================================
def create_component(order=None, contributor=None, issued=None, label=None,
                     notation=None, comment=None):
    component_id = uuid.uuid4().hex[:24]
    event = Component.Created(originator_id=component_id, originator_version=0,
                              order=order, contributor=contributor, issued=issued,
                              label=label, notation=notation, comment=comment)
    component = when(event)
    publish(event)
    return component


# =======================================================================================
# Mutators
# =======================================================================================
@when.register(Component.Created)
def _(event):
    """Create a new aggregate"""
    component = Component(event)
    component.increment_version()
    return component


@when.register(Component.Discarded)
def _(event, component):
    component.validate_event_originator(event)
    component._discarded = True
    component.increment_version()
    return component


@when.register(Component.IndicatorAdded)
def _(event, component):
    component.validate_event_originator(event)
    component._indicator_ids.append(event.indicator_id)
    component.increment_version()
    return component


# =======================================================================================
# Component Repository
# =======================================================================================

class Repository(object):

    """Abstract implementation of generic queries for managing components."""
    __metaclass__ = ABCMeta

    def insert_component(self, component, component_uri=None, subindex_name=None, index_name=None, weight=None
                         , provider_name=None, provider_url=None):
        pass