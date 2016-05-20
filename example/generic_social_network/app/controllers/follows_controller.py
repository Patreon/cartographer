#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, request, Blueprint
from generic_social_network.app import db
from generic_social_network.app.models.query_builders.follows_dbm import FollowsDBM
from generic_social_network.app.models.query_builders.people_dbm import PeopleDBM
from generic_social_network.app.resources.follow_resource import FollowSerializer

follows_blueprint = Blueprint('follows_blueprint', __name__)
follows_dbm = FollowsDBM(db)
people_dbm = PeopleDBM(db)


@follows_blueprint.route('/follows/<follower_id>/<followed_id>', methods=['POST', 'GET', 'DELETE'])
def route_follow(follower_id, followed_id):
    if request.method == 'POST':
        return create_follow(request, follower_id, followed_id)
    elif request.method == 'DELETE':
        return delete_follow(request, follower_id, followed_id)
    else:
        return read_follow(follower_id, followed_id)


@follows_blueprint.route('/follows', methods=['GET'])
def route_follows():
    return list_follows(request)


def read_follow(follower_id, followed_id):
    follow = get_follow_or_404(follower_id, followed_id)
    return success_with_follow(follow)


def list_follows(request_):
    return jsonify(JSONAPICollectionSerializer([
        FollowSerializer(
            follow,
            inbound_request=request_
        )
        for follow in follows_dbm.all()
    ]).as_json_api_document())


def delete_follow(request_, follower_id, followed_id):
    follow = get_follow_or_404(follower_id, followed_id)
    result = success_with_follow(follow)
    follows_dbm.delete(follower_id=follower_id, followed_id=followed_id)
    return result


def create_follow(request_, follower_id, followed_id):
    extant_follow = follows_dbm.find(follower_id=follower_id, followed_id=followed_id)
    if extant_follow is not None:
        abort(409,
              '{0} with follower id {1} and followed id {2} already exists'.format('follow', follower_id, followed_id))

    if people_dbm.find_by_id(follower_id) is None:
        abort(404)
    if people_dbm.find_by_id(followed_id) is None:
        abort(404)

    follows_dbm.create_with_ids(follower_id, followed_id)
    follow = follows_dbm.find(follower_id=follower_id, followed_id=followed_id)
    return success_with_follow(follow), 201


def get_follow_or_404(follower_id, followed_id):
    follow = follows_dbm.find(follower_id, followed_id)
    if follow is None:
        abort(404)
    return follow


def success_with_follow(follow):
    return jsonify(FollowSerializer(follow).as_json_api_document())
