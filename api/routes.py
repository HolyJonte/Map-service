# Den här koden skapar ett API med Flask:
# /cameras – returnerar en lista med fartkameror från Trafikverket.
# Båda använder funktioner från modulen 'fetch_data' för att hämta aktuell data.
# Informationen formateras och skickas ut i JSON-format till användare (t.ex. en karta).
# ---------------------------------------------

from flask import Blueprint, jsonify
from datainsamling.fetch_data import fetch_accidents, fetch_cameras, fetch_roadworks


# Skapar en "Blueprint" för API-rutter som kan kopplas till Flask-appen
trafik_bp = Blueprint('api', __name__)



# Route för att visa fartkameror
@trafik_bp.route('/cameras')
def get_cameras():
    try:
        data = fetch_cameras() # Hämtar fartkameradata från Trafikverket
        cameras = [] # Lista för alla kameror

        # Går igenom varje kamera i datan
        for cam in data["RESPONSE"]["RESULT"][0]["TrafficSafetyCamera"]:
            # Kontrollerar att kameran har position
            if "Geometry" in cam and cam["Geometry"]:
                geom = cam["Geometry"]["WGS84"]
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())

                # Lägger till kamerainformation i listan
                cameras.append({
                    "lat": lat,
                    "lng": lng,
                    "name": cam.get("Name", "Okänd kamera"),
                    "road": cam.get("RoadNumber", "Okänt vägnummer")
                })

        return jsonify(cameras) # Skickar tillbaka kamerorna i JSON-format

    # Om något går fel, returnera ett felmeddelande
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# Route för att visa vägarbeten
@trafik_bp.route('/roadworks')
def get_roadworks():
    try:
        data = fetch_roadworks()
        roadworks = []

        for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
            if "Geometry" in situation and situation["Geometry"]:
                geom = situation["Geometry"].get("WGS84")
                if geom:
                    lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())

                    deviation = situation.get("Deviation", [{}])[0]  # säkert sätt att hämta första objektet

                    roadworks.append({
                        "lat": lat,
                        "lng": lng,
                        "road": situation.get("RoadNumber", "Okänt vägnummer"),
                        "description": situation.get("Message", "Ingen beskrivning"),
                        "location": situation.get("LocationDescriptor", "Okänd plats"),
                        "severity": situation.get("SeverityText", "Okänd påverkan"),
                        "restrictions": [
                            deviation.get("TrafficRestrictionType", "Ingen information"),
                            deviation.get("TemporaryLimit", "Inga begränsningar"),
                            deviation.get("AffectedDirection", "Okänd riktning")
                        ],
                        "start": situation.get("StartTime"),
                        "end": situation.get("EndTime")
                    })

        return jsonify(roadworks)

    except Exception as e:
        return jsonify({"error": str(e)}), 500






"""
@trafik_bp.route('/api/olyckor')
def get_olyckor():
    try:
        data = fetch_accidents()
        accidents = []

        for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
            if "Geometry" in situation and situation["Geometry"]:
                geom = situation["Geometry"]["WGS84"]
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())

                accidents.append({
                    "lat": lat,
                    "lng": lng,
                    "location": situation.get("LocationDescriptor", "Okänd plats"),
                    "description": situation.get("Description", "Ingen beskrivning"),
                    "road": situation.get("Deviation", [{}])[0].get("LocationText", "Okänd väg"),
                    "impact": situation.get("Deviation", [{}])[0].get("Message", "Okänd påverkan")
                })

        return jsonify(accidents)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""