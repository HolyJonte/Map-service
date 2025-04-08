from flask import Blueprint, jsonify
from datainsamling.fetch_data import get_mocked_camera_data  # exempel

trafik_bp = Blueprint('trafik', __name__)

@trafik_bp.route("/cameras")
def cameras():
    data = get_mocked_camera_data()
    return jsonify(data)