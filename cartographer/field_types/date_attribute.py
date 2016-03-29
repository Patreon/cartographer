import ciso8601

import dateutil.parser

from cartographer.field_types import SchemaAttribute
from cartographer.utils.datetime import as_utc, make_naive


class DateAttribute(SchemaAttribute):
    @classmethod
    def format_value(cls, value):
        return as_utc(value).isoformat()

    @classmethod
    def from_json(cls, serialized_value):
        try:
            parsed_value = ciso8601.parse_datetime(serialized_value)
            assert parsed_value is not None  # Caveat: asserts won't run if python is run with -O.
        except Exception as e:
            parsed_value = dateutil.parser.parse(serialized_value)
        return make_naive(parsed_value)
