from flask import Blueprint, jsonify, request
from services.db_service import db
from bson import ObjectId

history_bp = Blueprint('history', __name__)

@history_bp.route('/', methods=['GET'])
def get_history():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    skip = (page - 1) * limit
    
    # Use db.history (seeded events) instead of raw detections for "Past Data"
    items = list(db.history.find({}, {"_id": 1, "serial": 1, "timestamp": 1, "waste_type": 1, "confidence": 1, "zone": 1, "action": 1})
                 .sort("timestamp", -1).skip(skip).limit(limit))
    
    for item in items: 
        item["_id"] = str(item["_id"])
        # Map seeder field name to what frontend expects if needed
        item["confidence_score"] = item.get("confidence", 0)
    
    return jsonify(items)

@history_bp.route('/filter', methods=['GET'])
def filter_history():
    t = request.args.get('type')
    query = {}
    if t: query["waste_type"] = t.lower()
    
    items = list(db.history.find(query, {"_id": 1, "serial": 1, "timestamp": 1, "waste_type": 1, "confidence": 1, "zone": 1, "action": 1})
                 .sort("timestamp", -1).limit(50))
    for item in items: 
        item["_id"] = str(item["_id"])
        item["confidence_score"] = item.get("confidence", 0)
    return jsonify(items)

@history_bp.route('/<id>', methods=['DELETE'])
def delete_record(id):
    db.detections.delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})
