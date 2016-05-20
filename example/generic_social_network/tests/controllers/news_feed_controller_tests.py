import json
from .controller_test_case import ControllerTestCase


class NewsFeedControllerTestCase(ControllerTestCase):
    def make_a_person(self, id_=1):
        person_json = {
            'data': {
                'type': 'person',
                'id': str(id_),
                'attributes': {
                    'name': 'Jane Doe'
                }
            }
        }
        return self.app.post('/people/{0}'.format(id_),
                             data=json.dumps(person_json),
                             content_type='application/json')

    def make_a_article(self, article_id=1, author_id=1):
        article_json = {
            'data': {
                'id': str(article_id),
                'type': 'article',
                'attributes': {
                    'title': 'An Inspirational Blog Article',
                    'body': 'Be yourself, but also you can change for the better.'
                },
                'relationships': {
                    'author': {
                        'data': {
                            'id': str(author_id),
                            'type': 'person'
                        }
                    }
                }
            }
        }
        return self.app.post('/articles/{0}'.format(article_id),
                             data=json.dumps(article_json),
                             content_type='application/json')

    def make_a_follow(self, follower_id, followed_id):
        return self.app.post('/follows/{0}/{1}'.format(follower_id, followed_id))

    def make_a_reasonable_newsfeed(self, person_id=1, author_ids=[20, 30]):
        self.make_a_person(person_id)
        for author_id in author_ids:
            self.make_a_person(author_id)
            for i in range(3):
                article_id = author_id + i
                self.make_a_article(article_id=article_id, author_id=author_id)
            self.make_a_follow(person_id, author_id)

    def test_get_news_feed(self):
        id_ = 1
        self.make_a_reasonable_newsfeed(person_id=id_)

        # get made person
        get_response = self.app.get('/news_feed/{0}'.format(id_))
        expected_response = {
            'data': [
                {'id': '20', 'type': 'article',
                 'attributes': {'title': 'An Inspirational Blog Article',
                                'body': 'Be yourself, but also you can change for the better.'},
                 'relationships': {'author': {'data': {'id': '20', 'type': 'person'}}}},
                {'id': '21', 'type': 'article',
                 'attributes': {'title': 'An Inspirational Blog Article',
                                'body': 'Be yourself, but also you can change for the better.'},
                 'relationships': {'author': {'data': {'id': '20', 'type': 'person'}}}},
                {'id': '22', 'type': 'article',
                 'attributes': {'title': 'An Inspirational Blog Article',
                                'body': 'Be yourself, but also you can change for the better.'},
                 'relationships': {'author': {'data': {'id': '20', 'type': 'person'}}}},
                {'id': '30', 'type': 'article',
                 'attributes': {'title': 'An Inspirational Blog Article',
                                'body': 'Be yourself, but also you can change for the better.'},
                 'relationships': {'author': {'data': {'id': '30', 'type': 'person'}}}},
                {'id': '31', 'type': 'article',
                 'attributes': {'title': 'An Inspirational Blog Article',
                                'body': 'Be yourself, but also you can change for the better.'},
                 'relationships': {'author': {'data': {'id': '30', 'type': 'person'}}}},
                {'id': '32', 'type': 'article',
                 'attributes': {'title': 'An Inspirational Blog Article',
                                'body': 'Be yourself, but also you can change for the better.'},
                 'relationships': {'author': {'data': {'id': '30', 'type': 'person'}}}}
            ],
            'included': [
                {'attributes': {'name': 'Jane Doe'}, 'type': 'person', 'id': '20'},
                {'attributes': {'name': 'Jane Doe'}, 'type': 'person', 'id': '30'}
            ]
        }
        self.check_jsonapi_response(get_response, 200, expected_response)


suite = NewsFeedControllerTestCase.suite()
