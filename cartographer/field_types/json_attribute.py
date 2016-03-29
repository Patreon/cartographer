from cartographer.field_types import SchemaAttribute


class JSONAttribute(SchemaAttribute):
    @classmethod
    def format_value(cls, value):
        # the final serializer will appropriately dump to json, we should *not* do that prematurely here
        return value
