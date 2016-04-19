import importlib
from collections import deque

from cartographer.utils.version import get_default_version, JSONAPIVersion


class JSONAPISerializer(object):
    def resource_id(self):
        """Override this in a subclass to return a unique id string"""
        raise NotImplementedError()

    @classmethod
    def resource_type(cls):
        """Override this in a subclass to return a type name string"""
        raise NotImplementedError()

    def attributes_dictionary(self):
        """Override this in a subclass to return json"""
        raise NotImplementedError()

    def linked_resources(self):
        """Override this in a subclass to link to other resources"""
        return {}

    def resource_url(self):
        return None

    def relationship_url(self):
        return None

    # internal usage

    def as_json_api_document(self, version=None):
        version = self._get_version(version)
        return self.document_with_data(self.as_json_api_data(version), version)

    def resource_id_str(self):
        id_ = self.resource_id()
        return str(id_) if id_ is not None else None

    def resource_key(self):
        try:
            if self.resource_id_str():
                return (self.resource_type(), self.resource_id_str())
            else:  # Collection or Null
                return None
        except NotImplementedError:
            return None

    def is_collection(self):
        return False

    def list_of_linked_resources(self):
        return self.linked_resources().values()

    def deeply_linked_resources(self, skip_self=True):
        all_linked_resources = []
        q = deque()
        resources_enqueued = set()

        def enqueue_if_never_enqued(linked_resource):
            linked_key = linked_resource.resource_key()
            if (not linked_key or
                    (linked_key not in resources_enqueued)):
                q.append(linked_resource)
                resources_enqueued.add(linked_key)

        def enqueue_linked_resources(resource):
            for linked_resource in resource.list_of_linked_resources():
                enqueue_if_never_enqued(linked_resource)

        if skip_self:  # prevent the toplevel object/collection from appearing in "linked"
            if self.is_collection(): # self is a collection, skip its members
                # I'm iterating over self.members() twice to make sure that
                # everything in the top-level collection gets marked as enqueued
                # before we enqueue any of their linked resources.
                # this prevents links between top-level resources from
                # causing problems
                for member_resource in self.members():
                    resources_enqueued.add(member_resource.resource_key())
                for member_resource in self.members():
                    enqueue_linked_resources(member_resource)
            else: # self is a single object, skip it and enqueue its children
                resources_enqueued.add(self.resource_key())
                enqueue_linked_resources(self)
        else:
            enqueue_if_never_enqued(self)

        while q:
            resource = q.popleft()
            if resource.resource_key():
                all_linked_resources.append(resource)

            enqueue_linked_resources(resource)

        return all_linked_resources

    def deeply_linked_resources_as_json(self, version, skip_self=True):
        return list(filter(None, [
            resource.as_json_api_data(version)
            for resource
            in self.deeply_linked_resources(skip_self)
        ]))

    def resource_links_json(self, version):
        links_json = {
            link_name: resource.as_link_json(version)
            for link_name, resource in self.linked_resources().items()
        }
        if self.resource_url():
            links_json["self"] = self.resource_url()
        return links_json

    def as_linkage_json(self):
        return {"type": self.resource_type(), "id": self.resource_id_str()}

    def relationship_urls_json(self, version):
        relationship_urls_json = {}
        if self.relationship_url():
            relationship_urls_json["self"] = self.relationship_url()
        if self.resource_url():
            if version == JSONAPIVersion.JSONAPI_RC2:
                relationship_urls_json["resource"] = self.resource_url()
            elif version == JSONAPIVersion.JSONAPI_RC3 or version == JSONAPIVersion.JSONAPI_1_0:
                relationship_urls_json["related"] = self.resource_url()
            else:
                raise ValueError("Unknown JSON API version")
        return relationship_urls_json

    def as_link_json(self, version):
        link_json = {}

        if version == JSONAPIVersion.JSONAPI_RC2:
            link_json.update(self.as_linkage_json())
        elif version == JSONAPIVersion.JSONAPI_RC3:
            link_json["linkage"] = self.as_linkage_json()
        elif version == JSONAPIVersion.JSONAPI_1_0:
            link_json["data"] = self.as_linkage_json()
        else:
            raise ValueError("Unknown JSON API version")

        link_json.update(self.relationship_urls_json(version))
        meta = self.meta()
        if meta is not None:
            link_json["meta"] = meta

        return link_json

    def as_json_api_data(self, version):
        if version == JSONAPIVersion.JSONAPI_1_0:
            attributes = self.attributes_dictionary()
            if 'id' in attributes:
                del attributes['id']
            json = {'attributes': attributes}
        else:
            json = self.attributes_dictionary()
        json["id"] = self.resource_id_str()
        json["type"] = self.resource_type()
        links = self.resource_links_json(version)
        if links:
            if version == JSONAPIVersion.JSONAPI_1_0:
                json["relationships"] = links
            else:
                json["links"] = links
        # TODO: optional keys: "meta"
        return json

    def next_page_url(self):
        return None

    def prev_page_url(self):
        return None

    def last_page_url(self):
        return None

    def first_page_url(self):
        return None

    def meta(self):
        return None

    def document_links_urls(self):
        links = {
            "next": self.next_page_url(),
            "prev": self.prev_page_url(),
            "last": self.last_page_url(),
            "first": self.first_page_url()
        }
        links = {key: value for key, value in links.items() if value}
        return links

    def included_resources_key(self, version):
        if version == JSONAPIVersion.JSONAPI_RC2:
            return "linked"
        elif version == JSONAPIVersion.JSONAPI_RC3 or version == JSONAPIVersion.JSONAPI_1_0:
            return "included"
        else:
            raise ValueError("Unknown JSON API version")

    def as_json_api_relationship_document(self, version=None):
        version = self._get_version(version)
        return self.document_with_data(self.as_linkage_json(), version, False)

    def document_with_data(self, data, version, skip_self=True):
        response = {"data": data}
        included_resources = self.deeply_linked_resources_as_json(version, skip_self)
        if included_resources:
            response[self.included_resources_key(version)] = included_resources
        links = self.document_links_urls()
        if links:
            response["links"] = links
        meta = self.meta()
        if meta is not None:
            response["meta"] = meta
        return response

    def _get_version(self, version=None):
        return version or self._flask_json_api_version() or get_default_version()

    # flask request context

    @staticmethod
    def _has_flask_request_context():
        return importlib.util.find_spec("flask") is not None

    @staticmethod
    def _flask_json_api_version():
        if JSONAPISerializer._has_flask_request_context():
            from flask import request
            if request:
                return request.get_json_api_version()
        return None
