class ConstraintError(Exception):
    """To be raised when an operation would otherwise cause a domain model constraint
    violation."""
    pass


class ConsistencyError(Exception):
    """To be raised when an internal consistency problem is detected."""
    pass


class DiscardedEntityError(Exception):
    """Raised when an attempt is made to use a discarded Entity."""
    pass