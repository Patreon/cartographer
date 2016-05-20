from generic_social_network.app.models.tables.follow import Follow
from generic_social_network.app.models.tables.post import Post


class PostsDBM:
    def __init__(self, db):
        self.db = db

    def reset(self):
        self.db.drop_posts()

    def all(self):
        return Post.query.all()

    def find_by_id(self, id_):
        matching = Post.query.filter_by(post_id=id_).all()
        if len(matching) == 0:
            return None
        if len(matching) == 1:
            return matching[0]
        raise Exception

    def find_by_title(self, title):
        return Post.query.filter_by(title=title).all()

    def find_by_author_id(self, author_id):
        return Post.query.filter_by(author_id=author_id).all()

    def find_posts_for_follower(self, person_id):
        return Post.query \
            .join(Follow, Post.author_id == Follow.followed_id) \
            .filter(Follow.follower_id == person_id) \
            .all()

    def create_from_json(self, json):
        Post.insert(json)
        self.db.session.commit()

    def update_from_json(self, json):
        Post.insert_on_duplicate_key_update(json)
        self.db.session.commit()

    def delete(self, post=None, post_id=None):
        if post_id is None:
            post_id = post.post_id
        Post.query.filter_by(post_id=post_id).delete()
        self.db.session.commit()

    def delete_matching_author_id(self, author_id):
        Post.query.filter_by(author_id=author_id).delete()
        self.db.session.commit()
