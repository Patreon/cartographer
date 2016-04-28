from cartographer.field_types import StringAttribute, SchemaRelationship
from cartographer.parsers.schema_parser import SchemaParser
from cartographer.resources.api_resource import APIResource
from cartographer.resources.resource_registry import ResourceRegistryKeys
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer
from generic_social_network.app.models.tables.follow import Follow


class FollowResource(APIResource):
    MODEL = Follow
    MODEL_GET = Follow.get
    # MODEL_PRIME = Follow.get.prime


@FollowResource.register(ResourceRegistryKeys.SCHEMA)
class FollowSchema(Schema):
    SCHEMA = {
        'type': 'follow',
        'id': StringAttribute(serializer_method='follow_id'),
        'relationships': {
            'follower': SchemaRelationship(model_type='user', id_attribute='follower_id'),
            'followed': SchemaRelationship(model_type='user', id_attribute='followed_id')
        }
    }


@FollowResource.register(ResourceRegistryKeys.SERIALIZER)
class FollowSerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return FollowSchema

    def follow_id(self):
        return "{follower_id}-{followed_id}".format(
            follower_id=self.model.follower_id,
            followed_id=self.model.followed_id
        )


@FollowResource.register(ResourceRegistryKeys.PARSER)
class FollowParser(SchemaParser):
    @classmethod
    def schema(cls):
        return FollowSchema
