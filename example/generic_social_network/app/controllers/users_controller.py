#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, request, Blueprint
from generic_social_network.app import db

from generic_social_network.app.models.query_builders.users_dbm import UsersDBM
from generic_social_network.app.resources.user_resource import UserSerializer, UserParser

users_blueprint = Blueprint('users_blueprint', __name__)
users_dbm = UsersDBM(db)


@users_blueprint.route('/users/<int:user_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def route_user(user_id):
    if request.method == 'POST':
        return create_user(request, user_id)
    elif request.method == 'PUT':
        return update_user(request, user_id)
    elif request.method == 'DELETE':
        return delete_user(user_id)
    else:
        return read_user(user_id)


@users_blueprint.route('/users', methods=['POST', 'GET'])
def route_users():
    if request.method == 'POST':
        return create_user(request, None)
    else:
        return list_users(request)


def read_user(user_id):
    user = get_user_or_404(user_id)
    return success_with_user(user)


def list_users(request_):
    return jsonify(JSONAPICollectionSerializer([
        UserSerializer(
            user,
            inbound_request=request_
        )
        for user in users_dbm.all()
    ]).as_json_api_document())


def delete_user(user_id):
    user = get_user_or_404(user_id)
    users_dbm.delete(user_id=user_id)
    return success_with_user(user)


def update_user(request_, user_id):
    def user_found_behavior(user):
        if user is None:
            abort(404)

    json = validate_inbound_user(request_, user_id, user_found_behavior)

    users_dbm.update_from_json(json)
    return read_user(json['user_id'])


def create_user(request_, user_id):
    def user_found_behavior(user_):
        if user_ is not None:
            abort(409, '{0} with id {1} already exists'.format('user', user_id))

    json = validate_inbound_user(request_, user_id, user_found_behavior)

    users_dbm.create_from_json(json)
    user = users_dbm.find_by_id(json['user_id'])
    return success_with_user(user), 201


def get_user_or_404(user_id):
    user = users_dbm.find_by_id(user_id)
    if user is None:
        abort(404)
    return user


def validate_inbound_user(request_, user_id, user_found_behavior):
    table_data = UserParser(inbound_request=request_).validated_table_data()
    table_data = standardize_user_ids_or_abort(table_data, user_id)
    user_id = table_data['user_id']
    user = users_dbm.find_by_id(user_id)
    user_found_behavior(user)
    return table_data


def standardize_user_ids_or_abort(json, user_id):
    if not json:
        abort(400, 'No user data was provided in your request')
    if 'user_id' in json:
        if user_id != json['user_id']:
            abort(400, 'Provided user object had a id that did not match the provided route')
    elif user_id:
        json['user_id'] = user_id
    return json


def success_with_user(user):
    return jsonify(UserSerializer(user).as_json_api_document())
