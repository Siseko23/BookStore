from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import stripe
import os

db = SQLAlchemy()
DB_NAME = "database.sqlite3"

def create_database(app):
    with app.app_context():
        db.create_all()
    print("Database Created")

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    stripe.api_key = app.config["STRIPE_SECRET_KEY"]  # Initialize Stripe

    from .models import Customer, Cart, Product, Order

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/")

    create_database(app)

    return app
