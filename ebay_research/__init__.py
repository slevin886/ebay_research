from flask import Flask
from ebay_research.config import ProductionConfig, DevelopmentConfig, TestingConfig


def create_app(settings='production'):
    app = Flask(__name__)
    if settings == 'development':
        app.config.from_object(DevelopmentConfig)
    elif settings == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(ProductionConfig)
    from ebay_research.routes import main
    app.register_blueprint(main)
    return app
