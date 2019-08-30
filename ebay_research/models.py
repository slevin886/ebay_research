from ebay_research import db, bcrypt, login_manager
from datetime import datetime
from flask_login import UserMixin

# TODO: add email confirmation of user perhaps


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    country = db.Column(db.String(20))
    state = db.Column(db.String(20))
    time_created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    permissions = db.Column(db.Integer)  # 1 = paid, 0 = unpaid
    searches = db.relationship('Search')

    def __init__(self, email, password, country, state, permissions):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.country = country
        self.state = state
        self.permissions = permissions

    def validate_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

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
