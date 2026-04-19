import random
import time
import datetime as dt
import json

# --- MOCK DATA ENGINE ---

class FeaturesEngine:
    def __init__(self):
        # Base zones for the city
        self.zones = [
            {"id": "Z1", "name": "Downtown Commercial", "pop_density": 0.9, "bins": 120},
            {"id": "Z2", "name": "Residential North", "pop_density": 0.6, "bins": 85},
            {"id": "Z3", "name": "University District", "pop_density": 0.8, "bins": 60},
            {"id": "Z4", "name": "Industrial Park", "pop_density": 0.2, "bins": 40},
            {"id": "Z5", "name": "Suburban South", "pop_density": 0.4, "bins": 30}, # Underserved
        ]

    # Feature 1: Predictive Waste Surge Intelligence
    def get_predictive_surge(self):
        now = dt.datetime.now()
        forecast = []
        for i in range(1, 4):
            day = now + dt.timedelta(days=i)
            is_weekend = day.weekday() >= 5
            base_vol = 1000
            if is_weekend:
                base_vol *= 1.4
            
            # Simulate a festival in Downtown on day 2
            event = None
            if i == 2:
                event = {"name": "Summer Music Festival", "zone": "Downtown Commercial", "impact": "+45%"}
                base_vol *= 1.45

            forecast.append({
                "date": day.strftime("%Y-%m-%d"),
                "day_name": day.strftime("%A"),
                "projected_volume_kg": int(base_vol * random.uniform(0.9, 1.1)),
                "risk_level": "High" if base_vol > 1300 else ("Medium" if base_vol > 1100 else "Low"),
                "event": event
            })
        return forecast

    # Feature 2: Waste DNA Fingerprinting
    def get_waste_dna(self):
        dna_profiles = []
        for z in self.zones:
            if "Commercial" in z["name"]:
                dist = {"Paper": 45, "Plastic": 30, "Organic": 15, "Metal": 10}
            elif "Residential" in z["name"] or "Suburban" in z["name"]:
                dist = {"Organic": 40, "Plastic": 35, "Paper": 15, "Metal": 10}
            elif "University" in z["name"]:
                dist = {"Plastic": 40, "Paper": 30, "Organic": 20, "Metal": 10}
            else: # Industrial
                dist = {"Metal": 50, "Plastic": 20, "Paper": 20, "Organic": 10}
                
            dna_profiles.append({
                "zone": z["name"],
                "signature": dist,
                "dominant_waste": max(dist, key=dist.get)
            })
        return dna_profiles

    # Feature 3: Carbon Credit Gamification
    def get_gamification(self):
        leaderboard = [
            {"rank": 1, "name": "EcoWarriors School", "type": "Institution", "greencoins": 14500, "co2_offset_kg": 450},
            {"rank": 2, "name": "GreenTech Campus", "type": "Corporate", "greencoins": 12200, "co2_offset_kg": 380},
            {"rank": 3, "name": "Sarah J.", "type": "Individual", "greencoins": 8450, "co2_offset_kg": 210},
            {"rank": 4, "name": "Block 42 Residents", "type": "Community", "greencoins": 7900, "co2_offset_kg": 195},
            {"rank": 5, "name": "Mike T.", "type": "Individual", "greencoins": 6120, "co2_offset_kg": 150},
        ]
        return {
            "leaderboard": leaderboard,
            "rewards_available": [
                {"cost": 500, "reward": "10% off Local Metro Card"},
                {"cost": 1000, "reward": "Free Coffee at Green Cafe"},
                {"cost": 5000, "reward": "Plant a Tree in City Park"}
            ]
        }

    # Feature 4: Conversational Assistant (Relies on Gemini in app.py, mock wrapper here)
    def generate_chat_prompt(self, message):
         return (
             f"You are a multilingual helpful waste disposal assistant. "
             f"User asks: '{message}'. Respond short, in the same language. "
             f"Tell them standard bin color (e.g. Blue for recyclable), drop-off rules, "
             f"and a 1-sentence environmental impact of doing it right."
         )

    # Feature 5: Contamination Root Cause Analyzer
    def get_contamination_logs(self):
        return [
            {
                "id": "ERR-994",
                "time": (dt.datetime.now() - dt.timedelta(minutes=45)).strftime("%H:%M"),
                "bin_id": "SC-102 (Metro Station)",
                "issue": "Food-stained Paper mixed in Recyclables",
                "root_cause_probability": "High foot traffic / lack of clear organic bin sign",
                "action_taken": "Dispatched digital nudge to station display screens."
            },
            {
                "id": "ERR-993",
                "time": (dt.datetime.now() - dt.timedelta(hours=2)).strftime("%H:%M"),
                "bin_id": "SC-104 (Tech Park)",
                "issue": "Lithium Battery in General Waste",
                "root_cause_probability": "Building B3 office cleanout",
                "action_taken": "Emailed facility manager Warning Notice #1."
            }
        ]

    # Feature 6: Waste-to-Resource Marketplace
    def get_marketplace(self):
        return {
            "supply": [
                {"id": "S1", "material": "Clean Cardboard", "quantity": "500 kg", "provider": "Tech Park logistics", "status": "Available"},
                {"id": "S2", "material": "Coffee Grounds", "quantity": "50 kg", "provider": "Downtown Cafes", "status": "Available"},
                {"id": "S3", "material": "Scrap Aluminum", "quantity": "120 kg", "provider": "Industrial Park Fab", "status": "Pending Pickup"}
            ],
            "demand": [
                {"id": "D1", "material": "Coffee Grounds", "quantity": "Required: 100 kg/week", "requester": "City Community Gardens", "match_score": "95%"},
                {"id": "D2", "material": "Clean Cardboard", "quantity": "Required: 200 kg", "requester": "EcoPackaging Startup", "match_score": "100%"}
            ]
        }

    # Feature 7: Live "City Metabolism" View
    def get_city_metabolism(self):
        # Nodes and connections for a Sankey-style or network flow diagram
        return {
            "nodes": [
                {"id": "Bins", "group": 1},
                {"id": "Truck Fleet A", "group": 2},
                {"id": "Truck Fleet B", "group": 2},
                {"id": "Recycling Center", "group": 3},
                {"id": "Compost Facility", "group": 3},
                {"id": "Landfill", "group": 4}
            ],
            "links": [
                {"source": "Bins", "target": "Truck Fleet A", "value": 60, "material": "Recyclables"},
                {"source": "Bins", "target": "Truck Fleet B", "value": 40, "material": "Mixed Waste"},
                {"source": "Truck Fleet A", "target": "Recycling Center", "value": 50},
                {"source": "Truck Fleet A", "target": "Compost Facility", "value": 10},
                {"source": "Truck Fleet B", "target": "Landfill", "value": 35},
                {"source": "Truck Fleet B", "target": "Recycling Center", "value": 5} # AI sorted at facility
            ],
            "pulse_rate_kg_per_min": random.randint(15, 30)
        }

    # Feature 8: Compliance Score per Building/Zone
    def get_compliance_scores(self):
        return [
            {"building": "Skyline Towers (Res)", "score": 94, "grade": "A", "trend": "+2"},
            {"building": "TechHub Alpha", "score": 88, "grade": "B+", "trend": "-1"},
            {"building": "Central Mall", "score": 72, "grade": "C", "trend": "-5"},
            {"building": "University Dorms", "score": 65, "grade": "D", "trend": "+4"}, # Needs improvement
        ]

    # Feature 9: "What If" Scenario Simulator
    def simulate_scenario(self, params):
        # params: {"add_bins": 20, "collection_shift_days": 2, "zone": "Z3"}
        add_bins = int(params.get("add_bins", 0))
        shift = int(params.get("collection_shift_days", 1))
        
        cost_savings = (shift - 1) * 2500 - (add_bins * 150)
        overflow_risk = max(5, 15 - add_bins * 0.5 + shift * 10)
        co2_impact = (-add_bins * 5) + ((shift-1) * -50) # Trucks drive less, save CO2
        
        return {
            "projected_cost_savings_usd": cost_savings,
            "overflow_risk_pct": round(overflow_risk, 1),
            "carbon_emissions_change_kg": co2_impact,
            "recommendation": "Highly Recommended" if cost_savings > 0 and overflow_risk < 20 else "Risky - Monitor closely"
        }

    # Feature 11: Waste Inequality Index
    def get_inequality_index(self):
        # Bins per 10k population derived from self.zones
        # pop_density is a mock multiplier. 
        res = []
        for z in self.zones:
            # mock pop = density * 100k
            pop = z["pop_density"] * 100000
            bins_per_10k = (z["bins"] / pop) * 10000 if pop > 0 else 0
            
            status = "Adequate"
            if bins_per_10k < 10:
                status = "Under-served"
            if bins_per_10k > 30:
                status = "Over-served"
                
            res.append({
                "zone": z["name"],
                "bins": z["bins"],
                "population_est": int(pop),
                "bins_per_10k": round(bins_per_10k, 1),
                "equity_status": status
            })
        return res

features_engine = FeaturesEngine()
