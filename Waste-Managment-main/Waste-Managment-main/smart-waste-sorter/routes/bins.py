from flask import Blueprint, jsonify, request
from services.db_service import db
from datetime import datetime

bins_bp = Blueprint('bins', __name__)

@bins_bp.route('/all', methods=['GET'])
def get_all_bins():
    bins = list(db.bins.find({}, {"_id": 0}))
    return jsonify(bins)

@bins_bp.route('/stats', methods=['GET'])
def get_bin_stats():
    total = db.bins.count_documents({})
    full = db.bins.count_documents({"fill_percentage": {"$gte": 90}})
    avg = list(db.bins.aggregate([{"$group": {"_id": None, "avg": {"$avg": "$fill_percentage"}}}]))
    
    return jsonify({
        "total_bins": total,
        "full_bins": full,
        "avg_fill": round(avg[0]["avg"], 1) if avg else 0,
        "network_status": "Optimal"
    })

@bins_bp.route('/<bin_id>/fill', methods=['PUT'])
def update_bin_fill(bin_id):
    fill = request.json.get("fill_percentage")
    if fill is None: return jsonify({"ok": False, "error": "Missing fill_percentage"}), 400
    
    db.bins.update_one(
        {"bin_id": bin_id},
        {"$set": {"fill_percentage": float(fill), "last_updated": datetime.utcnow()}}
    )
    return jsonify({"ok": True})
