import stripe
from flask import current_app

def create_stripe_charge(amount, token, description):
    """
    Creates a Stripe charge for payment processing
    """
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    try:
        charge = stripe.Charge.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            source=token,
            description=description
        )
        return charge
    except stripe.error.StripeError as e:
        print(f"Stripe Error: {e}")
        return None