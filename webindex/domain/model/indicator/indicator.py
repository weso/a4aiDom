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
        self._country_coverage = event.country_coverage
        self._provider_link = event.provider_link
        self._republish = event.republish
        self._high_low = event.high_low
        self._type = event.type
        self._label = event.label
        self._comment = event.comment
        self._notation = event.notation
        self._interval_starts = event.interval_starts
        self._interval_ends = event.interval_ends
        self._code = event.code
        self._organization = None

    def __repr__(self):
        return "{d}Indicator(id={id!r}," \
               "country_coverage={i._country_coverage!r}, " \
               "provider_link={i._provider_link!r}," \
               "republish={i._republish!r}, high_low={i._high_low!r}, " \
               "type={i._type!r}, label={i._label!r}, comment={i._comment!r}, " \
               "notation={i._notation!r}, interval_starts={i._interval_starts!r}, " \
               "interval_ends={i._interval_ends!r}, organization={i._organization})". \
            format(d="*Discarded* " if self._discarded else "", id=self._id, i=self)

    # =======================================================================================
    # Properties
    # =======================================================================================
    @property
    def country_coverage(self):
        self._check_not_discarded()
        return self._country_coverage

    @country_coverage.setter
    def country_coverage(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Indicator's country coverage cannot be empty")
        self._country_coverage = value
        self.increment_version()

    @property
    def provider_link(self):
        self._check_not_discarded()
        return self._provider_link

    @provider_link.setter
    def provider_link(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Indicator's provider_link cannot be empty")
        self._provider_link = value
        self.increment_version()

    @property
    def republish(self):
        self._check_not_discarded()
        return self._republish

    @republish.setter
    def republish(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Indicator's republish cannot be empty")
        self._republish = value
        self.increment_version()

    @property
    def code(self):
        self._check_not_discarded()
        return self._code

    @code.setter
    def code(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Indicator's code cannot be empty")

    @property
    def high_low(self):
        self._check_not_discarded()
        return self._high_low

    @high_low.setter
    def high_low(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Indicator's high_low cannot be empty")
        self._high_low = value
        self.increment_version()

    @property
    def ind_type(self):
        self._check_not_discarded()
        return self._type

    @ind_type.setter
    def ind_type(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Indicator's ind_type cannot be empty")
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
            raise ValueError("Indicator's label cannot be empty")
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
            raise ValueError("Indicator's comment cannot be empty")
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
            raise ValueError("Indicator's notation cannot be empty")
        self._notation = value
        self.increment_version()

    @property
    def interval_starts(self):
        self._check_not_discarded()
        return self._interval_starts

    @interval_starts.setter
    def interval_starts(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Indicator's interval_starts cannot be empty")
        self._interval_starts = value
        self.increment_version()

    @property
    def interval_ends(self):
        self._check_not_discarded()
        return self._interval_ends

    @interval_ends.setter
    def interval_ends(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Indicator's interval_ends cannot be empty")
        self._interval_ends = value
        self.increment_version()

    @property
    def organization(self):
        self._check_not_discarded()
        return self._organization

    @organization.setter
    def organization(self, value):
        self._check_not_discarded()
        self._organization = value
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


# =======================================================================================
# Indicator aggregate root factory
# =======================================================================================
def create_indicator(_type=None, country_coverage=None, provider_link=None,
                     republish=None, high_low=None, label=None, comment=None,
                     notation=None, interval_starts=None, interval_ends=None,
                     code=None, organization=None):
    indicator_id = uuid.uuid4().hex[:24]
    event = Indicator.Created(originator_id=indicator_id, originator_version=0,
                              type=_type, country_coverage=country_coverage,
                              provider_link=provider_link, republish=republish,
                              high_low=high_low, label=label, comment=comment,
                              notation=notation, interval_starts=interval_starts,
                              interval_ends=interval_ends, code=code,
                              organization=organization)
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

