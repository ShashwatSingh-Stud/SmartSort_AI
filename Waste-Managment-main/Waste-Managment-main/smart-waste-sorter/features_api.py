from flask import Blueprint, jsonify, request
from features_engine import features_engine

features_bp = Blueprint("features", __name__, url_prefix="/api/features")

@features_bp.route("/predictive_surge", methods=["GET"])
def predictive_surge():
    return jsonify({"ok": True, "forecast": features_engine.get_predictive_surge()})

@features_bp.route("/waste_dna", methods=["GET"])
def waste_dna():
    return jsonify({"ok": True, "profiles": features_engine.get_waste_dna()})

@features_bp.route("/gamification", methods=["GET"])
def gamification():
    return jsonify({"ok": True, "data": features_engine.get_gamification()})

@features_bp.route("/chat", methods=["POST"])
def chat():
    # In a real app we'd pass this to Gemini. For prototype, if Gemini fails we use a mock.
    data = request.json or {}
    message = data.get("message", "")
    prompt = features_engine.generate_chat_prompt(message)
    # The actual Gemini call will be intercepted in app.py if needed, or we just mock it currently
    mock_reply = "Please place recyclables in the Blue bin. Sorting properly helps reduce landfill mass and saves energy."
    return jsonify({"ok": True, "reply": mock_reply, "prompt_used": prompt})

@features_bp.route("/contamination", methods=["GET"])
def contamination():
    return jsonify({"ok": True, "logs": features_engine.get_contamination_logs()})

@features_bp.route("/marketplace", methods=["GET"])
def marketplace():
    return jsonify({"ok": True, "market": features_engine.get_marketplace()})

@features_bp.route("/metabolism", methods=["GET"])
def metabolism():
    return jsonify({"ok": True, "flow": features_engine.get_city_metabolism()})

@features_bp.route("/compliance", methods=["GET"])
def compliance():
    return jsonify({"ok": True, "scores": features_engine.get_compliance_scores()})

@features_bp.route("/simulate", methods=["POST"])
def simulate():
    params = request.json or {}
    return jsonify({"ok": True, "simulation": features_engine.simulate_scenario(params)})

@features_bp.route("/inequality", methods=["GET"])
def inequality():
    return jsonify({"ok": True, "index": features_engine.get_inequality_index()})
