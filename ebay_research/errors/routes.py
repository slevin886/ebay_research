from ebay_research.errors import error_page
from flask import render_template


@error_page.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@error_page.app_errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
