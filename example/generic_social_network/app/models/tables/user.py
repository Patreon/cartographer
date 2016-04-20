from generic_social_network.app import db
from sqlalchemy import Column, Integer, String


class User(db.Model):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(512), default='')
