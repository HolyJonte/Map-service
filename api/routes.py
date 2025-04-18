# Denna modul innehåller API-rutter för att hämta trafikdata från Trafikverket.

# Importerar nödvändiga moduler
from flask import Blueprint, jsonify
from api.logic import get_all_cameras, get_all_roadworks, get_all_accidents

# Skapar en Blueprint för att definiera API-rutter som kan användas i Flask-applikationen
trafik_bp = Blueprint('api', __name__)

# ==============================================================================
# Route för att hämta fartkameror
# ==============================================================================
@trafik_bp.route('/cameras')
def get_cameras():
    try:
        return jsonify(get_all_cameras())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================================================
# Route för att hämta vägarbeten
# ==============================================================================
@trafik_bp.route('/roadworks')
def get_roadworks():
    try:
        return jsonify(get_all_roadworks())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================================================
# Route för att hämta trafikolyckor
# ==============================================================================
@trafik_bp.route('/accidents')
def get_accidents():
    try:
        return jsonify(get_all_accidents())
    except Exception as e:
        return jsonify({"error": str(e)}), 500