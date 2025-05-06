# Denna modul styr rutter för hemsidan för data hämtat från Trafikverkets api.

# Importerar nödvändiga moduler
from flask import Blueprint, jsonify
from api.logic import get_cached_cameras, get_cached_roadworks, get_cached_accidents

# Skapar en Blueprint för att definiera API-rutter som kan användas i Flask-applikationen
trafik_bp = Blueprint('api', __name__)

# ==============================================================================
# Route för att hämta fartkameror
# ==============================================================================
@trafik_bp.route('/cameras')
def get_cameras():
    try:
        return jsonify(get_cached_cameras())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================================================
# Route för att hämta vägarbeten
# ==============================================================================
@trafik_bp.route('/roadworks')
def get_roadworks():
    try:
        return jsonify(get_cached_roadworks())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================================================================
# Route för att hämta trafikolyckor
# ==============================================================================
@trafik_bp.route('/accidents')
def get_accidents():
    try:
        return jsonify(get_cached_accidents())
    except Exception as e:
        return jsonify({"error": str(e)}), 500