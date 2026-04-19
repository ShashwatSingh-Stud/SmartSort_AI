from flask import Blueprint, jsonify
from services.db_service import db
from datetime import datetime, timedelta

overview_bp = Blueprint('overview', __name__)

@overview_bp.route('/stats', methods=['GET'])
def get_overview_stats():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Aggregates from detections
    items_today = db.detections.count_documents({"timestamp": {"$gte": today}})
    total_items = db.detections.count_documents({})
    
    # Most common waste type today
    pipeline = [
        {"$match": {"timestamp": {"$gte": today}}},
        {"$group": {"_id": "$waste_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    common_result = list(db.detections.aggregate(pipeline))
    most_common = common_result[0]["_id"] if common_result else "none"

    return jsonify({
        "items_today": items_today,
        "total_items": total_items,
        "most_common_waste": most_common.capitalize(),
        "peak_hour": "14:00"  # Mock current logic for peak
    })

@overview_bp.route('/bins', methods=['GET'])
def get_overview_bins():
    bins = list(db.bins.find({}, {"_id": 0}))
    return jsonify(bins)
