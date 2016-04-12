from enum import Enum


class JSONAPIVersion(Enum):
    JSONAPI_RC2 = "1.0RC2"
    JSONAPI_RC3 = "1.0RC3"
    JSONAPI_1_0 = "1.0"


JSONAPI_VALID_VERSIONS = [version for version in JSONAPIVersion]
_JSONAPI_DEFAULT_VERSION = JSONAPIVersion.JSONAPI_1_0


def get_default_version():
    return _JSONAPI_DEFAULT_VERSION


def set_default_version(version):
    global _JSONAPI_DEFAULT_VERSION
    _JSONAPI_DEFAULT_VERSION = version
