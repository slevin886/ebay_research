from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from ebay_research.config import ProductionConfig, DevelopmentConfig, TestingConfig
from redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler

# TODO: Enable Redis!

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
bcrypt = Bcrypt()
mail = Mail()


def create_app(settings='production'):
    app = Flask(__name__)
    if settings == 'development':
        app.config.from_object(DevelopmentConfig)
    elif settings == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(ProductionConfig)
    register_shellcontext(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    from ebay_research.routes import main
    from ebay_research.auth import auth
    from ebay_research.errors import error_page
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(error_page)
    # LOGGER CONFIGURATION
    # if not app.debug and not app.testing:
    #     auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    #     secure = None
    #     if app.config['MAIL_USE_TLS']:
    #         secure = app.config['MAIL_USE_TLS']
    #     mail_handler = SMTPHandler(
    #         mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
    #         fromaddr=app.config['MAIL_DEFAULT_SENDER'],
    #         toaddrs=app.config['MAIL_DEFAULT_SENDER'], subject='Genius Bidding Failure',
    #         credentials=auth, secure=secure)
    #     mail_handler.setLevel(logging.ERROR)
    #     app.logger.addHandler(mail_handler)
    return app


def register_shellcontext(app):
    """Register shell context objects."""
    from ebay_research import models

    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': models.User,
            'Search': models.Search,
        }

    app.shell_context_processor(shell_context)
