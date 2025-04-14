#Hämtar olyckor (använder fetch_data.py eller en funktion i api/routes.py som service).
#Tar reda på county och matchar mot prenumeranter (via user_repository.py).

#Kallar smsmodul/ för att skicka SMS.
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
from smsmodul.send_sms import send_sms
from api.logic import get_all_accidents

# Dummy-databas för test
dummy_subscribers = {
    "1": ["+46701234567", "+46709876543"],   # Stockholms län
    "3": ["+46701239876"],                   # Uppsala län
    "14": ["+46705551234"]                   # Västra Götaland
}

def get_subscribers_by_county(county):
    """
    Simulerar att hämta prenumeranter från en databas baserat på county.
    """
    return dummy_subscribers.get(county, [])

def notify_accidents():
    """
    Hämtar olycksdata och skickar SMS till prenumeranter baserat på län (county).
    """
    accidents = get_all_accidents()
    print(f"Hittade totalt {len(accidents)} olyckor")
    for a in accidents:
        print(a)

    
    if not accidents:
        #Här borde vi kanske inte skriva ut meddelande.
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

# Kör direkt om filen körs
if __name__ == "__main__":
    notify_accidents()
