# notifications.py
# Som en del av prenumerationsmodulen, ansvarar denna fil för att hantera 
# notifieringar till prenumeranter om olyckor och vägarbeten.
# Den skickar SMS och e-postmeddelanden till prenumeranter baserat på deras
# registrerade län och händelser som inträffar i deras område.
# Denna modul är en del av ett större system för att hantera prenumerationer
# och notifieringar för en tidning eller nyhetstjänst.

# importera nödvändiga moduler
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import json
from flask import url_for, current_app
from smsmodul.notification_service import send_sms, send_email
from datetime import datetime, timedelta, timezone
from api.logic import get_all_accidents, get_all_roadworks
from database.crud.subscriber_crud import get_subscribers_by_county, get_subscriptions_due_in_14_days
from database.crud.sms_crud import log_sms


MAX_SMS = 1
sms_sent = 0


# Fil för att lagra behandlade händelse-ID:n och deras tidsstämplar
PROCESSED_EVENTS_FILE = "processed_events.json"

# Lista för att lagra SMS-meddelanden som ska skickas
sms_to_send = []  

# Funktion för att ladda tidigare behandlade händelse-ID:n
def load_processed_events():
    """Laddar tidigare behandlade händelse-ID:n och deras tidsstämplar från JSON-fil."""
    try:
        # Kontrollera om filen finns och har innehåll
        with open(PROCESSED_EVENTS_FILE, 'r') as f:
            content = f.read().strip()
            # Om filen är tom, returnera en tom lista
            if not content:
                return []
            # Ladda JSON-innehållet och returnera det som en lista
            data = json.loads(content)
            return data
    # Om filen inte finns eller innehållet inte är giltig JSON, returnera en tom lista
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Funktion för att spara behandlade händelse-ID:n
def save_processed_events(processed_events):
    """Sparar behandlade händelse-ID:n och deras tidsstämplar till JSON-fil."""
    with open(PROCESSED_EVENTS_FILE, 'w') as f:
        json.dump(processed_events, f, indent=2)
    # TA BORT SEN, till för debugging
    print(f"DEBUG: Sparade {len(processed_events)} poster till {PROCESSED_EVENTS_FILE}")

# Funktion för att rensa gamla händelse-ID:n
def clean_old_events(processed_events, days_to_keep=30):
    """Rensa händelse-ID:n som är äldre än det angivna antalet dagar."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
    # Filtrera bort händelser som är äldre än cutoff_time
    cleaned_events = []
    
    # Loopa igenom de behandlade händelserna och behåll endast de som är nyare än cutoff_time
    for entry in processed_events:
        try:
            # Kontrollera om "processed_at" finns i posten
            processed_at = datetime.fromisoformat(entry["processed_at"])
            # Om "processed_at" är nyare än cutoff_time, behåll posten
            if processed_at >= cutoff_time:
                cleaned_events.append(entry)
        # Om "processed_at" inte finns eller inte kan parsas, hoppa över posten
        except (ValueError, KeyError) as e:
            print(f"Fel vid parsning av tidsstämpel för post: {entry}, hoppar över: {e}")
            continue
    
    # Spara de rensade händelserna tillbaka till filen
    return cleaned_events

# Funktion för att skicka notifieringar om olyckor och vägarbeten
def notify_accidents():
    """
    Hämtar händelser från dagens datum, identifierar nya händelser (accident eller roadwork)
    genom att jämföra ID:n mot processed_events.json, lägger till nya ID:n och skickar SMS.
    """
    # Ladda tidigare behandlade händelse-ID:n och deras tidsstämplar
    processed_events = load_processed_events()
    processed_ids = {entry["id"] for entry in processed_events if "id" in entry}
    print(f"Antal tidigare behandlade händelse-ID:n: {len(processed_ids)}")

    # Hämta olyckor och vägarbeten
    accidents = get_all_accidents()
    # Om olyckor inte finns, sätt till tom lista
    for ev in accidents:
        ev["type"] = "accident"
    # Om vägarbeten inte finns, sätt till tom lista
    roadworks = get_all_roadworks()
    for ev in roadworks:
        ev["type"] = "roadwork"

    # Kombinera olyckor och vägarbeten till en lista
    all_events = accidents + roadworks
    print(f"Hittade totalt {len(all_events)} händelser (olyckor + vägarbeten)")
    # Om inga händelser hittas, skriv ut meddelande och avsluta
    if not all_events:
        print("Inga händelser hittades.")
        save_processed_events(processed_events)
        return

    # Hämta dagens datum och skapa en lista för att samla nya händelser för idag och ännu inte behandlade
    today = datetime.now(timezone.utc).date()
    new_events = []
    # Loopa igenom alla händelser och filtrera ut de som ska behandlas idag
    for event in all_events:
          # Hämta händelse-ID (viktigt för att avgöra om det redan behandlats)
        event_id = event.get("id")
        if not event_id:
            continue
        
        # Kontrollera om händelsen redan har behandlats tidigare
        # (baserat på att ID finns i processed_events.json)
        if event_id in processed_ids:
            #print(f"Händelse ID {event_id} redan behandlad, hoppar över")
            continue

        # Hämta starttiden för händelsen
        start_time_str = event.get("start")
        if not start_time_str:
            print(f"Starttid saknas för händelse ID {event_id} vid plats: {event.get('location', 'okänd')}")
            continue

        try:
            # Konvertera starttiden till datetime-objekt
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            # Kontrollera om händelsen är för idag
            event_date = start_time.date()
            # Om händelsen är för idag, lägg till den i listan över nya händelser
            if event_date == today:
                new_events.append(event)
                #print(f"Hittade ny händelse: ID {event_id} vid {event.get('location', 'okänd')}")
        except ValueError as e:
            # Om det inte går att konvertera starttiden, skriv ut felmeddelande
            print(f"Kunde inte parsa starttid för händelse ID {event_id} vid {event.get('location', 'okänd')}: {e}")
            continue

    # Om inga nya händelser hittas, skriv ut meddelande och avsluta
    if not new_events:
        print("Inga nya händelser hittades för idag.")
        # Rensa gamla händelser och spara
        save_processed_events(processed_events)
        return

    # Om nya händelser hittas, skriv ut meddelande
    new_events_found = False
    # För att räkna antalet skickade SMS
    sms_count = 0   

    # Loopa igenom nya händelser och skicka SMS till prenumeranter
    for event in new_events:
        event_id = event.get("id")
        #print(f"Behandlar ny händelse: ID {event_id}, Typ: {event.get('type', 'okänd')}")

        # Hämta counties för händelsen
        raw_counties = event.get("county", [])
        # Om counties inte finns, skriv ut meddelande och hoppa över händelsen
        if not raw_counties:
            print(f"County saknas för händelse ID {event_id} vid plats: {event.get('location', 'okänd')}")
            continue

        # Hantera county: [2, 1] -> [1], annars unika ID:n
        if set(raw_counties) == {1, 2}:
            # Om både 1 och 2 finns, sätt till 1
            county_ids = [1]
        else:
            # Annars behåll unika ID:n
            county_ids = [id if id != 2 else 1 for id in raw_counties]
            county_ids = list(set(county_ids))  # Unika ID:n
        #print(f"Händelse ID {event_id} mappad till county IDs: {county_ids}")

        # Hämta händelsetyp och mappa till etikett
        event_type = event.get("type", "").lower()
        label_map = {"accident": "Olycka", "roadwork": "Vägarbete"}
        label = label_map.get(event_type)
        if not label:
            #print(f"Händelse ID {event_id} har okänd typ ({event_type}), hoppar över")
            continue

        # Hämta händelsens allvarlighetsgrad och kontrollera om den är relevant
        severity_text = event.get("severity", "Okänd påverkan")
        # Om allvarlighetsgraden inte är relevant, hoppa över händelsen
        if severity_text not in ("Stor påverkan", "Mycket stor påverkan"):
            continue

        # Skapa meddelande för SMS
        message = (
            f"{label} i ditt län:\n"
            f"Plats: {event.get('location')}\n"
            f"Beskrivning: {event.get('message')}\n"
            f"Start: {event.get('start')}\n"
            f"Se mer information här: {event.get('link')}"
        )
        

        # Hämta prenumeranter för länet
        new_events_found = True
        # Hämta prenumeranter för länet
        for county_id in county_ids:
            county = str(county_id)  
            # Om länet inte är giltigt, skriv ut meddelande och hoppa över
            print(f"Hämtar prenumeranter för county ID: {county}")
            subscribers = get_subscribers_by_county(county)
            # Om inga prenumeranter hittas, skriv ut meddelande och hoppa över
            if not subscribers:
                print(f"Inga prenumeranter hittades för county ID: {county}")
                continue

            print(f"Hittade {len(subscribers)} prenumeranter för county ID {county}")

            # Loopa igenom prenumeranter och skicka SMS
            for subscriber in subscribers:
                # Om prenumeranten inte har ett giltigt telefonnummer, skriv ut meddelande och hoppa över
                phone = subscriber['phone_number']

                # Om telefonnumret inte är giltigt, skriv ut meddelande och hoppa över
                try:
                    # Om sucess, skicka SMS med parametrarna to, message
                    success, _ = send_sms(to=phone, message=message, testMode=False)
                    if success:
                        # Om SMS skickas, skriv ut meddelande
                        print(f"SMS skickat till {phone} om händelse {event_id} ({event_type})")
                        # Logga SMS i databasen
                        sms_count += 1
                        sms_sent += 1

                        if sms_sent >= MAX_SMS:
                            print("🛑 Maxgräns för SMS nådd. Avslutar.")
                            return
                        else:
                            try:
                                log_sms(
                                    # Skapa en loggpost för SMS i databasen
                                    newspaper_id=subscriber["newspaper_id"],
                                    subscriber_id=subscriber["id"],
                                    recipient=phone,
                                    message=message
                                )

                                print(f"SMS loggat för subscriber_id={subscriber['id']}, newspaper_id={subscriber['newspaper_id']}")

                            # Om det uppstår ett fel vid loggning, skriv ut meddelande
                            except Exception as e:
                                print(f"Fel vid loggning av SMS för {phone}: {e}")
                            # Lägg till och spara direkt efter lyckat SMS
                            processed_events.append({
                                "id": event_id,
                                "processed_at": datetime.now(timezone.utc).isoformat()
                            })
                            save_processed_events(processed_events)

                            # Vänta en sekund mellan SMS för att undvika överbelastning av API:et
                            time.sleep(10)

                    # Om SMS inte skickas, skriv ut meddelande
                    else:
                        print(f"Misslyckades att skicka SMS till {phone}")
                # Om det uppstår ett fel vid SMS-sändning, skriv ut meddelande
                except Exception as e:
                    print(f"Fel vid SMS-sändning för {phone}: {e}")

    # Jag tar hem det här för att spara tid
    if sms_count > 0:
        print(f"Totalt skickade {sms_count} SMS.")
    else:
        print("Inga SMS skickades.")

    # Om inga nya händelser hittas, skriv ut meddelande och avsluta
    if not new_events_found:
        print("Inga nya händelser hittades för idag.")
    # Rensa gamla händelser och sparar de behandlade händelserna
    processed_events = clean_old_events(processed_events, days_to_keep=30)
    save_processed_events(processed_events)

# Funktion för att skicka notifieringar om prenumerationer som löper ut
def check_expiring_subscriptions():
    expiring = get_subscriptions_due_in_14_days()
    base_url = "https://trafikvida.ddns.net"
    sent_emails = []
    for subscriber in expiring:
        renewal_link = f"{base_url}/subscriptions/renew-subscription?mode=update&user_id={subscriber.user_id}"
        to = subscriber.email
        subject = "Prenumerationspåminnelse"
        message = (
            f"Hej!\n\n"
            f"Din SMS-prenumeration på trafikinformation löper ut om 14 dagar.\n"
            f"Ditt telefonnummer: {subscriber.phone_number}\n"
            f"Ditt län: {subscriber.county}\n"
            f"Förnya din prenumeration här: {renewal_link}\n\n"
            f"Vänliga hälsningar,\nTrafikViDa\n"
        )
        current_app.logger.debug(f"Sending email to {to} with subject: {subject}")
        try:
            send_email(to, subject, message)
            sent_emails.append({
                "email": to,
                "phone_number": subscriber.phone_number,
                "user_id": subscriber.user_id
            })
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {to}: {e}")
    return sent_emails  # Returnera lista över skickade e-postadresser


if __name__ == "__main__":
    notify_accidents()