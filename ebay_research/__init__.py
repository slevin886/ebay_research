from flask import Flask
from ebay_research.config import ProductionConfig, DevelopmentConfig, TestingConfig
from redis import Redis


def create_app(settings='production'):
    app = Flask(__name__)
    if settings == 'development':
        app.config.from_object(DevelopmentConfig)
    elif settings == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(ProductionConfig)
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    from ebay_research.routes import main
    app.register_blueprint(main)
    return app
