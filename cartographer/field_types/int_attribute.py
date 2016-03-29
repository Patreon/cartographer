from cartographer.field_types import SchemaAttribute


class IntAttribute(SchemaAttribute):
    @classmethod
    def format_value(cls, value):
        return int(value)
