from flask import Blueprint, jsonify
from datainsamling.fetch_data import fetch_cameras

trafik_bp = Blueprint('trafik', __name__)

@trafik_bp.route("/cameras")
def cameras():
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
