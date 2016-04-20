import itertools

from cartographer.utils.version import get_default_version


class PostedDocument(object):
    """This is a reader for JSON API Documents"""
    def __init__(self, json_data, version=None):
        self.json_data = json_data

        if version is None:
            version = get_default_version()
        self.version = version

    def data(self):
        if isinstance(self.json_data["data"], list):
            return [PostedResource(datum, self) for datum in self.json_data["data"]]
        else:
            return PostedResource(self.json_data["data"], self)

    def all_resource_json_data(self):
        data = self.json_data["data"]
        if not isinstance(data, list):
            data = [data]
        resources = itertools.chain([], data)

        if "included" in self.json_data:
            resources = itertools.chain(resources, self.json_data["included"])

        return resources

    def find_resource_by_type_and_id(self, resource_type, resource_id):
        for resource_json_data in self.all_resource_json_data():
            if resource_json_data.get("type") == resource_type and resource_json_data.get("id") == resource_id:
                return PostedResource(resource_json_data, self)
        return None


class PostedResource(object):
    """Represents a single object in a JSON API Document"""
    def __init__(self, json_data, document):
        self.json_data = json_data
        self.document = document

    def resource_type(self):
        return self.json_data["type"]

    def attribute(self, name):
        return self.json_data.get("attributes", {}).get(name)

    def assert_type(self, resource_type):
        if self.resource_type() != resource_type:
            raise Exception("Expected a " + resource_type + ", but got a " + self.resource_type())
        return self

    def relationship(self, relationship_name):
        if relationship_name not in self.json_data.get("relationships", {}):
            return None

        return PostedRelationship(self.json_data["relationships"][relationship_name], self.document)

    def relationship_id(self, relationship_name):
        relationship = self.relationship(relationship_name)
        return relationship.relationship_id() if relationship else None

    def related_resource(self, relationship_name):
        relationship = self.relationship(relationship_name)
        return relationship.resource() if relationship else None


class PostedRelationship(object):
    """Represents a named relationship in a JSON API Document"""
    def __init__(self, json_data, document):
        self.json_data = json_data
        self.document = document

    def relationship_id(self):
        if "data" in self.json_data:
            if isinstance(self.json_data["data"], list):
                return [PostedRelationshipID(datum, self.document) for datum in self.json_data["data"]]
            else:
                return PostedRelationshipID(self.json_data["data"], self.document)

    def resource(self):
        relationship_id = self.relationship_id()

        if isinstance(relationship_id, list):
            return [one_id.related_resource() for one_id in relationship_id]
        else:
            return relationship_id.related_resource()


class PostedRelationshipID(object):
    """Represents a the actual data of a relationship in a JSON API Document"""
    def __init__(self, json_data, document):
        self.json_data = json_data
        self.document = document

    def resource_type(self):
        return self.json_data.get("type")

    def resource_id(self):
        return self.json_data.get("id")

    def assert_type(self, resource_type):
        if self.resource_type() != resource_type:
            raise Exception("Expected a " + resource_type + ", but got a " + self.resource_type())
        return self

    def related_resource(self):
        return self.document.find_resource_by_type_and_id(self.resource_type(), self.resource_id())
