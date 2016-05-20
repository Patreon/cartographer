from cartographer.field_types import StringAttribute, SchemaRelationship
from cartographer.parsers.schema_parser import SchemaParser
from cartographer.resources.api_resource import APIResource
from cartographer.resources.resource_registry import ResourceRegistryKeys
from cartographer.schemas.schema import Schema
from cartographer.serializers import SchemaSerializer
from generic_social_network.app.models.tables.article import Article


class ArticleResource(APIResource):
    MODEL = Article
    MODEL_GET = Article.get
    # MODEL_PRIME = Article.get.prime


@ArticleResource.register(ResourceRegistryKeys.SCHEMA)
class ArticleSchema(Schema):
    SCHEMA = {
        'type': 'article',
        'id': StringAttribute('article_id'),
        'attributes': {
            'title': StringAttribute('title'),
            'body': StringAttribute('body'),
        },
        'relationships': {
            'author': SchemaRelationship(model_type='person', id_attribute='author_id')
        }
    }


@ArticleResource.register(ResourceRegistryKeys.SERIALIZER)
class ArticleSerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return ArticleSchema


@ArticleResource.register(ResourceRegistryKeys.PARSER)
class ArticleParser(SchemaParser):
    @classmethod
    def schema(cls):
        return ArticleSchema

    def validate(self, inbound_data):
        super().validate(inbound_data)
        if not (inbound_data.relationship_id('author') and inbound_data.relationship_id('author').resource_id()):
            raise Exception("Provided article object was missing the author id field")
        if not inbound_data.attribute('body'):
            raise Exception("Provided article object was missing the body field")
