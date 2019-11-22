from flask import Blueprint
recurring = Blueprint('recurring', __name__, template_folder='templates', static_folder='static', static_url_path='/trends/')
from . import routes
