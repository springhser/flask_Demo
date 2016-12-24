import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask_uploads import IMAGES

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'yoursmtp'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = "youremail"
    MAIL_PASSWORD = "yourpass"
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <xxx@example.com>'
    FLASKY_ADMIN = "admin@justin.com"
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_SLOW_DB_QUERY_TIME=0.5
    FLASKY_ADMIN_PERMISSION = 6
    FLASKY_USER_PERMISSION = 1
    UPLOADED_PIC_DEST = './app/static/pic'
    UPLOADED_PIC_ALLOW = IMAGES


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    'I use mysql'
    SQLALCHEMY_TRACK_MODIFICATIONS = True




config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}
