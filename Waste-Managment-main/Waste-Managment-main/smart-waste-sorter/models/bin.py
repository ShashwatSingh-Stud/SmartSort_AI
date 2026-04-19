from datetime import datetime

class SmartBin:
    def __init__(self, bin_id, name, waste_type, location=None, zone="Industrial Zone"):
        self.bin_id = bin_id
        self.name = name
        self.waste_type = waste_type.lower()
        self.location = location or {"lat": 18.52, "lng": 73.85}
        self.zone_name = zone
        self.fill_percentage = 0
        self.total_items_collected = 0
        self.status = "active"
        self.last_updated = datetime.utcnow()

    def to_dict(self):
        return {
            "bin_id": self.bin_id,
            "name": self.name,
            "waste_type": self.waste_type,
            "location": self.location,
            "zone_name": self.zone_name,
            "fill_percentage": self.fill_percentage,
            "total_items_collected": self.total_items_collected,
            "status": self.status,
            "last_updated": self.last_updated
        }
