from cartographer.field_types import ArrayRelationship, SchemaRelationship
from cartographer.permissions.base_mask import BaseMask
from cartographer.resources import get_resource_registry
from cartographer.resources.resource_registry import ResourceRegistryKeys
from cartographer.serializers import JSONAPISerializer
from cartographer.utils import config


class SchemaSerializer(JSONAPISerializer):
    """
    SchemaSerializer turns python models into JSON API responses.
    It does so by subclassing `JSONAPISerializer`, and implementing its main four methods --
    `resource_id`, `resource_type`, `attributes_dictionary`, and `linked_resources` --
    using the passed-in model and the associated `schema`.
    """

    def __init__(self, model,
                 inbound_request=None, inbound_session=None,
                 parent_serializer=None, relationship_name=None,
                 includes=None, requested_fields=None,
                 current_user_id=None):
        """
        Route files should pass in `inbound_request` and `inbound_session`,
        Resource files should pass in `parent_serializer` and `relationship_name`

        :param model: The model which will be serialized into JSON
        :param inbound_request: The current `JSONAPIRequest` which is prompting the creation of this resource
        :param inbound_session: The `JSONAPISession` which is active during the creation of this resource
        :param parent_serializer: The `JSONAPISerializer` which is creating this instance as one of its `linked_resources`
        :param relationship_name: The name by which the parent_serializer refers to this instance
        :param includes: An array of strings, representing the relationships which should be serialized
        :param requested_fields: A map from strings to arrays of strings,
            representing the resource types and their associated attributes which should be serialized
        :param current_user_id: The ID of the user on behalf of whom the resource is being created

        :return: A instance of SchemaSerializer (or more typically a subclass),
        which will typically have `as_json_api_document` called on it in a route to transform it into a JSON response.
        """

        self.model = model

        if parent_serializer:
            if not requested_fields:
                requested_fields = parent_serializer.requested_fields
            if not current_user_id:
                current_user_id = parent_serializer.current_user_id

        if includes is None:
            if parent_serializer is not None and relationship_name is not None:
                prefix = relationship_name + '.'
                includes = [include_path[len(prefix):]
                            for include_path in parent_serializer.includes
                            if include_path.startswith(prefix)]
                if len(includes) == 0:
                    # TODO: kill all uses of request.args.get('use-defaults-for-included-resources') in clients
                    includes = type(self).default_includes()
            else:
                if inbound_request:
                    includes = inbound_request.get_includes()
                if includes is None:
                    includes = type(self).default_includes()
        self.includes = includes

        if requested_fields is None and inbound_request:
            requested_fields = inbound_request.get_requested_fields()
        self.requested_fields = requested_fields

        if current_user_id is None and inbound_session:
            current_user_id = inbound_session.user_id
        self.current_user_id = current_user_id

        self._linked_resources = None
        self._masked_fields = None
        self._masked_includes = None

        self.prime_for_includes()

    @classmethod
    def schema(cls):
        """Override this in a subclass to define model <=> API mappings"""
        raise NotImplementedError()

    @classmethod
    def default_fields(cls):
        """Override this in a subclass to define which attributes should be included by default"""
        return cls.schema().attributes()

    @classmethod
    def default_includes(cls):
        """Override this in a subclass to define which relationships should be included by default"""
        return cls.schema().relationships()

    @classmethod
    def model_class(cls):
        return get_resource_registry().get(cls.resource_type(), {}).get(ResourceRegistryKeys.MODEL)

    @classmethod
    def serializer_class(cls):
        return get_resource_registry().get(cls.resource_type(), {}).get(ResourceRegistryKeys.SERIALIZER)

    @classmethod
    def mask_class(cls):
        return get_resource_registry().get(cls.resource_type(), {}).get(ResourceRegistryKeys.MASK, BaseMask)

    @classmethod
    def resource_type(cls):
        return cls.schema().resource_type()

    def resource_id(self):
        return self.schema().resource_id().to_json(self)

    @classmethod
    def route_prefix(cls):
        return cls.schema().route_prefix()

    def resource_url(self):
        if config.api_server and self.route_prefix():
            return "https://{server}/{route}/{id}".format(
                server=config.api_server,
                route=self.route_prefix(),
                id=self.resource_id_str()
            )
        return super().resource_url()

    # # Serialization

    # Included resources

    def linked_resources(self):
        """
        The primary entry point for serialization of relationships

        :return: A map from relationship names to the related resource
        """
        if self._linked_resources is None:
            links = {}
            relationship_keys = self.schema().relationships()
            if relationship_keys:
                for key in relationship_keys:
                    if self.should_include_relationship(key):
                        relationship = self.schema().relationship(key)
                        links[key] = relationship.related_serializer(self, key)
            self._linked_resources = links
        return self._linked_resources

    def normalized_includes(self):
        # If includes passed in are e.g ['pledges.campaign.goals', 'campaign'] for a UserResource,
        # we want to include 'pledges' and 'campaign' here,
        # even tho the literal string 'pledges' is not in the self.includes array
        return [include.split('.')[0]
                for include in self.includes]

    def should_include_relationship(self, key):
        """
        Checks if the user requested the related resource and our Masks allow it.

        :param key: The name by which the parent resource refers to the child resource
        :return: A boolean indicating whether or not the relationship matching the given key should be serialized
        """
        if key not in self.normalized_includes():
            return False
        if self._masked_includes is None:
            self._masked_includes = self.mask_class().includes_cant_view(self.model, self.current_user_id)
        return key not in self._masked_includes

    # SQL Priming for Serialization

    def prime_for_includes(self):
        """
        While serializing resources, a tree structure linking parent resources to child relationships is formed.
        Sibling nodes in this tree do not know about each other,
        yet often make nearly identical SQL requests to hydrate their attributes and relationships.
        Priming is how we make this more performant --
        at initialization time, each sibling node primes the queries it will perform,
        so that when a node eventually performs the query, it can perform all the queries together
        (via our `https://github.com/Patreon/flask-caching-services` `MultigetCache` wrapper)
        """
        relationship_keys = self.schema().relationships()
        if relationship_keys:
            for key in relationship_keys:
                # Often times checking should_include_relationship issues a query,
                # but priming is cheap, so we over-prime rather than check self.should_include_relationship(key)
                self.prime_schema_relationship(key)

    def prime_schema_relationship(self, key):
        relationship_data_schema = self.schema().relationship(key)
        relationship_type = None
        id_attribute = None
        if isinstance(relationship_data_schema, SchemaRelationship):
            if not isinstance(relationship_data_schema, ArrayRelationship):
                relationship_type = relationship_data_schema.model_type
                id_attribute = relationship_data_schema.id_attribute

        if relationship_type is not None and id_attribute is not None and hasattr(self.model, id_attribute):
            relationship_model_get_primer = get_resource_registry().get(relationship_type) \
                .get(ResourceRegistryKeys.MODEL_PRIME)
            if relationship_model_get_primer is not None:
                relationship_model_get_primer(getattr(self.model, id_attribute))

    # Attributes

    def attributes_dictionary(self):
        """
        The primary entry point for serialization of attributes

        :return: A map from attribute names to their values
        """
        result = {}
        attribute_keys = self.schema().attributes()
        if attribute_keys:
            for key in attribute_keys:
                if self.should_include_attribute(key):
                    attribute = self.schema().attribute(key)
                    result[key] = attribute.to_json(self)
        return result

    def should_include_attribute(self, key):
        """
        Checks if the user requested the attribute and our Masks allow it.

        :param key: The name of the attribute of the resource
        :return: A boolean indicating whether or not the attribute matching the given key should be serialized
        """
        if self.requested_fields is not None and self.resource_type() in self.requested_fields:
            if key not in self.requested_fields[self.resource_type()]:
                return False
        elif key not in self.default_fields():
            return False
        if self._masked_fields is None:
            self._masked_fields = self.mask_class().fields_cant_view(self.model, self.current_user_id)
        return key not in self._masked_fields
