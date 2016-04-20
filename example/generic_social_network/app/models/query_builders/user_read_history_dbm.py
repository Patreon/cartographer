from generic_social_network.app.models.tables.user_read_history import UserReadHistory


class UserReadHistoryDBM:
    def __init__(self, db):
        self.db = db

    def reset(self):
        self.db.drop_user_read_history()

    def all(self):
        return UserReadHistory.query.all()

    def find(self, user_id=None, post_id=None):
        query = UserReadHistory.query
        if user_id is not None:
            query = query.filter(UserReadHistory.user_id == user_id)
        if post_id is not None:
            query = query.filter(UserReadHistory.post_id == post_id)
        results = query.all()

        if user_id is not None and post_id is not None:
            if len(results) == 0:
                return None
            if len(results) == 1:
                return results[0]
            raise Exception

        return results

    def find_by_user_id(self, user_id):
        return self.find(user_id=user_id)

    def find_by_post_id(self, post_id):
        return self.find(post_id=post_id)

    def create(self, post):
        self.db.session.add(post)
        self.db.session.commit()

    def create_from_json(self, json):
        self.create(UserReadHistory.from_json(json))

    def update(self, user_read_history):
        self.delete(user_read_history=user_read_history)
        self.create(user_read_history)

    def update_from_json(self, json):
        self.update(UserReadHistory.from_json(json))

    def delete(self, user_read_history):
        self.delete_by_ids(user_id=user_read_history.user_id,
                           post_id=user_read_history.post_id)

    def delete_by_ids(self, user_id=None, post_id=None):
        query = UserReadHistory.query
        if user_id is not None:
            query = query.filter(UserReadHistory.user_id == user_id)
        if post_id is not None:
            query = query.filter(UserReadHistory.post_id == post_id)
        query.delete()
        self.db.session.commit()

    def create_with_ids(self, user_id, post_id):
        return self.create_from_json({'user_id': user_id,
                                      'post_id': post_id})
