from cartographer.requests.jsonapi_flask_request_mixin import JSONAPIFlaskRequestMixin
from nose.tools import *


def test_parse_parameters_to_dictionary():
    params = {
        'fields[user]': 'fields-user',
        'fields[post][one]': 'fields-post-one',
        'includes': 'users,posts'
    }
    expected_result = {
        'user': 'fields-user',
        'post': {
            'one': 'fields-post-one'
        }
    }
    assert_equals(JSONAPIFlaskRequestMixin._parse_parameters_to_dictionary(params).get('fields'),
                  expected_result)
