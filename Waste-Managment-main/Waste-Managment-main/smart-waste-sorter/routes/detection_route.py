from flask import Blueprint, request, jsonify
from services.gemini_service import ai_service
from services.db_service import db
from models.detection import WasteDetection
from models.contamination import ContaminationLog
import time

detection_route_bp = Blueprint('detection_route', __name__)

@detection_route_bp.route('/', methods=['POST'])
def process_detection():
    data = request.json
    base64_img = data.get("image")
    if not base64_img:
        return jsonify({"ok": False, "error": "No image data"}), 400

    # 1. AI Classification
    ai_resp = ai_service.classify_waste(base64_img)
    if not ai_resp["ok"]:
        return jsonify(ai_resp), 500

    # 2. Save Detection
    detection = WasteDetection(
        waste_type=ai_resp["category"],
        confidence=ai_resp["confidence"],
        image_base64=base64_img,
        model="gemini-1.5-flash",
        is_contamination=ai_resp["is_contamination"]
    )
    db.detections.insert_one(detection.to_dict())

    # 3. Update Bin
    bin_doc = db.get_bin(ai_resp["category"])
    if bin_doc:
        db.update_bin_stats(bin_doc["bin_id"])
    
    # 4. Handle Contamination
    if ai_resp["is_contamination"]:
        log = ContaminationLog(
            error_code="SORT_ERR_01",
            description=ai_resp["contamination_reason"] or "Auto-detected sorting error",
            bin_id=bin_doc["bin_id"] if bin_doc else "unknown",
            severity="high"
        )
        db.contamination.insert_one(log.to_dict())

    return jsonify({
        "ok": True,
        "prediction": {
            "category": ai_resp["category"],
            "confidence": ai_resp["confidence"],
            "ts": time.time()
        }
    })
