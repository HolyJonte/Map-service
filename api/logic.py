
# Importerar funktioner för att hämta data från Trafikverket
from api.fetch_data import fetch_cameras, fetch_situations


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
                    "message": deviation.get("Message", "Inget meddelande"),
                    "location": deviation.get("LocationDescriptor", "Okänd plats"),
                    "severity": deviation.get("SeverityText", "Okänd påverkan"),
                    "start": deviation.get("StartTime"),
                    "end": deviation.get("EndTime")
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

        # Loopa över alla deviation-objekt i situationen
        for deviation in situation.get("Deviation", []):
            if deviation.get("MessageType") != "Olycka":
                continue

            # Hämtar länsnummer (CountyNo) från deviation
            county = deviation.get("CountyNo", None)

            # Om länsnumret inte finns, hoppa över denna deviation
            geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
            if not geom:
                continue
            try:
                # Konverterar strängformatet till latitud och longitud
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())
            # Om det inte går att konvertera, hoppa över denna deviation
            except ValueError:
                continue

            # Lägger till olyckan i listan med nödvändig information
            accidents.append({
                "lat": lat,
                "lng": lng,
                "message": deviation.get("Message", "Ingen beskrivning"),
                "start": deviation.get("StartTime"),
                "end": deviation.get("EndTime"),
                "severity": deviation.get("SeverityText", "Okänd påverkan"),
                "location": deviation.get("LocationDescriptor", "Okänd plats"),
                "county": county
            })
    # Returnerar listan med olyckor
    return accidents