import datetime

from generic_social_network.app import db
from sqlalchemy import Column, Integer, DateTime


class UserReadHistory(db.Model):
    __tablename__ = 'user_read_history'

    user_id = Column(Integer, primary_key=True, index=True, nullable=False)
    post_id = Column(Integer, primary_key=True, index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
