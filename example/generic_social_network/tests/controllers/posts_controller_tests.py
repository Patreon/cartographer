import json
from copy import deepcopy
from .controller_test_case import ControllerTestCase


class PostsControllerTestCase(ControllerTestCase):
    def default_post_json(self, post_id=1, author_id=1):
        return {
            'data': {
                'id': str(post_id),
                'type': 'post',
                'attributes': {
                    'title': 'An Inspirational Blog Post',
                    'body': 'Be yourself, but also you can change for the better.'
                },
                'relationships': {
                    'author': {
                        'data': {
                            'id': str(author_id),
                            'type': 'user'
                        }
                    }
                }
            }
        }

    def default_author_json(self, author_id=1):
        return {
            'data': {
                'type': 'user',
                'id': str(author_id),
                'attributes': {
                    'name': 'Jane Doe'
                }
            }
        }

    def make_an_author(self, author_id=1):
        return self.app.post('/users',
                             data=json.dumps(self.default_author_json(author_id)),
                             content_type='application/json')

    def make_a_post(self, post_id=1, author_id=1):
        return self.app.post('/posts',
                             data=json.dumps(self.default_post_json(post_id=post_id, author_id=author_id)),
                             content_type='application/json')

    def make_an_author_and_post(self, post_id=1, author_id=1):
        self.make_an_author(author_id=author_id)
        self.make_a_post(post_id=post_id, author_id=author_id)

    def test_get_post(self):
        author_id = 1
        post_id = 1
        self.make_an_author_and_post(post_id=post_id, author_id=author_id)

        # get made post
        get_response = self.app.get('/posts/{0}'.format(post_id))
        expected_response = self.default_post_json(post_id=post_id, author_id=author_id)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(get_response, 200, expected_response)

    def test_get_nonexistant_post(self):
        response = self.app.get('/posts/999')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_create_valid_post(self):
        author_id = 1
        self.make_an_author(author_id)

        post_id = 1
        post_data = self.default_post_json(post_id)
        create_response = self.app.post('/posts', data=json.dumps(post_data),
                                        content_type='application/json')
        expected_response = deepcopy(post_data)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(create_response, 201, expected_response)

    def test_create_invalid_post(self):
        # missing author
        post_id = 1
        post_data = self.default_post_json(post_id=post_id)
        del post_data['data']['relationships']['author']['data']['id']
        create_response = self.app.post('/posts', data=json.dumps(post_data),
                                        content_type='application/json')
        self.check_response(create_response, 400,
                            {'error': 'Provided post object was missing the author id field'})

        author_id = 1
        self.make_an_author(author_id)
        post_data = self.default_post_json(post_id=post_id, author_id=author_id)
        del post_data['data']['attributes']['body']
        create_response = self.app.post('/posts', data=json.dumps(post_data),
                                        content_type='application/json')
        self.check_response(create_response, 400,
                            {'error': 'Provided post object was missing the body field'})

    def test_create_best_effort_post_id(self):
        post_id = 1
        post_data_no_id = self.default_post_json(post_id=post_id)
        del post_data_no_id['data']['id']
        self.make_an_author()
        create_response = self.app.post('/posts', data=json.dumps(post_data_no_id),
                                        content_type='application/json')

        expected_response = deepcopy(post_data_no_id)
        expected_response['data'].update({'id': str(post_id)})
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(create_response, 201, expected_response)

    def test_create_duplicate_post_id(self):
        author_id = 1
        post_id = 1
        self.make_an_author_and_post(author_id=author_id, post_id=post_id)

        post_data = self.default_post_json(post_id)
        create_response = self.app.post('/posts', data=json.dumps(post_data),
                                        content_type='application/json')
        self.check_response(create_response, 409,
                            {'error': 'post with id {0} already exists'.format(post_id)})

    def test_delete_post(self):
        author_id = 1
        post_id = 1
        self.make_an_author_and_post(author_id=author_id, post_id=post_id)
        post_data = self.default_post_json(post_id)

        # delete made user
        delete_response = self.app.delete('/posts/{0}'.format(post_id))
        expected_response = None
        self.check_jsonapi_response(delete_response, 204, expected_response)

        # check that get now fails
        response = self.app.get('/posts/{0}'.format(post_id))
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_delete_nonexistant_post(self):
        response = self.app.delete('/posts/999')
        self.check_response(response, 409,
                            {
                                'error': 'A conflict happened while processing the request.  The resource might have been modified while the request was being processed.'})

    def test_update_post(self):
        author_id = 1
        post_id = 1
        self.make_an_author_and_post(author_id=author_id, post_id=post_id)

        # modify the post
        post_data = self.default_post_json(post_id)
        post_data['title'] = 'Now for Something Different'
        update_response = self.app.put('/posts/{0}'.format(post_id), data=json.dumps(post_data),
                                       content_type='application/json')
        expected_response = deepcopy(post_data)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(update_response, 200, expected_response)

        # check that get now has the new data too
        get_response = self.app.get('/posts/{0}'.format(post_id))
        self.check_jsonapi_response(get_response, 200, expected_response)

    def test_update_invalid_user(self):
        author_id = 1
        post_id = 1
        self.make_an_author_and_post(author_id=author_id, post_id=post_id)

        # modify the user in an invalid way (missing author id)
        post_data = self.default_post_json(post_id)
        del post_data['data']['relationships']['author']['data']['id']
        update_response = self.app.put('/posts/{0}'.format(post_id), data=json.dumps(post_data),
                                       content_type='application/json')
        self.check_response(update_response, 400,
                            {'error': 'Provided post object was missing the author id field'})

        # check that get still has the old data
        get_response = self.app.get('/posts/{0}'.format(post_id))
        expected_response = self.default_post_json(post_id)
        expected_response.update({'included': [self.default_author_json()['data']]})
        self.check_jsonapi_response(get_response, 200, expected_response)

    def test_update_nonexistant_user(self):
        # without post body data
        response = self.app.put('/posts/999')
        self.check_response(response, 400, None)

        # with post body data
        post_id = 987
        post_data = self.default_post_json(post_id)
        response = self.app.put('/posts/{0}'.format(post_id), data=json.dumps(post_data),
                                content_type='application/json')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})


suite = PostsControllerTestCase.suite()
