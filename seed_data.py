import json
from app import create_app
from models import db, Product

app = create_app()

with app.app_context():
    with open('data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = []
    for p in data:
        product = Product(
            id=p["id"],
            name=p["name"],
            price=p["price"],
            discount_price=p.get("discount_price"),
            stock=p.get("stock", 0),
            image_url=p.get("image_url"),
            description=p.get("description"),
            category=p.get("category"),
            brand=p.get("brand"),
            color=p.get("color"),
            size=p.get("size"),
            material=p.get("material"),
            rating=p.get("rating"),
            reviews=p.get("reviews"),
            additional_images=p.get("additional_images"),
            specifications=p.get("specifications"),
            shipping_info=p.get("shipping_info"),
            return_policy=p.get("return_policy"),
            warranty=p.get("warranty"),
            available=p.get("available", True),
            tags=p.get("tags"),
        )
        products.append(product)

    db.session.add_all(products)
    db.session.commit()

    print("✅ All products from data/products.json added to the database.")
