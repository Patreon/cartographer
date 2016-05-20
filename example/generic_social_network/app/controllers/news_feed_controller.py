#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, Blueprint, request, session
from generic_social_network.app import db
from generic_social_network.app.models.query_builders.posts_dbm import PostsDBM
from generic_social_network.app.models.query_builders.people_dbm import PeopleDBM

from generic_social_network.app.models.query_builders.follows_dbm import FollowsDBM
from generic_social_network.app.resources.post_resource import PostSerializer

news_feed_blueprint = Blueprint('news_feed_blueprint', __name__)
follows_dbm = FollowsDBM(db)
people_dbm = PeopleDBM(db)
posts_dbm = PostsDBM(db)


@news_feed_blueprint.route('/news_feed/<int:person_id>', methods=['GET'])
def read_news_feed(person_id):
    person = get_person_or_404(person_id)
    posts = posts_dbm.find_posts_for_follower(person_id)
    return jsonify(JSONAPICollectionSerializer([
        PostSerializer(
            post,
            inbound_request=request,
            inbound_session=session
        )
        for post in posts
    ]).as_json_api_document())


def get_person_or_404(post_id):
    person = people_dbm.find_by_id(post_id)
    if person is None:
        abort(404)
    return person
