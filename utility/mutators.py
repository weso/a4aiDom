from singledispatch import singledispatch


# =======================================================================================
# Mutators - all aggregate creation and mutation is performed by the generic when()
# function.
# =======================================================================================
def mutate(obj, event):
    return when(event, obj)


@singledispatch
def when(event):
    """Modify an entity (usually an aggregate root) by replaying an event.

    Dispatch on the type of the first arg, hence (event, self) """
    raise NotImplementedError("No _when() implementation for {!r}".format(event))
