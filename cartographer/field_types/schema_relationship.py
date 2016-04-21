from cartographer.resources import get_resource_registry
from cartographer.resources.resource_registry import ResourceRegistryKeys


class SchemaRelationship(object):
    """
    `SchemaRelationship` describes how to translate related resources to and from JSON API and our Python models.

    `SchemaRelationship` is has one primary method,
    `related_serializer`, for creating a `JSONAPISerializer` instance based on its input arguments.
    Subclasses of `SchemaSerializer` can override this method
    to customize serialization behavior.
    Parsing of related resources is not currently handled by this class,
    and instead is handled by the `PostedDocument` class (or, more typically, its subclass `SchemaParser`.
    """

    def __init__(self, model_type, id_attribute=None, model_property=None,
                 model_method=None, serializer_method=None, includes=None):
        """
        NOTE: only one of id_attribute, model_property, model_method, or serializer_method should be provided

        :param model_type: the JSON API `type` string for the related model
        :param id_attribute: the foreign key column on the parent serializer model which identifies the related serializer
        :param model_property: the property on the parent serializer model which returns the related serializer
        :param model_method: the property on the parent serializer model which returns the related serializer
        :param serializer_method: the name of the method on the parent serializer object which uses this schema
        which should be called to get the child serializer.
        :return: an instance of SchemaRelationship,
        which will later be used to serialize Python into JSON API.
        """

        identifier_args = [id_attribute, model_property, model_method, serializer_method]
        provided_identifiers = [identifier
                                for identifier in identifier_args
                                if identifier]
        if len(provided_identifiers) > 1:
            raise Exception("only one of [{}] should be provided".format(identifier_args.join(", ")))

        self.model_type = model_type
        self.id_attribute = id_attribute
        self.model_property = model_property
        self.model_method = model_method
        self.serializer_method = serializer_method
        self.includes = includes

    def related_serializer(self, parent_serializer, relationship_key):
        """
        :param parent_serializer: The serializer which has our return value as a related resource
        :param relationship_key: The name by which the parent serializer knows this child
        :return: The child serializer which will later be used to serialize a related resource
        """
        if self.serializer_method is not None:
            return getattr(parent_serializer, self.serializer_method)()

        model = None
        if self.id_attribute is not None:
            related_model_getter = self.resource_registry_entry().get(ResourceRegistryKeys.MODEL_GET)
            model_id = getattr(parent_serializer.model, self.id_attribute)
            if model_id is not None and related_model_getter is not None:
                model = related_model_getter(model_id)
        elif self.model_property is not None:
            model = getattr(parent_serializer.model, self.model_property)
        elif self.model_method is not None:
            model = getattr(parent_serializer.model, self.model_method)()

        if model:
            serializer_class = self.resource_registry_entry().get(ResourceRegistryKeys.SERIALIZER)
            return serializer_class(
                model,
                parent_serializer=parent_serializer,
                relationship_name=relationship_key,
                includes=self.includes
            )
        else:
            from cartographer.serializers import JSONAPINullSerializer
            return JSONAPINullSerializer()

    def resource_registry_entry(self):
        return get_resource_registry().get(self.model_type, {})
