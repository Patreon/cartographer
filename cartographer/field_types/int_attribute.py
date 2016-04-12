from cartographer.field_types import SchemaAttribute


class IntAttribute(SchemaAttribute):
    @classmethod
    def format_value_for_json(cls, value):
        return int(value)
