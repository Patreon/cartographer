#!venv/bin/python
import unittest
from generic_social_network.tests.controllers import people_controller_tests, posts_controller_tests, follows_controller_tests, \
    news_feed_controller_tests

runner = unittest.TextTestRunner()
controllers_test_suite = unittest.TestSuite([
    people_controller_tests.suite,
    posts_controller_tests.suite,
    follows_controller_tests.suite,
    news_feed_controller_tests.suite
])
runner.run(controllers_test_suite)
