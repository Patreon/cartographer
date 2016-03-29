from cartographer.field_types import SchemaAttribute


class StringAttribute(SchemaAttribute):
    @classmethod
    def format_value(cls, value):
        return str(value)
