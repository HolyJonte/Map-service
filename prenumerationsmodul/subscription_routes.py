from flask import Blueprint, request, jsonify, render_template, current_app, session
from datetime import datetime, timedelta

from betalningsmodul.klarna_integration import initiate_payment, verify_payment, cancel_token
from database.database import initialize_database
from database.county_utils import get_counties
from database.crud.newspaper_crud import get_all_newspaper_names

from database.crud.subscriber_crud import (
    add_subscriber, update_subscriber, subscriber_exists,
    deactivate_subscriber, manual_add_subscriber, get_all_subscribers,
    get_subscriber_klarna_token, remove_inactive_subscribers
)

from database.crud.pending_crud import (
    add_pending_subscriber, get_pending_subscriber, delete_pending_subscriber
)


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
    return render_template('subscription.html')

# ==========================================================================================
# Rutt för att starta prenumeration  (När man klickar på "Starta prenumeration" i appen)
# ==========================================================================================
@subscription_routes.route('/start-subscription', methods=['POST'])
def start_subscription():
    try:
        data = request.get_json(force=True)  # Säkerställ JSON även om Content-Type saknas
        phone_number = data.get('phone_number')
        county = data.get('county')
        newspaper_id = data.get('newspaper_id')

        if not phone_number or not county or not newspaper_id:
            return jsonify({"error": "Phone number, county and newspaper are required"}), 400

        session_id, client_token = initiate_payment(phone_number, county, tokenize=True)

        if not add_pending_subscriber(session_id, phone_number, county, newspaper_id):
            return jsonify({"error": "Phone number already in process"}), 400

        return jsonify({"session_id": session_id, "client_token": client_token}), 200

    except Exception as e:
        current_app.logger.error(f"Fel i start_subscription: {e}")
        return jsonify({"error": f"Serverfel: {str(e)}"}), 500


# ==========================================================================================
# Rutt för att verifiera betalning och aktivera prenumeration (När man klickar på "Betala" i Klarna)
# ==========================================================================================
@subscription_routes.route('/prenumeration-startad', methods=['GET', 'POST'])
def prenumeration_startad():
    if request.method == 'POST':
        data = request.get_json()

        # ✅ Hantera fejksvar från test-knappen
        if data.get("status") == "AUTHORIZED" and data.get("authorization_token") == "fake-token-123":
            session_id = data.get("session_id")
            klarna_token = "simulated_klarna_token_xyz"

            if not session_id:
                return jsonify({"error": "Missing session_id"}), 400

            result = get_pending_subscriber(session_id)
            if not result:
                return jsonify({"error": "Session ID not found"}), 404

            phone_number = result.phone_number
            county = result.county
            newspaper_id = result.newspaper_id

            if subscriber_exists(phone_number):
                delete_pending_subscriber(session_id)
                return jsonify({"error": "already_subscribed"}), 400

            add_subscriber(phone_number, county, newspaper_id, klarna_token)
            delete_pending_subscriber(session_id)
            subscriber_id = subscriber_exists(phone_number)

            return render_template("confirmation.html", subscriber_id=subscriber_id)

        # ✅ Hantera vanliga Klarna-svar
        try:
            is_valid, session_id, klarna_token = verify_payment(data)
        except Exception as e:
            return jsonify({"error": f"Failed to verify payment: {str(e)}"}), 500

        if not is_valid or not session_id:
            return jsonify({"message": "Payment not completed or invalid"}), 400

        result = get_pending_subscriber(session_id)
        if not result:
            return jsonify({"error": "Session ID not found"}), 404

        phone_number = result.phone_number
        county = result.county

        if subscriber_exists(phone_number):
            delete_pending_subscriber(session_id)
            return jsonify({"error": "already_subscribed"}), 400

        add_subscriber(phone_number, county, newspaper_id, klarna_token)
        delete_pending_subscriber(session_id)
        subscriber_id = subscriber_exists(phone_number)

        return render_template("confirmation.html", subscriber_id=subscriber_id)

    # GET-anrop (t.ex. direktlänk till sidan)
    return render_template("confirmation.html")


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