#!/usr/bin/env python

from ebay_research import create_app
import os

settings = os.environ.get('APP_SETTINGS')

if settings == "development":
    app = create_app(settings='development')
elif settings == 'testing':
    app = create_app(settings='testing')
else:
    app = create_app(settings='production')

if __name__ == '__main__':
    app.run()
