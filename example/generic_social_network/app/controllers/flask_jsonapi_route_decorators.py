import functools
from flask import abort, jsonify, request, session


def parse_inbound_jsonapi_request(resource, http_method):
    def decorator(route):
        @functools.wraps(route)
        def wrapped_route(*args, **kwargs):
            # Get the table_data from the parser
            table_data = None
            try:
                table_data = resource.PARSER(inbound_request=request, inbound_session=session).validated_table_data()
            except Exception as e:
                abort(400, ', '.join(e.args))
            if not table_data:
                abort(400, 'No {} data was provided in your request'.format(
                    resource.type_string()
                ))

            # standardize IDs (compare the route against the request body)
            model_id = kwargs.get('model_id')
            id_key = resource.SCHEMA.resource_id().model_attribute
            if id_key:
                if id_key in table_data and model_id:
                    if model_id != table_data[id_key]:
                        abort(400, 'Provided {} object had a id that did not match the provided route'.format(
                            resource.type_string()
                        ))
                elif model_id:
                    table_data[id_key] = model_id
                model_id = table_data.get(id_key)

            # put the table_data and model_id in the kwargs to pass them along
            kwargs['table_data'] = table_data
            kwargs['model_id'] = model_id
            return route(*args, **kwargs)
        return wrapped_route
    return decorator


def find_prior_model(resource):
    def decorator(route):
        @functools.wraps(route)
        def wrapped_route(*args, **kwargs):
            model = None
            if 'model_id' in kwargs:
                model = resource.MODEL_GET(kwargs['model_id'])
            kwargs['prior_model'] = model
            return route(*args, **kwargs)
        return wrapped_route
    return decorator


def serialize_outbound_jsonapi_response(resource, http_method):
    code_for_http_method = {
        'POST': 201,
        'GET': 200,
        'PUT': 200,
        'DELETE': 204
    }[http_method]

    def decorator(route):
        @functools.wraps(route)
        def wrapped_route(*args, **kwargs):
            model = route(*args, **kwargs)
            jsonapi_document = jsonify({})
            if model:
                jsonapi_document = jsonify(resource.SERIALIZER(
                    model,
                    inbound_request=request,
                    inbound_session=session
                ).as_json_api_document())
            return jsonapi_document, code_for_http_method
        return wrapped_route
    return decorator
