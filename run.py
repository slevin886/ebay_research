from ebay_research import create_app
import os

settings = os.environ.get('APP_SETTINGS')
if settings == "development":
    app = create_app(settings='development')
else:
    app = create_app()

if __name__ == '__main__':
    app.run()
