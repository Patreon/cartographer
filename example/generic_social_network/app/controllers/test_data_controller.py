#!flask/bin/python
import json

from flask import jsonify, Blueprint
from generic_social_network.app import db
from generic_social_network.app.services import db_wrapper

test_data_blueprint = Blueprint('test_data_blueprint', __name__)


@test_data_blueprint.route('/initialize_test_data', methods=['GET'])
def initialize_test_data():
    from generic_social_network.app import my_app
    test_data = TestData(my_app)
    test_data.make_a_reasonable_newsfeed()
    return jsonify({'success': True})


@test_data_blueprint.route('/clear_test_data', methods=['GET'])
def clear_test_data():
    db_wrapper.reset(db)
    return jsonify({'success': True})


class TestData(object):
    def __init__(self, app):
        self.app = app.test_client()

    def make_a_person(self, id_=1):
        person_json = {
            'data': {
                'type': 'person',
                'id': id_,
                'attributes': {
                    'name': 'Jane Doe'
                }
            }
        }
        return self.app.post('/people/{0}'.format(id_),
                             data=json.dumps(person_json),
                             content_type='application/json')

    def make_a_post(self, post_id=1, author_id=1):
        post_json = {
            'data': {
                'type': 'post',
                'id': post_id,
                'attributes': {
                    'title': 'An Inspirational Blog Post',
                    'body': 'Be yourself, but also you can change for the better.'
                },
                'relationships': {
                    'author': {
                        'data': {
                            'type': 'person',
                            'id': author_id
                        }
                    }
                }
            }
        }
        return self.app.post('/posts/{0}'.format(post_id),
                             data=json.dumps(post_json),
                             content_type='application/json')

    def make_a_follow(self, follower_id, followed_id):
        return self.app.post('/follows/{0}/{1}'.format(follower_id, followed_id))

    def make_a_reasonable_newsfeed(self, person_id=1, author_ids=[20, 30]):
        self.make_a_person(person_id)
        for author_id in author_ids:
            self.make_a_person(author_id)
            for i in range(3):
                post_id = pow(author_id, i + 1)
                self.make_a_post(post_id=post_id, author_id=author_id)
            self.make_a_follow(person_id, author_id)
