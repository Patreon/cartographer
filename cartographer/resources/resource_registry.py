from enum import Enum


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

    def register_resource(self, type_string, schema, model=None,
                          serializer=None, parser=None, mask=None):
        self.registry[type_string] = {
            ResourceRegistryKeys.TYPE: type_string,
            ResourceRegistryKeys.SCHEMA: schema,
            ResourceRegistryKeys.MODEL: model,
            ResourceRegistryKeys.SERIALIZER: serializer,
            ResourceRegistryKeys.PARSER: parser,
            ResourceRegistryKeys.MASK: mask,
        }
