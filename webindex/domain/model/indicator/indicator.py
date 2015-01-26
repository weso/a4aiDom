__author__ = 'guillermo'

from webindex.domain.model.entity import Entity
import uuid
from webindex.domain.model.events import publish
from utility.mutators import when, mutate
from abc import ABCMeta
from webindex.domain.model.events import DomainEvent
from webindex.domain.model.indicator.organization import Organization


# =======================================================================================
# Indicator aggregate root entity
# =======================================================================================
class Indicator(Entity):
    """ Indicator aggregate root entity
    """

    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    class OrganizationAdded(DomainEvent):
        pass

    def __init__(self, event):
        super(Indicator, self).__init__(event.originator_id, event.originator_version)
        self._id = event.id
        self._index = event.index
        self._indicator = event.indicator
        self._name = event.name
        self._parent = event.parent
        self._provider_url = event.provider_url
        self._description = event.description
        #self._component = event.component
        self._uri = event.uri
        #self._weight = event.weight
        self._subindex = event.subindex
        self._type = event.type
        self._children = event.children
        self._provider_name = event.provider_name
        self._republish = event.republish
        #self._high_low = event.high_low

    def __repr__(self):
        return "{d}Indicator(id={id!r}," \
               "country_coverage={i._country_coverage!r}, " \
               "provider_link={i._provider_link!r}," \
               "republish={i._republish!r}, high_low={i._high_low!r}, " \
               "type={i._type!r}, label={i._label!r}, comment={i._comment!r}, " \
               "notation={i._notation!r}, interval_starts={i._interval_starts!r}, " \
               "interval_ends={i._interval_ends!r}, organization={i._organization})". \
            format(d="*Discarded* " if self._discarded else "", id=self._id, i=self)

    def to_dict(self):
        return {
            'index': self._index, 'indicator': self._indicator, 'name': self._name,
            'parent': self._parent, 'provider_url': self._provider_url, 'description': self._description,
            #'component': self._component,
            'uri': self._uri,
            #'weight': self._weight,
            'subindex': self._subindex,
            'id': self._id, 'type': self._type, 'children': [child.to_dict() for child in self._children],
            #'high_low': self._high_low,
            'provider_name': self._provider_name, 'republish': self._republish
        }

    # =======================================================================================
    # Properties
    # =======================================================================================
    @property
    def id(self):
        return self._id

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index
        self.increment_version()

    @property
    def indicator(self):
        return self._indicator

    @indicator.setter
    def indicator(self, indicator):
        self._indicator = indicator
        self.increment_version()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.increment_version()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
        self.increment_version()

    # @property
    # def component(self):
    #     return self._component
    #
    # @component.setter
    # def component(self, component):
    #     self._component = component
    #     self.increment_version()

    @property
    def subindex(self):
        return self._subindex

    @subindex.setter
    def subindex(self, subindex):
        self._subindex = subindex
        self.increment_version()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type
        self.increment_version()

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        self._children = children
        self.increment_version()

    @property
    def provider_url(self):
        return self._provider_url

    @provider_url.setter
    def provider_url(self, provider_url):
        self._provider_url = provider_url
        self.increment_version()

    @property
    def description(self):
        return self._description

    @description.setter
    def children(self, description):
        self._description = description
        self.increment_version()

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, uri):
        self._uri = uri
        self.increment_version()

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, weight):
        self._weight = weight
        self.increment_version()

    @property
    def provider_name(self):
        return self._provider_name

    @provider_name.setter
    def provider_name(self, provider_name):
        self._provider_name = provider_name
        self.increment_version()

    @property
    def republish(self):
        return self._republish

    @republish.setter
    def republish(self, republish):
        self._republish = republish
        self.increment_version()

    @property
    def high_low(self):
        return self._high_low

    @high_low.setter
    def high_low(self, high_low):
        self._high_low = high_low
        self.increment_version()

    # =======================================================================================
    # Commands
    # =======================================================================================
    def discard(self):
        """Discard this indicator.

        After a call to this method, the indicator can no longer be used.
        """
        self._check_not_discarded()
        event = Indicator.Discarded(originator_id=self.id,
                                    originator_version=self.version)

        self._apply(event)
        publish(event)

    def _apply(self, event):
        mutate(self, event)

    def add_organization(self, label=None):
        self._check_not_discarded()
        event = Indicator.OrganizationAdded(originator_id=self.id,
                                            originator_version=self.version,
                                            label=label)
        self._apply(event)
        publish(event)

    def add_child(self, indicator):
        # TODO: use event system
        self._children.append(indicator)
        self.increment_version()


# =======================================================================================
# Indicator aggregate root factory
# =======================================================================================
def create_indicator(id=None, index=None, indicator=None, name=None,
                     provider_url=None, description=None, uri= None,
                     parent=None,
                     #component=None,
                     # weight=None,
                     provider_name=None, republish=None,
                     # high_low=None,
                     subindex=None, type=None, children=[]):
    indicator_id = uuid.uuid4().hex[:24]
    event = Indicator.Created(originator_id=indicator_id, originator_version=0,
                              id=id, index=index, indicator=indicator, name=name,
                              parent=parent,
                              #component=component,
                              provider_url=provider_url,
                              description=description, uri=uri,
                              #weight=weight,
                              provider_name=provider_name, republish=republish,
                              subindex=subindex, type=type, children=children,
                              #high_low=high_low
                              )
    indicator = when(event)
    publish(event)
    return indicator




# =======================================================================================
# Mutators
# =======================================================================================
@when.register(Indicator.Created)
def _(event):
    """Create a new aggregate root"""
    indicator = Indicator(event)
    indicator.increment_version()
    return indicator


@when.register(Indicator.Discarded)
def _(event, indicator):
    indicator.validate_event_originator(event)
    indicator._discarded = True
    indicator.increment_version()
    return indicator

@when.register(Indicator.OrganizationAdded)
def _(event, indicator):
    """
    It creates a organization object for adding to the indicator object
    :param event:
    :return:
    """

    indicator.validate_event_originator(event)
    organization = Organization(event.label)
    indicator.organization = organization
    indicator.increment_version()
    return indicator




# =======================================================================================
# Indicator Repository
# =======================================================================================
class Repository(object):
    """Abstract implementation of generic queries for managing indicators."""
    __metaclass__ = ABCMeta

    def find_indicators_by_code(self, indicator_code):
        pass

    def find_indicators_index(self):
        pass

    def find_indicators_sub_indexes(self):
        pass

    def find_indicators_components(self, parent=None):
        pass

    def find_indicators_primary(self, parent=None):
        pass

    def find_indicators_secondary(self, parent=None):
        pass

    def find_indicators_indicators(self, parent=None):
        pass

    def find_indicators_by_level(self, level, parent=None):
        pass

    def find_indicator_children(self, indicator):
        pass

    def indicator_error(self, indicator_code):
        pass

    def indicator_uri(self, indicator_code):
        pass

    def insert_indicator(self, indicator, indicator_uri=None, component_name=None, subindex_name=None, index_name=None,
                         weight=None, provider_name=None, provider_url=None):
        pass

