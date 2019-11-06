from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from ebay_research.config import ProductionConfig, DevelopmentConfig, TestingConfig
from redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()
mail = Mail()


def create_app(settings='production'):
    app = Flask(__name__)
    # Talisman(app, content_security_policy=None)
    if settings == 'development':
        app.config.from_object(DevelopmentConfig)
    elif settings == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(ProductionConfig)
        sentry_sdk.init(
            dsn="https://d93a22d6384f49809d90100f65157218@sentry.io/1808965",
            integrations=[FlaskIntegration(), SqlalchemyIntegration()]
        )
    register_shellcontext(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    from ebay_research.routes import main
    from ebay_research.auth import auth
    from ebay_research.errors import error_page
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(error_page)
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
