from flask import Blueprint
error_page = Blueprint('error_page', __name__, template_folder='templates', static_folder='static', static_url_path='/error/')
from . import routes