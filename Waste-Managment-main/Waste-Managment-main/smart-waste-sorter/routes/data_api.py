from flask import Blueprint, jsonify
import json
import os

data_api_bp = Blueprint('data_api', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_DATA_DIR = os.path.join(BASE_DIR, 'mock_data')

def load_json(filename):
    try:
        with open(os.path.join(MOCK_DATA_DIR, filename), 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e), "data": []}

@data_api_bp.route('/zones', methods=['GET'])
def get_zones():
    return jsonify(load_json('zone_summary.json'))

@data_api_bp.route('/analytics', methods=['GET'])
def get_analytics():
    return jsonify(load_json('predictive_analytics.json'))

@data_api_bp.route('/gamification', methods=['GET'])
def get_gamification():
    return jsonify(load_json('gamification_users.json'))

@data_api_bp.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(load_json('collection_logs.json'))

@data_api_bp.route('/bins', methods=['GET'])
def get_bins():
    return jsonify(load_json('smart_bins.json'))
