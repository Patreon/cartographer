from cartographer.field_types import StringAttribute, SchemaRelationship
from cartographer.parsers.schema_parser import SchemaParser
from cartographer.resources.api_resource import APIResource
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer
from generic_social_network.app.models.tables.post import Post


class PostSchema(Schema):
    SCHEMA = {
        'type': 'post',
        'id': StringAttribute('post_id'),
        'attributes': {
            'title': StringAttribute('title'),
            'body': StringAttribute('body'),
        },
        'relationships': {
            'author': SchemaRelationship(model_type='user', id_attribute='author_id')
        }
    }


class PostSerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return PostSchema


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


class PostResource(APIResource):
    SCHEMA = PostSchema
    SERIALIZER = PostSerializer
    PARSER = PostParser
    # MASK = PostMask
    MODEL = Post

PostResource.register()
