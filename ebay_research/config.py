import os

DB_URL = os.environ.get('DATABASE_URL')

if 'RDS_HOSTNAME' in os.environ:
    DATABASE = {
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
    }
    DB_URL = 'postgres://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s' % DATABASE


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB limit of file uploads
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL')
    EBAY_API = os.environ.get('EBAY_API')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ADMIN_EMAIL = 'slevin886@gmail.com'


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
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/ebay_research_test"
