from cartographer.field_types import StringAttribute, SchemaRelationship, EnumAttribute
from cartographer.parsers.schema_parser import SchemaParser
from cartographer.resources.api_resource import APIResource
from cartographer.resources.resource_registry import ResourceRegistryKeys
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer
from generic_social_network.app.models.tables.post import Post, PostType


class PostResource(APIResource):
    MODEL = Post
    MODEL_GET = Post.get
    # MODEL_PRIME = Post.get.prime


@PostResource.register(ResourceRegistryKeys.SCHEMA)
class PostSchema(Schema):
    SCHEMA = {
        'type': 'post',
        'id': StringAttribute()
                .read_from(model_property='post_id')
                .self_explanatory(),
        'attributes': {
            'title': StringAttribute()
                .read_from(model_property='title')
                .description("The post's title text"),
            'body': StringAttribute()
                .read_from(model_property='body')
                .description("The posts's content"),
            'type': EnumAttribute(PostType)
                .read_from(model_property='type')
                .description("The post content and type and presentation style"),
        },
        'relationships': {
            'author': SchemaRelationship(model_type='user', id_attribute='author_id')
        }
    }


@PostResource.register(ResourceRegistryKeys.SERIALIZER)
class PostSerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return PostSchema


@PostResource.register(ResourceRegistryKeys.PARSER)
class PostParser(SchemaParser):
    @classmethod
    def schema(cls):
        return PostSchema

    def validate(self, inbound_data):
        super().validate(inbound_data)
        if not (inbound_data.relationship_id('author') and inbound_data.relationship_id('author').resource_id()):
            raise Exception("Provided post object was missing the author id field")
        if not inbound_data.attribute('body'):
            raise Exception("Provided post object was missing the body field")
