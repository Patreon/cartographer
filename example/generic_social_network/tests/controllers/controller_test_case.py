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
        assert response.status_code == expected_code
        if expected_json is not None:
            assert json.loads(response.data) == expected_json

    @classmethod
    def suite(cls):
        return unittest.TestLoader().loadTestsFromTestCase(cls)
