from enum import Enum

from cartographer.field_types import SchemaAttribute


class EnumAttribute(SchemaAttribute):
    def __init__(self, enum_class):
        super().__init__()

        if not issubclass(enum_class, Enum):
            raise TypeError('Got a non-Enum argument ' + repr(enum_class))

        self.enum_class = enum_class

    def is_valid(self, value):
        if not super().is_valid(value):
            return False

        return value in [enum_value.value for enum_value in list(self.enum_class)]

    def format_value_for_json(self, value):
        if isinstance(value, self.enum_class):
            return value.value

        return value

    def from_json(self, serialized_value):
        return self.enum_class(serialized_value)
