import json
from copy import deepcopy
from .controller_test_case import ControllerTestCase


class PeopleControllerTestCase(ControllerTestCase):
    def default_person_json(self, id_=1):
        return {
            'data': {
                'type': 'person',
                'id': str(id_),
                'attributes': {
                    'name': 'Jane Doe'
                }
            }
        }

    def make_a_person(self, id_=1):
        return self.app.post('/people/{0}'.format(id_),
                             data=json.dumps(self.default_person_json(id_)),
                             content_type='application/json')

    def test_get_person(self):
        id_ = 1
        post_data = self.default_person_json(id_)
        self.make_a_person(id_)

        # get made person
        get_response = self.app.get('/people/{0}'.format(id_))
        self.check_jsonapi_response(get_response, 200, post_data)

    def test_get_nonexistant_person(self):
        response = self.app.get('/people/999')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_create_valid_person(self):
        id_ = 1
        post_data = self.default_person_json(id_)
        create_response = self.app.post('/people/{0}'.format(id_), data=json.dumps(post_data),
                                        content_type='application/json')
        self.check_jsonapi_response(create_response, 201, post_data)

    def test_create_invalid_person(self):
        # missing name
        post_data = {
            'data': {
                'type': 'person',
                'id': '1'
            }
        }
        create_response = self.app.post('/people/1', data=json.dumps(post_data), content_type='application/json')
        self.check_response(create_response, 400,
                            {'error': 'Provided person object was missing the name field'})

    def test_create_best_effort_personid(self):
        post_data_no_id = {
            'data': {
                'type': 'person',
                'attributes': {
                    'name': 'Jane Doe'
                }
            }
        }
        create_response = self.app.post('/people/1', data=json.dumps(post_data_no_id),
                                        content_type='application/json')
        expected_response = deepcopy(post_data_no_id)
        expected_response['data'].update({'id': '1'})
        self.check_jsonapi_response(create_response, 201, expected_response)


    def test_create_duplicate_personid(self):
        id_ = 1
        self.make_a_person(id_)

        post_data = self.default_person_json(id_)
        create_response = self.app.post('/people/{0}'.format(id_), data=json.dumps(post_data),
                                        content_type='application/json')
        self.check_response(create_response, 409,
                            {'error': 'person with id 1 already exists'})

    def test_delete_person(self):
        id_ = 1
        post_data = self.default_person_json(id_)
        self.make_a_person(id_)

        # delete made person
        delete_response = self.app.delete('/people/{0}'.format(id_))
        self.check_jsonapi_response(delete_response, 200, post_data)

        # check that get now fails
        response = self.app.get('/people/{0}'.format(id_))
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_delete_nonexistant_person(self):
        response = self.app.delete('/people/999')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})

    def test_update_person(self):
        id_ = 1
        post_data = self.default_person_json(id_)
        self.make_a_person(id_)

        # modify the person
        post_data['name'] = 'John Doe'
        update_response = self.app.put('/people/{0}'.format(id_), data=json.dumps(post_data),
                                       content_type='application/json')
        self.check_jsonapi_response(update_response, 200, post_data)

        # check that get now has the new data too
        get_response = self.app.get('/people/{0}'.format(id_))
        self.check_jsonapi_response(update_response, 200, post_data)

    def test_update_invalid_person(self):
        id_ = 1
        post_data = self.default_person_json(id_)
        self.make_a_person(id_)

        # modify the person in an invalid way (missing name)
        del post_data['data']['attributes']['name']
        update_response = self.app.put('/people/{0}'.format(id_), data=json.dumps(post_data),
                                       content_type='application/json')
        self.check_response(update_response, 400,
                            {'error': 'Provided person object was missing the name field'})

        # check that get still has the old data
        post_data = self.default_person_json(id_)
        get_response = self.app.get('/people/{0}'.format(id_))
        self.check_jsonapi_response(get_response, 200, post_data)

    def test_update_nonexistant_person(self):
        # without post body data
        response = self.app.put('/people/999')
        self.check_response(response, 400, None)

        # with post body data
        id_ = 987
        post_data = self.default_person_json(id_)
        response = self.app.put('/people/{0}'.format(id_), data=json.dumps(post_data), content_type='application/json')
        self.check_response(response, 404,
                            {
                                'error': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'})


suite = PeopleControllerTestCase.suite()
