from cartographer.field_types import StringAttribute
from cartographer.parsers.schema_parser import SchemaParser
from cartographer.resources.api_resource import APIResource
from cartographer.resources.resource_registry import ResourceRegistryKeys
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer
from generic_social_network.app.models.tables.person import Person


class PeopleResource(APIResource):
    MODEL = Person
    MODEL_GET = Person.get
    # MODEL_PRIME = Person.get.prime


@PeopleResource.register(ResourceRegistryKeys.SCHEMA)
class PeopleSchema(Schema):
    SCHEMA = {
        'type': 'person',
        'id': StringAttribute('person_id'),
        'attributes': {
            'name': StringAttribute('name')
        }
    }


@PeopleResource.register(ResourceRegistryKeys.SERIALIZER)
class PeopleSerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return PeopleSchema


@PeopleResource.register(ResourceRegistryKeys.PARSER)
class PeopleParser(SchemaParser):
    @classmethod
    def schema(cls):
        return PeopleSchema

    def validate(self, inbound_data):
        super().validate(inbound_data)
        if not inbound_data.attribute('name'):
            raise Exception("Provided person object was missing the name field")
