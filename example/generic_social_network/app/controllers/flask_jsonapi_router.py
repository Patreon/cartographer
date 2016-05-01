from flask import abort, jsonify, request, session
from flask.views import MethodView

from cartographer.serializers import JSONAPICollectionSerializer


class FlaskJSONAPIRouter(MethodView):
    APP = None

    def post(self):
        # if not self.RESOURCE.MASK.can_create(session.user_id):
        #     abort(403)

        def model_found_behavior(model):
            if model is not None:
                abort(409, '{0} with id {1} already exists'.format(
                    self.RESOURCE.type_string(),
                    self.id_for_model(model)
                ))

        json = self.get_validated_inbound_model(None, model_found_behavior)

        model_id = self.MODEL_CREATE(json)
        model = self.RESOURCE.MODEL_GET(model_id)
        return self.success_with_model(model), 201

    def get(self, model_id):
        if model_id is None:
            return self.list()
        else:
            return self.read(model_id)

    def put(self, model_id):
        def model_found_behavior(model):
            if model is None:
                abort(404)
            # elif not self.RESOURCE.MASK.can_edit(model, session.user_id):
            #     abort(403)

        json = self.get_validated_inbound_model(model_id, model_found_behavior)

        self.MODEL_UPDATE(json)
        model_id = self.id_from_table_data(json)
        model = self.get_model_or_error(model_id)
        return self.success_with_model(model)

    def delete(self, model_id):
        model = self.get_model_or_error(model_id, 409)
        # if not self.RESOURCE.MASK.can_delete(model, session.user_id):
        #     abort(403)
        self.MODEL_DELETE(model_id)
        return jsonify({}), 204

    def read(self, model_id):
        model = self.get_model_or_error(model_id)
        # if not self.RESOURCE.MASK.can_view(model, session.user_id):
        #     abort(403)
        return self.success_with_model(model)

    def list(self):
        # if not self.RESOURCE.MASK.can_list(session.user_id):
        #     abort(403)
        all_models = self.MODEL_LIST()
        return jsonify(JSONAPICollectionSerializer([
            self.RESOURCE.SERIALIZER(
                model,
                inbound_request=request,
                inbound_session=session
            )
            for model in all_models
        ]).as_json_api_document())

    def get_model_or_error(self, model_id, error_code=404):
        model = self.RESOURCE.MODEL_GET(model_id)
        if model is None:
            abort(error_code)
        return model

    def success_with_model(self, model):
        return jsonify(self.RESOURCE.SERIALIZER(
            model,
            inbound_request=request,
            inbound_session=session
        ).as_json_api_document())

    def get_validated_inbound_model(self, model_id, model_found_behavior):
        table_data = None
        try:
            table_data = self.RESOURCE.PARSER(inbound_request=request).validated_table_data()
        except Exception as e:
            abort(400, ', '.join(e.args))
        table_data = self.standardize_ids_or_abort(table_data, model_id)
        model_id = self.id_from_table_data(table_data)
        model = None
        if model_id:
            model = self.RESOURCE.MODEL_GET(model_id)
        model_found_behavior(model)
        return table_data

    def standardize_ids_or_abort(self, json, model_id):
        if not json:
            abort(400, 'No {} data was provided in your request'.format(
                self.RESOURCE.type_string()
            ))
        id_key = self.key_for_id_in_table_data()
        if id_key in json and model_id:
            if model_id != json[id_key]:
                abort(400, 'Provided {} object had a id that did not match the provided route'.format(
                    self.RESOURCE.type_string()
                ))
        elif model_id:
            json[self.key_for_id_in_table_data()] = model_id
        return json

    @classmethod
    def key_for_id_in_table_data(cls):
        return cls.RESOURCE.SCHEMA.resource_id().model_attribute

    @classmethod
    def id_from_table_data(cls, table_data):
        return table_data.get(cls.key_for_id_in_table_data())

    @classmethod
    def id_for_model(cls, model):
        return cls.RESOURCE.SERIALIZER(model).resource_id()

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
