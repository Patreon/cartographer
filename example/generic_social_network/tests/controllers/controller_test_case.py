import json
import unittest


class ControllerTestCase(unittest.TestCase):
    def setUp(self):
        from generic_social_network.app import my_app, db

        my_app.config['TESTING'] = True
        self.app = my_app.test_client()
        self.db = db
        from generic_social_network.app.services import db_wrapper
        db_wrapper.reset(self.db)

    def tearDown(self):
        from generic_social_network.app.services import db_wrapper
        db_wrapper.reset(self.db)

    def check_response(self, response, expected_code, expected_json):
        # print('comparing', response.status_code, 'to', expected_code,
        #       "\nand comparing", json.loads(response.data), 'to', expected_json)
        if response.status_code != expected_code:
            print(response.status_code, expected_code)
        assert response.status_code == expected_code
        if expected_json is not None:
            response_json = json.loads(response.data.decode('utf-8'))
            if response_json != expected_json:
                print(response_json, 'not equal to', expected_json)
            assert response_json == expected_json

    def check_jsonapi_response(self, response, expected_code, expected_json):
        # print('comparing', response.status_code, 'to', expected_code,
        #       "\nand comparing", json.loads(response.data.decode('utf-8')), 'to', expected_json)
        if response.status_code != expected_code:
            print(response.status_code, expected_code)
        assert response.status_code == expected_code
        if expected_json is not None:
            response_json = json.loads(response.data.decode('utf-8'))
            if response_json.get('data') != expected_json.get('data'):
                print(response_json.get('data'), 'not equal to', expected_json.get('data'))
            assert response_json.get('data') == expected_json.get('data')
            response_included = response_json.get('included', [])
            expected_included = expected_json.get('included', [])
            for i in response_included:
                if i not in expected_included:
                    print(i, 'not in', expected_included)
                assert i in expected_included
            for i in expected_included:
                assert i in response_included

    @classmethod
    def suite(cls):
        return unittest.TestLoader().loadTestsFromTestCase(cls)
