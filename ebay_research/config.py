import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB limit of file uploads
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    EBAY_API = os.environ.get('EBAY_API')


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    FLASK_ENV = 'development'


class TestingConfig(Config):
    TESTING = True
    FLASK_ENV = 'testing'
    # not yet relevant but should be
    BCRYPT_LOG_ROUNDS = 4
    # disable csrf tokens for WTF forms (might not be relevant)
    WTF_CSRF_ENABLED = False
    # SQLALCHEMY_DATABASE_URI = "postgresql://localhost/crosstab_test"
