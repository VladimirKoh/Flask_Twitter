import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mykey123412'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123123vv@127.0.0.1/flask-chat'
    SQLALCHEMY_TRACK_MODIFICATIONS = False