from cartographer.field_types import StringAttribute, SchemaRelationship
from cartographer.parsers.schema_parser import SchemaParser
from cartographer.resources.api_resource import APIResource
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer
from generic_social_network.app.models.tables.follow import Follow


class FollowSchema(Schema):
    SCHEMA = {
        'type': 'follow',
        'id': StringAttribute(resource_method='follow_id'),
        'relationships': {
            'follower': SchemaRelationship(model_type='user', id_attribute='follower_id'),
            'followed': SchemaRelationship(model_type='user', id_attribute='followed_id')
        }
    }


class FollowSerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return FollowSchema

    def follow_id(self):
        return "{follower_id}-{followed_id}".format(
            follower_id=self.model.follower_id,
            followed_id=self.model.followed_id
        )


class FollowParser(SchemaParser):
    @classmethod
    def schema(cls):
        return FollowSchema


class FollowResource(APIResource):
    SCHEMA = FollowSchema
    SERIALIZER = FollowSerializer
    PARSER = FollowParser
    # MASK = FollowMask
    MODEL = Follow

FollowResource.register()
