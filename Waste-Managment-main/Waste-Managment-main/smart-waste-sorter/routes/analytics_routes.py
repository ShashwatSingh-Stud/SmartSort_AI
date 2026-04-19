from flask import Blueprint, jsonify
from services.db_service import db
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/weekly', methods=['GET'])
def get_weekly_analytics():
    # 7-day data
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": start}}},
        {"$group": {
            "_id": {
                "day": {"$dayOfWeek": "$timestamp"},
                "type": "$waste_type"
            },
            "count": {"$sum": 1}
        }}
    ]
    results = list(db.detections.aggregate(pipeline))
    
    # Process into daily lists for Chart.js
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    cats = ["plastic", "paper", "metal", "organic"]
    # Initialize empty format
    data = {cat: [0]*7 for cat in cats}
    
    for r in results:
        day_idx = r["_id"]["day"] - 1 # MongoDB dayOfWeek is 1-7 (Sun-Sat)
        t = r["_id"]["type"]
        if t in data:
            data[t][day_idx] = r["count"]
            
    return jsonify({"labels": days, "datasets": data})

@analytics_bp.route('/distribution', methods=['GET'])
def get_distribution():
    pipeline = [
        {"$group": {"_id": "$waste_type", "count": {"$sum": 1}}}
    ]
    results = list(db.detections.aggregate(pipeline))
    
    total = sum(r["count"] for r in results)
    if total == 0: return jsonify([])
    
    dist = []
    for r in results:
        dist.append({
            "label": r["_id"].capitalize(),
            "pct": round((r["count"]/total)*100, 1),
            "count": r["count"]
        })
    return jsonify(dist)

@analytics_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    # Simplified repeat of overview + extra
    total_items = db.detections.count_documents({})
    most_common = list(db.detections.aggregate([{"$group": {"_id": "$waste_type", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 1}]))
    
    return jsonify({
        "total_all_time": total_items,
        "most_common": most_common[0]["_id"].capitalize() if most_common else "N/A",
        "active_hubs": 6
    })
