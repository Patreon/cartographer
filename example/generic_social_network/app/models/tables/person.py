from generic_social_network.app import db
from sqlalchemy import Column, Integer, String


class Person(db.Model):
    __tablename__ = 'people'

    person_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(512), default='')
