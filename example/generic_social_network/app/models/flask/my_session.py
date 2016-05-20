from cartographer.requests.session_interface import JSONAPISessionInterface
from flask.sessions import SessionMixin, SecureCookieSessionInterface


class MySession(dict, SessionMixin, JSONAPISessionInterface):
    def __init__(self, person_id=None, **kwargs):
        super().__init__(**kwargs)
        self['person_id'] = person_id

    @property
    def person_id(self):
        return self['person_id']


class MySessionInterface(SecureCookieSessionInterface):
    session_class = MySession
    salt = 'my-cookie-session'
