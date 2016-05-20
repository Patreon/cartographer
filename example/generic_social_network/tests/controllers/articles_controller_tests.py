import json
from copy import deepcopy
from .controller_test_case import ControllerTestCase


class ArticlesControllerTestCase(ControllerTestCase):
    def default_article_json(self, article_id=1, author_id=1):
        return {
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

    def default_author_json(self, author_id=1):
        return {
            'data': {
                'type': 'person',
                'id': str(author_id),
                'attributes': {
                    'name': 'Jane Doe'
                }
            }
        }

    def make_an_author(self, author_id=1):
        return self.app.post('/people/{0}'.format(author_id),
                             data=json.dumps(self.default_author_json(author_id)),
                             content_type='application/json')

    def make_a_article(self, article_id=1, author_id=1):
        return self.app.post('/articles/{0}'.format(article_id),
                             data=json.dumps(self.default_article_json(article_id=article_id, author_id=author_id)),
                             content_type='application/json')

    def make_an_author_and_article(self, article_id=1, author_id=1):
        self.make_an_author(author_id=author_id)
        self.make_a_article(article_id=article_id, author_id=author_id)

    def test_get_article(self):
        author_id = 1
        article_id = 1
        self.make_an_author_and_article(article_id=article_id, author_id=author_id)

        # get made article
        get_response = self.app.get('/articles/{0}'.format(article_id))
        expected_response = self.default_article_json(article_id=article_id, author_id=author_id)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(get_response, 200, expected_response)

    def test_get_nonexistant_article(self):
        response = self.app.get('/articles/999')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_create_valid_article(self):
        author_id = 1
        self.make_an_author(author_id)

        article_id = 1
        article_data = self.default_article_json(article_id)
        create_response = self.app.post('/articles/{0}'.format(article_id), data=json.dumps(article_data),
                                        content_type='application/json')
        expected_response = deepcopy(article_data)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(create_response, 201, expected_response)

    def test_create_invalid_article(self):
        # missing author
        article_id = 1
        article_data = self.default_article_json(article_id=article_id)
        del article_data['data']['relationships']['author']['data']['id']
        create_response = self.app.post('/articles/{0}'.format(article_id), data=json.dumps(article_data),
                                        content_type='application/json')
        self.check_response(create_response, 400,
                            {'error': 'Provided article object was missing the author id field'})

        author_id = 1
        self.make_an_author(author_id)
        article_data = self.default_article_json(article_id=article_id, author_id=author_id)
        del article_data['data']['attributes']['body']
        create_response = self.app.post('/articles/{0}'.format(article_id), data=json.dumps(article_data),
                                        content_type='application/json')
        self.check_response(create_response, 400,
                            {'error': 'Provided article object was missing the body field'})

    def test_create_best_effort_article_id(self):
        article_id = 1
        article_data_no_id = self.default_article_json(article_id=article_id)
        del article_data_no_id['data']['id']
        self.make_an_author()
        create_response = self.app.post('/articles/{0}'.format(article_id), data=json.dumps(article_data_no_id),
                                        content_type='application/json')

        expected_response = deepcopy(article_data_no_id)
        expected_response['data'].update({'id': str(article_id)})
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(create_response, 201, expected_response)

    def test_create_duplicate_article_id(self):
        author_id = 1
        article_id = 1
        self.make_an_author_and_article(author_id=author_id, article_id=article_id)

        article_data = self.default_article_json(article_id)
        create_response = self.app.post('/articles/{0}'.format(article_id), data=json.dumps(article_data),
                                        content_type='application/json')
        self.check_response(create_response, 409,
                            {'error': 'article with id {0} already exists'.format(article_id)})

    def test_delete_article(self):
        author_id = 1
        article_id = 1
        self.make_an_author_and_article(author_id=author_id, article_id=article_id)
        article_data = self.default_article_json(article_id)

        # delete made person
        delete_response = self.app.delete('/articles/{0}'.format(article_id))
        expected_response = deepcopy(article_data)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(delete_response, 200, expected_response)

        # check that get now fails
        response = self.app.get('/articles/{0}'.format(article_id))
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_delete_nonexistant_article(self):
        response = self.app.delete('/articles/999')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_update_article(self):
        author_id = 1
        article_id = 1
        self.make_an_author_and_article(author_id=author_id, article_id=article_id)

        # modify the article
        article_data = self.default_article_json(article_id)
        article_data['title'] = 'Now for Something Different'
        update_response = self.app.put('/articles/{0}'.format(article_id), data=json.dumps(article_data),
                                       content_type='application/json')
        expected_response = deepcopy(article_data)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(update_response, 200, expected_response)

        # check that get now has the new data too
        get_response = self.app.get('/articles/{0}'.format(article_id))
        self.check_jsonapi_response(get_response, 200, expected_response)

    def test_update_invalid_person(self):
        author_id = 1
        article_id = 1
        self.make_an_author_and_article(author_id=author_id, article_id=article_id)

        # modify the person in an invalid way (missing author id)
        article_data = self.default_article_json(article_id)
        del article_data['data']['relationships']['author']['data']['id']
        update_response = self.app.put('/articles/{0}'.format(article_id), data=json.dumps(article_data),
                                       content_type='application/json')
        self.check_response(update_response, 400,
                            {'error': 'Provided article object was missing the author id field'})

        # check that get still has the old data
        get_response = self.app.get('/articles/{0}'.format(article_id))
        expected_response = self.default_article_json(article_id)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(get_response, 200, expected_response)

    def test_update_nonexistant_person(self):
        # without article body data
        response = self.app.put('/articles/999')
        self.check_response(response, 400, None)

        # with article body data
        article_id = 987
        article_data = self.default_article_json(article_id)
        response = self.app.put('/articles/{0}'.format(article_id), data=json.dumps(article_data),
                                content_type='application/json')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})


suite = ArticlesControllerTestCase.suite()
