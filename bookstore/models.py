from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)  # ✅ Add department field
    password_hash = db.Column(db.String(150), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    cart_item = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))
    wishlist_items = db.relationship('Wishlist', backref=db.backref('customer', lazy=True))


    @property
    def password(self):
        raise AttributeError('Password is not a Readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f'<Customer {self.id}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=True)  # Add this line
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    department=db.Column(db.String(100),nullable=False)

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))
    wishlist = db.relationship('Wishlist', backref=db.backref('product', lazy=True))



    def __str__(self):
        return f'<Product {self.product_name}>'


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return f'<Cart {self.id}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False, default="Pending")
    payment_id = db.Column(db.String(1000), nullable=False)
    pickup_details = db.Column(db.String(255), nullable=True,
                               default="Pick up details will be provided once processed.")

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def update_status(self, new_status):
        """Update order status and adjust pickup details accordingly."""
        self.status = new_status
        if new_status == "Paid":
            self.pickup_details = "Your order has been confirmed. Please wait for further updates."
        elif new_status == "Delivered":
            self.pickup_details = "Please fetch your item at the library along with your student card."
        elif new_status == "Accepted":
            self.pickup_details = "Your order has been Accepted. Please wait for further updates."
        elif new_status == "Out for delivery":
            self.pickup_details = "Your order is now Out for delivery. Please wait for further updates."
        else:
            self.pickup_details = "Your order has been Canceled. Please wait for further communications"



        db.session.commit()


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # Rating from 1 to 5
    review_text = db.Column(db.Text, nullable=True)  # Optional review text
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # Backreferences
    customer = db.relationship('Customer', backref=db.backref('reviews', lazy=True))
    product = db.relationship('Product', backref=db.backref('reviews', lazy=True))

    def __str__(self):
        return f'<Review {self.id} - Rating: {self.rating}>'


# Wishlist Model
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Wishlist Item {self.id}>'

    # Book Suggestion Model


class BookSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    book_title = db.Column(db.String(200), nullable=False)

    suggestion_date = db.Column(db.DateTime, default=datetime.utcnow)

