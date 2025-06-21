from app import create_app
from models import db, User  # make sure `User` model is correctly imported

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"Total users: {len(users)}\n")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
