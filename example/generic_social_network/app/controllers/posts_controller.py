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

    def create_model(self, table_data, request=None, session=None):
        return posts_dbm.create_from_json(table_data)

    def update_model(self, table_data, request=None, session=None):
        return posts_dbm.update_from_json(table_data)

    def delete_model(self, model_id, request=None, session=None):
        return posts_dbm.delete_by_id(model_id)

    def list_models(self, request=None, session=None):
        return posts_dbm.all


PostRouter.register_router(posts_blueprint)
