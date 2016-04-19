from flask import Flask, jsonify, make_response
from generic_social_network.app.models.flask.my_request import MyRequest
from generic_social_network.app.models.flask.my_session import MySessionInterface

from .services import db_wrapper

my_app = Flask(__name__)
my_app.session_interface = MySessionInterface()
my_app.request_class = MyRequest

db = db_wrapper.connect(my_app)

# set up routing & controllers
from .controllers import users_controller, posts_controller, follows_controller, news_feed_controller, \
    test_data_controller

my_app.register_blueprint(users_controller.users_blueprint)
my_app.register_blueprint(posts_controller.posts_blueprint)
my_app.register_blueprint(follows_controller.follows_blueprint)
my_app.register_blueprint(news_feed_controller.news_feed_blueprint)
my_app.register_blueprint(test_data_controller.test_data_blueprint)


# set up error handling
def json_error_description(error_):
    return make_response(jsonify({'error': error_.description}), error_.code)


for error in list(range(400, 420)) + list(range(500, 506)):
    my_app.error_handler_spec[None][error] = json_error_description
