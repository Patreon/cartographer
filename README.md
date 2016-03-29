Cartographer
=====
Python library for using [JSON API](http://jsonapi.org/), especially with [Flask](http://flask.pocoo.org/).


Table of Contents
-----
1. Schemas
    1. Attributes
    2. Relationships
2. Resources
3. Parsers
4. Masks
5. Miscellaneous


Schemas
-----
The core element of the Cartographer system is the Schema.
The schema is a map from our models to their API output and vice versa.
It is formatted to resemble the output structure of JSON API resources:

```python
{
    "type": "widget",
    "id": StringAttribute("widget_id"),
    "atributes": {
        "price": IntAttribute("amount_cents")
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
`value`, for serializing from Python into JSON,
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
`resource`, for creating a `JSONAPISerializer` instance based on its input arguments.
Subclasses of `SchemaResource` can override this method
to customize serialization behavior.
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

But what's really going on behind the scenes?
To understand `SchemaSerializer`, one must first understand its superclass `JSONAPISerializer`.
`JSONAPISerializer` is a class which has four key methods,
one for each of the top-level keys in a JSON API resource:
* `resource_id`, to provide the `id` field
* `resource_type`, to provide the `type` field
* `as_json`, to provide the `attributes` fields
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


Parsers
-----
Parsers are the objects that are responsible for turning JSON input into Python code consumable by our model layer.
Typically, this is done via subclassing `SchemaParser`
and overriding the `schema` class method to point to a `Schema` class.
Should you have a complete `Schema` (as described above),
then that should be all that's needed to parse JSON input from your route file / controller.

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


Miscellaneous
-----
### `resource_registry`

The `resource_registry` is a map from `type` strings to their corresponding
model class, `Schema` class, `SchemaSerializer` and `SchemaParser` classes, and `Mask` class.
This is used when `SchemaRelationship` instances need to create their related resources,
and when Serializers and Parsers need to apply masking rules.


TODO:
-----
* make example (generic_social_network)
* check that the resource_registry strategy works
* more hidden gotchas. i.e. .get.prime in schema_serializer isnt yet complaining, but we definitely don't have anything re: multigets yet
* pull over tests
* port `patreon_py` over to using this library via `pip`