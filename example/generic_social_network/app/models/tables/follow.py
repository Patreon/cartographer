from generic_social_network.app import db
from sqlalchemy import Column, Integer, ForeignKey


class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, nullable=False)
    followed_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, nullable=False)
