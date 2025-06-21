# main.py
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

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set SQLite path (adjusted for Replit or Linux paths)
    db_path = os.getenv('DATABASE_URI', 'sqlite:///shopzone.db')  # Default fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Create database directory if needed
    if db_path.startswith("sqlite:///"):
        db_file = db_path.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_file)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    db.init_app(app)
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

# Run server
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
