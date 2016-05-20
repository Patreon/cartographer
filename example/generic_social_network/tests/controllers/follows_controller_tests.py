import json
from .controller_test_case import ControllerTestCase


class FollowsControllerTestCase(ControllerTestCase):
    def make_a_person(self, id_='mypersonid'):
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

    def make_a_follow(self, follower_id, followed_id):
        return self.app.post('/follows/{0}/{1}'.format(follower_id, followed_id))

    def make_people_and_follow(self, follower_id, followed_id):
        self.make_a_person(follower_id)
        self.make_a_person(followed_id)
        self.make_a_follow(follower_id, followed_id)

    def expected_json(self, follower_id, followed_id):
        return {
            'data': {
                'id': '{follower_id}-{followed_id}'.format(
                    follower_id=follower_id,
                    followed_id=followed_id
                ),
                'attributes': {},
                'type': 'follow',
                'relationships': {
                    'follower': {
                        'data': {
                            'id': str(follower_id),
                            'type': 'person'
                        }
                    },
                    'followed': {
                        'data': {
                            'id': str(followed_id),
                            'type': 'person'
                        }
                    }
                }
            },
            'included': [
                {
                    'id': str(follower_id),
                    'attributes': {'name': 'Jane Doe'},
                    'type': 'person'
                },
                {
                    'id': str(followed_id),
                    'attributes': {'name': 'Jane Doe'},
                    'type': 'person'
                }
            ]
        }

    def test_get_follow(self):
        follower_id, followed_id = 1, 2
        self.make_people_and_follow(follower_id, followed_id)

        expected_response = self.expected_json(follower_id, followed_id)
        get_response = self.app.get('/follows/{0}/{1}'.format(follower_id, followed_id))
        self.check_jsonapi_response(get_response, 200, expected_response)

    def test_get_nonexistant_follow(self):
        # 404's when the people don't exist
        response = self.app.get('/follows/nonce/nonce2')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

        # also 404's when the people exist, but there's no follow
        follower_id, followed_id = 1, 2
        self.make_a_person(follower_id)
        self.make_a_person(followed_id)

        response = self.app.get('/follows/follower/nonce')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_create_valid_follow(self):
        follower_id, followed_id = 1, 2
        self.make_a_person(follower_id)
        self.make_a_person(followed_id)

        expected_response = self.expected_json(follower_id, followed_id)
        create_response = self.app.post('/follows/{0}/{1}'.format(follower_id, followed_id))
        self.check_jsonapi_response(create_response, 201, expected_response)

    def test_create_invalid_follow(self):
        person_id = 'mypersonid'
        self.make_a_person(person_id)
        # follower doesn't exist
        create_response = self.app.post('/follows/nonce/{0}'.format(person_id))
        self.check_response(create_response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})
        # followed doesn't exist
        create_response = self.app.post('/follows/{0}/nonce'.format(person_id))
        self.check_response(create_response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_create_duplicate_follow(self):
        follower_id, followed_id = 1, 2
        self.make_people_and_follow(follower_id, followed_id)

        create_response = self.app.post('/follows/{0}/{1}'.format(follower_id, followed_id))
        self.check_response(create_response, 409,
                            {'error': 'follow with follower id 1 and followed id 2 already exists'})

    def test_delete_follow(self):
        follower_id, followed_id = 1, 2
        self.make_people_and_follow(follower_id, followed_id)

        # delete made follow
        expected_response = self.expected_json(follower_id, followed_id)
        delete_response = self.app.delete('/follows/{0}/{1}'.format(follower_id, followed_id))
        self.check_jsonapi_response(delete_response, 200, expected_response)

        # check that get now fails
        response = self.app.get('/follows/{0}/{1}'.format(follower_id, followed_id))
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_delete_nonexistant_follow(self):
        follower_id, followed_id = 1, 2
        self.make_a_person(follower_id)
        self.make_a_person(followed_id)

        delete_response = self.app.delete('/follows/{0}/{1}'.format(follower_id, followed_id))
        self.check_response(delete_response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

suite = FollowsControllerTestCase.suite()
