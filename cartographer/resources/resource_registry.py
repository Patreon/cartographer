from collections import defaultdict
from enum import Enum

from cartographer.utils.collections import filter_dict


class ResourceRegistryKeys(Enum):
    TYPE = "type"
    SCHEMA = "schema"
    SERIALIZER = "serializer"
    PARSER = "parser"
    MASK = "mask"
    MODEL = "model"
    MODEL_GET = "model_get"
    MODEL_PRIME = "model_prime"


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

    def register_resource(self, type_string, schema,
                          serializer=None, parser=None, mask=None,
                          model=None, model_get=None, model_prime=None,):
        self.registry[type_string].update(filter_dict({
            ResourceRegistryKeys.TYPE: type_string,
            ResourceRegistryKeys.SCHEMA: schema,
            ResourceRegistryKeys.SERIALIZER: serializer,
            ResourceRegistryKeys.PARSER: parser,
            ResourceRegistryKeys.MASK: mask,
            ResourceRegistryKeys.MODEL: model,
            ResourceRegistryKeys.MODEL_GET: model_get,
            ResourceRegistryKeys.MODEL_PRIME: model_prime
        }))
