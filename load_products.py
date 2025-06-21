import json
from app import create_app
from models import db, Product

app = create_app()

try:
    with open("data/products.json", "r") as file:
        products = json.load(file)
except FileNotFoundError:
    print("❌ Error: products.json file not found")
    exit(1)
except json.JSONDecodeError:
    print("❌ Error: Invalid JSON format in products.json")
    exit(1)

required_fields = {"name", "description", "price", "image_url", "stock"}
total = len(products)
success = 0
skipped = 0

with app.app_context():
    new_products = []
    
    for i, p in enumerate(products, 1):
        print(f"Processing {i}/{total}...", end="\r")
        
        # Field validation
        if not required_fields.issubset(p.keys()):
            missing = required_fields - set(p.keys())
            print(f"\n⛔ Missing fields {missing} in product: {p.get('name', 'Unnamed')}")
            skipped += 1
            continue
            
        # Check for duplicates
        if Product.query.filter_by(name=p["name"]).first():
            print(f"\n⚠️ Product '{p['name']}' already exists. Skipping.")
            skipped += 1
            continue
            
        # Create product
        new_products.append(Product(
            name=p["name"],
            description=p["description"],
            price=float(p["price"]),  # Ensure numeric type
            image_url=p["image_url"],
            stock=int(p["stock"])     # Ensure integer type
        ))
        success += 1
    
    # Bulk insert
    db.session.bulk_save_objects(new_products)
    db.session.commit()
    
    print(f"\n✅ Done. Success: {success}, Skipped: {skipped}")