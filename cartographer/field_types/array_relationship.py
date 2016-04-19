from cartographer.field_types import SchemaRelationship
from cartographer.resources.resource_registry import ResourceRegistryKeys


class ArrayRelationship(SchemaRelationship):
    def __init__(self, model_type, model_property=None, model_method=None,
                 serializer_method=None, includes=None):
        super().__init__(model_type=model_type, model_property=model_property, model_method=model_method,
                         serializer_method=serializer_method, includes=includes)

    def related_serializer(self, parent_serializer, relationship_key):
        from cartographer.serializers import JSONAPICollectionSerializer

        if self.serializer_method is not None:
            return getattr(parent_serializer, self.serializer_method)()

        models = []
        if self.id_attribute is not None:
            raise Exception("id_attribute provided for an ArrayRelationship.")
        elif self.model_property is not None:
            models = getattr(parent_serializer.model, self.model_property)
        elif self.model_method is not None:
            models = getattr(parent_serializer.model, self.model_method)()

        serializer_class = self.resource_registry_entry().get(ResourceRegistryKeys.SERIALIZER)
        # TODO: custom collection class, custom arguments to serializer_class
        return JSONAPICollectionSerializer([
            serializer_class(
                model,
                parent_serializer=parent_serializer,
                relationship_name=relationship_key
            )
            for model in models
        ])
