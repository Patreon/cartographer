from collections import defaultdict
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
        self.registry = defaultdict(dict)
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
        existing_registration = self.registry[type_string]
        additional_details = filter_dict({
            ResourceRegistryKeys.TYPE: type_string,
            ResourceRegistryKeys.SCHEMA: schema,
            ResourceRegistryKeys.MODEL: model,
            ResourceRegistryKeys.SERIALIZER: serializer,
            ResourceRegistryKeys.PARSER: parser,
            ResourceRegistryKeys.MASK: mask,
        })
        self.registry[type_string] = dict(existing_registration.items() | additional_details.items())
