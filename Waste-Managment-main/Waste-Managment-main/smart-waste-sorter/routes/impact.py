from flask import Blueprint, jsonify
from services.db_service import db
from config import Config

impact_bp = Blueprint('impact', __name__)

@impact_bp.route('/stats', methods=['GET'])
def get_impact_stats():
    # Fetch pre-calculated impact document from seeder
    impact_doc = db.impact.find_one({}, sort=[("generated_at", -1)])
    
    if impact_doc:
        # Format for frontend
        return jsonify({
            "total_co2_saved": impact_doc.get("co2_saved_kg", 0),
            "trees_equivalent": impact_doc.get("trees_equivalent", 0),
            "items_recycled": impact_doc.get("total_items_recycled", 0),
            "contamination_rate": impact_doc.get("contamination_rate_pct", 0),
            "monthly_trend": impact_doc.get("monthly_trend", []),
            "per_zone": impact_doc.get("per_zone_impact", [])
        })
    
    # Fallback if seeder hasn't run
    return jsonify({
        "total_co2_saved": 0,
        "trees_equivalent": 0,
        "items_recycled": 0,
        "contamination_rate": 0
    })
