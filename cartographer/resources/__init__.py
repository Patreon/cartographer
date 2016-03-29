from .resource_registry import ResourceRegistry

_resource_registry = ResourceRegistry()


def get_resource_registry(registry=_resource_registry):
    return registry
