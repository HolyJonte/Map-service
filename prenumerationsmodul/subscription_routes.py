# subscription_routes.py
from flask import Blueprint, request, jsonify
from flask import render_template
from datetime import datetime, timedelta
from betalningsmodul.klarna_integration import initiate_payment, verify_payment, cancel_token
from prenumerationsmodul.repository import (initialize_database, add_pending_subscriber, get_pending_subscriber, 
                                        delete_pending_subscriber, subscriber_exists, add_subscriber, 
                                        update_subscriber, get_subscriber_klarna_token, deactivate_subscriber, 
                                        manual_add_subscriber, get_all_subscribers, remove_inactive_subscribers)

### VI BEHÖVER: Lägga in admin inlogg och flask session hantering så att vi kan kräva inloigg 
### ex komma åt rutter som /subscribers (alla prenumeranter)

subscription_routes = Blueprint('subscriptions', __name__)

# Kör funktionen för att initiera databasen när modulen laddas
initialize_database()

# Renderar startsidan för prenumerationer
@subscription_routes.route('/subscription', methods=['GET'])
def show_subscription_page():
    return render_template('subscription.html')
# Rutt för att starta prenumeration
@subscription_routes.route('/start-subscription', methods=['POST'])
def start_subscription():
    data = request.json
    phone_number = data.get('phone_number')
    county = data.get('county')
    
    if not phone_number or not county:
        return jsonify({"error": "Phone number and county are required"}), 400
    
    try:
        session_id, client_token = initiate_payment(phone_number, county, tokenize=True)
    except Exception as e:
        return jsonify({"error": f"Failed to initiate payment: {str(e)}"}), 500
    
    # Använd user_database för att lägga till en väntande prenumerant
    if not add_pending_subscriber(session_id, phone_number, county):
        return jsonify({"error": "Phone number already in process"}), 400
    
    return jsonify({"session_id": session_id, "client_token": client_token}), 200
# Rutt för att verifiera betalning och aktivera prenumeration
@subscription_routes.route('/prenumeration-startad', methods=['GET', 'POST'])
def prenumeration_startad():
    if request.method == 'POST':
        # Hantera callback från Klarna
        data = request.json
        
        try:
            is_valid, session_id, klarna_token = verify_payment(data)
        except Exception as e:
            return jsonify({"error": f"Failed to verify payment: {str(e)}"}), 500
        
        if not is_valid or not session_id:
            return jsonify({"message": "Payment not completed or invalid"}), 400
        
        # Hämta den väntande prenumeranten
        result = get_pending_subscriber(session_id)
        if not result:
            return jsonify({"error": "Session ID not found"}), 404
        
        phone_number, county = result
        
        # Kontrollera om prenumeranten redan finns och lägg till eller uppdatera
        existing = subscriber_exists(phone_number)
        if existing:
            update_subscriber(phone_number, klarna_token)
        else:
            if not add_subscriber(phone_number, county, klarna_token):
                return jsonify({"error": "Phone number already exists"}), 400
        
        # Ta bort från pending_subscribers
        delete_pending_subscriber(session_id)
        
        return jsonify({"message": f"Subscriber {phone_number} added or renewed as active"}), 201
    
    else:  # GET
        # Visa bekräftelsesida för användaren
        return render_template('confirmation.html')
# Rutt för att avbryta prenumeration
@subscription_routes.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    data = request.json
    subscriber_id = data.get('id')
    phone_number = data.get('phone_number')
    
    if not subscriber_id or not phone_number:
        return jsonify({"error": "Subscriber ID and phone number are required"}), 400
    
    klarna_token = get_subscriber_klarna_token(subscriber_id, phone_number)
    if not klarna_token:
        return jsonify({"error": "Subscriber not found or invalid credentials"}), 404
    
    try:
        success = cancel_token(klarna_token)
    except Exception as e:
        return jsonify({"error": f"Failed to cancel subscription with Klarna: {str(e)}"}), 500
    
    if not success:
        return jsonify({"error": "Failed to cancel subscription with Klarna"}), 500
    
    deactivate_subscriber(subscriber_id, phone_number)
    
    return jsonify({"message": f"Subscription for {phone_number} cancelled"}), 200

### KRÄVA INLOGG
## Rutt för att lägga till prenumerant manuellt
@subscription_routes.route('/man-add-subscriber', methods=['POST'])
def man_add_subscriber():
    data = request.json
    phone_number = data.get('phone_number')
    county = data.get('county')
    active = data.get('active', 1)
    subscription_start = data.get('subscription_start')
    last_payment = data.get('last_payment')
    klarna_token = data.get('klarna_token')

    if not phone_number or not county:
        return jsonify({"error": "Phone number and county are required"}), 400

    if manual_add_subscriber(phone_number, county, active, subscription_start, last_payment, klarna_token):
        return jsonify({"message": f"Subscriber {phone_number} added successfully"}), 201
    else:
        return jsonify({"error": "Phone number already exists"}), 400
### KRÄVA INLOGG
# Rutt för att hämta alla prenumeranter
@subscription_routes.route('/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = get_all_subscribers()
    return jsonify(subscribers), 200

def check_subscriptions():
    remove_inactive_subscribers()