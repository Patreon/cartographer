from generic_social_network.app.models.tables.user import User
from .follows_dbm import FollowsDBM
from .posts_dbm import PostsDBM


class UsersDBM:
    def __init__(self, db):
        self.db = db

    def reset(self):
        self.db.drop_users()

    def all(self):
        return User.query.all()

    def find_by_id(self, id_):
        matching = User.query.filter_by(user_id=id_).all()
        if len(matching) == 0:
            return None
        if len(matching) == 1:
            return matching[0]
        raise Exception

    def create_from_json(self, json):
        User.insert(json)
        self.db.session.commit()

    def update_from_json(self, json):
        User.insert_on_duplicate_key_update(json)
        self.db.session.commit()

    def delete(self, user=None, user_id=None):
        if user_id is None:
            user_id = user.user_id
        User.query.filter_by(user_id=user_id).delete()
        self.db.session.commit()
        FollowsDBM(self.db).delete_matching_follower_id(user_id)
        FollowsDBM(self.db).delete_matching_followed_id(user_id)
        PostsDBM(self.db).delete_matching_author_id(user_id)
