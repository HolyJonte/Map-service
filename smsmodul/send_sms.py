import requests
import json

### OBS! Ta bort raderna när vi testat klart (samma kod ligger i app.py)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from requests.auth import HTTPBasicAuth

# Tillagt av Jonte och Madde
from database.crud.sms_crud import log_sms



# Lagt till parametrar (Madde och Jonte)
def send_sms(to, message, newspaper_id=None, subscriber_id=None, testMode=True):
    # Ange rätt endpoint-URL från HelloSMS-dokumentationen
    url = "https://api.hellosms.se/v1/sms/send/"  # OBS: Ändra till den korrekta API-URL:en beroende på om det är test eller äkta

    # Exempelpayload för testning: verifiera integration och kostnadsuppdelning
    payload = {
        "to": [to] if isinstance(to, list) else to,
        "from": "TrafikViDa",
        "message": message,
        "testMode": testMode  # Viktigt! Detta säkerställer att inga riktiga SMS skickas
    }

    # Ange de nödvändiga headers, inklusive autentisering (exempel med Bearer-token)
    headers = {
        "Content-Type": "application/json",
    }

    api_username = "t85457034225838g5781392b"  # Byt ut mot ditt användarnamn
    api_password = "UrUjA8u6AdedAZajyNYR"  # Byt ut mot ditt lösenord

    try:
        # Skicka POST-anropet
        response = requests.post(url, json=payload, headers=headers
                                 , auth=HTTPBasicAuth(api_username, api_password))
        response.raise_for_status()  # Om statuskod inte är 2xx, höjs ett fel.

        # Skriv ut svar för att se hur det ser ut (t.ex. antal SMS-segment etc.)
        print("Statuskod:", response.status_code)
        print("Response:", json.dumps(response.json(), indent=2))

        # Logga SMS till databasen om ID:n är angivna (Tillagt av Jonte och Madde)
        if newspaper_id and subscriber_id:
            log_sms(newspaper_id, subscriber_id, to, message)

    except requests.exceptions.RequestException as e:
        print("Något gick fel:", e)

if __name__ == '__main__':
    send_sms(
        to="0701234567",  # Telefonnummer (eller en lista med nummer)
        message="Hej! Det här är ett testmeddelande.",
        newspaper_id=123,  # Om du har ett id för tidningen
        subscriber_id=456,  # Om du har ett id för prenumeranten
        testMode=True  # Om du vill testa utan att faktiskt skicka SMS
    )
