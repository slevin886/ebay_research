from ebay_research import db, bcrypt, login_manager
from datetime import datetime
from flask_login import UserMixin
import os
from time import time
import jwt


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=True)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    permissions = db.Column(db.Integer)  # 1 = paid, 0 = unpaid
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True, default=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    searches = db.relationship('Search', lazy='dynamic')
    results = db.relationship('Results', lazy='dynamic')

    def __init__(self, email, password, country, state, permissions, registered_on=datetime.utcnow(), confirmed=False,
                 admin=False, confirmed_on=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.country = country
        self.state = state
        self.permissions = permissions
        self.registered_on = registered_on
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.admin = admin

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.add(self)

    def validate_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def get_confirmation_token(self, expires_in=1800):
        return jwt.encode({'confirmation_token': self.id, 'exp': time() + expires_in},
                          os.environ.get('SECRET_KEY'), algorithm='HS256').decode('utf-8')

    @staticmethod
    def confirm_token(token):
        try:
            user_id = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])['confirmation_token']
        except:
            return
        return User.query.get(user_id)

    def confirm_account(self):
        self.confirmed = True
        self.confirmed_on = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return f"<User(email={self.email}, country={self.country}, state={self.state}, confirmed={self.confirmed})>"

    def __str__(self):
        return f"User: email={self.email}, country={self.country}, state={self.state}, confirmed={self.confirmed}\n"

class Search(db.Model):
    __tablename__ = 'search'
    id = db.Column(db.Integer, primary_key=True)
    time_searched = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    keywords = db.Column(db.String(80), nullable=False)
    excluded_words = db.Column(db.String(80), nullable=True)
    sort_order = db.Column(db.String(50), nullable=False)
    listing_type = db.Column(db.String(50), nullable=True)
    min_price = db.Column(db.Float, default=0.0, nullable=False)
    max_price = db.Column(db.Float, nullable=True)
    item_condition = db.Column(db.String(50), nullable=True)
    is_successful = db.Column(db.Boolean, nullable=False, default=True)
    downloaded = db.Column(db.Boolean, default=False, nullable=False)
    pages_wanted = db.Column(db.Integer, default=1, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    search_results = db.relationship('Results', uselist=False)

    def __repr__(self):
        return f"<Search(full_query={self.keywords}, time_searched={self.time_searched}, user_id={self.user_id})>"


class Results(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    avg_price = db.Column(db.Float)
    median_price = db.Column(db.Float)
    min_price = db.Column(db.Float, nullable=True)
    max_price = db.Column(db.Float, nullable=True)
    returned_count = db.Column(db.Integer)
    top_rated_percent = db.Column(db.Float)  # top rated seller %
    top_rated_listing = db.Column(db.Float, nullable=True)  # top rated listing %
    top_seller = db.Column(db.String(200))
    top_seller_count = db.Column(db.Integer)
    largest_cat_name = db.Column(db.String(200), nullable=True)
    largest_cat_count = db.Column(db.Integer, nullable=True)
    largest_sub_name = db.Column(db.String(200), nullable=True)
    largest_sub_count = db.Column(db.Integer, nullable=True)
    total_entries = db.Column(db.Integer)
    total_watch_count = db.Column(db.Integer)
    avg_shipping_price = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))

    def __repr__(self):
        return f"<Results(id={self.id}, largest_category={self.largest_cat_name}, returned_count={self.returned_count})"
