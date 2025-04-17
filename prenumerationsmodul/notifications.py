#Hämtar olyckor (använder fetch_data.py eller en funktion i api/routes.py som service).
#Tar reda på county och matchar mot prenumeranter (via user_repository.py).

#Kallar smsmodul/ för att skicka SMS.
import sys
import os
## För att kunna testa när vi kör filen enskilt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from datetime import datetime, timedelta, timezone

from smsmodul.send_sms import send_sms
from api.logic import get_all_accidents
from database.crud.subscriber_crud import get_subscribers_by_county

# Fil för att lagra behandlade händelse-ID:n och deras tidsstämplar
PROCESSED_EVENTS_FILE = "processed_events.json"

def load_processed_events():
    """Laddar tidigare behandlade händelse-ID:n och deras tidsstämplar från JSON-fil."""
    try:
        with open(PROCESSED_EVENTS_FILE, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []

def save_processed_events(processed_events):
    """Sparar behandlade händelse-ID:n och deras tidsstämplar till JSON-fil."""
    with open(PROCESSED_EVENTS_FILE, 'w') as f:
        json.dump(processed_events, f)

## 30 DAGAR kanske onödigt länge
def clean_old_events(processed_events, days_to_keep=30):
    """Rensa händelse-ID:n som är äldre än det angivna antalet dagar."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
    cleaned_events = []
    
    for entry in processed_events:
        try:
            processed_at = datetime.fromisoformat(entry["processed_at"])
            if processed_at >= cutoff_time:
                cleaned_events.append(entry)
        except (ValueError, KeyError) as e:
            print(f"Fel vid parsning av tidsstämpel för post: {entry}, hoppar över: {e}")
            continue
    
    return cleaned_events

def notify_accidents():
    """
    Hämtar händelser från dagens datum, identifierar nya händelser (accident eller roadwork),
    och skickar SMS till prenumeranter med anpassat meddelande.
    """
    # Ladda tidigare behandlade händelse-ID:n
    processed_events = load_processed_events()
    processed_ids = {entry["id"] for entry in processed_events if "id" in entry}

    # Hämta alla händelser
    events = get_all_accidents()
    print(f"Hittade totalt {len(events)} händelser")

    if not events:
        print("Inga händelser hittades.")
        return

    # Filtrera händelser till bara dagens datum
    today = datetime.now(timezone.utc).date()
    todays_events = []
    for event in events:
        start_time_str = event.get("start")
        if not start_time_str:
            print("Starttid saknas för en händelse vid plats:", event.get("location"))
            continue
        try:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            event_date = start_time.date()
            if event_date == today:
                todays_events.append(event)
        except ValueError as e:
            print(f"Kunde inte parsa starttid för händelse vid {event.get('location')}: {e}")
            continue

    if not todays_events:
        print("Inga händelser hittades för dagens datum.")
        return

    new_events_found = False

    for event in todays_events:
        # Anta att varje händelse har ett unikt ID
        event_id = event.get("id")
        if not event_id:
            print("Händelse saknar ID, hoppar över:", event.get("location"))
            continue

        # Kolla om händelsen redan har behandlats
        if event_id in processed_ids:
            continue

        # Markera händelsen som ny
        new_events_found = True
        county = event.get("county")

        # Om county saknas, hoppa över
        if not county:
            print("County saknas för en händelse vid plats:", event.get("location"))
            continue

        county = str(county)

        # Hämta prenumeranter från databasen
        subscribers = get_subscribers_by_county(county)
        if not subscribers:
            print(f"Inga prenumeranter hittades för county: {county}")
            continue

        # Kontrollera händelsetyp (accident eller roadwork) och skapa anpassat meddelande
        event_type = event.get("type", "").lower()
        if event_type == "accident":
            message = (f"Olycka i {county}:\n"
                       f"Plats: {event.get('location')}\n"
                       f"Beskrivning: {event.get('message')}\n"
                       f"Start: {event.get('start')}")
        elif event_type == "roadwork":
            message = (f"Vägarbete i {county}:\n"
                       f"Plats: {event.get('location')}\n"
                       f"Beskrivning: {event.get('message')}\n"
                       f"Start: {event.get('start')}")
        else:
            print(f"Okänd händelsetyp '{event_type}' för händelse {event_id}, hoppar över")
            continue

        print("Meddelande som skickas:", message)

        # Skicka SMS till varje prenumerant
        for phone in subscribers:
            try:
                send_sms(to=phone, message=message)
                print(f"SMS skickat till {phone} om händelse {event_id} ({event_type})")
            except Exception as e:
                print(f"Fel vid SMS till {phone}: {e}")

        # Lägg till händelsen i listan med behandlade händelser
        processed_events.append({
            "id": event_id,
            "processed_at": datetime.now(timezone.utc).isoformat()
        })

    # Rensa gamla poster (äldre än 30 dagar)
    processed_events = clean_old_events(processed_events, days_to_keep=30)

    # Spara den uppdaterade listan
    save_processed_events(processed_events)

    if not new_events_found:
        print("Inga nya händelser hittades för dagens datum.")

if __name__ == "__main__":
    notify_accidents()
