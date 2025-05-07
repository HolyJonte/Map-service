import requests
import json
import time
from flask import Blueprint, request, jsonify, Flask, abort
from requests.auth import HTTPBasicAuth
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
## För att kunna testa när vi kör filen enskilt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Aktuell arbetskatalog:", os.getcwd())

# Skapa ett Blueprint för notifikationsrelaterade rutter
notification_bp = Blueprint('notification', __name__)

#----------------------------------------------------------------------------------------
# Funktion för att skicka SMS via HelloSMS API
#----------------------------------------------------------------------------------------

def send_sms(to, message, testMode=True):
    # Ange rätt endpoint-URL från HelloSMS-dokumentationen
    url = os.getenv("SMS_API_URL")  # OBS: Ändra till den korrekta API-URL:en beroende på om det är test eller äkta
    api_username = os.getenv("SMS_API_USER")  # Byt ut mot ditt användarnamn
    api_password = os.getenv("SMS_API_PASS")  # Byt ut mot ditt lösenord

    # Exempelpayload för testning: verifiera integration och kostnadsuppdelning
    payload = {
        "to": [to] if isinstance(to, list) else to,
        "from": "TrafikViDa",
        "message": message,
        "shortLinks": True,
        "testMode": testMode  # Viktigt! Detta säkerställer att inga riktiga SMS skickas
    }

    # Ange de nödvändiga headers, inklusive autentisering (exempel med Bearer-token)
    headers = {
        "Content-Type": "application/json",
    }

    try:
        # Skicka POST-anropet
        response = requests.post(url, json=payload, headers=headers
                                 , auth=HTTPBasicAuth(api_username, api_password))
        response.raise_for_status()  # Om statuskod inte är 2xx, höjs ett fel.
        response_data = response.json()

        # Skriv ut svar för att se hur det ser ut (t.ex. antal SMS-segment etc.)
        print("Statuskod:", response.status_code)
        print("Response:", json.dumps(response.json(), indent=2))

        return True, {
            "status": "success",
            "statusText": "SMS skickat framgångsrikt",
            "messageIds": response_data.get("messageIds", [])
        }

    except requests.exceptions.RequestException as e:
        print("Något gick fel:", e)
        return False
    
#----------------------------------------------------------------------------------------
# Funktion för att skicka e-post via SMTP
#----------------------------------------------------------------------------------------

# Funktion för att skicka e-post
def send_email (to, subject, message):
     # Hämta SMTP-konfiguration från miljövariabler
    smtp_server = os.getenv("EMAIL_SERVER")
    smtp_port = int(os.getenv("EMAIL_PORT"))
    smtp_user = os.getenv("EMAIL_USER")
    smtp_password = os.getenv("EMAIL_PASS")
    default_sender = os.getenv("EMAIL_DEFAULT_SENDER")

    # Skapa e-postmeddelande
    msg = MIMEMultipart()
    msg['From'] = default_sender
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Anslut till SMTP-servern
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Aktivera TLS
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"E-post skickad till {to} med ämne: {subject}")
        return True
    except Exception as e:
        print(f"Fel vid skickande av e-post till {to}: {e}")
        return False

#----------------------------------------------------------------------------------------
# API_KEY kontroll för varje request på detta blueprint
#----------------------------------------------------------------------------------------

API_KEY = os.getenv("NOTIFICATION_KEY")

@notification_bp.before_request
def check_api_key():
    if request.path.startswith('/notification/'):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            abort(401, description="Invalid or missing API key")

#----------------------------------------------------------------------------------------
# API-rutter
#----------------------------------------------------------------------------------------

@notification_bp.route('/send-sms', methods=['POST'])
def api_send_sms():
    data = request.get_json(force=True)
    to      = data.get('to')
    message = data.get('message')
    test    = data.get('testMode', True)

    if not to or not message:
        return jsonify(error="Missing 'to' or 'message'"), 400

    success, payload = send_sms(to, message, testMode=test)
    status_code = 200 if success else 500
    return jsonify(payload), status_code

if __name__ == "__main__":
    
    pass
# Lägg till testkod här vid behov (istället för pass)
