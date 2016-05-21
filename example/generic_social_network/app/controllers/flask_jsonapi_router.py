from flask import abort, jsonify, request, session
from flask.views import MethodView
from cartographer.serializers import JSONAPICollectionSerializer

from .flask_jsonapi_route_decorators import parse_inbound_jsonapi_request, find_prior_model, \
    serialize_outbound_jsonapi_response


class FlaskJSONAPIRouter(MethodView):
    APP = None

    def post(self):
        @parse_inbound_jsonapi_request(self.RESOURCE, 'POST')
        @find_prior_model(self.RESOURCE)
        @serialize_outbound_jsonapi_response(self.RESOURCE, 'POST')
        def inner_post(table_data=None, model_id=None, prior_model=None):
            # if not self.RESOURCE.MASK.can_create(session.user_id):
            #     abort(403)

            if prior_model is not None:
                abort(409, '{0} with id {1} already exists'.format(
                    self.RESOURCE.type_string(),
                    model_id
                ))

            model_id = self.create_model(table_data, inbound_request=request, inbound_session=session)
            return self.RESOURCE.MODEL_GET(model_id)

        return inner_post()

    def get(self, model_id):
        if model_id is None:
            return self.list()
        else:
            return self.read(model_id)

    def put(self, model_id):
        @parse_inbound_jsonapi_request(self.RESOURCE, 'PUT')
        @find_prior_model(self.RESOURCE)
        @serialize_outbound_jsonapi_response(self.RESOURCE, 'PUT')
        def inner_put(table_data=None, model_id=None, prior_model=None):
            if prior_model is None:
                abort(404)
            # elif not self.RESOURCE.MASK.can_edit(prior_model, session.user_id):
            #     abort(403)

            self.update_model(table_data, inbound_request=request, inbound_session=session)
            return self.RESOURCE.MODEL_GET(model_id)

        return inner_put(model_id=model_id)

    def delete(self, model_id):
        @find_prior_model(self.RESOURCE)
        @serialize_outbound_jsonapi_response(self.RESOURCE, 'DELETE')
        def inner_delete(model_id=None, prior_model=None):
            # if not self.RESOURCE.MASK.can_delete(prior_model, session.user_id):
            #     abort(403)
            if not prior_model:
                abort(409)
            self.delete_model(model_id, inbound_request=request, inbound_session=session)
            return None

        return inner_delete(model_id=model_id)

    def read(self, model_id):
        @find_prior_model(self.RESOURCE)
        @serialize_outbound_jsonapi_response(self.RESOURCE, 'GET')
        def inner_read(model_id=None, prior_model=None):
            # if not self.RESOURCE.MASK.can_view(model, session.user_id):
            #     abort(403)
            if prior_model is None:
                abort(404)
            return prior_model

        return inner_read(model_id=model_id)

    def list(self):
        # if not self.RESOURCE.MASK.can_list(session.user_id):
        #     abort(403)
        all_models = self.list_models(request=request, inbound_session=session)
        return jsonify(JSONAPICollectionSerializer([
            self.RESOURCE.SERIALIZER(
                model,
                inbound_request=request,
                inbound_session=session
            )
            for model in all_models
        ]).as_json_api_document()), 200

    @classmethod
    def register_router(cls, app):
        cls.APP = app
        endpoint_str = cls.__class__.__name__
        url = '/' + cls.RESOURCE.type_string() + 's'
        pk = 'model_id'
        pk_type = 'string'

        view_func = cls.as_view(endpoint_str)
        app.add_url_rule(url, defaults={pk: None},
                         view_func=view_func, methods=['GET', ])
        app.add_url_rule(url, view_func=view_func, methods=['POST', ])
        app.add_url_rule('%s/<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                         methods=['GET', 'PUT', 'DELETE'])
