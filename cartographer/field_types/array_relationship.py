from cartographer.field_types import SchemaRelationship
from cartographer.resources.resource_registry import ResourceRegistryKeys


class ArrayRelationship(SchemaRelationship):
    def __init__(self, model_type, model_property=None, model_method=None,
                 resource_method=None, includes=None):
        super().__init__(model_type=model_type, model_property=model_property, model_method=model_method,
                         resource_method=resource_method, includes=includes)

    def resource(self, parent_resource, relationship_key):
        from cartographer.serializers import JSONAPICollectionSerializer

        if self.resource_method is not None:
            return getattr(parent_resource, self.resource_method)()

        models = []
        if self.id_attribute is not None:
            raise Exception("id_attribute provided for an ArrayRelationship.")
        elif self.model_property is not None:
            models = getattr(parent_resource.model, self.model_property)
        elif self.model_method is not None:
            models = getattr(parent_resource.model, self.model_method)()

        resource_class = self.resource_registry_entry().get(ResourceRegistryKeys.SERIALIZER)
        # TODO: custom collection class, custom arguments to resource_class
        return JSONAPICollectionSerializer([
            resource_class(
                model,
                parent_resource=parent_resource,
                relationship_name=relationship_key
            )
            for model in models
        ])
