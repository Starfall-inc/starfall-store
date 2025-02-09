from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))

    products = db.relationship('Product', backref='category', lazy=True)
