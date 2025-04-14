# Den här koden skapar ett API med Flask:
# /cameras – returnerar en lista med fartkameror från Trafikverket.
# /roadworks – returnerar en lista med vägarbeten från Trafikverket.
# /accidents – returnerar en lista med olyckor från Trafikverket.
# Alla använder funktioner från modulen 'fetch_data' för att hämta aktuell data.
# Informationen formateras och skickas ut i JSON-format till användare (t.ex. en karta).
# ---------------------------------------------

# Importerar nödvändiga moduler
from flask import Blueprint, jsonify
from api.logic import get_all_cameras, get_all_roadworks, get_all_accidents

trafik_bp = Blueprint('api', __name__)

@trafik_bp.route('/cameras')
def get_cameras():
    try:
        return jsonify(get_all_cameras())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trafik_bp.route('/roadworks')
def get_roadworks():
    try:
        return jsonify(get_all_roadworks())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trafik_bp.route('/accidents')
def get_accidents():
    try:
        return jsonify(get_all_accidents())
    except Exception as e:
        return jsonify({"error": str(e)}), 500