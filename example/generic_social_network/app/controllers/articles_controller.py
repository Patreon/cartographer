#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, request, Blueprint
from generic_social_network.app import db
from generic_social_network.app.models.query_builders.articles_dbm import ArticlesDBM
from generic_social_network.app.models.query_builders.people_dbm import PeopleDBM
from generic_social_network.app.resources.article_resource import ArticleSerializer, ArticleParser

articles_blueprint = Blueprint('articles_blueprint', __name__)
articles_dbm = ArticlesDBM(db)
people_dbm = PeopleDBM(db)


@articles_blueprint.route('/articles/<int:article_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def route_article(article_id):
    if request.method == 'POST':
        return create_article(request, article_id)
    elif request.method == 'PUT':
        return update_article(request, article_id)
    elif request.method == 'DELETE':
        return delete_article(request, article_id)
    else:
        return read_article(article_id)


@articles_blueprint.route('/articles', methods=['POST', 'GET'])
def route_articles():
    if request.method == 'POST':
        return create_article(request, None)
    else:
        return list_articles(request)


def read_article(article_id):
    article = get_article_or_404(article_id)
    return success_with_article(article)


def list_articles(request_):
    return jsonify(JSONAPICollectionSerializer([
        ArticleSerializer(
            article,
            inbound_request=request_
        )
        for article in articles_dbm.all()
    ]).as_json_api_document())


def delete_article(request_, article_id):
    article = get_article_or_404(article_id)
    articles_dbm.delete(article_id=article_id)
    return success_with_article(article)


def update_article(request_, article_id):
    def article_found_behavior(article):
        if article is None:
            abort(404)

    json = validate_inbound_article(request_, article_id, article_found_behavior)

    articles_dbm.update_from_json(json)
    return read_article(json['article_id'])


def create_article(request_, article_id):
    def article_found_behavior(article):
        if article is not None:
            abort(409, '{0} with id {1} already exists'.format('article', article_id))

    json = validate_inbound_article(request_, article_id, article_found_behavior)

    articles_dbm.create_from_json(json)
    article = articles_dbm.find_by_id(json['article_id'])
    return success_with_article(article), 201


def get_article_or_404(article_id):
    article = articles_dbm.find_by_id(article_id)
    if article is None:
        abort(404)
    return article


def success_with_article(article, request_=None):
    if request_ is None:
        request_ = request
    return jsonify(ArticleSerializer(article, inbound_request=request_).as_json_api_document())


def validate_inbound_article(request_, article_id, article_found_behavior):
    try:
        table_data = ArticleParser(inbound_request=request_).validated_table_data()
    except Exception as e:
        abort(400, ', '.join(e.args))
    table_data = standardize_article_ids_or_abort(table_data, article_id)
    article_id = table_data['article_id']
    article = articles_dbm.find_by_id(article_id)
    article_found_behavior(article)
    return table_data


def standardize_article_ids_or_abort(json, article_id):
    if not json:
        abort(400, 'No article data was provided in your request')
    if 'article_id' in json:
        if article_id != json['article_id']:
            abort(400, 'Provided article object had a id that did not match the provided route')
    elif article_id:
        json['article_id'] = article_id
    return json
