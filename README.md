Cartographer
=====
[![CI Status](https://circleci.com/gh/Patreon/cartographer.svg?style=shield&circle-token=d4ade402a04c4a6c63172d78ebfe705a799fc3f4)](https://circleci.com/gh/Patreon/cartographer)
[![Version](https://img.shields.io/pypi/v/cartographer.svg?style=flat)](http://pypi.python.org/pypi/cartographer)
[![License](https://img.shields.io/pypi/l/cartographer.svg?style=flat)](http://pypi.python.org/pypi/cartographer)
[![Python Version](https://img.shields.io/pypi/pyversions/cartographer.svg?style=flat)](http://pypi.python.org/pypi/cartographer)

Python library for using [JSON API](http://jsonapi.org/), especially with [Flask](http://flask.pocoo.org/).


Table of Contents
-----
1. Schemas
    1. Attributes
    2. Relationships
2. Resources
3. Parsers
4. Masks
5. APIResource
6. Installation
7. Contributing


Schemas
-----
The core element of the Cartographer system is the Schema.
The schema is a map from our models to their API output and vice versa.
It is formatted to resemble the output structure of JSON API resources:

```python
{
    "type": "widget",
    "id": StringAttribute()
            .read_from(model_property="widget_id")
            .self_explanatory(),
    "attributes": {
        "price": IntAttribute()
            .read_from(model_property="amount_cents")
            .description('The wiget price in cents'),
    },
    "relationships": {
        "distributing-store": SchemaRelationship(
            model_type="store",
            id_attribute="store_id"
        )
    }
}
```

The keys in this dictionary are the keys in the JSON API output or input.
The values are objects which describe what properties in our system these JSON API keys represent.


#### Type and ID

JSON API resources always have, at minimum, two keys: `type`, and `id`.
These two keys uniquely identify the resource.
Typically, in the API route structure, one can refer to resource with
`https://api.yourservice.com/<type>/<id>`,
issuing `GET`, `PATCH`, or `DELETE` requests to that URL.


#### Attributes

The attributes section defines properties of the resource in question.
The values in the schema are `SchemaAttribute` instances,
responsible for describing how to translate to and from our Python models.

`SchemaAttribute` is a very simple class, with two primary methods:
`to_json`, for serializing from Python into JSON,
and `from_json` for parsing from JSON into Python.
Subclasses of `SchemaAttribute` can override either of these methods
to customize (de)serialization behavior.

Currently, there are 5 subclasses of `SchemaAttribute`:
* `BoolAttribute`
* `DateAttribute`
* `IntAttribute`
* `StringAttribute`
* `JSONAttribute`
    * In general for JSON API, nested attributes are discouraged, so usage of `JSONAttribute` is discouraged


#### Relationships

The relationships section defines the related resources of the resource in question.
The values in the schema are `SchemaRelationship` instances,
responsible for describing how to translate to and from our Python models.

`SchemaRelationship` is a more complicated class, with only one primary method,
`related_serializer`, for creating a `JSONAPISerializer` instance based on its input arguments.
Subclasses of `SchemaResource` can override this method
to customize the `JSONAPISerializer` to be returned.
Parsing of related resources is handled by the `PostedDocument` class in the Parsers section of this README.

Currently, there is only one subclass of `SchemaRelationship`,
`ArrayRelationship`, which creates an `JSONAPICollectionSerializer` rather than a single `JSONAPISerializer`


Serializers
-----
Serializers are the objects that are responsible for turning Python code into JSON output.
Typically, this is done via subclassing `SchemaSerializer`
and overriding the `schema` class method to point to a `Schema` class.
Should you have a complete `Schema` (as described above),
then that (plus adding your new `SchemaSerializer` to the [`resource_registry`](#Miscellaneous))
should be all that's needed to serialize a model into JSON output in your route file / controller.
For example:
```python
class UserSerializer(SchemaSerializer):
    @classmethod
    def schema(cls):
        return UserSchema
```

But what's really going on behind the scenes?
To understand `SchemaSerializer`, one must first understand its superclass `JSONAPISerializer`.
`JSONAPISerializer` is a class which has four key methods,
one for each of the top-level keys in a JSON API resource:
* `resource_id`, to provide the `id` field
* `resource_type`, to provide the `type` field
* `attributes_dictionary`, to provide the `attributes` fields
* `linked_resources`, to provide the `relationships` fields

Overriding and implementing these four methods in a subclass of `JSONAPISerializer`
allows you to call `as_json_api_document()` on your subclass
and get out a properly formatted JSON API response.

`SchemaResource`'s core mechanic is as simple as that:
it uses the provided `Schema` and the `model` it is initialized with
to implement each of those four `JSONAPISerializer` methods.

In addition to saving you the work of overriding those four methods for each resource type in your API,
`SchemaResource` also gives you JSON API query parameter handling for free:
* By passing in the `requested_fields` named initialization parameter,
`SchemaResource` will only serialize attributes matching those listed keys
* By passing in the `includes` named initialization parameter,
`SchemaResource` will only serialize related resources matching those listed keys.
* But rather than either of those, you should just pass in `inbound_request` and `inbound_session`,
which `SchemaResource` will use to parse the `requested_fields` and `includes` off of the request object,
and the `current_user_id` off of the session object for you.
* Also, each `SchemaSerializer` will initialize each related resource `Serializer`
with the appropriate query parameter handling, via the `parent_resource` named initialization parameter
(don't worry, you shouldn't have to worry about this unless you're manually implementing
a method on a `Serializer` to return a custom related resource `Serializer`
rather than relying on `SchemaRelationship`s in the `Schema`).


Parsers
-----
Parsers are the objects that are responsible for turning JSON input into Python code consumable by our model layer.
Typically, this is done via subclassing `SchemaParser`
and overriding the `schema` class method to point to a `Schema` class.
Should you have a complete `Schema` (as described above),
then that should be all that's needed to parse JSON input from your route file / controller.
For example:
```python
class UserParser(SchemaParser):
    @classmethod
    def schema(cls):
        return UserSchema
```

But what's really going on behind the scenes?
To understand `SchemaParser`, one must first understand its superclass `PostedDocument`.
`PostedDocument` is a class which allows easy navigation of a JSON API document which has been sent to the server.
The `PostedDocument` provides this via three related classes:
* `PostedResource`, which represents a single object in a JSON API Document
* `PostedRelationship`, which represents a named relationship in a JSON API Document
* `PostedRelationshipID`, which represents a the actual data of a relationship in a JSON API Document

`SchemaParser` uses these convenience classes and their methods to navigate the JSON input
and turn it into a Python dictionary.
This return value is formatted such that it can be dropped directly into a
SQLAlchemy `.insert()` or `.get(widget_id).update()` call.
This typically amounts to using the `Schema` to figure out the keys of that dictionary,
and flattening the `attributes` and `relationships` sections into the top level.

`SchemaParser` also provides an overridable method `validate` that allows for validation of the JSON input.
Calling `validated_table_data` from the route / controller is encouraged,
as this will validate the input before parsing it.


Masks
-----
Masks are the objects that are responsible for controlling user access
to particular resources, and their attributes and relationships.

To control access to the resources themselves, Masks have five methods, corresponding to CRUDL:
* `can_create` (true by default)
* `can_view` (true by default)
* `can_list` (false by default)
* `can_edit` (false by default)
* `can_delete` (false by default)

These can and should be used in your route file / controller to control access to the requested resource(s).

Should one be allowed access at that level,
Masks can provide more fine-grained access control at the per-attribute and per-relationship level:
* `fields_cant_view` (always called after `can_view`)
* `fields_cant_edit` (always called after `can_edit`)
* `includes_cant_create` (always called after `can_edit`)
* `includes_cant_view` (always called after `can_view`)
* `includes_cant_edit` (always called after `can_edit`)
* `includes_cant_delete` (always called after `can_edit`)

Each of these methods returns the empty list by default,
so it is strongly encouraged that you write your Mask alongside your Schema
to avoid any security issues.

By using `SchemaSerializer` and `SchemaParser`,
the corresponding Mask for your resource will be used at (de)serialization time
to appropriately remove fields from the output, or disallow their input.
`SchemaSerializer` and `SchemaParser`, however,
will assume that the CRUDL checks have already been used,
and will not check whether or not the resource *itself* should be (de)serialized.

To hook your Mask up to its corresponding Serializer and Parser, you should register your Mask in its appropriate place in the [`resource_registry`](#Miscellaneous).


Resource Registration
-----
### `resource_registry`

The `resource_registry` is a map from `type` strings to a dict of:
* `ResourceRegistryKeys.MODEL`, the resource's corresponding model class
* `ResourceRegistryKeys.MODEL_GET`, a method for fetching models by id
* `ResourceRegistryKeys.MODEL_PRIME`, a method for optimizing future `MODEL_GET` calls
* `ResourceRegistryKeys.SCHEMA`, the resource's corresponding `Schema` class
* `ResourceRegistryKeys.SERIALIZER`, the resource's corresponding `SchemaSerializer` class
* `ResourceRegistryKeys.PARSER`, the resource's corresponding `SchemaParser` class
* `ResourceRegistryKeys.MASK`, the resource's corresponding `Mask` class

This map is used under the hood when `SchemaRelationship` instances need to create their related resources,
and when `Serializer`s and `Parser`s need to apply `mask`ing rules.

You can add your classes to the registry via
`cartographer.resource_registry.get_resource_registry_container().register_resource()`,
or (more commonly) use the `APIResource` convenience class and decorators outlined below.

### `APIResource`

`APIResource` is a convenience class for registering
the family of classes used in cartographer for a given domain object.
It has a class properties corresponding to the entries in the `resource_registry`:
* `APIResource.SCHEMA`, a subclass of `Schema`
* `APIResource.SERIALIZER`, a subclass of `SchemaSerializer`
* `APIResource.PARSER`, a subclass of `SchemaParser`
* `APIResource.MASK`, a subclass of `BaseMask`
* `APIResource.MODEL`, the object class which you are serializing and parsing
* `APIResource.MODEL_GET`, a method that can be passed an `id` and will return an instance of `APIResource.MODEL`
* `APIResource.MODEL_PRIME`, a method that can be passed an `id` which will improve the performance of future `MODEL_GET` calls

To use this convenience class, you subclass it and either define those class properties
and then call `MyAPIResourceSubclass.register_class()`
or use e.g.
```python
@MyAPIResourceSubclass.register(ResourceRegistryKeys.PARSER)
class MySchemaParserSubclass(SchemaParser):
    ...
```


Installation
-----
Get the egg from [PyPI](https://pypi.python.org/pypi/cartographer),
typically via `pip`: `pip install cartographer`


Contributing
---
1. `git clone git@github.com:Patreon/cartographer.git`
2. `cd cartographer`
3. `git checkout -b my-meaningful-improvements`
4. Write beautiful code that improves the project, creating or modifying tests to prove correctness.
5. Commit said code and tests in a well-organized way.
6. Confirm tests pass with `./run_tests.sh` (you may need to `./setup_environments.sh` first)
7. `git push origin my-meaningful-improvements`
8. Open a pull request (`hub pull-request`, if you have [`hub`](https://github.com/github/hub))
9. Have a chill discussion with the community about how to best integrate your improvements into mainline deployments
