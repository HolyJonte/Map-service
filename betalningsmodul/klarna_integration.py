# klarna_integration.py
import requests
import base64
import os


# Konfiguration för Playground
KLARNA_API_URL = "https://api.playground.klarna.com"  # Playground API-bas-URL
KLARNA_API_KEY = 'd0a11e27-6f26-4b94-9d75-5c30713b1009' 
KLARNA_API_SECRET = 'klarna_test_api_WVNlYVdGZVVxRU1WNUxBLXoyZjJmViNzRnhpLTV1ekIsZDBhMTFlMjctNmYyNi00Yjk0LTlkNzUtNWMzMDcxM2IxMDA5LDEsbXNUV1VyMGl4RVlnT0tBNjFDZjNac3NTMDFWQmZBVm5FUlRJdnNEbHJVVT0' 
KLARNA_CLIENT_ID = 'klarna_test_client_UGtPJHNGMVdZMHVmZ0I1LyUoUilnaSNDMiV3YWZ4ZlMsNjkzZWJiZTItZjI0ZS00ZmQ1LWFlMzQtZDczOGNlMDlhZjBmLDEsakJlRVNBQytFZGFjTVAyUXBYdnNHWGNWai9jTUR6M1QydVIweHpOVTNQUT0'

# Bas-URL för appen (används för callbacks)
BASE_URL = "https://trafikvida.ddns.net"

# Autentisering: Base64-kodad "username:password"
auth_string = f"{KLARNA_API_KEY}:{KLARNA_API_SECRET}"
auth_header = "Basic " + base64.b64encode(auth_string.encode()).decode("ascii")

# Funktioner för att hantera betalningar.
# Denna funktion anropas från subscription_routes.py för att skapa en betalningssession hos Klarna
#Tar emot parametrar från subscription_routes.py, parametrarna används inte
# men behöver tas emot här ändå eftersom de kommer från formuläret. Ev kan vi ta bort senare?
def initiate_payment(_phone_number, _county, tokenize=False, payment_method='credit_card'):
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }

    # Skapar grundläggande betalningsdata
    payment_data = {
        "purchase_country": "SE",
        "purchase_currency": "SEK",
        "locale": "sv-SE",
        "order_amount": 9900,  # 99 SEK i öre
        "order_tax_amount": 0,
        "order_lines": [
            {
                "type": "digital",
                "name": "SMS-prenumeration",
                "quantity": 1,
                "unit_price": 9900,
                "tax_rate": 0,
                "total_amount": 9900,
                "total_tax_amount": 0,
            }
        ],
        "customer": {
            "first_name": "Alice",
            "last_name": "Test",
            "email": "customer@email.se",
            "phone": _phone_number,
            "street_address": "Södra Blasieholmshamnen 2",
            "postal_code": "11148",
            "city": "Stockholm",
            "country": "SE"
        },
        "merchant_urls": {
            "checkout": f"{BASE_URL}/subscriptions/subscription",
            "confirmation": f"{BASE_URL}/subscriptions/prenumeration-startad",
            "push": f"{BASE_URL}/subscriptions/prenumeration-startad"
        }
    }

    # Hantera payment_method parametern för att lägga till specifika data beroende på betalmetod
    if payment_method == 'direct_debit':
        payment_data["customer"]["personal_number"] = "19770111-6050"  # Testpersonnummer för Direct Debit

    elif payment_method in ['credit_card', 'debit_card']:
        # Ingen ytterligare data behövs här för dessa betalmetoder, Klarna widget kommer hantera det
        pass

    elif payment_method == 'bank_transfer':
        # Klarna Playground hanterar detta genom Demo Bank i widgeten
        pass

    # Om tokenize är True, lägg till "intent" för att skapa en token för återkommande betalningar
    if tokenize:
        payment_data["intent"] = "buy_and_tokenize"

    response = requests.post(
        f"{KLARNA_API_URL}/payments/v1/sessions",
        json=payment_data,
        headers=headers,
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(f"Failed to create session: {response.text}")

    session_data = response.json()
    session_id = session_data["session_id"]
    client_token = session_data["client_token"]

    return session_id, client_token, KLARNA_CLIENT_ID

def verify_payment(data):
    #Verifierar betalningsstatus från callback
    session_id = data.get("session_id")
    payment_status = data.get("status")
    klarna_token = data.get("klarna_token")
    # Verifierar att betalningen är slutförd
    if payment_status == "completed":
        return True, session_id, klarna_token
    return False, None, None

def create_recurring_order(klarna_token, amount):
    #Skapar en återkommande betalning i Playground
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    order_data = {
        "purchase_country": "SE",
        "purchase_currency": "SEK",
        "order_amount": amount,
        "order_tax_amount": 0,
        "order_lines": [
            {
                "type": "digital",
                "name": "SMS-prenumeration förnyelse",
                "quantity": 1,
                "unit_price": amount,
                "tax_rate": 0,
                "total_amount": amount,
                "total_tax_amount": 0
            }
        ]
    }

    response = requests.post(
        f"{KLARNA_API_URL}/payments/v1/customer-tokens/{klarna_token}/orders",
        json=order_data,
        headers=headers,
        timeout=10
    )

    return response.status_code == 200

def cancel_token(klarna_token):
    #Avslutar en kundtoken i Playground
    headers = {
        "Authorization": auth_header
    }
    response = requests.delete(
        f"{KLARNA_API_URL}/payments/v1/customer-tokens/{klarna_token}",
        headers=headers,
        timeout=10  # Timeput för begäran 10 sekunder
    )
    return response.status_code == 204