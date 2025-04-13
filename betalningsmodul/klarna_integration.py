import requests
import base64

### Behöver key och secret i config eller liknade fil sen
# Konfiguration för Playground
KLARNA_API_URL = "https://api.playground.klarna.com/"  # Playground API-bas-URL
KLARNA_API_KEY = "d1305bd70-d66c-4dc5-bb73-54d6c73a9998"  # Hämta från Playground Merchant Portal
#Klarna kräver Basic Authentication, där API-nyckeln och kod kombineras och kodas i Base64
KLARNA_API_SECRET = "klarna_test_api_NWJweD8vODE_SGQ4KUIyczR6ZkEoIUEzQjdweC13SHMsMTMwNWJkNzAtZDY2Yy00ZGM1LWJiNzMtNTRkNmM3M2E5OTk4LDEsZ0ZKREo4SXdpMVN5djZWVmc5UVNubjdsWjBjbElMQ2o0MVRKWU03QnBzTT0"  # Hämta från Playground Merchant Portal

CALLBACK_URL = "https://02d3-176-10-137-52.ngrok-free.app/prenumeration-startad" # Behöver lägga vår URL till /prenumeration-startad här OBS!!!

# Autentisering: Base64-kodad "username:password"
auth_string = f"{KLARNA_API_KEY}:{KLARNA_API_SECRET}"
auth_header = "Basic " + base64.b64encode(auth_string.encode()).decode("ascii")

# Funktioner för att hantera betalningar. 
# Denna funktion anropas från subscription_routes.py för att skapa en betalningssession hos Klarna 
#Tar emot parametrar från subscription_routes.py, parametrarna används inte
# men behöver tas emot här ändå eftersom de kommer från formuläret. Ev kan vi ta bort senare?
def initiate_payment(_phone_number, _county, tokenize=False):
    """Skapar en betalningssession i Klarna Playground"""
    headers = {
        "Authorization": auth_header, # Lägger till autentiseringsheader för att identifiera oss mot Klarna
        "Content-Type": "application/json" # Anger att vi skickar JSON-data
    }
    # Skapar betalningsdata som skickas till Klarna för att starta en session
    payment_data = {
        "purchase_country": "SE",  # Sverige för test
        "purchase_currency": "SEK",
        "locale": "sv-SE",
        "order_amount": 9900,  # 99 SEK i öre
        "order_tax_amount": 0,  # Ingen moms 
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
        "merchant_urls": {
        "checkout": "https://02d3-176-10-137-52.ngrok-free.app/subscription",
        "confirmation": "https://02d3-176-10-137-52.ngrok-free.app/prenumeration-startad",
        "push": "https://02d3-176-10-137-52.ngrok-free.app/prenumeration-startad"
    }
}
        
    

    # Om tokenize är True, lägg till "intent" för att skapa en token för återkommande betalningar
    if tokenize:
        payment_data["intent"] = "buy_and_tokenize"  # För att få en kundtoken för återkommande betalningar
    #
    response = requests.post(
        f"{KLARNA_API_URL}/payments/v1/sessions",
        json=payment_data,
        headers=headers,
        timeout=10  # Timeout för begäran
    )
    # Kod 200 är sucsess, annars visar den ett felmeddelande
    if response.status_code != 200:
        raise Exception(f"Failed to create session: {response.text}")
    
    session_data = response.json()
    session_id = session_data["session_id"]
    client_token = session_data["client_token"]  # För frontend-widget
    
    return session_id, client_token

def verify_payment(data):
    """Verifierar betalningsstatus från callback"""
    session_id = data.get("session_id")
    payment_status = data.get("status")  # Anta att detta kommer från callback
    klarna_token = data.get("klarna_token")  # Token för återkommande betalningar
    
    # Här kan du lägga till ett extra API-anrop för att verifiera sessionen om nödvändigt
    if payment_status == "completed":
        return True, session_id, klarna_token
    return False, None, None

def create_recurring_order(klarna_token, amount):
    """Skapar en återkommande betalning i Playground"""
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    order_data = {
        "purchase_country": "SE",
        "purchase_currency": "SEK",
        "order_amount": amount,  # T.ex. 10000 öre
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
        timeout=10  # Timeout för begäran
    )
    
    return response.status_code == 200

def cancel_token(klarna_token):
    """Avslutar en kundtoken i Playground"""
    headers = {
        "Authorization": auth_header
    }
    response = requests.delete(
        f"{KLARNA_API_URL}/payments/v1/customer-tokens/{klarna_token}",
        headers=headers,
        timeout=10  # Timeout för begäran
    )
    return response.status_code == 204