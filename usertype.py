from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    user = User.query.first()
    if user:
        print(f"👤 Username: {user.username}, Email: {user.email}, Type: {user.user_type}")
    else:
        print("No users found.")
