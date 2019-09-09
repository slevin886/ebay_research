from ebay_research import db, bcrypt, login_manager
from datetime import datetime
from flask_login import UserMixin
import os
from time import time
import jwt

# TODO: add email confirmation of user perhaps


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
    registered_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    permissions = db.Column(db.Integer)  # 1 = paid, 0 = unpaid
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    searches = db.relationship('Search')

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

    def __repr__(self):
        return f"<User(email={self.email}, country={self.country}, state={self.state}, permissions={self.permissions})>"


class Search(db.Model):
    __tablename__ = 'search'
    id = db.Column(db.Integer, primary_key=True)
    time_searched = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    full_query = db.Column(db.String(125))
    is_successful = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<Search(full_query={self.full_query}, time_searched={self.time_searched}, user_id={self.user_id})>"
