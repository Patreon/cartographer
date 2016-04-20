from .resource_registry import ResourceRegistry

_resource_registry = ResourceRegistry()


def get_resource_registry_container():
    global _resource_registry
    _resource_registry.call_initialization_hook()
    return _resource_registry


def get_resource_registry():
    return get_resource_registry_container().registry
