# Denna modul innehåller funktioner för att hämta och bearbeta data från Trafikverkets API.

# Importerar funktioner för att hämta data från Trafikverket
from api.fetch_data import fetch_cameras, fetch_situations
from datetime import datetime, timezone
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

    for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
        for deviation in situation.get("Deviation", []):
            if deviation.get("MessageType") != "Olycka":
                continue
            print("Deviation data:", deviation)

            geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
            if not geom:
                continue

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

