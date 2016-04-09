from cartographer.field_types import SchemaAttribute


class StringAttribute(SchemaAttribute):
    @classmethod
    def format_value_for_json(cls, value):
        return str(value)
