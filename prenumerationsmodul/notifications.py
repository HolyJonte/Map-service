#Hämtar olyckor (använder fetch_data.py eller en funktion i api/routes.py som service).
#Tar reda på county och matchar mot prenumeranter (via user_repository.py).

#Kallar smsmodul/ för att skicka SMS.

from smsmodul.send_sms import send_sms
from api.logic import get_all_accidents

""" def notify_accidents():
    accidents = get_all_accidents()
    for accident in accidents:
        county = accident.get("county")
        if not county:
            continue
        subscribers = get_subscribers_by_county(county)
        if not subscribers:
            continue
        message = (f"Olycka i {county}:\n"
                   f"Plats: {accident.get('location')}\n"
                   f"Beskrivning: {accident.get('message')}\n"
                   f"Start: {accident.get('start')}")
        for phone in subscribers:
            try:
                send_sms(to=phone, message=message)
                print(f"SMS skickat till {phone}")
            except Exception as e:
                print(f"Fel vid SMS till {phone}: {e}") """

# Simulerad databas: en hårdkodad dictionary som returnerar telefonnummer baserat på county
dummy_subscribers = {
    "1": ["+46701234567", "+46709876543"],
    "3": ["+46701239876"],
    "14": ["+46705551234"]
}

def get_subscribers_by_county(county):
    """
    Simulerar att hämta prenumeranter från en databas baserat på county.
    Ändra detta när din riktiga databas är på plats.
    """
    return dummy_subscribers.get(str(county), [])

def notify_accidents():
    """
    Hämtar olycksdata och skickar SMS till prenumeranter baserat på county.
    För test syfte används en simulerad databas (dummy_subscribers).
    """
    accidents = get_all_accidents()

    if not accidents:
        print("Inga olyckor hittades.")
        return

    for accident in accidents:
        county = accident.get("county")
        
        # Om county saknas i olycksdata, skriv ut ett meddelande och hoppa över
        if not county:
            print("County saknas för en olycka vid plats:", accident.get("location"))
            continue

        county = str(county) 

        # Använd simulerad funktion för att hämta prenumeranter
        subscribers = get_subscribers_by_county(county)
        if not subscribers:
            print(f"Inga prenumeranter hittades för county: {county}")
            continue

        message = (f"Olycka i {county}:\n"
                   f"Plats: {accident.get('location')}\n"
                   f"Beskrivning: {accident.get('message')}\n"
                   f"Start: {accident.get('start')}")
        # Skicka SMS till varje prenumerant
        print("Meddelande som skickas:", message)
                
        for phone in subscribers:
            try:
                send_sms(to=phone, message=message)
                print(f"SMS skickat till {phone}")
            except Exception as e:
                print(f"Fel vid SMS till {phone}: {e}")

# För teständamål, kör notifieringslogiken direkt om filen exekveras
if __name__ == "__main__":
    notify_accidents()
