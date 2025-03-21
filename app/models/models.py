from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
import uuid
from sqlalchemy.dialects.postgresql import ARRAY


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
    auth_provider = db.Column(
        db.Enum('google', 'manual', name='auth_provider_enum'),
        server_default='manual'
    )
    profile_pic_url = db.Column(db.String(255), default='none')
    address_lat = db.Column(db.String(255))
    address_lon = db.Column(db.String(255))

    # Relationships
    orders = db.relationship('Order', back_populates='user')
    reviews = db.relationship('ProductReview', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref='user', lazy=True)
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'


class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    category_image = db.Column(db.String(255))
    description = db.Column(db.Text)  # Change String(255) → Text

    products = db.relationship('Product', backref='category_rel', lazy=True)

    def __repr__(self):
        return f'<ProductCategory {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category_image": self.category_image,
            "description": self.description
        }


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    tags = db.Column(ARRAY(db.String(50)), default=[])

    # ✅ JSONB field for dynamic attributes
    attributes = db.Column(JSONB, nullable=True, default={})

    # Relationships
    reviews = db.relationship('ProductReview', backref='product', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref='product', lazy=True)
    order_details = db.relationship('OrderDetail', backref='product', lazy=True)
    featured = db.relationship('FeaturedProduct', backref='product', lazy=True, uselist=False)
    # One-to-Many Relationship with ProductImage
    images = db.relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 2)  # Rounds to 2 decimal places

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),  # Convert Decimal to float
            "images": [image.to_dict() for image in self.images],  # Convert ProductImage
            "description": self.description,
            "stock_quantity": self.stock_quantity,
            "category_id": self.category_id,
            "is_available": self.is_available,
            "attributes": self.attributes,  # Include attributes in API responses
            "reviews": [review.to_dict() for review in self.reviews],  # ✅ Include user info
            "avg_rating": self.average_rating,
        }


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    # Define the relationship
    product = db.relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage {self.image_url}>"

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url
        }


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    method_name = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)

    # orders = db.relationship('Order', backref='payment_method', lazy=True)

    def __repr__(self):
        return f'<PaymentMethod {self.method_name}>'


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    payment_method = db.Column(db.String(50), nullable=True)  # Changed from ForeignKey to String
    order_place_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.TIMESTAMP)
    actual_delivery_date = db.Column(db.TIMESTAMP)
    is_completed = db.Column(db.Boolean, default=False)
    total = db.Column(db.Numeric(10, 2))
    shipping_address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    delivery_charges = db.Column(db.Numeric(10, 2), default=0.00)
    coordinate_lat = db.Column(db.Float)
    coordinate_lon = db.Column(db.Float)

    user = db.relationship('User', back_populates='orders')

    order_details = db.relationship('OrderDetail', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id}>'

    @property
    def total_amount(self):
        return sum(detail.subtotal for detail in self.order_details) + float(self.delivery_charges or 0)


class OrderDetail(db.Model):
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Float)

    def __repr__(self):
        return f'<OrderDetail {self.id}>'

    def calculate_subtotal(self):
        self.subtotal = self.quantity * self.price
        return self.subtotal


class FeaturedProduct(db.Model):
    __tablename__ = 'featured_product'
    id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique row ID
    cart_id = db.Column(db.String(20), unique=False)  # Now it's NOT a primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_cart_item'),  # Avoid duplicate items
    )

    def __repr__(self):
        return f'<Cart {self.cart_id}>'


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
        """Convert the ProductReview instance to a dictionary with user details."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user": {
                "profile_pic_url": self.user.profile_pic_url,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name
            } if self.user else None
        }


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


class Banner(db.Model):
    __tablename__ = 'banners'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=True)  # Image path or URL
    title = db.Column(db.String(255), nullable=True)  # Optional banner title
    description = db.Column(db.Text, nullable=True)  # Optional description
    link = db.Column(db.String(255), nullable=True)  # Clickable link (optional)
    active = db.Column(db.Boolean, default=True)  # Whether the banner is active
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "active": self.active,
        }


class PaymentTransaction(db.Model):
    __tablename__ = "payment_transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)  # Juspay Transaction ID
    payment_status = db.Column(db.String(50), default="PENDING")  # PENDING, CHARGED, FAILED
    payment_method = db.Column(db.String(50))  # UPI, CARD, NET_BANKING, etc.
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with Order
    order = db.relationship("Order", backref="payment_transactions", lazy=True)

    def __repr__(self):
        return f"<PaymentTransaction {self.transaction_id} - {self.payment_status}>"
