# Den här koden skapar ett API med Flask:
# /cameras – returnerar en lista med fartkameror från Trafikverket.
# /roadworks – returnerar en lista med vägarbeten från Trafikverket.
# /accidents – returnerar en lista med olyckor från Trafikverket.
# Alla använder funktioner från modulen 'fetch_data' för att hämta aktuell data.
# Informationen formateras och skickas ut i JSON-format till användare (t.ex. en karta).
# ---------------------------------------------

# Importerar nödvändiga moduler
from flask import Blueprint, jsonify
#Importerar funktioner för att hämta data från Trafikverket
from datainsamling.fetch_data import fetch_cameras, fetch_situations

# Skapar en "Blueprint" för API-rutter som kan kopplas till Flask-appen
trafik_bp = Blueprint('api', __name__)


#==================================================================================================
# Route för att visa fartkameror
#==================================================================================================

@trafik_bp.route('/cameras')
def get_cameras():
    try:
        # Hämtar fartkameradata från Trafikverket
        data = fetch_cameras()
        # Lista för alla kameror
        cameras = []

        # Går igenom varje kamera i datan
        for cam in data["RESPONSE"]["RESULT"][0]["TrafficSafetyCamera"]:
            # Kontrollerar att kameran har position
            if "Geometry" in cam and cam["Geometry"]:
                # Hämtar koordinaterna för kameran
                geom = cam["Geometry"]["WGS84"]
                # Omvandlar sträng till lat/lng-float
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())

                # Lägger till kamerainformation i listan
                cameras.append({
                    "lat": lat,
                    "lng": lng,
                    "name": cam.get("Name", "Okänd kamera"),
                    "road": cam.get("RoadNumber", "Okänt vägnummer")
                })

        # Skickar tillbaka kamerorna i JSON-format
        return jsonify(cameras)

    # Om något går fel, returnera ett felmeddelande
    except Exception as e:
        return jsonify({"error": str(e)}), 500




#==================================================================================================
# Route för att visa vägarbeten
#==================================================================================================

@trafik_bp.route('/roadworks')
def get_roadworks():
    try:
        # Hämtar trafiksituationer från Trafikverket
        data = fetch_situations()
        # Lista för vägarbeten
        roadworks = []


        for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
            # Går igenom alla avvikelser i situationen
            for deviation in situation.get("Deviation", []):
                if deviation.get("MessageType") != "Vägarbete":
                    # Hoppa över allt som inte är vägarbete
                    continue

                # Hämtar geometrin för vägarbetet
                geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
                if geom:
                    # Omvandlar strängen till lat/lng-float
                    lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())

                    # Lägger till vägarbetets information i listan
                    roadworks.append({
                        "lat": lat,
                        "lng": lng,
                        "message": deviation.get("Message", "Inget meddelande"),
                        "location": deviation.get("LocationDescriptor", "Okänd plats"),
                        "severity": deviation.get("SeverityText", "Okänd påverkan"),
                        "start": deviation.get("StartTime"),
                        "end": deviation.get("EndTime")
                    })

        # Returnerar listan med vägarbeten som JSON
        return jsonify(roadworks)

    # Om något går fel, returnera ett felmeddelande
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#==================================================================================================
# Route för att visa olyckor
#==================================================================================================

@trafik_bp.route('/accidents')
def get_accidents():
    try:
        # Hämtar trafiksituationer från Trafikverket
        data = fetch_situations()
        # Lista för olyckor
        accidents = []

        for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
            # Går igenom alla avvikelser i situationen
            for deviation in situation.get("Deviation", []):
                if deviation.get("MessageType") != "Olycka":
                    # Hoppa över allt som inte är olycka
                    continue

                # Hämtar geometrin för olyckan
                geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
                if geom:
                    # Omvandlar strängen till lat/lng-float
                    lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())

                    # Lägger till olyckans information i listan
                    accidents.append({
                        "lat": lat,
                        "lng": lng,
                        "message": deviation.get("Message", "Ingen beskrivning"),
                        "start": deviation.get("StartTime"),
                        "end": deviation.get("EndTime"),
                        "severity": deviation.get("SeverityText", "Okänd påverkan"),
                        "location": deviation.get("LocationDescriptor", "Okänd plats")
                    })

        # Returnerar listan med olyckor som JSON
        return jsonify(accidents)

    # Om något går fel, returnera ett felmeddelande
    except Exception as e:
        return jsonify({"error": str(e)}), 500


