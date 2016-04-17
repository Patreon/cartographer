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
                 serializer_method=None):
        """
        Note: only one of model_attribute and serializer_method should be provided.
        Note: is_property is not relevant for serializer_method

        :param model_attribute: the name of the attribute on the python model that should be (de)serialized
        :param is_property: whether or not model_attribute is a property (if False, it is presumed it is a method)
        :param serializer_method: the name of the method on the serializer object which uses this schema
        which should be called to get the serialized value.
        :return: an instance of SchemaAttribute,
        which will later be used by a Parser or Serializer to move between JSON API and Python
        """

        identifier_args = [model_attribute, serializer_method]
        provided_identifiers = [identifier
                                for identifier in identifier_args
                                if identifier]
        if len(provided_identifiers) > 1:
            raise Exception("only one of [{}] should be provided".format(identifier_args.join(", ")))

        self.model_attribute = model_attribute
        self.is_property = is_property
        self.serializer_method = serializer_method

    def to_json(self, serializer):
        """
        :param serializer: The serializer which is currently responsible for serializing this value
        :return: The value which the json library can serialize,
        which will have been formatted via format_value_for_json
        """
        value = None
        if self.model_attribute:
            value = getattr(serializer.model, self.model_attribute)
            if not self.is_property:
                value = value()
        elif self.serializer_method:
            value = getattr(serializer, self.serializer_method)()

        if value is not None:
            value = self.format_value_for_json(value)

        return value

    @classmethod
    def format_value_for_json(cls, value):
        """
        :param value: The raw value, almost always the output of self.value
        :return: The formatted value, which can be dropped into a Python dictionary as the output of this Serializer,
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
