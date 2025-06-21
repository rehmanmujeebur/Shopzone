document.addEventListener('DOMContentLoaded', function() {
    const stripe = Stripe('{{ stripe_public_key }}');
    const elements = stripe.elements();
    const cardElement = elements.create('card', {
        style: {
            base: {
                fontSize: '16px',
                color: '#32325d',
            }
        }
    });
    
    cardElement.mount('#card-element');
    
    const form = document.getElementById('payment-form');
    
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const submitButton = document.getElementById('submit-button');
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
        
        // Calculate total from server to prevent tampering
        const total = parseFloat('{{ total }}');
        
        const {error, paymentMethod} = await stripe.createPaymentMethod({
            type: 'card',
            card: cardElement,
            billing_details: {
                name: document.getElementById('first_name').value + ' ' + document.getElementById('last_name').value,
                email: document.getElementById('email').value,
                address: {
                    line1: document.getElementById('address').value,
                    city: document.getElementById('city').value,
                    postal_code: document.getElementById('postal_code').value,
                    country: document.getElementById('country').value
                }
            }
        });
        
        if (error) {
            const errorElement = document.getElementById('card-errors');
            errorElement.textContent = error.message;
            submitButton.disabled = false;
            submitButton.textContent = 'Pay $' + total.toFixed(2);
        } else {
            try {
                const response = await fetch('/create-payment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrf_token]').value
                    },
                    body: JSON.stringify({
                        payment_method_id: paymentMethod.id,
                        email: document.getElementById('email').value,
                        first_name: document.getElementById('first_name').value,
                        last_name: document.getElementById('last_name').value,
                        address: document.getElementById('address').value,
                        city: document.getElementById('city').value,
                        postal_code: document.getElementById('postal_code').value,
                        country: document.getElementById('country').value,
                        total: total
                    })
                });
                
                const paymentResponse = await response.json();
                
                if (paymentResponse.error) {
                    throw new Error(paymentResponse.error);
                }
                
                // Confirm the payment on the client
                const {error: confirmError} = await stripe.confirmCardPayment(
                    paymentResponse.client_secret
                );
                
                if (confirmError) {
                    throw confirmError;
                }
                
                // Redirect to confirmation page
                window.location.href = '/order-confirmation/' + paymentResponse.order_id;
                
            } catch (err) {
                document.getElementById('card-errors').textContent = err.message;
                submitButton.disabled = false;
                submitButton.textContent = 'Pay $' + total.toFixed(2);
            }
        }
    });
});