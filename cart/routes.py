import os
import json
import stripe
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, current_app, session, flash
from flask_login import login_required

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe_public_key = os.getenv('STRIPE_PUBLIC_KEY')

# ✅ Load products from products.json
def load_products():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        current_app.logger.error("products.json not found")
        return []
    except json.JSONDecodeError:
        current_app.logger.error("Invalid JSON in products.json")
        return []

# ✅ Get product by ID
def get_product_by_id(product_id):
    products = load_products()
    return next((product for product in products if product["id"] == product_id), None)

# 🛒 View Cart
@cart_bp.route('/')
@login_required
def view_cart():
    cart_items = session.get('cart_items', [])

    subtotal = sum(item['product']['price'] * item['quantity'] for item in cart_items)
    shipping = 5.00 if subtotal < 50 and cart_items else 0.00
    total = subtotal + shipping

    return render_template('view_cart.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           shipping=shipping,
                           total=total)

# ➕ Add to Cart
@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    cart_items = session.get('cart_items', [])

    for item in cart_items:
        if item['product']['id'] == product['id']:
            item['quantity'] += 1
            break
    else:
        cart_items.append({'product': product, 'quantity': 1})

    session['cart_items'] = cart_items
    return redirect(url_for('cart.view_cart'))

# ✅ Checkout Page (🔒 Login Required)
@cart_bp.route('/checkout')
@login_required
def checkout():
    cart_items = session.get('cart_items', [])

    if not cart_items:
        return redirect(url_for('cart.view_cart'))

    subtotal = sum(item['product']['price'] * item['quantity'] for item in cart_items)
    shipping = 5.00 if subtotal < 50 and cart_items else 0.00
    total = subtotal + shipping

    return render_template('checkout.html',
                           cart_items=cart_items,
                           total=total,
                           stripe_public_key=stripe_public_key)

# 💳 Create Payment (🔒 Login Required)
@cart_bp.route('/create-payment', methods=['POST'])
@login_required
def create_payment():
    try:
        cart_items = session.get('cart_items', [])
        orders = session.get('orders', [])

        data = request.json

        # Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(float(data['total']) * 100),
            currency='usd',
            payment_method=data['payment_method_id'],
            confirmation_method='manual',
            confirm=True,
            metadata={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'address': data['address'],
                'city': data['city'],
                'postal_code': data['postal_code'],
                'country': data['country']
            }
        )

        # Save order
        order_id = len(orders) + 1
        order = {
            'id': order_id,
            'items': cart_items.copy(),
            'total': float(data['total']),
            'customer': {
                'name': f"{data['first_name']} {data['last_name']}",
                'email': data['email'],
                'address': {
                    'line1': data['address'],
                    'city': data['city'],
                    'postal_code': data['postal_code'],
                    'country': data['country']
                }
            },
            'payment_status': 'pending'
        }
        orders.append(order)
        session['orders'] = orders

        # Clear cart after successful order creation
        session['cart_items'] = []

        return jsonify({
            'success': True,
            'order_id': order_id,
            'client_secret': intent.client_secret
        })

    except stripe.error.CardError as e:
        return jsonify({'error': e.user_message}), 400
    except Exception as e:
        current_app.logger.error(f"Payment error: {str(e)}")
        return jsonify({'error': 'Payment failed. Please try again.'}), 500

# ✅ Order Confirmation Page (🔒 Login Required)
@cart_bp.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    orders = session.get('orders', [])
    order = next((o for o in orders if o['id'] == order_id), None)

    if not order:
        return redirect(url_for('cart.view_cart'))

    return render_template('order_confirmation.html', order=order)

@cart_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart_items = session.get('cart_items', [])
    new_cart = []

    for item in cart_items:
        if item['product']['id'] != product_id:
            new_cart.append(item)

    session['cart_items'] = new_cart
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))

