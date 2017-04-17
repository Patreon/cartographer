from cartographer.resources import get_resource_registry_container

from .jsonapi_serializer import JSONAPISerializer
from .jsonapi_null_serializer import JSONAPINullSerializer
from .jsonapi_collection_serializer import JSONAPICollectionSerializer
from .schema_serializer import SchemaSerializer


def serializer_for_model(model):
    return get_resource_registry_container().get_serializer_for_model(model)
