AUTHENTICATION_REQUIRED_401 = 401
NOT_AUTHORIZED_403 = 403
INVALID_REQUEST_400 = 400
REQUEST_ENTITY_TOO_LARGE_413 = 413
NOT_FOUND_404 = 404
INTERNAL_SERVER_ERROR_500 = 500
RESOURCE_CONFLICT_409 = 409
PAYMENT_REQUIRED_402 = 402
HEADER_PRECONDITIONS_FAILED = 412
LOCKED_423 = 423
TOO_MANY_REQUESTS_429 = 429


class JSONAPIException(Exception):
    status_code = INTERNAL_SERVER_ERROR_500
    error_title = "Internal Error."
    error_type_ = None
    error_description = None

    @property
    def error_type(self):
        return self.error_type_ or type(self).__name__

    def __init__(self, status_code=None, error_type=None, error_title=None,
                 error_description=None):
        self.status_code = status_code or self.status_code
        self.error_title = error_title or self.error_title
        self.error_description = error_description or self.error_description or self.error_title
        self.error_type_ = error_type


class ParameterMissing(JSONAPIException):
    status_code = INVALID_REQUEST_400
    parameter_name = None

    def __init__(self, parameter_name=None):
        self.error_title = \
            "Parameter '{}' is missing.".format(parameter_name or self.parameter_name)


class ParameterInvalid(JSONAPIException):
    status_code = INVALID_REQUEST_400

    def __init__(self, parameter_name, parameter_value):
        self.error_title = \
            "Invalid value for parameter '{}'.".format(parameter_name)
        self.error_description = \
            "Invalid parameter for '{0}': {1}.".format(parameter_name, parameter_value)


class BadPageCountParameter(ParameterInvalid):
    def __init__(self, parameter_value):
        super().__init__(parameter_name='page[count]',
                         parameter_value=parameter_value)
        self.error_description = "Page sizes must be integers."


class BadPageCursorParameter(ParameterInvalid):
    def __init__(self, parameter_value):
        super().__init__(parameter_name='page[cursor]',
                         parameter_value=parameter_value)
        self.error_description = "Provided cursor was not parsable."


class BadPageOffsetParameter(ParameterInvalid):
    def __init__(self, parameter_value):
        super().__init__(parameter_name='page[offset]',
                         parameter_value=parameter_value)
        self.error_description = "Page offsets must be integers."


class DataMissing(ParameterMissing):
    parameter_name = 'data'
