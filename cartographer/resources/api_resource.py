from cartographer.parsers.schema_parser import SchemaParser
from cartographer.permissions.base_mask import BaseMask
from cartographer.resources import get_resource_registry_container
from cartographer.resources.resource_registry import ResourceRegistryKeys
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer


class APIResource(object):
    SCHEMA = Schema
    SERIALIZER = SchemaSerializer
    PARSER = SchemaParser
    MASK = BaseMask
    MODEL = None
    MODEL_GET = None
    MODEL_PRIME = None

    @classmethod
    def type_string(cls):
        return cls.SCHEMA.schema()['type']

    @classmethod
    def register(cls, registry_key):
        def wrapping_function(wrapped_class):
            if registry_key == ResourceRegistryKeys.SCHEMA:
                cls.SCHEMA = wrapped_class
            if registry_key == ResourceRegistryKeys.SERIALIZER:
                cls.SERIALIZER = wrapped_class
            if registry_key == ResourceRegistryKeys.PARSER:
                cls.PARSER = wrapped_class
            if registry_key == ResourceRegistryKeys.MASK:
                cls.MASK = wrapped_class
            if registry_key == ResourceRegistryKeys.MODEL:
                cls.MODEL = wrapped_class
            if registry_key == ResourceRegistryKeys.MODEL_GET:
                cls.MODEL_GET = wrapped_class
            if registry_key == ResourceRegistryKeys.MODEL_PRIME:
                cls.MODEL_PRIME = wrapped_class

            cls.register_class()

            return wrapped_class

        return wrapping_function

    @classmethod
    def register_class(cls):
        registry = get_resource_registry_container()
        registry.register_resource(
            type_string=cls.type_string(),
            schema=cls.SCHEMA,
            serializer=cls.SERIALIZER,
            parser=cls.PARSER,
            mask=cls.MASK,
            model=cls.MODEL,
            model_get=cls.MODEL_GET,
            model_prime=cls.MODEL_PRIME
        )
