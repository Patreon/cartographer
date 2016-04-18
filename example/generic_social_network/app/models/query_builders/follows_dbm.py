from generic_social_network.app.models.tables.follow import Follow


class FollowsDBM:
    def __init__(self, db):
        self.db = db

    def reset(self):
        self.db.drop_follows()

    def all(self):
        return Follow.query.all()

    def find(self, follower_id=None, followed_id=None):
        query = Follow.query
        if follower_id is not None:
            query = query.filter(Follow.follower_id == follower_id)
        if followed_id is not None:
            query = query.filter(Follow.followed_id == followed_id)
        results = query.all()

        if follower_id is not None and followed_id is not None:
            if len(results) == 0:
                return None
            if len(results) == 1:
                return results[0]
            raise Exception

        return results

    def find_by_follower_id(self, follower_id):
        return self.find(follower_id=follower_id)

    def find_by_followed_id(self, followed_id):
        return self.find(followed_id=followed_id)

    def create_with_ids(self, follower_id, followed_id):
        Follow.insert({
            'follower_id': follower_id,
            'followed_id': followed_id
        })
        self.db.session.commit()

    def delete(self, follower_id=None, followed_id=None):
        if not followed_id or not followed_id:
            raise Exception
        Follow.query.filter_by(follower_id=follower_id, followed_id=followed_id).delete()
        self.db.session.commit()

    def delete_matching_follower_id(self, follower_id):
        Follow.query.filter_by(follower_id=follower_id).delete()
        self.db.session.commit()

    def delete_matching_followed_id(self, followed_id):
        Follow.query.filter_by(followed_id=followed_id).delete()
        self.db.session.commit()
