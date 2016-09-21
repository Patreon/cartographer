from sqlalchemy import types


class EnumType(types.TypeDecorator):
    impl = types.Text

    def __init__(self, enum_type):
        super().__init__()

        self.enum_type = enum_type

    def process_bind_param(self, value, dialect):
        if not value:
            return value
        if isinstance(value, self.enum_type):
            return value.value

        return value

    def process_literal_param(self, value, dialect):
        return self.process_bind_param(value, dialect)

    def process_result_value(self, value, dialect):
        if not value:
            return value

        return self.enum_type(value)
