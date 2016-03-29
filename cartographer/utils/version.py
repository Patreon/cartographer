from enum import Enum


class JSONAPIVersion(Enum):
    JSONAPI_RC2 = "1.0RC2"
    JSONAPI_RC3 = "1.0RC3"
    JSONAPI_1_0 = "1.0"


JSONAPI_DEFAULT_VERSION = JSONAPIVersion.JSONAPI_1_0
