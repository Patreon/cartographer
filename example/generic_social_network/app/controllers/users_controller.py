#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, request, Blueprint
from generic_social_network.app import db
from generic_social_network.app.controllers.flask_jsonapi_router import FlaskJSONAPIRouter
from generic_social_network.app.models.query_builders.users_dbm import UsersDBM
from generic_social_network.app.resources.user_resource import UserSerializer, UserParser, UserResource

users_blueprint = Blueprint('users_blueprint', __name__)
users_dbm = UsersDBM(db)


class UserRouter(FlaskJSONAPIRouter):
    RESOURCE = UserResource
    MODEL_CREATE = users_dbm.create_from_json
    MODEL_UPDATE = users_dbm.update_from_json
    MODEL_DELETE = users_dbm.delete_by_id
    MODEL_LIST = users_dbm.all

UserRouter.register_router(users_blueprint)
