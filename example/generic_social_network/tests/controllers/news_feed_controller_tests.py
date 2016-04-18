import json
from .controller_test_case import ControllerTestCase


class NewsFeedControllerTestCase(ControllerTestCase):
    def make_a_user(self, id_=1):
        user_json = {
            'name': 'Jane Doe',
            'id': id_
        }
        return self.app.post('/users/{0}'.format(id_),
                             data=json.dumps(user_json),
                             content_type='application/json')

    def make_a_post(self, post_id=1, author_id=1):
        post_json = {
            'id': post_id,
            'author_id': author_id,
            'title': 'An Inspirational Blog Post',
            'body': 'Be yourself, but also you can change for the better.',
        }
        return self.app.post('/posts/{0}'.format(post_id),
                             data=json.dumps(post_json),
                             content_type='application/json')

    def make_a_follow(self, follower_id, followed_id):
        return self.app.post('/follows/{0}/{1}'.format(follower_id, followed_id))

    def make_a_reasonable_newsfeed(self, user_id=1, author_ids=[20, 30]):
        self.make_a_user(user_id)
        for author_id in author_ids:
            self.make_a_user(author_id)
            for i in range(3):
                post_id = author_id + i
                self.make_a_post(post_id=post_id, author_id=author_id)
            self.make_a_follow(user_id, author_id)

    def test_get_news_feed(self):
        id_ = 1
        self.make_a_reasonable_newsfeed(user_id=id_)

        # get made user
        get_response = self.app.get('/news_feed/{0}'.format(id_))
        expected_response = {'posts': [
            {'body': 'Be yourself, but also you can change for the better.', 'author_id': 20,
             'id': 20, 'title': 'An Inspirational Blog Post'},
            {'body': 'Be yourself, but also you can change for the better.', 'author_id': 20,
             'id': 21, 'title': 'An Inspirational Blog Post'},
            {'body': 'Be yourself, but also you can change for the better.', 'author_id': 20,
             'id': 22, 'title': 'An Inspirational Blog Post'},
            {'body': 'Be yourself, but also you can change for the better.', 'author_id': 30,
             'id': 30, 'title': 'An Inspirational Blog Post'},
            {'body': 'Be yourself, but also you can change for the better.', 'author_id': 30,
             'id': 31, 'title': 'An Inspirational Blog Post'},
            {'body': 'Be yourself, but also you can change for the better.', 'author_id': 30,
             'id': 32, 'title': 'An Inspirational Blog Post'}]}
        self.check_response(get_response, 200, expected_response)

suite = NewsFeedControllerTestCase.suite()
