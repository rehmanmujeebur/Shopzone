import json
import os
from flask import Blueprint, render_template, abort, request
from types import SimpleNamespace

products_bp = Blueprint('products', __name__, url_prefix='/products')

def load_products():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_to_namespace(data):
    """Recursively convert dictionaries to SimpleNamespace objects"""
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = convert_to_namespace(value)
        return SimpleNamespace(**data)
    elif isinstance(data, list):
        return [convert_to_namespace(item) for item in data]
    return data

@products_bp.route('/')
def products():
    products_data = load_products()

    # Get query parameters
    category = request.args.get('category', '').strip().lower()
    sort = request.args.get('sort', '').strip()
    search = request.args.get('search', '').strip().lower()

    # Filter by category
    if category:
        products_data = [
            p for p in products_data
            if p.get('category', '').lower() == category
        ]

    # Filter by search in name, brand, description, category, color
    if search:
        products_data = [
            p for p in products_data
            if search in p.get('name', '').lower() or
               search in p.get('brand', '').lower() or
               search in p.get('description', '').lower() or
               search in p.get('category', '').lower() or
               search in p.get('color', '').lower()
        ]

    # Sort by price
    if sort == 'asc':
        products_data = sorted(products_data, key=lambda p: p.get('price', 0))
    elif sort == 'desc':
        products_data = sorted(products_data, key=lambda p: p.get('price', 0), reverse=True)

    # Unique categories from original data
    all_data = load_products()
    categories = sorted(set(p.get('category') for p in all_data if p.get('category')))

    return render_template(
        'products.html',
        products=products_data,
        categories=categories,
        selected_category=category,
        selected_sort=sort,
        search_query=search
    )

@products_bp.route('/<int:product_id>')
def product_detail(product_id):
    products_data = load_products()
    product = next((p for p in products_data if p['id'] == product_id), None)

    if not product:
        abort(404, description="Product not found")

    product_obj = convert_to_namespace(product)

    related = [convert_to_namespace(p) for p in products_data if p['id'] != product_id][:4]

    return render_template('product_details.html', product=product_obj, related_products=related)

# Debug route
@products_bp.route('/debug/<int:product_id>')
def debug_product(product_id):
    products_data = load_products()
    product = next((p for p in products_data if p['id'] == product_id), None)
    return json.dumps(product, indent=2)
