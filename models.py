from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Enum
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin
from datetime import date, timedelta, datetime
import enum

# Metadata with naming convention for foreign keys
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# User model
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')
    phone_number = db.Column(db.String(15), nullable=True)
    verification_code = db.Column(db.String(6), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    # Relationships
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='user', cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-orders.user', '-reviews.user', '-password')

    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value:
            raise ValueError("Failed simple email validation")
        return value

    @validates('phone_number')
    def validate_phone_number(self, key, value):
        if value and (len(value) < 10 or len(value) > 15):
            raise ValueError("Phone number must be between 10 and 15 characters")
        return value

    def __repr__(self):
        return f'<User id={self.id} name={self.name} email={self.email} role={self.role}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'phone_number': self.phone_number,
            'verification_code': self.verification_code,
            'is_verified': self.is_verified
        }

# Product model
class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(150), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    functionality = db.Column(db.Text, nullable=True)
    
    # Relationships
    order_products = db.relationship('OrderProduct', back_populates='product', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='product', cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-order_products.product', '-reviews.product')

    def __repr__(self):
        return f'<Product id={self.id} name={self.name} category={self.category} price={self.price}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'functionality': self.functionality,
        }

# Order model
class OrderStatus(enum.Enum):
    PENDING = "Pending"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"

class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False, default=date.today)
    total_price = db.Column(db.Float, nullable=False)
    order_status = db.Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    delivery_date = db.Column(db.Date, nullable=True)

    # Relationships
    order_products = db.relationship('OrderProduct', back_populates='order')
    user = db.relationship('User', back_populates='orders')

    # Serialization rules
    serialize_rules = ('-order_products.order', '-user.orders', '-user.password')

    def __repr__(self):
        return f'<Order id={self.id} user_id={self.user_id} order_date={self.order_date} total_price={self.total_price} status={self.order_status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'customer_name':self.user.name,
            'order_date': self.order_date,
            'total_price': self.total_price,
            'order_status': self.order_status.value,
            'delivery_date': self.delivery_date,
            'order_products': [op.to_dict() for op in self.order_products]
        }

    @staticmethod
    def calculate_delivery_date(order_date): 
        # Example: Set delivery date to 7 days after order_date
        delivery_date = order_date + timedelta(days=7)
        return delivery_date

# Association table for Order-Product Many-to-Many relationship
class OrderProduct(db.Model, SerializerMixin):
    __tablename__ = 'order_products'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    # Relationships
    product = relationship('Product', back_populates='order_products')
    order = relationship('Order', back_populates='order_products')

    # Serialization rules
    serialize_rules = ('-product.order_products', '-order.order_products')

    def __repr__(self):
        return f'<OrderProduct order_id={self.order_id} product_id={self.product_id} quantity={self.quantity}>'

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'product': self.product.to_dict(),
        }

# Review model
class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    review_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

    # Serialization rules
    serialize_rules = ('-user.reviews', '-product.reviews')

    def __repr__(self):
        return f'<Review id={self.id} user_id={self.user_id} product_id={self.product_id} rating={self.rating}>'

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "comments": self.comments,
            "rating": self.rating,
            "review_date": self.review_date.strftime('%Y-%m-%d')
        }

