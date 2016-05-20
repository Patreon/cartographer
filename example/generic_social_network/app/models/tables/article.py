from copy import copy

from generic_social_network.app import db
from sqlalchemy import Column, Integer, ForeignKey, String, Text


class Article(db.Model):
    __tablename__ = 'articles'

    article_id = Column(Integer, primary_key=True, nullable=False)
    author_id = Column(Integer, ForeignKey("people.person_id"), index=True, nullable=False)
    title = Column(String(512), default='')
    body = Column(Text)
