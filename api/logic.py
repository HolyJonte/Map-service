# Denna modul innehåller funktioner för att bearbeta data från Trafikverkets API.

# Importerar funktioner för att hämta data från Trafikverket
from api.fetch_data import fetch_cameras, fetch_situations
from datetime import datetime, timezone, timedelta
import threading

import sys
import os

# För att kunna testa när vi kör filen enskilt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



#===========================================================================================================
# Hämtar och returnerar fartkameror
#===========================================================================================================

def get_all_cameras():
    # Hämtar JSON-data från Trafikverket
    data = fetch_cameras()
    # Lista för att lagra kameror
    cameras = []

    # Loopar genom varje kamera i datan
    for cam in data["RESPONSE"]["RESULT"][0]["TrafficSafetyCamera"]:
        # Kontrollerar att kameran har en geometri (lat/lng)
        if "Geometry" in cam and cam["Geometry"]:
            # Hämta latitud och longitud från geometrin
            geom = cam["Geometry"]["WGS84"]
            # Konverterar strängformatet till latitud och longitud
            lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())

            # Lägger till kameran i listan med nödvändig information
            cameras.append({
                "lat": lat,
                "lng": lng,
                "name": cam.get("Name", "Okänd kamera"),
                "road": cam.get("RoadNumber", "Okänt vägnummer")
            })
    # Returnerar listan med kameror
    return cameras


#===========================================================================================================
# Hämtar och returnerar vägarbeten
#===========================================================================================================

def get_all_roadworks():
    # Hämtar JSON-data från Trafikverket
    data = fetch_situations()
    # Lista för att lagra vägarbeten
    roadworks = []

    # Loopar genom varje situation i datan
    for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
        # Varje sitation kan ha flera "Deviation"-objekt
        for deviation in situation.get("Deviation", []):
            # Filtrerar för att endast få vägarbeten
            if deviation.get("MessageType") != "Vägarbete":
                continue
            # Hämta geometrin (lat/lng) från deviation
            geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
            # Konverterar strängformatet till latitud och longitud
            if geom:
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())
                # Lägger till vägarbetet i listan med nödvändig information
                roadworks.append({
                    "lat": lat,
                    "lng": lng,
                    "id": deviation.get("Id", "Inget id"),
                    "message": deviation.get("Message", "Inget meddelande"),
                    "location": deviation.get("LocationDescriptor", "Okänd plats"),
                    "county": deviation.get("CountyNo", None),
                    "severity": deviation.get("SeverityText", "Okänd påverkan"),
                    "start": deviation.get("StartTime"),
                    "end": deviation.get("EndTime"),
                    "link": deviation.get("WebLink", "Läs mer om trafikläget på: https://www.trafikverket.se/trafikinformation/vag/?map_x=650778.00005&map_y=7200000&map_z=2&map_l=101000000000000")
                })
    # Returnerar listan med vägarbeten
    return roadworks


#===========================================================================================================
# Hämtar och returnerar olyckor
#===========================================================================================================


def get_all_accidents():
    # Hämtar JSON-data från Trafikverket
    data = fetch_situations()
    # Lista för att lagra olyckor
    accidents = []

    # Loopar genom varje situation i datan
    for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
        # Varje situation kan ha flera "Deviation"-objekt
        for deviation in situation.get("Deviation", []):
            # Filtrerar för att endast få olyckor
            if deviation.get("MessageType") != "Olycka":
                continue

            # Hämta geometrin (lat/lng) från deviation
            geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
            if not geom:
                continue

            # Försöker konvertera strängformatet till latitud och longitud
            try:
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())
            except ValueError:
                continue

            # Tidsfilter: Ta bara med olyckor som inte har passerat sluttiden
            end_time_str = deviation.get("EndTime")
            if end_time_str:
                try:
                    end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                    if end_time < datetime.now(timezone.utc):
                        continue  # Skippar om olyckan är gammal
                except Exception:
                    pass  # Fortsätter om datum inte kunde tolkas

            # Lägger till olyckan i listan med nödvändig information
            accidents.append({
                "lat": lat,
                "lng": lng,
                "id": deviation.get("Id", "Inget id"),
                "message": deviation.get("Message", "Ingen beskrivning"),
                "start": deviation.get("StartTime"),
                "end": deviation.get("EndTime"),
                "severity": deviation.get("SeverityText", "Okänd påverkan"),
                "location": deviation.get("LocationDescriptor", "Okänd plats"),
                "county": deviation.get("CountyNo", None),
                "link": deviation.get("WebLink", "Läs mer om trafikläget på: https://www.trafikverket.se/trafikinformation/vag/?map_x=650778.00005&map_y=7200000&map_z=2&map_l=101000000000000")
            })

    return accidents

#===========================================================================================================
# Hämtar alla kameror, vägarbeten och olyckor från Trafikverket och lagrar dem i en cache
#===========================================================================================================

# Cache för att lagra kameror, vägarbeten och olyckor
cache = {
    "active": {
        "cameras": [],
        "roadworks": [],
        "accidents": [],
        "last_updated": None
    },
    # Förhindrar flera samtidiga uppdateringar
    "updating": False
}

# Funktion för att uppdatera cachen med ny data
def update_cache():
    # Undvik parallella uppdateringar
    if cache["updating"]:
        return

# Om en uppdatering redan pågår, vänta tills den är klar
    cache["updating"] = True
    try:
        # Hämta ny data
        new_cameras = get_all_cameras()
        new_roadworks = get_all_roadworks()
        new_accidents = get_all_accidents()
        # Byt ut "active" bara när all ny data är redo
        cache["active"] = {
            "cameras": new_cameras,
            "roadworks": new_roadworks,
            "accidents": new_accidents,
            "last_updated": datetime.now()
        }

    # Skriv ut loggmeddelande
    finally:
        cache["updating"] = False

# Funktion för att hämta kameror, vägarbeten och olyckor från cachen
def get_cached_cameras():
    # Om cachen inte har uppdaterats på mer än 60 sekunder, starta en ny tråd för att uppdatera den
    if not cache["active"]["last_updated"] or datetime.now() - cache["active"]["last_updated"] > timedelta(seconds=60):
        # Starta en ny tråd för att uppdatera cachen
        threading.Thread(target=update_cache).start()
    # Om cachen har uppdaterats nyligen, returnera den cachade datan
    return cache["active"]["cameras"]

# Funktion för att hämta vägarbeten och olyckor från cachen
def get_cached_roadworks():
    get_cached_cameras()
    return cache["active"]["roadworks"]

# Funktion för att hämta olyckor från cachen
def get_cached_accidents():
    get_cached_cameras()
    return cache["active"]["accidents"]

# Funktion för att hämta senaste uppdateringstid från cachen
def preload_cache():
    # Kör detta om sidan körs på PythonAnywhere
    if "PYTHONANYWHERE_DOMAIN" in os.environ:
        update_cache()

    # Kör detta om sidan körs lokalt (så att det går snabbare att testa sidan)
    else:
        threading.Thread(target=update_cache).start()

# Kör preload_cache() när sidan laddas (alltså direkt man startar servern på PythonAnywhere)
preload_cache()

