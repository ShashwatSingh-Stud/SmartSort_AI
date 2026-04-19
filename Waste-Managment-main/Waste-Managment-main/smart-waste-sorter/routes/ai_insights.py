from flask import Blueprint, jsonify
from services.db_service import db
from services.gemini_service import ai_service
from datetime import datetime

ai_insights_bp = Blueprint('ai_insights', __name__)

@ai_insights_bp.route('/generate', methods=['GET'])
def generate_insights():
    # 1. Check Cache
    cached = db.insights.find_one({}).sort("generated_at", -1)
    if cached:
        return jsonify(cached["data"])

    # 2. Get Data for AI (last 50)
    history = list(db.detections.find({}, {"_id": 0, "image_base64": 0}).sort("timestamp", -1).limit(50))
    
    # 3. Request Gemini
    insights_data = ai_service.get_ai_insights(history)
    
    if insights_data:
        # Cache results
        db.insights.insert_one({
            "generated_at": datetime.utcnow(),
            "data": insights_data
        })
        return jsonify(insights_data)
    
    return jsonify({"error": "Failed to generate AI insights"}), 500

@ai_insights_bp.route('/tips/<category>', methods=['GET'])
def get_category_tips(category):
    cat = category.lower()
    
    # Professional Mock Tips fallback
    mock_tips = {
        "plastic": {
            "biodegradable": False,
            "tips": [
                "Always remove caps and rings from PET bottles; they are often made of different, non-recyclable plastic.",
                "Rinse containers thoroughly. Even a small amount of food residue can contaminate an entire recycling batch.",
                "Check for the resin identification code (1-7). Most curbside programs only accept 1 and 2."
            ]
        },
        "paper": {
            "biodegradable": True,
            "tips": [
                "Shredded paper is often too small for sorting machines; check if your local MRF accepts it in bags.",
                "Avoid recycling pizza boxes with grease stains; oil prevents the paper fibers from binding during pulping.",
                "Glossy magazines are recyclable, but remove any plastic wrapping or attached CD samples first."
            ]
        },
        "metal": {
            "biodegradable": False,
            "tips": [
                "Aluminum cans are infinitely recyclable. One recycled can saves enough energy to power a TV for 3 hours.",
                "Empty aerosol cans are recyclable in many areas if they are completely depressurized.",
                "Don't worry about removing labels from tin cans; they are burned off during the smelting process."
            ]
        },
        "organic": {
            "biodegradable": True,
            "tips": [
                "Never put 'biodegradable' plastic bags in organic bins unless they are specifically certified for industrial composting.",
                "Avoid adding large amounts of meat or dairy to home compost piles as they attract pests.",
                "Eggshells and coffee grounds are excellent nitrogen sources for your organic waste recycling."
            ]
        }
    }
    
    data = mock_tips.get(cat, {"biodegradable": False, "tips": ["Always check local guidelines for unknown materials."]})
    return jsonify(data)

