from cartographer.serializers import JSONAPISerializer
from cartographer.utils.version import JSONAPIVersion


class JSONAPICollectionSerializer(JSONAPISerializer):
    """This class be either be used directly or subclassed"""
    always_heterogeneous = False
    homogeneous_type = None
    links = {}

    def __init__(self, members=[], links={}):
        self._members = list(members) if members else members
        self.links = links

    def members(self):
        """Override in subclasses"""
        return self._members

    def is_collection(self):
        return True

    def next_page_url(self):
        return self.links.get('next')

    def prev_page_url(self):
        return self.links.get('prev')

    def last_page_url(self):
        return self.links.get('last')

    def first_page_url(self):
        return self.links.get('first')

    def pagination_urls(self):
        pagination_urls = {}
        if self.next_page_url():
            pagination_urls["next"] = self.next_page_url()
        if self.prev_page_url():
            pagination_urls["prev"] = self.prev_page_url()
        if self.first_page_url():
            pagination_urls["first"] = self.first_page_url()
        if self.last_page_url():
            pagination_urls["last"] = self.last_page_url()
        return pagination_urls

    def relationship_urls_json(self, version):
        relationship_urls_json = super().relationship_urls_json(version)
        relationship_urls_json.update(self.pagination_urls())
        return relationship_urls_json

    def as_link_json_rc2(self, version):
        resource_types = set([member.resource_type() for member in self.members()])
        is_heterogeneous = len(resource_types) > 1
        if is_heterogeneous or self.always_heterogeneous:
            data = [member.as_link_json() for member in self.members()]
            link_json = {
                "data": data
            }
            link_json.update(self.relationship_urls_json(version))
            return link_json
        resource_type = resource_types.pop() if resource_types else self.homogeneous_type
        if resource_type:
            link_json = {
                "type": resource_type,
                "ids": [member.resource_id_str() for member in self.members()]
            }
            link_json.update(self.relationship_urls_json(version))
            return link_json
        return {
            "ids": []
        }

    def as_linkage_json(self):
        return [member.as_linkage_json() for member in self.members()]

    def as_link_json(self, version):
        # if we drop RC2, then this override will probably go away
        if version == JSONAPIVersion.JSONAPI_RC2:
            return self.as_link_json_rc2(version)
        elif version == JSONAPIVersion.JSONAPI_RC3 or version == JSONAPIVersion.JSONAPI_1_0:
            key = 'data' if version == JSONAPIVersion.JSONAPI_1_0 else 'linkage'
            link_json = {key: self.as_linkage_json()}
            if version == JSONAPIVersion.JSONAPI_1_0:
                links = self.relationship_urls_json(version)
                if links:
                    link_json['links'] = links
            else:
                link_json.update(self.relationship_urls_json(version))
            meta = self.meta()
            if meta is not None:
                link_json["meta"] = meta
            return link_json
        else:
            raise ValueError("Unknown JSON API version")

    def as_json_api_data(self, version):
        return [member.as_json_api_data(version) for member in self.members()]

    def list_of_linked_resources(self):
        return self.members()
