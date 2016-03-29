class SchemaAttribute(object):
    """
    `SchemaAttribute` describes how to translate attributes between JSON API and our Python models.

    `SchemaAttribute` is a very simple class, with two primary methods:
    `value`, for serializing from Python into JSON,
    and `from_json` for parsing from JSON into Python.
    Subclasses of `SchemaAttribute` can override either of these methods
    to customize (de)serialization behavior, typically per JSON output type
    (string, int, bool, date, etc.)
    """

    def __init__(self, model_attribute=None, is_property=True,
                 resource_method=None):
        """
        Note: only one of model_attribute and resource_method should be provided.
        Note: is_property is not relevant for resource_method

        :param model_attribute: the name of the attribute on the python model that should be (de)serialized
        :param is_property: whether or not model_attribute is a property (if False, it is presumed it is a method)
        :param resource_method: the name of the method on the resource object which uses this schema
        which should be called to get the serialized value.
        :return: an instance of SchemaAttribute,
        which will later be used by a Parser or Resource to move between JSON API and Python
        """

        identifier_args = [model_attribute, resource_method]
        provided_identifiers = [identifier
                                for identifier in identifier_args
                                if identifier]
        if len(provided_identifiers) > 1:
            raise Exception("only one of [{}] should be provided".format(identifier_args.join(", ")))

        self.model_attribute = model_attribute
        self.is_property = is_property
        self.resource_method = resource_method

    def value(self, resource):
        """
        :param resource: The resource which is currently responsible for serializing this value
        :return: The raw value to be serialized, which will be formatted via format_value
        """
        value = None
        if self.model_attribute:
            value = getattr(resource.model, self.model_attribute)
            if not self.is_property:
                value = value()
        elif self.resource_method:
            value = getattr(resource, self.resource_method)()

        if value is not None:
            value = self.format_value(value)

        return value

    @classmethod
    def format_value(cls, value):
        """
        :param value: The raw value, almost always the output of self.value
        :return: The formatted value, which can be dropped into a Python dictionary as the output of this Resource,
        typically which will have json.dumps called on it to return to a client
        """
        return value

    @classmethod
    def from_json(cls, serialized_value):
        """
        :param serialized_value: The value to be parsed, as pulled directly from RequestInterface.get_json(force=True)
        :return: The parsed value, which can be dropped into a Python dictionary as the output of this Parser,
        typically which will be inserted into a SQLAlchemy table.
        """
        return serialized_value
