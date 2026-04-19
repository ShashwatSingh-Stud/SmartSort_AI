from datetime import datetime

class WasteMarketplaceItem:
    def __init__(self, material_type, quantity_kg, location, contact="admin@smartsort.ai"):
        self.material_type = material_type.lower()
        self.quantity_kg = float(quantity_kg)
        self.status = "available"
        self.listed_date = datetime.utcnow()
        self.location = location
        self.contact_info = contact

    def to_dict(self):
        return {
            "material_type": self.material_type,
            "quantity_kg": self.quantity_kg,
            "status": self.status,
            "listed_date": self.listed_date,
            "location": self.location,
            "contact_info": self.contact_info
        }
