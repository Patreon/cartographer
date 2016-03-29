from enum import Enum

from cartographer.utils.collections import filter_dict


class ResourceRegistryKeys(Enum):
    TYPE = "type"
    SCHEMA = "schema"
    MODEL = "model"
    SERIALIZER = "serializer"
    PARSER = "parser"
    MASK = "mask"


class ResourceRegistry(object):
    def __init__(self):
        self.registry = {}
        self.initialization_hook = None
        self.hook_called = False

    def set_initialization_hook(self, hook=None):
        self.initialization_hook = hook

    def call_initialization_hook(self):
        if not self.hook_called and self.initialization_hook:
            self.initialization_hook()
            self.hook_called = True

    def register_resource(self, type_string, schema, model=None,
                          serializer=None, parser=None, mask=None):
        self.registry[type_string] = filter_dict({
            ResourceRegistryKeys.TYPE: type_string,
            ResourceRegistryKeys.SCHEMA: schema,
            ResourceRegistryKeys.MODEL: model,
            ResourceRegistryKeys.SERIALIZER: serializer,
            ResourceRegistryKeys.PARSER: parser,
            ResourceRegistryKeys.MASK: mask,
        })
