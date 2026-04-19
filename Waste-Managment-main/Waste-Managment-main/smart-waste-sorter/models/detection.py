from datetime import datetime

class WasteDetection:
    def __init__(self, waste_type, confidence, bin_id=None, image_base64=None, model="gemini-1.5-flash", zone="Industrial Zone", is_contamination=False, session_id=None):
        self.timestamp = datetime.utcnow()
        self.waste_type = waste_type.lower()
        self.confidence_score = float(confidence)
        self.bin_id = bin_id
        self.image_base64 = image_base64
        self.model_used = model
        self.session_id = session_id
        self.location_zone = zone
        self.is_contamination = is_contamination

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "waste_type": self.waste_type,
            "confidence_score": self.confidence_score,
            "bin_id": self.bin_id,
            "image_base64": self.image_base64,
            "model_used": self.model_used,
            "session_id": self.session_id,
            "location_zone": self.location_zone,
            "is_contamination": self.is_contamination
        }
