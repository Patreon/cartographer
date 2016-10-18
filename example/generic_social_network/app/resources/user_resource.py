from cartographer.field_types import StringAttribute
from cartographer.parsers.schema_parser import SchemaParser
from cartographer.resources.api_resource import APIResource
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer
from generic_social_network.app.models.tables.user import User


class UserSchema(Schema):
    SCHEMA = {
        'type': 'user',
        'id': StringAttribute()
                .read_from(model_property='user_id')
                .self_explanatory(),
        'attributes': {
            'name': StringAttribute()
                .read_from(model_property='name')
                .self_explanatory(),
        }
    }


class UserSerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return UserSchema


class UserParser(SchemaParser):
    @classmethod
    def schema(cls):
        return UserSchema

    def validate(self, inbound_data):
        super().validate(inbound_data)
        if not inbound_data.attribute('name'):
            raise Exception("Provided user object was missing the name field")


class UserResource(APIResource):
    SCHEMA = UserSchema
    SERIALIZER = UserSerializer
    PARSER = UserParser
    # MASK = BaseMask
    MODEL = User
    MODEL_GET = User.get
    # MODEL_PRIME = User.get.prime
