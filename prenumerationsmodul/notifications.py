import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from smsmodul.send_sms import send_sms
from datetime import datetime, timedelta, timezone
from api.logic import get_all_accidents, get_all_roadworks
from database.crud.subscriber_crud import get_subscribers_by_county
from database.crud.sms_crud import log_sms

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
        json.dump(processed_events, f, indent=2)
    # TA BORT SEN, till för debugging
    print(f"DEBUG: Sparade {len(processed_events)} poster till {PROCESSED_EVENTS_FILE}")

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
    Hämtar händelser från dagens datum, identifierar nya händelser (accident eller roadwork)
    genom att jämföra ID:n mot processed_events.json, lägger till nya ID:n och skickar SMS.
    """
    processed_events = load_processed_events()
    processed_ids = {entry["id"] for entry in processed_events if "id" in entry}
    print(f"Antal tidigare behandlade händelse-ID:n: {len(processed_ids)}")

    # Hämta olyckor och vägarbeten
    accidents = get_all_accidents()
    for ev in accidents:
        ev["type"] = "accident"
    roadworks = get_all_roadworks()
    for ev in roadworks:
        ev["type"] = "roadwork"

    all_events = accidents + roadworks
    print(f"Hittade totalt {len(all_events)} händelser (olyckor + vägarbeten)")
    if not all_events:
        print("Inga händelser hittades.")
        save_processed_events(processed_events)
        return

    today = datetime.now(timezone.utc).date()

    new_events = []
    for event in all_events:
        event_id = event.get("id")
        if not event_id:
            continue

        if event_id in processed_ids:
            print(f"Händelse ID {event_id} redan behandlad, hoppar över")
            continue

        start_time_str = event.get("start")
        if not start_time_str:
            print(f"Starttid saknas för händelse ID {event_id} vid plats: {event.get('location', 'okänd')}")
            continue

        try:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            event_date = start_time.date()
            if event_date == today:
                new_events.append(event)
                print(f"Hittade ny händelse: ID {event_id} vid {event.get('location', 'okänd')}")
        except ValueError as e:
            print(f"Kunde inte parsa starttid för händelse ID {event_id} vid {event.get('location', 'okänd')}: {e}")
            continue

    if not new_events:
        print("Inga nya händelser hittades för idag.")
        save_processed_events(processed_events)
        return

    new_events_found = False

    for event in new_events:
        event_id = event.get("id")
        print(f"Behandlar ny händelse: ID {event_id}, Typ: {event.get('type', 'okänd')}")

        raw_counties = event.get("county", [])
        if not raw_counties:
            print(f"County saknas för händelse ID {event_id} vid plats: {event.get('location', 'okänd')}")
            continue

        # Hantera county: [2, 1] -> [1], annars unika ID:n
        if set(raw_counties) == {1, 2}:
            county_ids = [1]
        else:
            county_ids = [id if id != 2 else 1 for id in raw_counties]
            county_ids = list(set(county_ids))  # Unika ID:n
        print(f"Händelse ID {event_id} mappad till county IDs: {county_ids}")

        event_type = event.get("type", "").lower()
        label_map = {"accident": "Olycka", "roadwork": "Vägarbete"}
        label = label_map.get(event_type)
        if not label:
            print(f"Händelse ID {event_id} har okänd typ ({event_type}), hoppar över")
            continue

        severity_text = event.get("severity", "Okänd påverkan")
        if severity_text not in ("Stor påverkan", "Mycket stor påverkan"):
            continue

        message = (
            f"{label} i ditt län:\n"
            f"Plats: {event.get('location')}\n"
            f"Beskrivning: {event.get('message')}\n"
            f"Start: {event.get('start')}\n"
            f"Se mer information här: {event.get('link')}"
        )
        

        new_events_found = True
        for county_id in county_ids:
            county = str(county_id)  # Numeriskt ID som sträng för get_subscribers_by_county
            print(f"Hämtar prenumeranter för county ID: {county}")
            subscribers = get_subscribers_by_county(county)
            if not subscribers:
                print(f"Inga prenumeranter hittades för county ID: {county}")
                continue

            print(f"Hittade {len(subscribers)} prenumeranter för county ID {county}")

            for subscriber in subscribers:
                phone = subscriber.phone_number
                try:
                    success = send_sms(to=phone, message=message)
                    if success:
                        print(f"SMS skickat till {phone} om händelse {event_id} ({event_type})")
                        try:
                            log_sms(
                                newspaper_id=subscriber.newspaper_id,
                                subscriber_id=subscriber.id,
                                recipient=phone,
                                message=message
                            )
                            print(f"SMS loggat för subscriber_id={subscriber.id}, newspaper_id={subscriber.newspaper_id}")
                        except Exception as e:
                            print(f"Fel vid loggning av SMS för {phone}: {e}")
                        # Lägg till och spara direkt efter lyckat SMS
                        processed_events.append({
                            "id": event_id,
                            "processed_at": datetime.now(timezone.utc).isoformat()
                        })
                        save_processed_events(processed_events)
                    else:
                        print(f"Misslyckades att skicka SMS till {phone}")
                except Exception as e:
                    print(f"Fel vid SMS-sändning för {phone}: {e}")

    if not new_events_found:
        print("Inga nya händelser hittades för idag.")
    processed_events = clean_old_events(processed_events, days_to_keep=30)
    save_processed_events(processed_events)

if __name__ == "__main__":
    notify_accidents()