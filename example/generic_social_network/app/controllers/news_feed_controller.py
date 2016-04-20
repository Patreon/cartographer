#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, Blueprint, request, session
from generic_social_network.app import db
from generic_social_network.app.models.query_builders.user_read_history_dbm import UserReadHistoryDBM
from generic_social_network.app.models.query_builders.posts_dbm import PostsDBM
from generic_social_network.app.models.query_builders.users_dbm import UsersDBM

from generic_social_network.app.models.query_builders.follows_dbm import FollowsDBM
from generic_social_network.app.resources.post_resource import PostSerializer

news_feed_blueprint = Blueprint('news_feed_blueprint', __name__)
follows_dbm = FollowsDBM(db)
users_dbm = UsersDBM(db)
posts_dbm = PostsDBM(db)
user_read_history_dbm = UserReadHistoryDBM(db)


@news_feed_blueprint.route('/news_feed/<int:user_id>', methods=['GET'])
def read_news_feed(user_id):
    user = get_user_or_404(user_id)
    posts = posts_dbm.find_posts_for_follower(user_id)
    return jsonify(JSONAPICollectionSerializer([
        PostSerializer(
            post,
            inbound_request=request,
            inbound_session=session
        )
        for post in posts
    ]).as_json_api_document())


def get_user_or_404(post_id):
    user = users_dbm.find_by_id(post_id)
    if user is None:
        abort(404)
    return user

