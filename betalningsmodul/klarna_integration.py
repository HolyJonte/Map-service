# # Denna modul innehåller funktioner för att hantera betalningar mot Klarna API

import requests
import base64
import os


# Konfiguration för Playground
KLARNA_API_URL = os.getenv("KLARNA_API_URL")  # Playground API-bas-URL
KLARNA_API_KEY = os.getenv("KLARNA_API_KEY")
KLARNA_API_SECRET = os.getenv("KLARNA_API_SECRET")
KLARNA_CLIENT_ID = os.getenv("KLARNA_CLIENT_ID")
SUBSCRIPTION_PRICE = os.getenv("SUBSCRIPTION_PRICE")  # Prenumerationspriset i kr
PRICE_ORE = int(SUBSCRIPTION_PRICE) * 100  # Omvandla till öre
# Bas-URL för appen (används för callbacks)
BASE_URL = "https://trafikvida.ddns.net"

# Autentisering: Base64-kodad "username:password"
auth_string = f"{KLARNA_API_KEY}:{KLARNA_API_SECRET}"
auth_header = "Basic " + base64.b64encode(auth_string.encode()).decode("ascii")


# Denna funktion anropas från subscription_routes.py för att skapa en betalningssession hos Klarna
# Tar emot parametrar från subscription_routes.py, county används inte
# men behöver tas emot här ändå eftersom de kommer från formuläret. 
def initiate_payment(_phone_number, _county, tokenize=True, payment_method='credit_card'):
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }

    normalized_phone = _phone_number.strip()
    if not normalized_phone.startswith('+46'):
        normalized_phone = '+46' + normalized_phone.lstrip('0')
    if not normalized_phone.startswith('+46') or len(normalized_phone) != 12:
        raise ValueError("Ogiltigt telefonnummer: Måste vara i formatet +46701234567")

    # Skapar grundläggande betalningsdata
    payment_data = {
        "acquiring_channel": "ECOMMERCE",
        "intent": "buy_and_tokenize",
        "purchase_country": "SE",
        "purchase_currency": "SEK",
        "locale": "sv-SE",
        "order_amount": PRICE_ORE,
        "order_tax_amount": 0,
        "order_lines": [
            {
                "type": "digital",
                "name": "SMS-prenumeration",
                "quantity": 1,
                "unit_price": PRICE_ORE,
                "tax_rate": 0,
                "total_amount": PRICE_ORE,
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
            "push": f"{BASE_URL}/subscriptions/klarna-push"
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

    return session_id, client_token



