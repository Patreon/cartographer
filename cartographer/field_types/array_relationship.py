from cartographer.field_types import SchemaRelationship
from cartographer.serializers import JSONAPICollectionSerializer


class ArrayRelationship(SchemaRelationship):
    def resource(self, parent_resource, relationship_key):
        if self.resource_method is not None:
            return getattr(parent_resource, self.resource_method)()

        models = []
        if self.id_attribute is not None:
            # TODO: 'id' on to-many relations?
            models = []
        elif self.model_property is not None:
            models = getattr(parent_resource.model, self.model_property)
        elif self.model_method is not None:
            models = getattr(parent_resource.model, self.model_method)()

        resource_class = self.classes_map().get('resource_class')
        # TODO: custom collection class, custom arguments to resource_class
        return JSONAPICollectionSerializer([
            resource_class(
                model,
                parent_resource=parent_resource,
                relationship_name=relationship_key
            )
            for model in models
        ])
