from generic_social_network.app.models.tables.follow import Follow
from generic_social_network.app.models.tables.article import Article


class ArticlesDBM:
    def __init__(self, db):
        self.db = db

    def reset(self):
        self.db.drop_articles()

    def all(self):
        return Article.query.all()

    def find_by_id(self, id_):
        matching = Article.query.filter_by(article_id=id_).all()
        if len(matching) == 0:
            return None
        if len(matching) == 1:
            return matching[0]
        raise Exception

    def find_by_title(self, title):
        return Article.query.filter_by(title=title).all()

    def find_by_author_id(self, author_id):
        return Article.query.filter_by(author_id=author_id).all()

    def find_articles_for_follower(self, person_id):
        return Article.query \
            .join(Follow, Article.author_id == Follow.followed_id) \
            .filter(Follow.follower_id == person_id) \
            .all()

    def create_from_json(self, json):
        Article.insert(json)
        self.db.session.commit()

    def update_from_json(self, json):
        Article.insert_on_duplicate_key_update(json)
        self.db.session.commit()

    def delete(self, article=None, article_id=None):
        if article_id is None:
            article_id = article.article_id
        Article.query.filter_by(article_id=article_id).delete()
        self.db.session.commit()

    def delete_matching_author_id(self, author_id):
        Article.query.filter_by(author_id=author_id).delete()
        self.db.session.commit()
