import os


def _db_file_location():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "../../../sqlite.db")


def connect(app):
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.ext.declarative import declarative_base
    from generic_social_network.app.models.tables.my_model import MyModel

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + _db_file_location()
    db = SQLAlchemy(app=app, model_class=declarative_base(cls=MyModel, name='MyModel'))
    # db.engine.echo = True
    return db


def build_if_needed(db):
    if len(db.engine.table_names()) == 0:
        db.create_all()


def drop_users(db):
    from generic_social_network.app.models.tables.follow import Follow
    from generic_social_network.app.models.tables.post import Post
    from generic_social_network.app.models.tables.user import User
    User.drop(db.engine, checkfirst=True)
    Follow.drop(db.engine, checkfirst=True)
    Post.drop(db.engine, checkfirst=True)


def drop_posts(db):
    from generic_social_network.app.models.tables.post import Post
    Post.drop(db.engine, checkfirst=True)


def drop_follows(db):
    from generic_social_network.app.models.tables.follow import Follow
    Follow.drop(db.engine, checkfirst=True)


def drop_user_read_history(db):
    from generic_social_network.app.models.tables.user_read_history import UserReadHistory
    UserReadHistory.drop(db.engine, checkfirst=True)


def reset(db):
    db.drop_all()
    db.create_all()
