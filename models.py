from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# =======================
# User Model
# =======================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='Customer')  # e.g., 'Admin', 'Customer', 'Vendor'


    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# =======================
# Product Model
# =======================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.PickleType)  # list
    material = db.Column(db.String(100))
    rating = db.Column(db.Float)
    reviews = db.Column(db.Integer)
    additional_images = db.Column(db.PickleType)  # list
    specifications = db.Column(db.JSON)  # dict
    shipping_info = db.Column(db.JSON)  # dict
    return_policy = db.Column(db.String(255))
    warranty = db.Column(db.String(255))
    available = db.Column(db.Boolean, default=True)
    tags = db.Column(db.PickleType)  # list
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f"Product('{self.name}', ₹{self.price})"

# =======================
# Cart Item Model
# =======================
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f"CartItem(user={self.user_id}, product={self.product_id}, qty={self.quantity})"

# =======================
# Order Model
# =======================
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    stripe_payment_id = db.Column(db.String(100))

    items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f"Order(id={self.id}, user={self.user_id}, total=₹{self.total})"

# =======================
# Order Item Model
# =======================
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"OrderItem(order={self.order_id}, product={self.product_id}, qty={self.quantity})"
