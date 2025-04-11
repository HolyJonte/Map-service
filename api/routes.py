# Den här koden skapar ett API med Flask:
# /cameras – returnerar en lista med fartkameror från Trafikverket.
# Båda använder funktioner från modulen 'fetch_data' för att hämta aktuell data.
# Informationen formateras och skickas ut i JSON-format till användare (t.ex. en karta).
# ---------------------------------------------

from flask import Blueprint, jsonify
from datainsamling.fetch_data import fetch_cameras, fetch_roadworks


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
            deviation = situation["Deviation"][0]
            geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")

            if geom:
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())
                message = deviation.get("Message", "Inget meddelande")

                roadworks.append({
                    "lat": lat,
                    "lng": lng,
                    "message": message
                })

        return jsonify(roadworks)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
