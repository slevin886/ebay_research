from ebay_research import db
from datetime import datetime

# TODO: add confirmation of user perhaps


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    country = db.Column(db.String(20))
    state = db.Column(db.String(20))
    time_created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    permissions = db.Column(db.Integer)  # 1 = paid, 0 = unpaid
    searches = db.relationship('Search')


class Search(db.Model):
    __tablename__ = 'search'
    id = db.Column(db.Integer, primary_key=True)
    time_searched = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    full_query = db.Column(db.String(125))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
