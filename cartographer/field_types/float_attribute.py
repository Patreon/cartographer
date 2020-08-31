from cartographer.field_types import SchemaAttribute


class FloatAttribute(SchemaAttribute):
    @classmethod
    def format_value_for_json(cls, value):
        return float(value)
