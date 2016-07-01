from cartographer.field_types import StringAttribute, DateAttribute, SchemaRelationship
from cartographer.parsers.schema_parser import SchemaParser
from cartographer.resources.api_resource import APIResource
from cartographer.resources.resource_registry import ResourceRegistryKeys
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer
from generic_social_network.app.models.tables.user_read_history import UserReadHistory


class UserReadHistoryResource(APIResource):
    MODEL = UserReadHistory
    MODEL_GET = UserReadHistory.get
    # MODEL_PRIME = UserReadHistory.get.prime


@UserReadHistoryResource.register(ResourceRegistryKeys.SCHEMA)
class UserReadHistorySchema(Schema):
    SCHEMA = {
        'type': 'user-read-history',
        'id': StringAttribute()
                .read_from(serializer_method='user_read_history_id')
                .self_explanatory(),
        'attributes': {
            'timestamp': DateAttribute()
                .read_from(model_property='timestamp')
                .description('The time the user last read this post'),
        },
        'relationships': {
            'user': SchemaRelationship(model_type='user', id_attribute='user_id'),
            'post': SchemaRelationship(model_type='post', id_attribute='post_id'),
        }
    }


@UserReadHistoryResource.register(ResourceRegistryKeys.SERIALIZER)
class UserReadHistorySerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return UserReadHistorySchema


@UserReadHistoryResource.register(ResourceRegistryKeys.PARSER)
class UserReadHistoryParser(SchemaParser):
    @classmethod
    def schema(cls):
        return UserReadHistorySchema
