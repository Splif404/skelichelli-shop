import os
from flask import Flask, render_template, jsonify, request
import stripe
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


stripe.api_key = os.getenv('STRIPE_SECRET_KEY') 

YOUR_DOMAIN = os.getenv('DOMAIN', 'http://localhost:4745')

@app.route('/')
def index():
    return render_template('index.html', stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'))

@app.route('/buy')
def buy():
    return render_template('buy.html', stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'))

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    basket = data.get('basket')
    delivery = data.get('delivery')
    products = {
        'classic_white': {
            'name': 'Classic White T-Shirt',
            'amount': 2000
        },
        'black_logo': {
            'name': 'Black Logo Tee',
            'amount': 2500
        },
        'colorful_summer': {
            'name': 'Colorful Summer Tee',
            'amount': 2200
        }
    }
    if not basket or not isinstance(basket, list) or len(basket) == 0:
        return jsonify(error='Basket is empty.'), 400
    line_items = []
    for item in basket:
        pid = item.get('product_id')
        qty = item.get('quantity', 1)
        product = products.get(pid)
        if not product or qty < 1:
            return jsonify(error='Invalid product or quantity.'), 400
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product['name'],
                },
                'unit_amount': product['amount'],
            },
            'quantity': qty,
        })
    # For now, just print the delivery and basket info (in production, store it securely)
    print('Delivery info:', delivery)
    print('Basket:', basket)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4745)