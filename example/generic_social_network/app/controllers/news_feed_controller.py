#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, Blueprint, request, session
from generic_social_network.app import db
from generic_social_network.app.models.query_builders.articles_dbm import ArticlesDBM
from generic_social_network.app.models.query_builders.people_dbm import PeopleDBM

from generic_social_network.app.models.query_builders.follows_dbm import FollowsDBM
from generic_social_network.app.resources.article_resource import ArticleSerializer

news_feed_blueprint = Blueprint('news_feed_blueprint', __name__)
follows_dbm = FollowsDBM(db)
people_dbm = PeopleDBM(db)
articles_dbm = ArticlesDBM(db)


@news_feed_blueprint.route('/news_feed/<int:person_id>', methods=['GET'])
def read_news_feed(person_id):
    person = get_person_or_404(person_id)
    articles = articles_dbm.find_articles_for_follower(person_id)
    return jsonify(JSONAPICollectionSerializer([
        ArticleSerializer(
            article,
            inbound_request=request,
            inbound_session=session
        )
        for article in articles
    ]).as_json_api_document())


def get_person_or_404(article_id):
    person = people_dbm.find_by_id(article_id)
    if person is None:
        abort(404)
    return person
