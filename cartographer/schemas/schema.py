class Schema(object):
    """
    The core element of the Cartographer system is the Schema.
    The schema is a map from our models to their API output and vice versa.
    Subclasses should define a class variable SCHEMA,
    formatted to resemble the output structure of JSON API resources:

    ```python
    {
        "type": "widget",
        "id": StringAttribute("widget_id"),
        "atributes": {
            "price": IntAttribute("amount_cents")
        },
        "relationships": {
            "manufacturer": SchemaRelationship(
                model_type="manufacturer",
                id_attribute="manufacturer_id"
            )
        }
    }
    ```

    Each of these top-level keys has corresponding utility methods on this class:
    * `resource_type` to access the value of `type` in the schema
    * `resource_id` to access the `SchemaAttribute` class corresponding to the `id` of the resource
    * `attributes` to list all attribute keys, and `attribute` to look up one particular attribute
    * `relationships` to list all attribute keys, and `relationship` to look up one particular relationship
    """

    @classmethod
    def schema(cls):
        """Override this or provide a class variable SCHEMA in a subclass to define model <=> API mappings"""
        return cls.SCHEMA

    @classmethod
    def route_prefix(cls):
        """Override this to define the API route namespace for these resources"""
        # TODO: migrate this to `route_prefixes`, and [cls.resource_type()] is the default,
        # with subclasses appending the plural form if they want.
        return None

    # Convenience methods for accessing pieces of the schema.

    @classmethod
    def resource_type(cls):
        return cls.schema().get('type')

    @classmethod
    def resource_id(cls):
        return cls.schema().get('id')

    @classmethod
    def attributes(cls):
        return list(cls.schema().get('attributes', {}).keys())

    @classmethod
    def attribute(cls, key):
        return cls.schema().get('attributes', {}).get(key)

    @classmethod
    def relationships(cls):
        return list(cls.schema().get('relationships', {}).keys())

    @classmethod
    def relationship(cls, key):
        return cls.schema().get('relationships', {}).get(key)

    @classmethod
    def schema_lookup(cls, json_key):
        return cls.schema().get(json_key)
