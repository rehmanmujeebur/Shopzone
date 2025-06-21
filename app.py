# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, User
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app():  # ✅ app is not global, must be created from this factory
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    app.secret_key = os.getenv("SECRET_KEY")
    print("ENV SECRET_KEY:", app.secret_key)

    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
    app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')

    db_path = os.getenv('DATABASE_URI')
    if db_path and db_path.startswith("sqlite"):
        db_file = db_path.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    Migrate(app, db)
    login_manager.init_app(app)

    from auth.routes import auth_bp
    from products.routes import products_bp
    from cart.routes import cart_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')

    @app.route('/')
    def home():
        return render_template('index.html')

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Run server only when called directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
