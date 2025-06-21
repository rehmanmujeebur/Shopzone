from app import create_app
from models import db, Product

app = create_app()

with app.app_context():
    count = Product.query.count()
    print(f"✅ Total products in database: {count}")
