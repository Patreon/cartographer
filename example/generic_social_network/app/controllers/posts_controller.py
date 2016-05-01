#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, request, Blueprint
from generic_social_network.app import db
from generic_social_network.app.controllers.flask_jsonapi_router import FlaskJSONAPIRouter
from generic_social_network.app.models.query_builders.posts_dbm import PostsDBM
from generic_social_network.app.resources.post_resource import PostResource

posts_blueprint = Blueprint('posts_blueprint', __name__)
posts_dbm = PostsDBM(db)


class PostRouter(FlaskJSONAPIRouter):
    RESOURCE = PostResource
    MODEL_CREATE = posts_dbm.create_from_json
    MODEL_UPDATE = posts_dbm.update_from_json
    MODEL_DELETE = posts_dbm.delete_by_id
    MODEL_LIST = posts_dbm.all

PostRouter.register_router(posts_blueprint)
