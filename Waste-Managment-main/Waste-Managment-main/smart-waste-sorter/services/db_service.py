import random
from pymongo import MongoClient
from datetime import datetime
import sys
from config import Config

class MockCollection:
    def __init__(self, data=None):
        self.data = data or []
    def _filter(self, query):
        if not query: return self.data
        filtered = self.data
        for k, v in query.items():
            if isinstance(v, dict): # Handle basic $ne, $in etc if needed, but keeping it simple
                if "$ne" in v: filtered = [d for d in filtered if d.get(k) != v["$ne"]]
                continue
            filtered = [d for d in filtered if d.get(k) == v]
        return filtered
    def find(self, query=None, projection=None): 
        return MockCollection(self._filter(query))
    def sort(self, key, direction=-1):
        try: self.data.sort(key=lambda x: x.get(key), reverse=(direction == -1))
        except: pass
        return self
    def skip(self, n): 
        self.data = self.data[n:]
        return self
    def limit(self, n): 
        self.data = self.data[:n]
        return self
    def to_list(self, length=None): return self.data[:length] if length else self.data
    def find_one(self, query=None, sort=None): 
        d = self._filter(query)
        if d: return d[0]
        return None
    def count_documents(self, query): return len(self._filter(query))
    def update_one(self, query, update, upsert=False): return None
    def delete_one(self, query): return None
    def insert_one(self, doc): return None
    def insert_many(self, docs): return None
    def create_index(self, keys, **kwargs): return None
    def __iter__(self): return iter(self.data)

class DBService:
    def __init__(self):
        try:
            self.client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
            self.client.admin.command('ping')
            self.db = self.client.get_database()
            self.detections = self.db.waste_detections
            self.bins = self.db.smart_bins
            self.users = self.db.users_greencoins
            self.contamination = self.db.contamination_logs
            self.marketplace = self.db.waste_marketplace
            self.analytics = self.db.city_analytics
            self.insights = self.db.ai_insights_cache
            self.impact = self.db.impact_stats
            self.history = self.db.history_events
            self.report = self.db.report_summary
        except Exception as e:
            print(f"MongoDB connection failed: {e}. Switching to Jury-Ready Mock Mode.")
            self.detections = MockCollection([{"waste_type": "plastic", "timestamp": datetime.utcnow()}] * 160)
            self.bins = MockCollection([
                {"bin_id": "B-001", "name": "Nexus Hub 1", "zone": "Downtown", "fill_percentage": 68, "waste_type": "plastic"},
                {"bin_id": "B-002", "name": "Nexus Hub 2", "zone": "Industrial", "fill_percentage": 42, "waste_type": "metal"},
                {"bin_id": "B-003", "name": "Green Bin 1", "zone": "Park Area", "fill_percentage": 15, "waste_type": "organic"},
                {"bin_id": "B-004", "name": "Eco Bin A", "zone": "Residential", "fill_percentage": 89, "waste_type": "paper"},
                {"bin_id": "B-005", "name": "Metro Center", "zone": "Downtown", "fill_percentage": 30, "waste_type": "plastic"},
                {"bin_id": "B-006", "name": "North Gate", "zone": "Industrial", "fill_percentage": 55, "waste_type": "metal"},
            ])
            self.users = MockCollection([
                {"user_name": "EcoWarrior_99", "green_coins": 4250, "rank": 1},
                {"user_name": "GreenMatrix", "green_coins": 3800, "rank": 2},
                {"user_name": "WasteNinja", "green_coins": 3100, "rank": 3},
                {"user_name": "SustainBot", "green_coins": 2950, "rank": 4},
                {"user_name": "RecyclePro", "green_coins": 2700, "rank": 5}
            ])
            self.contamination = MockCollection([
                {"error_code": "C-409", "timestamp": datetime.utcnow(), "description": "Metal detected in Organic bin", "action_taken": "Automated Alert Sent"},
                {"error_code": "C-412", "timestamp": datetime.utcnow(), "description": "Lid sensor failure", "action_taken": "Maintenance Scheduled"}
            ])
            self.marketplace = MockCollection([
                {"material_type": "Recycled HDPE", "quantity_kg": 1250, "status": "available"},
                {"material_type": "Clear PET Flakes", "quantity_kg": 800, "status": "available"},
                {"material_type": "Mixed Paper Bale", "quantity_kg": 2100, "status": "available"}
            ])
            self.analytics = MockCollection([
                {"type": "surge_prediction", "day_name": "Friday", "predicted_kg": 1450, "highlight": "Local Festival — +15%"},
                {"type": "surge_prediction", "day_name": "Saturday", "predicted_kg": 1380, "highlight": "Bulk Collection — +40%"},
                {"type": "daily", "total_kg": 980, "date": datetime.utcnow(), "zones": [
                    {"zone_name": "Downtown Core", "waste_breakdown": {"plastic": 45, "paper": 25, "metal": 10, "organic": 20}},
                    {"zone_name": "Industrial North", "waste_breakdown": {"plastic": 15, "paper": 10, "metal": 70, "organic": 5}},
                    {"zone_name": "Green Valley", "waste_breakdown": {"plastic": 20, "paper": 30, "metal": 5, "organic": 45}}
                ]}
            ])
            self.insights = MockCollection([{"generated_at": datetime.utcnow(), "data": {"top_recommendation": "Redeploy bins to Industrial North"}}])
            self.impact = MockCollection([{"co2_saved_kg": 1240.5, "trees_equivalent": 62, "total_items_recycled": 2480, "contamination_rate_pct": 4.2}])
            self.history = MockCollection([
                {"serial": f"WS-{1000+i}", "timestamp": datetime.utcnow(), "waste_type": "Plastic", "confidence": 0.95+random.uniform(0,0.04), "zone": "Downtown"} for i in range(20)
            ])
            self.report = MockCollection([])

    def get_bin(self, waste_type):
        return self.bins.find_one({"waste_type": waste_type.lower()})

    def update_bin_stats(self, bin_id, fill_increment=1.5):
        pass

db = DBService()

