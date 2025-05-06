import requests
import json
from flask import Blueprint, request, jsonify, render_template, current_app, session, redirect, url_for
from datetime import datetime, timedelta

from betalningsmodul.klarna_integration import initiate_payment, verify_payment, cancel_token, auth_header
from database.database import initialize_database
from database.county_utils import get_counties
from database.crud.newspaper_crud import get_all_newspaper_names

from database.crud.subscriber_crud import (
    add_subscriber, update_subscriber, subscriber_exists,
    deactivate_subscriber, manual_add_subscriber, get_all_subscribers,
    get_subscriber_klarna_token, remove_inactive_subscribers
)

from database.crud.pending_crud import (
    add_pending_subscriber, get_pending_subscriber, delete_pending_subscriber, get_all_pending_subscribers
)

from database.crud.sms_crud import get_sms_count_for_newspaper


### VI BEHÖVER: Lägga in admin inlogg och flask session hantering så att vi kan kräva inloigg
### ex komma åt rutter som /subscribers (alla prenumeranter)

subscription_routes = Blueprint('subscriptions', __name__)

# Kör funktionen för att initiera databasen när modulen laddas
initialize_database()

# ==========================================================================================
# Rutter för prenumerationer
# ==========================================================================================

@subscription_routes.route('/subscription', methods=['GET'])
def show_subscription_page():
    if not session.get('user_logged_in'):
        return redirect(url_for('user_routes.login'))
    return render_template('subscription.html')


@subscription_routes.route('/prenumerera')
def prenumerera_check():
    if session.get('user_logged_in'):
        return redirect(url_for('subscriptions.show_subscription_page'))
    else:
        session['next'] = url_for('subscriptions.show_subscription_page')
        return redirect(url_for('user_routes.serve_login_choice'))

# ==========================================================================================
# Rutt för att starta prenumeration  (När man klickar på "Starta prenumeration" i appen)
# ==========================================================================================
@subscription_routes.route('/start-subscription', methods=['POST'])
def start_subscription():
    try:
        data = request.get_json(force=True)
        phone_number = data.get('phone_number')
        counties = data.get('counties') 
        newspaper_id = data.get('newspaper_id')

        if not phone_number or not counties or not newspaper_id:
            return jsonify({"error": "Phone number, counties and newspaper are required"}), 400

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401
        
         # Kontrollera om telefonnumret redan är registrerat
        if subscriber_exists(phone_number):
            return jsonify({"error": "already_subscribed"}), 400


        # Om du behöver passa county som EN sträng (kommaseparerad) till Klarna (eller databasen)
        counties_str = ",".join(str(c) for c in counties)

        # Skicka counties_str om Klarna behöver ett enda "county"
        session_id, client_token = initiate_payment(phone_number, counties_str, tokenize=False)

        # Skicka counties_str till add_pending_subscriber också
        if not add_pending_subscriber(session_id, user_id, phone_number, counties_str, newspaper_id):
            return jsonify({"error": "Phone number already in process"}), 400

        return jsonify({
            "session_id": session_id,
            "client_token": client_token,
        }), 200

    except Exception as e:
        current_app.logger.error(f"Fel i start_subscription: {e}")
        return jsonify({"error": f"Serverfel: {str(e)}"}), 500


# ==========================================================================================
# Rutt för att verifiera betalning och aktivera prenumeration (När man klickar på "Betala" i Klarna)
# ==========================================================================================
@subscription_routes.route('/prenumeration-startad', methods=['POST'])
def prenumeration_startad():
    try:
        if request.method == 'POST':
            data = request.get_json()

            # ✅ Läs in token från ny authorize-logik
            session_id = data.get("session_id")
            authorization_token = data.get("authorization_token")

            if not session_id or not authorization_token:
                return jsonify({"error": "Missing session_id or Klarna token"}), 400

            # Kontrollera pending subscriber
            result = get_pending_subscriber(session_id)
            current_app.logger.debug(f"Pending subscriber dir: {dir(result)}")

            if not result:
                return jsonify({"error": "Session ID not found"}), 404

            user_id = session.get('user_id')
            if not user_id:
                return jsonify({"error": "User not logged in"}), 401

            phone_number = result.phone_number
            county = result.county
            newspaper_id = result.newspaper_id
            
            url = f"https://api.playground.klarna.com/payments/v1/authorizations/{authorization_token}/order"
            headers = {"Authorization": auth_header, "Content-Type": "application/json"}
            payload = {
                "purchase_country": "SE",
                "purchase_currency": "SEK",
                "order_amount": 9900,
                "order_tax_amount": 0,
                "order_lines": [
                    {
                        "type": "digital",
                        "name": "SMS-Prenumeration",
                        "quantity": 1,
                        "unit_price": 9900,
                        "tax_rate": 0,
                        "total_amount": 9900,
                        "total_tax_amount": 0
                    }
                ],
                "merchant_reference1": f"sub-{user_id}",
                "merchant_data": json.dumps({"county": str(county)})
            }
            current_app.logger.debug("Payload som skickas till Klarna:")
            current_app.logger.debug(json.dumps(payload, indent=2))
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code not in [200, 201]:
                return jsonify({"error": "Failed to create order: " + response.text}), 500

            order_data = response.json()
            klarna_token = order_data.get( authorization_token)

            add_subscriber(phone_number, user_id, county, newspaper_id, klarna_token)
            delete_pending_subscriber(session_id)
            subscriber_id = subscriber_exists(phone_number)

            return render_template("confirmation.html", subscriber_id=subscriber_id)
        
    except Exception as e:
        current_app.logger.error(f"Fel i prenumeration_startad: {e}")
        return jsonify({"error": f"Serverfel: {str(e)}"}), 500



# ==========================================================================================
# Rutt för att avbryta prenumeration
# ==========================================================================================
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


# ==========================================================================================
# Rutt för att hämta alla län (counties) i Sverige
# ==========================================================================================
@subscription_routes.route('/counties', methods=['GET'])
def get_county_list():
    return jsonify(get_counties())
# ==========================================================================================
# Rutt för att hämta in alla tidningar från databasen.
# ==========================================================================================

@subscription_routes.route('/newspapers', methods=['GET'])
def get_newspaper_names():
    try:
        # Hämta alla tidningars namn
        newspaper_names = get_all_newspaper_names()

        # Kontrollera om vi fick några tidningar
        if not newspaper_names:
            return jsonify({"error": "No newspapers found"}), 404

        # Returnera listan som JSON
        return jsonify(newspaper_names)

    except Exception as e:
        # Returnera ett felmeddelande om något går fel
        return jsonify({"error": f"Failed to fetch newspapers: {str(e)}"}), 500


### KRÄVA INLOGG
# ==========================================================================================
# Rutt för manuellt lägga till en prenumerant
# ==========================================================================================
    ###OBS! LÄGGTILL NEWSPAPER
@subscription_routes.route('/man-add-subscriber', methods=['POST'])
def man_add_subscriber():
    data = request.json
    phone_number = data.get('phone_number')
    county = data.get('county')
    newspaper_id = data.get('newspaper_id')
    active = data.get('active', 1)
    subscription_start = data.get('subscription_start')
    last_payment = data.get('last_payment')
    klarna_token = data.get('klarna_token')

    if not phone_number or not county:
        return jsonify({"error": "Phone number and county are required"}), 400
    # Kolla att active är 0 eller 1
    if active not in (0, 1):
        current_app.logger.error(f"Ogiltigt active-värde: {active}")
        return jsonify({"error": "Active must be 0 or 1"}), 400

    if manual_add_subscriber(phone_number, county, newspaper_id, active, subscription_start, last_payment, klarna_token):
        return jsonify({"message": f"Subscriber {phone_number} added successfully"}), 201
    else:
        return jsonify({"error": "Phone number already exists"}), 400


### KRÄVA INLOGG
# ==========================================================================================
# Rutt för att hämta alla prenumeranter
# ==========================================================================================
@subscription_routes.route('/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = get_all_subscribers()
    return jsonify(subscribers), 200

def check_subscriptions():
    remove_inactive_subscribers()

# ==========================================================================================
# Rutt för att hantera push från klarna och hämta klarna_order_id
# ==========================================================================================
@subscription_routes.route('/klarna-push', methods=['POST'])
def handle_klarna_push():
    try:
        klarna_order_id = request.args.get('klarna_order_id')
        if not klarna_order_id:
            return jsonify({"error": "Missing klarna_order_id"}), 400

        # Hämta orderdetaljer från Order Management API
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            f"https://api.playground.klarna.com/ordermanagement/v1/orders/{klarna_order_id}",
            headers=headers,
            timeout=10 # Timeout för att undvika hängande anrop
        )
        if response.status_code != 200:
            current_app.logger.error(f"Failed to fetch order details: {response.text}")
            return jsonify({"error": "Failed to fetch order details"}), 500

        order_data = response.json()
        # Kontrollera att ordern är godkänd
        if order_data.get("status") in ["CAPTURED", "COMPLETED"]:
            # Hämta kundens telefonnummer från order_data
            phone_number = order_data.get("billing_address", {}).get("phone")
            if not phone_number:
                return jsonify({"error": "Phone number not found in order data"}), 400

            # Hitta matchande pending_subscriber baserat på phone_number
            result = None
            for pending in get_all_pending_subscribers():
                if pending["phone_number"] == phone_number:
                    result = pending
                    break
            if not result:
                return jsonify({"error": "No matching pending subscriber found"}), 404

            # Kontrollera om prenumeration redan finns
            if subscriber_exists(phone_number):
                return jsonify({"error": "already_subscribed"}), 400

            # Aktivera prenumeration
            user_id = result["user_id"]
            county = result["county"]
            newspaper_id = result["newspaper_id"]
            klarna_token = order_data.get("recurring_token")
            if not klarna_token:
                return jsonify({"error": "No recurring token found"}), 400

            add_subscriber(phone_number, user_id, county, newspaper_id, klarna_token)

            # Radera pending_subscriber en gång efter hantering
            delete_pending_subscriber(result["session_id"])

        return jsonify({"message": "Push notification received"}), 200
    except Exception as e:
        current_app.logger.error(f"Fel i handle_klarna_push: {e}")
        return jsonify({"error": f"Serverfel: {str(e)}"}), 500

# ==========================================================================================
# Rutt för att hantera spårning av SMS
# ==========================================================================================

@subscription_routes.route('/sms-count/<int:newspaper_id>', methods=['GET'])
def get_sms_count(newspaper_id):
    try:
        count = get_sms_count_for_newspaper(newspaper_id)
        return jsonify({"sms_count": count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
