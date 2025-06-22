# main.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, User, Product  # ✅ Include Product model
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set SQLite DB path
    db_path = os.getenv('DATABASE_URI', 'sqlite:///shopzone.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create db directory if needed
    if db_path.startswith("sqlite:///"):
        db_file = db_path.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from auth.routes import auth_bp
    from products.routes import products_bp
    from cart.routes import cart_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')

    # Home route with featured products
    @app.route('/')
    def home():
        featured_products = Product.query.filter_by(is_featured=True).all()
        return render_template('index.html', featured_products=featured_products)

    return app

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # ✅ Modern SQLAlchemy method

# Run server
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
