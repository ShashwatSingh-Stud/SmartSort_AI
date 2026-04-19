from flask import Blueprint, jsonify, request
from services.db_service import db
from services.gemini_service import ai_service
from bson import ObjectId

cityos_bp = Blueprint('cityos', __name__)

@cityos_bp.route('/surge', methods=['GET'])
def get_surge():
    # Fetch surge predictions from seeder
    predictions = list(db.analytics.find({"type": "surge_prediction"}).sort("date", 1))
    
    forecast = []
    for p in predictions:
        forecast.append({
            "day_name": p["day_name"],
            "risk_level": "High" if p["predicted_kg"] > 1200 else "Medium" if p["predicted_kg"] > 900 else "Low",
            "projected_volume_kg": p["predicted_kg"],
            "event": {"name": p["highlight"].split(" — ")[0], "impact": p["highlight"].split(" — ")[1]} if p.get("highlight") else None
        })
    
    # Fallback for demo if seeder failed
    if not forecast:
        forecast = [
            {"day_name": "Friday", "risk_level": "High", "projected_volume_kg": 1398, "event": {"name": "Music Festival", "impact": "+45%"}},
            {"day_name": "Saturday", "risk_level": "Medium", "projected_volume_kg": 1312, "event": None}
        ]
        
    return jsonify({"forecast": forecast})

@cityos_bp.route('/dna', methods=['GET'])
def get_dna():
    # Fetch most recent zone records from seeder
    record = db.analytics.find_one({"type": {"$ne": "surge_prediction"}}, sort=[("date", -1)])
    
    profiles = []
    if record and "zones" in record:
        for z in record["zones"]:
            # Format breakdown for frontend (capitalize keys)
            sig = {k.capitalize(): v for k, v in z["waste_breakdown"].items()}
            profiles.append({
                "zone": z["zone_name"],
                "signature": sig
            })
    
    if not profiles:
        profiles = [{"zone": "Downtown Core", "signature": {"Plastic": 45, "Paper": 25, "Metal": 10, "Organic": 20}}]
        
    return jsonify({"profiles": profiles})

@cityos_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    # Seeder uses users_greencoins (db.users)
    users = list(db.users.find({}, {"_id": 0}).sort("green_coins", -1).limit(5))
    formatted_users = []
    for i, u in enumerate(users):
        formatted_users.append({
            "rank": u.get("rank", i + 1),
            "name": u["user_name"],
            "greencoins": u["green_coins"]
        })
    
    return jsonify({
        "data": {
            "leaderboard": formatted_users,
            "rewards_available": [
                {"cost": 500, "reward": "Transit Pass"},
                {"cost": 1200, "reward": "Utility Rebate"}
            ]
        }
    })

@cityos_bp.route('/contamination', methods=['GET'])
def get_contamination():
    # Seeder has contamination_logs (db.contamination)
    logs = list(db.contamination.find({}, {"_id": 0}).sort("timestamp", -1).limit(4))
    formatted_logs = []
    for l in logs:
        formatted_logs.append({
            "id": l["error_code"],
            "time": l["timestamp"].strftime("%H:%M"),
            "issue": l["description"],
            "action_taken": l.get("action_taken", "Investigating")
        })
    return jsonify({"logs": formatted_logs})

@cityos_bp.route('/marketplace', methods=['GET'])
def get_marketplace():
    # Frontend expects { "market": { "supply", "demand" } }
    supply = list(db.marketplace.find({"status": "available"}, {"_id": 0}))
    formatted_supply = [{"material": s["material_type"], "quantity": f"{s['quantity_kg']}kg"} for s in supply]
    
    return jsonify({
        "market": {
            "supply": formatted_supply,
            "demand": [
                {"material": "HDPE Plastic", "match_score": "98%"},
                {"material": "Corrugated Cardboard", "match_score": "85%"}
            ]
        }
    })

@cityos_bp.route('/metabolism', methods=['GET'])
def get_metabolism():
    # Calculate pulse from latest analytics
    latest = db.analytics.find_one({"type": {"$ne": "surge_prediction"}}, sort=[("date", -1)])
    kg = latest.get("total_kg", 850) if latest else 850
    pulse = round(kg / 120, 1) # Mock throughput rate kg/min
    
    return jsonify({
        "flow": {
            "pulse_rate_kg_per_min": pulse,
            "nodes": [1,2,3,4,5,6],
            "links": [
                {"source": "Hub Alpha", "target": "MRF Center", "value": int(pulse * 0.4)},
                {"source": "Hub Beta", "target": "MRF Center", "value": int(pulse * 0.3)}
            ]
        }
    })

@cityos_bp.route('/compliance', methods=['GET'])
def get_compliance():
    # Return professional-grade compliance scores
    return jsonify({
        "scores": [
            {"building": "Skyline Residency", "grade": "A+", "score": 96, "trend": "+2%"},
            {"building": "Grand Plaza", "grade": "B", "score": 78, "trend": "-1%"},
            {"building": "Metro Hub", "grade": "A", "score": 91, "trend": "+4%"},
            {"building": "North Gate", "grade": "B+", "score": 88, "trend": "0%"}
        ]
    })

@cityos_bp.route('/inequality', methods=['GET'])
def get_inequality():
    return jsonify({
        "index": [
            {"zone": "Downtown Commercial", "equity_status": "Balanced", "bins_per_10k": 85},
            {"zone": "West Slopes", "equity_status": "Under-served", "bins_per_10k": 22},
            {"zone": "Industrial Park", "equity_status": "Over-served", "bins_per_10k": 110}
        ]
    })

@cityos_bp.route('/simulate', methods=['POST'])
def run_simulation():
    add_bins = request.json.get("add_bins", 10)
    # Mock Monte Carlo result
    return jsonify({
        "simulation": {
            "projected_cost_savings_usd": add_bins * 120,
            "carbon_emissions_change_kg": -(add_bins * 15),
            "overflow_risk_pct": max(5, 45 - (add_bins * 2)),
            "recommendation": "Highly Recommended" if add_bins > 15 else "Marginal Benefit"
        }
    })

@cityos_bp.route('/chat', methods=['POST'])
def ai_chat():
    msg = request.json.get("message")
    # Call Gemini
    resp = ai_service.model.generate_content(f"User is a city waste manager. Question: {msg}. Policy: Be professional and data-driven.")
    return jsonify({"reply": resp.text})
