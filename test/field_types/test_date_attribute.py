import nose.tools as t

from cartographer.field_types.date_attribute import DateAttribute


def test_not_nullable_date_field_errors_on_none():
    attribute = DateAttribute().self_explanatory()

    with t.assert_raises(AttributeError):
        attribute.from_json(None)


def test_nullable_date_field_can_parse_none():
    attribute = DateAttribute().self_explanatory().nullable()

    parsed_value = attribute.from_json(None)

    t.assert_equals(parsed_value, None)
