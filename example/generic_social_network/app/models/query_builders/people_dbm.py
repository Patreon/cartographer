from generic_social_network.app.models.tables.person import Person
from .follows_dbm import FollowsDBM
from .posts_dbm import PostsDBM


class PeopleDBM:
    def __init__(self, db):
        self.db = db

    def reset(self):
        self.db.drop_people()

    def all(self):
        return Person.query.all()

    def find_by_id(self, id_):
        matching = Person.query.filter_by(person_id=id_).all()
        if len(matching) == 0:
            return None
        if len(matching) == 1:
            return matching[0]
        raise Exception

    def create_from_json(self, json):
        Person.insert(json)
        self.db.session.commit()

    def update_from_json(self, json):
        Person.insert_on_duplicate_key_update(json)
        self.db.session.commit()

    def delete(self, person=None, person_id=None):
        if person_id is None:
            person_id = person.person_id
        Person.query.filter_by(person_id=person_id).delete()
        self.db.session.commit()
        FollowsDBM(self.db).delete_matching_follower_id(person_id)
        FollowsDBM(self.db).delete_matching_followed_id(person_id)
        PostsDBM(self.db).delete_matching_author_id(person_id)
