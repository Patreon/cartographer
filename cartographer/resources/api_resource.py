from cartographer.parsers.schema_parser import SchemaParser
from cartographer.permissions.base_mask import BaseMask
from cartographer.resources import get_resource_registry_container
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer


class APIResource(object):
    SCHEMA = Schema
    SERIALIZER = SchemaSerializer
    PARSER = SchemaParser
    MASK = BaseMask
    MODEL = None

    @classmethod
    def type_string(cls):
        return cls.SCHEMA.schema()['type']

    @classmethod
    def register(cls):
        registry = get_resource_registry_container()
        registry.register_resource(
            type_string=cls.type_string(),
            schema=cls.SCHEMA,
            model=cls.MODEL,
            serializer=cls.SERIALIZER,
            parser=cls.PARSER,
            mask=cls.MASK
        )
