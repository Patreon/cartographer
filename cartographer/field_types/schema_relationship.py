from cartographer.resources import get_resource_registry
from cartographer.resources.resource_registry import ResourceRegistryKeys


class SchemaRelationship(object):
    """
    `SchemaRelationship` describes how to translate related resources to and from JSON API and our Python models.

    `SchemaRelationship` is has one primary method,
    `resource`, for creating a `JSONAPISerializer` instance based on its input arguments.
    Subclasses of `SchemaSerializer` can override this method
    to customize serialization behavior.
    Parsing of related resources is not currently handled by this class,
    and instead is handled by the `PostedDocument` class (or, more typically, its subclass `SchemaParser`.
    """

    def __init__(self, model_type, id_attribute=None, model_property=None,
                 model_method=None, resource_method=None, includes=None):
        """
        NOTE: only one of id_attribute, model_property, model_method, or resource_method should be provided

        :param model_type: the JSON API `type` string for the related model
        :param id_attribute: the foreign key column on the parent resource model which identifies the related resource
        :param model_property: the property on the parent resource model which returns the related resource
        :param model_method: the property on the parent resource model which returns the related resource
        :param resource_method: the name of the method on the parent resource object which uses this schema
        which should be called to get the serializable child resource.
        :return: an instance of SchemaRelationship,
        which will later be used to serialize Python into JSON API.
        """

        identifier_args = [id_attribute, model_property, model_method, resource_method]
        provided_identifiers = [identifier
                                for identifier in identifier_args
                                if identifier]
        if len(provided_identifiers) > 1:
            raise Exception("only one of [{}] should be provided".format(identifier_args.join(", ")))

        self.model_type = model_type
        self.id_attribute = id_attribute
        self.model_property = model_property
        self.model_method = model_method
        self.resource_method = resource_method
        self.includes = includes

    def resource(self, parent_resource, relationship_key):
        """
        :param parent_resource: The resource which has our return value as a related resource
        :param relationship_key: The name by which the parent resource knows this child resource
        :return: The child resource (or resource collection) which will later be serialized
        """
        if self.resource_method is not None:
            return getattr(parent_resource, self.resource_method)()

        model = None
        if self.id_attribute is not None:
            relationship_model_class = self.resource_registry_entry().get(ResourceRegistryKeys.MODEL)
            model_id = getattr(parent_resource.model, self.id_attribute)
            if model_id is not None:
                model = relationship_model_class.get(model_id)
        elif self.model_property is not None:
            model = getattr(parent_resource.model, self.model_property)
        elif self.model_method is not None:
            model = getattr(parent_resource.model, self.model_method)()

        if model:
            relationship_resource_class = self.resource_registry_entry().get(ResourceRegistryKeys.SERIALIZER)
            return relationship_resource_class(
                model,
                parent_resource=parent_resource,
                relationship_name=relationship_key,
                includes=self.includes
            )
        else:
            from cartographer.serializers import JSONAPINullSerializer
            return JSONAPINullSerializer()

    def resource_registry_entry(self):
        return get_resource_registry().get(self.model_type, {})
