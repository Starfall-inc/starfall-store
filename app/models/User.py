from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(255))
    joined_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    default_location = db.Column(db.String(255))
    role = db.Column(db.String(20), default='customer')
    status = db.Column(db.String(20), default='active')
    cart_id = db.Column(db.String(25), db.ForeignKey('carts.id'))
    auth_provider = db.Column(db.Enum('google', 'manual'), default='manual')
    profile_pic_url = db.Column(db.String(255), default='none')
    address_lat = db.Column(db.String(255))
    address_lon = db.Column(db.String(255))

    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('ProductReview', backref='user', lazy=True)
