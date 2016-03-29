from cartographer.serializers import JSONAPISerializer
from cartographer.utils.version import JSONAPIVersion


class JSONAPINullSerializer(JSONAPISerializer):
    def as_linkage_json(self):
        return None

    def as_link_json(self, version):
        if version == JSONAPIVersion.JSONAPI_RC2:
            return {"id": None}
        elif version == JSONAPIVersion.JSONAPI_RC3:
            return {"linkage": self.as_linkage_json()}
        elif version == JSONAPIVersion.JSONAPI_1_0:
            return {"data": self.as_linkage_json()}
        else:
            raise ValueError("Unknown JSON API version")
