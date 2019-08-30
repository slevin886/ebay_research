from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from ebay_research.config import ProductionConfig, DevelopmentConfig, TestingConfig
from redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login_manager = LoginManager()
login_manager.login_view = 'main.login'
bcrypt = Bcrypt()


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
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    from ebay_research.routes import main
    app.register_blueprint(main)
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
