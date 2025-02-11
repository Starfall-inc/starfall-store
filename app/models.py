from app.extensions import db
from datetime import datetime

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
    cart_id = db.Column(db.String(25))  # Removed incorrect ForeignKey
    auth_provider = db.Column(db.Enum('google', 'manual', name='auth_provider_enum'), default='manual')
    profile_pic_url = db.Column(db.String(255), default='none')
    address_lat = db.Column(db.String(255))
    address_lon = db.Column(db.String(255))

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('ProductReview', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref='user', lazy=True)
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))

    products = db.relationship('Product', backref='category_rel', lazy=True)

    def __repr__(self):
        return f'<ProductCategory {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column('category', db.Integer, db.ForeignKey('product_category.id'))
    price = db.Column(db.Numeric(10,2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Numeric(10,2), nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text)

    # Relationships
    reviews = db.relationship('ProductReview', backref='product', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref='product', lazy=True)
    order_details = db.relationship('OrderDetail', backref='product', lazy=True)
    featured = db.relationship('FeaturedProduct', backref='product', lazy=True, uselist=False)

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),  # Convert Decimal to float
            "image_url": self.image_url,
            "description": self.description,
            "stock_quantity": self.stock_quantity,
            "category_id": self.category_id,
            "is_available": self.is_available
        }

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    method_name = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)

    orders = db.relationship('Order', backref='payment_method', lazy=True)

    def __repr__(self):
        return f'<PaymentMethod {self.method_name}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    payment_method_id = db.Column('payment_method', db.Integer, db.ForeignKey('payment_methods.id'))
    order_place_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.TIMESTAMP)
    actual_delivery_date = db.Column(db.TIMESTAMP)
    is_completed = db.Column(db.Boolean, default=False)
    total = db.Column(db.Float)
    shipping_address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    delivery_charges = db.Column(db.Numeric(10,2), default=0.00)
    coordinate_lat = db.Column(db.Float)
    coordinate_lon = db.Column(db.Float)

    order_details = db.relationship('OrderDetail', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id}>'

    @property
    def total_amount(self):
        return sum(detail.subtotal for detail in self.order_details) + float(self.delivery_charges or 0)

class OrderDetail(db.Model):
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float)

    def __repr__(self):
        return f'<OrderDetail {self.id}>'

    def calculate_subtotal(self):
        self.subtotal = self.quantity * self.price
        return self.subtotal

class FeaturedProduct(db.Model):
    __tablename__ = 'featured_product'
    id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    from_date = db.Column('from', db.TIMESTAMP, nullable=False)
    to_date = db.Column('to', db.TIMESTAMP, nullable=False)

    def __repr__(self):
        return f'<FeaturedProduct {self.id}>'

    @property
    def is_active(self):
        now = datetime.utcnow()
        return self.from_date <= now <= self.to_date

class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.String(25), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_cart_item'),
    )

    def __repr__(self):
        return f'<Cart {self.id}>'

class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_review'),
        db.CheckConstraint('rating BETWEEN 1 AND 5', name='valid_rating_range'),
    )

    def __repr__(self):
        return f'<ProductReview {self.id}>'

    def to_dict(self):
        """Convert the ProductReview instance to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# Note: The Review model seems redundant with ProductReview, consider consolidating
class Review(db.Model):
    __tablename__ = 'review'
    revId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column('product', db.Integer, db.ForeignKey('products.id'))
    star = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.revId}>'

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f'<Session {self.session_id}>'

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at