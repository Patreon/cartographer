from cartographer.requests.jsonapi_flask_request_mixin import JSONAPIFlaskRequestMixin
from flask import Request


class MyRequest(Request, JSONAPIFlaskRequestMixin):
    pass
