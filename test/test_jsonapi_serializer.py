from cartographer.serializers import JSONAPISerializer, JSONAPINullSerializer, \
    JSONAPICollectionSerializer
from nose.tools import *


class ExampleSerializer(JSONAPISerializer):
    def __init__(self, id):
        self._id = id

    def resource_type(self):
        return "example"

    def resource_id(self):
        return str(self._id)

    def attributes_dictionary(self):
        return {
            "title": "an example"
        }


class LinkingResource(JSONAPISerializer):
    def __init__(self, id, link):
        self._id = id
        self._link = link

    def resource_type(self):
        return "linking_example"

    def resource_id(self):
        return str(self._id)

    def attributes_dictionary(self):
        return {
            "title": "an example of linking"
        }

    def linked_resources(self):
        return {
            "something": self._link
        }


def test_api_resource():
    resource = ExampleSerializer(1)
    expected_json = {
        "data": {
            "type": "example",
            "id": "1",
            "attributes": {
                "title": "an example"
            }
        }
    }
    assert_equal(expected_json, resource.as_json_api_document())


def test_linked_resource():
    resource = LinkingResource(1, ExampleSerializer(2))
    expected_json = {
        "data": {
            "type": "linking_example",
            "id": "1",
            "attributes": {
                "title": "an example of linking"
            },
            "relationships": {
                "something": {
                    "data": {"type": "example", "id": "2"}
                }
            }
        },
        "included": [
            {
                "type": "example",
                "id": "2",
                "attributes": {
                    "title": "an example"
                }
            }
        ]
    }
    assert_equal(expected_json, resource.as_json_api_document())


def test_linked_null():
    resource = LinkingResource(1, JSONAPINullSerializer())
    expected_json = {
        "data": {
            "type": "linking_example",
            "id": "1",
            "attributes": {
                "title": "an example of linking"
            },
            "relationships": {
                "something": {
                    "data": None
                }
            }
        }
    }
    assert_equal(expected_json, resource.as_json_api_document())


def test_linked_collection():
    resource = LinkingResource(1, JSONAPICollectionSerializer([ExampleSerializer(2), ExampleSerializer(3)]))
    expected_json = {
        "data": {
            "type": "linking_example",
            "id": "1",
            "attributes": {
                "title": "an example of linking"
            },
            "relationships": {
                "something": {
                    "data": [{"type": "example", "id": "2"}, {"type": "example", "id": "3"}]
                }
            }
        },
        "included": [
            {
                "type": "example",
                "id": "2",
                "attributes": {
                    "title": "an example"
                }
            },
            {
                "type": "example",
                "id": "3",
                "attributes": {
                    "title": "an example"
                }
            },
        ]
    }
    assert_equal(expected_json, resource.as_json_api_document())


def test_linked_heterogeneous_collection():
    resource = LinkingResource(1, JSONAPICollectionSerializer([ExampleSerializer(2), LinkingResource(2, ExampleSerializer(3))]))
    expected_json = {
        "data": {
            "type": "linking_example",
            "id": "1",
            "attributes": {
                "title": "an example of linking"
            },
            "relationships": {
                "something": {
                    "data": [{
                        "type": "example",
                        "id": "2"
                    }, {
                        "type": "linking_example",
                        "id": "2"
                    }]
                }
            }
        },
        "included": [
            {
                "type": "example",
                "id": "2",
                "attributes": {
                    "title": "an example"
                }
            },
            {
                "type": "linking_example",
                "id": "2",
                "attributes": {
                    "title": "an example of linking"
                },
                "relationships": {"something": {"data": {"type": "example", "id": "3"}}}
            },
            {
                "type": "example",
                "id": "3",
                "attributes": {
                    "title": "an example"
                }
            },
        ]
    }
    assert_equal(expected_json, resource.as_json_api_document())


def test_toplevel_collection():
    resource = JSONAPICollectionSerializer([ExampleSerializer(2), LinkingResource(2, ExampleSerializer(3))])
    expected_json = {
        "data": [
            {
                "type": "example",
                "id": "2",
                "attributes": {
                    "title": "an example"
                }
            },
            {
                "type": "linking_example",
                "id": "2",
                "attributes": {
                    "title": "an example of linking"
                },
                "relationships": {"something": {"data": {"type": "example", "id": "3"}}}
            },
        ],
        "included": [
            {
                "type": "example",
                "id": "3",
                "attributes": {
                    "title": "an example"
                }
            },
        ]
    }
    assert_equal.__self__.maxDiff = None
    assert_equal(expected_json, resource.as_json_api_document())


def test_toplevel_collection_with_repeats():
    example_resource = ExampleSerializer(10)
    resource = JSONAPICollectionSerializer([
        example_resource,
        LinkingResource(2,
            JSONAPICollectionSerializer([
                example_resource,
                LinkingResource(3, example_resource)
            ])
        )
    ])
    expected_json = {
        "data": [
            {
                "type": "example",
                "id": "10",
                "attributes": {
                    "title": "an example"
                }
            },
            {
                "type": "linking_example",
                "id": "2",
                "attributes": {
                    "title": "an example of linking"
                },
                "relationships": {
                    "something": {"data": [
                        {"type": "example", "id": "10"},
                        {"type": "linking_example", "id": "3"}
                    ]}
                }
            },
        ],
        "included": [
            {
                "type": "linking_example",
                "id": "3",
                "attributes": {
                    "title": "an example of linking"
                },
                "relationships": {
                    "something": {"data": {"type": "example", "id": "10"}}
                }
            },
        ]
    }
    assert_equal(expected_json, resource.as_json_api_document())
