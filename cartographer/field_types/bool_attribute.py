from cartographer.field_types import SchemaAttribute


class BoolAttribute(SchemaAttribute):
    @classmethod
    def format_value_for_json(cls, value):
        return bool(value)

    @classmethod
    def from_json(cls, serialized_value):
        return bool(str(serialized_value).lower() not in ['false', '0'])
