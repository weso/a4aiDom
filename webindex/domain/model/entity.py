from webindex.domain.exceptions import ConsistencyError
from webindex.domain.model.events import DomainEvent


# =======================================================================================
# Entities
# =======================================================================================

class Entity(object):
    """The base class of all entities.

    Attributes:
        id: A unique identifier.
        version: An integer version.
        discarded: True if this entity should no longer be used, otherwise False.
        Source (https://bitbucket.org/sixty-north/d5-kanban-python)
    """

    class Created(DomainEvent):
        pass

    class Discarded(DomainEvent):
        pass

    class AttributeChanged(DomainEvent):
        pass

    def __init__(self, entity_id, version):
        self._id = entity_id
        self._version = version
        self._discarded = False

    def increment_version(self):
        self._version += 1

    @property
    def id(self):
        """A string unique identifier for the entity."""
        self._check_not_discarded()
        return self._id

    @property
    def version(self):
        """An integer version for the entity."""
        self._check_not_discarded()
        return self._version

    def validate_event_originator(self, event):
        if event.originator_id != self.id:
            raise ConsistencyError("Event originator id mismatch: {} != {}".
                                   format(event.originator_id, self.id))
        if event.originator_version != self.version:
            raise ConsistencyError("Event originator version mismatch: {} != {}".
                                   format(event.originator_version, self.version))

    @property
    def discarded(self):
        """True if this entity is marked as discarded, otherwise False."""
        return self._discarded

    def _check_not_discarded(self):
        if self._discarded:
            raise DiscardedEntityError("Attempt to use {}".format(repr(self)))


# =======================================================================================
# Exceptions - for signalling errors
# =======================================================================================

class DiscardedEntityError(Exception):
    """Raised when an attempt is made to use a discarded Entity."""
    pass
