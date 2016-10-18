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

    def __init__(self):
        self.description_string = None
        self.is_self_explanatory = False

        self.model_property = None
        self.model_method = None
        self.serializer_method = None

        self.is_nullable = False
        self.is_optional_on_create = False
        self.is_computed = False

    def read_from(self, *, model_property=None, model_method=None, serializer_method=None):
        """
        Defines how to retrieve the value of the property. Only one parameter is allowed.

        :param model_property: The property is read directly from the model using this property name
        :param model_method: The property is read via a method on the model using this name
        :param serializer_method: The property value is read via the serializer using a method of this name
        """
        self.model_property = model_property
        self.model_method = model_method
        self.serializer_method = serializer_method
        return self

    def description(self, description_string):
        """Set a description for this attribute. Useful for documentation"""
        self.description_string = description_string
        return self

    def self_explanatory(self):
        self.is_self_explanatory = True
        return self

    def nullable(self):
        """Allows this property to be `null` during creation and update."""
        self.is_nullable = True
        return self

    def optional_on_create(self):
        """During creation, this property can be omitted."""
        self.is_optional_on_create = True
        return self

    def computed(self):
        """This attribute can only be read and specifying it on creation or update will result in an error."""
        self.is_computed = True
        return self

    def verify_configuration(self):
        """Checks that the attribute definition is in a usable state and has no conflicts"""
        read_from_sources = [self.model_property, self.model_method, self.serializer_method]
        if len(list(filter(None, read_from_sources))) != 1:
            raise ValueError(
                'One of `model_property`, `model_method` or `serializer_method` should be supplied to `read_from`.',
            )

        if not self.is_self_explanatory and not self.description_string:
            raise ValueError('Description string must be provided using `description` or marked as `self_explanatory`.')

        if self.is_computed and self.is_optional_on_create:
            raise ValueError('A `computed` property cannot be assigned during creation.')

    def get_value(self, serializer):
        """
        Extracts the attribute value using the serializer

        :param serializer: The serializer which is currently responsible for serializing this value
        :return: The raw value of the attribute before any processing
        """
        if self.model_property:
            return getattr(serializer.model, self.model_property)
        if self.model_method:
            return getattr(serializer.model, self.model_method)()
        if self.serializer_method:
            return getattr(serializer, self.serializer_method)()

        raise ValueError('Could not retrieve attribute value.')

    def is_valid(self, value):
        """Returns whether the value to be serialized is valid according to this attribute's description"""
        if not self.is_nullable and value is None:
            return False

        return True

    def to_json(self, serializer):
        """
        :param serializer: The serializer which is currently responsible for serializing this value
        :return: The value which the json library can serialize,
        which will have been formatted via format_value_for_json
        """
        value = self.get_value(serializer)
        if value is None:
            return value

        return self.format_value_for_json(value)

    @classmethod
    def format_value_for_json(cls, value):
        """
        :param value: The raw value, almost always the output of self.value
        :return: The formatted value, which can be dropped into a Python dictionary as the output of this Serializer,
        typically which will have json.dumps called on it to return to a client
        """
        return value

    def from_json(self, serialized_value):
        """
        :param serialized_value: The value to be parsed, as pulled directly from RequestInterface.get_json(force=True)
        :return: The parsed value, which can be dropped into a Python dictionary as the output of this Parser,
        typically which will be inserted into a SQLAlchemy table.
        """
        return serialized_value
