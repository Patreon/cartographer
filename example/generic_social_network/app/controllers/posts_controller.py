#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, request, Blueprint
from generic_social_network.app import db
from generic_social_network.app.models.query_builders.posts_dbm import PostsDBM
from generic_social_network.app.models.query_builders.users_dbm import UsersDBM
from generic_social_network.app.resources.post_resource import PostSerializer, PostParser

posts_blueprint = Blueprint('posts_blueprint', __name__)
posts_dbm = PostsDBM(db)
users_dbm = UsersDBM(db)


@posts_blueprint.route('/posts/<int:post_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def route_post(post_id):
    if request.method == 'POST':
        return create_post(request, post_id)
    elif request.method == 'PUT':
        return update_post(request, post_id)
    elif request.method == 'DELETE':
        return delete_post(request, post_id)
    else:
        return read_post(post_id)


@posts_blueprint.route('/posts', methods=['POST', 'GET'])
def route_posts():
    if request.method == 'POST':
        return create_post(request, None)
    else:
        return list_posts(request)


def read_post(post_id):
    post = get_post_or_404(post_id)
    return success_with_post(post)


def list_posts(request_):
    return jsonify(JSONAPICollectionSerializer([
        PostSerializer(
            post,
            inbound_request=request_
        )
        for post in posts_dbm.all()
    ]).as_json_api_document())


def delete_post(request_, post_id):
    post = get_post_or_404(post_id)
    posts_dbm.delete(post_id=post_id)
    return success_with_post(post)


def update_post(request_, post_id):
    def post_found_behavior(post):
        if post is None:
            abort(404)

    json = validate_inbound_post(request_, post_id, post_found_behavior)

    posts_dbm.update_from_json(json)
    return read_post(json['post_id'])


def create_post(request_, post_id):
    def post_found_behavior(post):
        if post is not None:
            abort(409, '{0} with id {1} already exists'.format('post', post_id))

    json = validate_inbound_post(request_, post_id, post_found_behavior)

    posts_dbm.create_from_json(json)
    post = posts_dbm.find_by_id(json['post_id'])
    return success_with_post(post), 201


def get_post_or_404(post_id):
    post = posts_dbm.find_by_id(post_id)
    if post is None:
        abort(404)
    return post


def success_with_post(post, request_=None):
    if request_ is None:
        request_ = request
    return jsonify(PostSerializer(post, inbound_request=request_).as_json_api_document())


def validate_inbound_post(request_, post_id, post_found_behavior):
    table_data = PostParser(inbound_request=request_).validated_table_data()
    table_data = standardize_post_ids_or_abort(table_data, post_id)
    post_id = table_data['post_id']
    post = posts_dbm.find_by_id(post_id)
    post_found_behavior(post)
    return table_data


def standardize_post_ids_or_abort(json, post_id):
    if not json:
        abort(400, 'No post data was provided in your request')
    if 'post_id' in json:
        if post_id != json['post_id']:
            abort(400, 'Provided post object had a id that did not match the provided route')
    elif post_id:
        json['post_id'] = post_id
    return json
