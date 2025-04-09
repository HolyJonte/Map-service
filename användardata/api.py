from flask import Blueprint, jsonify
from datainsamling.fetch_data import fetch_accidents, fetch_cameras

trafik_bp = Blueprint('api', __name__)

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


@trafik_bp.route('/cameras')
def get_cameras():
    try:
        data = fetch_cameras()
        cameras = []

        for cam in data["RESPONSE"]["RESULT"][0]["TrafficSafetyCamera"]:
            if "Geometry" in cam and cam["Geometry"]:
                geom = cam["Geometry"]["WGS84"]
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())

                cameras.append({
                    "lat": lat,
                    "lng": lng,
                    "name": cam.get("Name", "Okänd kamera"),
                    "active": cam.get("Active", False)
                })

        return jsonify(cameras)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
