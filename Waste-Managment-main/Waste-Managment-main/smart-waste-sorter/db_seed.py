"""
SmartSort AI — db_seed.py
Jury-Ready Demo Data Seeder
Populates ALL 8 pages with realistic, impressive data.
Run: python db_seed.py
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.getenv("DB_NAME", "smartsort_ai")

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def ts(days_ago=0, hours_ago=0, minutes_ago=0):
    """Return a datetime offset from now."""
    return datetime.utcnow() - timedelta(
        days=days_ago, hours=hours_ago, minutes=minutes_ago
    )

def drop_all():
    collections = [
        "waste_detections", "smart_bins", "users_greencoins",
        "contamination_logs", "waste_marketplace", "city_analytics",
        "ai_insights_cache", "impact_stats", "history_events"
    ]
    for col in collections:
        db[col].drop()
    print("  Dropped all existing collections.")

# ─────────────────────────────────────────────
# 1. SMART BINS  →  Overview + City Bin Map
# ─────────────────────────────────────────────
def seed_smart_bins():
    bins = [
        {
            "bin_id": "BIN-001",
            "name": "Central Plaza — Plastic",
            "waste_type": "plastic",
            "fill_percentage": 72,
            "status": "active",
            "zone": "Downtown Commercial",
            "lat": 28.6139, "lng": 77.2090,
            "total_items_collected": 1420,
            "last_updated": ts(hours_ago=1),
            "sensor_battery": 87,
            "is_full": False
        },
        {
            "bin_id": "BIN-002",
            "name": "Central Plaza — Paper",
            "waste_type": "paper",
            "fill_percentage": 45,
            "status": "active",
            "zone": "Downtown Commercial",
            "lat": 28.6142, "lng": 77.2095,
            "total_items_collected": 980,
            "last_updated": ts(hours_ago=2),
            "sensor_battery": 91,
            "is_full": False
        },
        {
            "bin_id": "BIN-003",
            "name": "Industrial Park — Metal",
            "waste_type": "metal",
            "fill_percentage": 91,
            "status": "full",
            "zone": "Industrial Park",
            "lat": 28.6200, "lng": 77.2150,
            "total_items_collected": 2310,
            "last_updated": ts(minutes_ago=30),
            "sensor_battery": 65,
            "is_full": True
        },
        {
            "bin_id": "BIN-004",
            "name": "Residential North — Organic",
            "waste_type": "organic",
            "fill_percentage": 38,
            "status": "active",
            "zone": "Residential North",
            "lat": 28.6080, "lng": 77.2060,
            "total_items_collected": 870,
            "last_updated": ts(hours_ago=3),
            "sensor_battery": 78,
            "is_full": False
        },
        {
            "bin_id": "BIN-005",
            "name": "University District — Plastic",
            "waste_type": "plastic",
            "fill_percentage": 55,
            "status": "active",
            "zone": "University District",
            "lat": 28.6050, "lng": 77.2110,
            "total_items_collected": 1150,
            "last_updated": ts(hours_ago=1),
            "sensor_battery": 94,
            "is_full": False
        },
        {
            "bin_id": "BIN-006",
            "name": "Suburban South — Paper",
            "waste_type": "paper",
            "fill_percentage": 22,
            "status": "active",
            "zone": "Suburban South",
            "lat": 28.6010, "lng": 77.2200,
            "total_items_collected": 430,
            "last_updated": ts(hours_ago=5),
            "sensor_battery": 82,
            "is_full": False
        },
    ]
    db["smart_bins"].insert_many(bins)
    db["smart_bins"].create_index([("bin_id", ASCENDING)], unique=True)
    db["smart_bins"].create_index([("zone", ASCENDING)])
    print(f"  Seeded {len(bins)} smart bins.")


# ─────────────────────────────────────────────
# 2. WASTE DETECTIONS  →  Overview + Analytics + History
# ─────────────────────────────────────────────
def seed_waste_detections():
    zones       = ["Downtown Commercial", "Industrial Park",
                   "Residential North", "University District",
                   "Suburban South"]
    waste_types = ["plastic", "paper", "metal", "organic"]
    bin_ids     = ["BIN-001", "BIN-002", "BIN-003", "BIN-004", "BIN-005", "BIN-006"]

    # Weighted so plastic is most common (jury sees Plastic as top waste)
    weights     = [0.40, 0.25, 0.20, 0.15]

    detections = []
    # 7 days of data — ramping up towards Friday (surge)
    daily_counts = {6: 40, 5: 52, 4: 3, 3: 49, 2: 68, 1: 53, 0: 44}

    for days_ago, count in daily_counts.items():
        for i in range(count):
            wtype      = random.choices(waste_types, weights=weights)[0]
            hour       = random.randint(8, 20)
            confidence = round(random.uniform(0.72, 0.98), 2)
            is_contam  = random.random() < 0.06  # 6% contamination rate
            detections.append({
                "waste_type":          wtype,
                "confidence_score":    confidence,
                "bin_id":              random.choice(bin_ids),
                "zone":                random.choice(zones),
                "model_used":          "gemini-1.5-flash",
                "session_id":          f"SES-{1000 + days_ago}",
                "is_contamination":    is_contam,
                "contamination_reason": "Mixed waste in wrong bin" if is_contam else None,
                "timestamp":           ts(days_ago=days_ago,
                                          hours_ago=random.randint(0, 14),
                                          minutes_ago=random.randint(0, 59)),
                "image_base64":        None,
                "co2_saved_kg":        round(random.uniform(0.3, 0.8), 2),
            })

    db["waste_detections"].insert_many(detections)
    db["waste_detections"].create_index([("timestamp", DESCENDING)])
    db["waste_detections"].create_index([("waste_type", ASCENDING)])
    db["waste_detections"].create_index([("bin_id", ASCENDING)])
    print(f"  Seeded {len(detections)} waste detections.")


# ─────────────────────────────────────────────
# 3. USERS / GREEN COINS  →  City OS Leaderboard
# ─────────────────────────────────────────────
def seed_users():
    users = [
        {
            "rank": 1,
            "user_name": "EcoWarriors School",
            "organization": "St. Xavier's Green Club",
            "green_coins": 14500,
            "total_items_sorted": 2900,
            "streak_days": 42,
            "badge": "Platinum Recycler",
            "joined_date": ts(days_ago=120),
            "last_active": ts(hours_ago=2),
        },
        {
            "rank": 2,
            "user_name": "GreenTech Campus",
            "organization": "IIT Innovation Hub",
            "green_coins": 12200,
            "total_items_sorted": 2440,
            "streak_days": 35,
            "badge": "Gold Sorter",
            "joined_date": ts(days_ago=90),
            "last_active": ts(hours_ago=5),
        },
        {
            "rank": 3,
            "user_name": "Sarah J.",
            "organization": "Individual",
            "green_coins": 8450,
            "total_items_sorted": 1690,
            "streak_days": 28,
            "badge": "Silver Champion",
            "joined_date": ts(days_ago=60),
            "last_active": ts(hours_ago=1),
        },
        {
            "rank": 4,
            "user_name": "Block 42 Residents",
            "organization": "Residential Society",
            "green_coins": 7900,
            "total_items_sorted": 1580,
            "streak_days": 21,
            "badge": "Bronze Warrior",
            "joined_date": ts(days_ago=75),
            "last_active": ts(hours_ago=8),
        },
        {
            "rank": 5,
            "user_name": "Mike T.",
            "organization": "Individual",
            "green_coins": 6120,
            "total_items_sorted": 1224,
            "streak_days": 14,
            "badge": "Active Sorter",
            "joined_date": ts(days_ago=45),
            "last_active": ts(days_ago=1),
        },
        {
            "rank": 6,
            "user_name": "CleanCity NGO",
            "organization": "NGO",
            "green_coins": 5400,
            "total_items_sorted": 1080,
            "streak_days": 10,
            "badge": "Active Sorter",
            "joined_date": ts(days_ago=30),
            "last_active": ts(days_ago=2),
        },
    ]
    db["users_greencoins"].insert_many(users)
    db["users_greencoins"].create_index([("green_coins", DESCENDING)])
    print(f"  Seeded {len(users)} users/leaderboard entries.")


# ─────────────────────────────────────────────
# 4. CONTAMINATION LOGS  →  City OS + AI Insights
# ─────────────────────────────────────────────
def seed_contamination():
    logs = [
        {
            "error_code":    "ERR-994",
            "timestamp":     ts(hours_ago=1, minutes_ago=20),
            "description":   "Food-stained Paper mixed in Recyclables",
            "bin_id":        "BIN-002",
            "zone":          "Downtown Commercial",
            "action_taken":  "Dispatched digital nudge to station display screens.",
            "severity":      "medium",
            "resolved":      False,
        },
        {
            "error_code":    "ERR-993",
            "timestamp":     ts(hours_ago=3, minutes_ago=45),
            "description":   "Lithium Battery in General Waste",
            "bin_id":        "BIN-001",
            "zone":          "Downtown Commercial",
            "action_taken":  "Emailed facility manager Warning Notice #1.",
            "severity":      "high",
            "resolved":      False,
        },
        {
            "error_code":    "ERR-992",
            "timestamp":     ts(hours_ago=6),
            "description":   "Glass Bottle in Organic Bin",
            "bin_id":        "BIN-004",
            "zone":          "Residential North",
            "action_taken":  "Automated alert sent to waste handler team.",
            "severity":      "medium",
            "resolved":      True,
        },
        {
            "error_code":    "ERR-991",
            "timestamp":     ts(days_ago=1, hours_ago=2),
            "description":   "Plastic Bag in Metal Recycling",
            "bin_id":        "BIN-003",
            "zone":          "Industrial Park",
            "action_taken":  "Public notice posted on app; bin flagged for manual check.",
            "severity":      "low",
            "resolved":      True,
        },
        {
            "error_code":    "ERR-990",
            "timestamp":     ts(days_ago=1, hours_ago=8),
            "description":   "Medical Waste in Paper Bin",
            "bin_id":        "BIN-006",
            "zone":          "Suburban South",
            "action_taken":  "Health authority notified. Bin quarantined.",
            "severity":      "high",
            "resolved":      True,
        },
        {
            "error_code":    "ERR-989",
            "timestamp":     ts(days_ago=2, hours_ago=4),
            "description":   "Electronic Waste improperly disposed",
            "bin_id":        "BIN-005",
            "zone":          "University District",
            "action_taken":  "E-waste collection drive scheduled.",
            "severity":      "high",
            "resolved":      True,
        },
        {
            "error_code":    "ERR-988",
            "timestamp":     ts(days_ago=3),
            "description":   "Cooking Oil poured into recycling chute",
            "bin_id":        "BIN-001",
            "zone":          "Downtown Commercial",
            "action_taken":  "Maintenance crew dispatched for bin cleaning.",
            "severity":      "medium",
            "resolved":      True,
        },
        {
            "error_code":    "ERR-987",
            "timestamp":     ts(days_ago=4, hours_ago=3),
            "description":   "Aerosol Can in Organic Waste",
            "bin_id":        "BIN-004",
            "zone":          "Residential North",
            "action_taken":  "Resident education pamphlet dispatched.",
            "severity":      "medium",
            "resolved":      True,
        },
    ]
    db["contamination_logs"].insert_many(logs)
    db["contamination_logs"].create_index([("timestamp", DESCENDING)])
    db["contamination_logs"].create_index([("severity", ASCENDING)])
    print(f"  Seeded {len(logs)} contamination logs.")


# ─────────────────────────────────────────────
# 5. WASTE MARKETPLACE  →  City OS Circular Economy
# ─────────────────────────────────────────────
def seed_marketplace():
    items = [
        {
            "material_type":  "Clean Cardboard",
            "quantity_kg":    500,
            "status":         "available",
            "price_per_kg":   4.50,
            "listed_date":    ts(days_ago=2),
            "zone":           "Industrial Park",
            "contact":        "industrialpark@smartsort.ai",
            "description":    "Dry, clean corrugated cardboard bales. Ready for pickup.",
            "co2_offset_kg":  225.0,
        },
        {
            "material_type":  "Coffee Grounds",
            "quantity_kg":    50,
            "status":         "available",
            "price_per_kg":   8.00,
            "listed_date":    ts(days_ago=1),
            "zone":           "Downtown Commercial",
            "contact":        "downtown@smartsort.ai",
            "description":    "Fresh coffee grounds — ideal for composting or skincare.",
            "co2_offset_kg":  18.0,
        },
        {
            "material_type":  "Scrap Aluminum",
            "quantity_kg":    120,
            "status":         "available",
            "price_per_kg":   85.00,
            "listed_date":    ts(days_ago=3),
            "zone":           "Industrial Park",
            "contact":        "metals@smartsort.ai",
            "description":    "Sorted aluminum cans and foil. High purity grade.",
            "co2_offset_kg":  1020.0,
        },
        {
            "material_type":  "Office Paper",
            "quantity_kg":    300,
            "status":         "available",
            "price_per_kg":   3.20,
            "listed_date":    ts(days_ago=4),
            "zone":           "University District",
            "contact":        "university@smartsort.ai",
            "description":    "A4 white office paper — shredded and baled.",
            "co2_offset_kg":  135.0,
        },
        {
            "material_type":  "HDPE Plastic Bottles",
            "quantity_kg":    200,
            "status":         "available",
            "price_per_kg":   22.00,
            "listed_date":    ts(days_ago=1),
            "zone":           "Residential North",
            "contact":        "north@smartsort.ai",
            "description":    "Clean HDPE bottles, labels removed. Ready for granulation.",
            "co2_offset_kg":  360.0,
        },
        {
            "material_type":  "Organic Compost Mix",
            "quantity_kg":    800,
            "status":         "sold",
            "price_per_kg":   2.00,
            "listed_date":    ts(days_ago=7),
            "zone":           "Suburban South",
            "contact":        "south@smartsort.ai",
            "description":    "Processed organic waste — ready-to-use compost.",
            "co2_offset_kg":  400.0,
        },
    ]
    db["waste_marketplace"].insert_many(items)
    db["waste_marketplace"].create_index([("status", ASCENDING)])
    db["waste_marketplace"].create_index([("listed_date", DESCENDING)])
    print(f"  Seeded {len(items)} marketplace listings.")


# ─────────────────────────────────────────────
# 6. CITY ANALYTICS  →  City OS DNA + Predictive Surge
# ─────────────────────────────────────────────
def seed_city_analytics():
    zones_data = [
        {
            "zone_name": "Downtown Commercial",
            "waste_breakdown": {"metal": 10, "organic": 15, "paper": 45, "plastic": 30},
        },
        {
            "zone_name": "Residential North",
            "waste_breakdown": {"metal": 10, "organic": 40, "paper": 15, "plastic": 35},
        },
        {
            "zone_name": "University District",
            "waste_breakdown": {"metal": 5,  "organic": 20, "paper": 50, "plastic": 25},
        },
        {
            "zone_name": "Industrial Park",
            "waste_breakdown": {"metal": 50, "organic": 10, "paper": 20, "plastic": 20},
        },
        {
            "zone_name": "Suburban South",
            "waste_breakdown": {"metal": 10, "organic": 40, "paper": 15, "plastic": 35},
        },
    ]

    # 7-day historical daily analytics
    daily_kg = [820, 940, 310, 964, 1398, 1312, 890]
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    records = []

    for i, (day, kg) in enumerate(zip(day_names, daily_kg)):
        records.append({
            "date":        ts(days_ago=(6 - i)),
            "day_name":    day,
            "total_kg":    kg,
            "zones":       zones_data,
            "item_counts": {
                "plastic": int(kg * 0.40 / 0.35),
                "paper":   int(kg * 0.25 / 0.25),
                "metal":   int(kg * 0.20 / 0.45),
                "organic": int(kg * 0.15 / 0.30),
            },
        })

    # Predictive surge for next 3 days
    surge_predictions = [
        {
            "type":         "surge_prediction",
            "day_name":     "Thursday",
            "predicted_kg": 964,
            "highlight":    None,
            "date":         ts(days_ago=-1),
        },
        {
            "type":         "surge_prediction",
            "day_name":     "Friday",
            "predicted_kg": 1398,
            "highlight":    "Summer Music Festival — +45%",
            "date":         ts(days_ago=-2),
        },
        {
            "type":         "surge_prediction",
            "day_name":     "Saturday",
            "predicted_kg": 1312,
            "highlight":    None,
            "date":         ts(days_ago=-3),
        },
    ]

    db["city_analytics"].insert_many(records + surge_predictions)
    db["city_analytics"].create_index([("date", DESCENDING)])
    db["city_analytics"].create_index([("type", ASCENDING)])
    print(f"  Seeded {len(records)} daily analytics + {len(surge_predictions)} surge predictions.")


# ─────────────────────────────────────────────
# 7. IMPACT STATS  →  Impact Page
# ─────────────────────────────────────────────
def seed_impact():
    impact = {
        "generated_at":        datetime.utcnow(),
        "total_items_recycled": 9160,
        "total_kg_processed":   4820.5,
        "co2_saved_kg":         4580.0,
        "trees_equivalent":     209,
        "water_saved_litres":   183200,
        "energy_saved_kwh":     9320,
        "contamination_rate_pct": 6.2,
        "bins_monitored":       6,
        "active_zones":         5,
        "greencoins_awarded":   49170,
        "top_waste_type":       "plastic",
        "monthly_trend": [
            {"month": "October",  "kg": 3200, "items": 6400},
            {"month": "November", "kg": 3800, "items": 7600},
            {"month": "December", "kg": 4100, "items": 8200},
            {"month": "January",  "kg": 4400, "items": 8800},
            {"month": "February", "kg": 4650, "items": 9300},
            {"month": "March",    "kg": 4820, "items": 9160},
        ],
        "per_zone_impact": [
            {"zone": "Downtown Commercial", "co2_kg": 1100, "items": 2200},
            {"zone": "Industrial Park",     "co2_kg": 1500, "items": 2100},
            {"zone": "Residential North",   "co2_kg": 800,  "items": 1700},
            {"zone": "University District", "co2_kg": 700,  "items": 2000},
            {"zone": "Suburban South",      "co2_kg": 480,  "items": 1160},
        ],
    }
    db["impact_stats"].insert_one(impact)
    print("  Seeded impact statistics.")


# ─────────────────────────────────────────────
# 8. AI INSIGHTS CACHE  →  AI Insights Page
# ─────────────────────────────────────────────
def seed_ai_insights():
    insight = {
        "generated_at": datetime.utcnow(),
        "expires_at":   datetime.utcnow() + timedelta(hours=1),
        "top_recommendation": (
            "Prioritize plastic collection in Downtown Commercial and University "
            "District — both zones show 30–35% plastic composition with bins "
            "approaching 70% fill. Schedule pickup within 6 hours to avoid overflow."
        ),
        "trend_analysis": (
            "Waste volumes show a consistent Friday surge (+38–45%) correlated "
            "with weekend market activity. Industrial Park accounts for 50% metal "
            "waste — a bulk recycling partnership with local smelters could reduce "
            "logistics costs by an estimated 22%."
        ),
        "contamination_risk_zones": [
            {
                "zone":   "Downtown Commercial",
                "risk":   "High",
                "reason": "2 unresolved contamination events in 24 hours. "
                          "Food-stained paper and lithium battery misplacement detected."
            },
            {
                "zone":   "Residential North",
                "risk":   "Medium",
                "reason": "Recurring organic-plastic mix in evening hours (6–9 PM). "
                          "Recommend targeted awareness campaign."
            },
            {
                "zone":   "Industrial Park",
                "risk":   "Low",
                "reason": "Consistent metal sorting. Minimal cross-contamination."
            },
        ],
        "weekly_forecast": [
            {"day": "Thursday", "predicted_kg": 964,  "confidence": 0.91},
            {"day": "Friday",   "predicted_kg": 1398, "confidence": 0.88,
             "note": "Summer Music Festival surge (+45%)"},
            {"day": "Saturday", "predicted_kg": 1312, "confidence": 0.85},
            {"day": "Sunday",   "predicted_kg": 890,  "confidence": 0.82},
        ],
        "quick_wins": [
            "Install a second plastic bin at University District — current bin at 55% fill by noon.",
            "Metal bin BIN-003 in Industrial Park is 91% full — dispatch collection immediately.",
            "Contamination rate dropped 1.8% this week — reinforce positive feedback via GreenCoins.",
        ],
        "model_used": "gemini-1.5-flash",
        "data_points_analysed": 309,
    }
    db["ai_insights_cache"].insert_one(insight)
    db["ai_insights_cache"].create_index(
        [("expires_at", ASCENDING)], expireAfterSeconds=0
    )
    print("  Seeded AI insights cache.")


# ─────────────────────────────────────────────
# 9. HISTORY EVENTS  →  History Page
# ─────────────────────────────────────────────
def seed_history():
    """Mirror of waste_detections formatted for history page display."""
    waste_types = ["plastic", "paper", "metal", "organic"]
    weights     = [0.40, 0.25, 0.20, 0.15]
    zones       = ["Downtown Commercial", "Industrial Park",
                   "Residential North", "University District", "Suburban South"]
    bin_ids     = ["BIN-001", "BIN-002", "BIN-003",
                   "BIN-004", "BIN-005", "BIN-006"]
    events = []
    for i in range(150):
        days_ago   = random.randint(0, 6)
        wtype      = random.choices(waste_types, weights=weights)[0]
        confidence = round(random.uniform(0.72, 0.98), 2)
        is_contam  = random.random() < 0.06
        events.append({
            "serial":          i + 1,
            "waste_type":      wtype,
            "confidence":      confidence,
            "bin_id":          random.choice(bin_ids),
            "zone":            random.choice(zones),
            "model_used":      "gemini-1.5-flash",
            "is_contamination": is_contam,
            "action":          "Sorted" if not is_contam else "Flagged",
            "timestamp":       ts(
                                   days_ago=days_ago,
                                   hours_ago=random.randint(0, 14),
                                   minutes_ago=random.randint(0, 59)
                               ),
            "co2_saved_kg":    round(random.uniform(0.3, 0.8), 2),
            "greencoins":      random.choice([10, 15, 20, 25]),
        })
    db["history_events"].insert_many(events)
    db["history_events"].create_index([("timestamp", DESCENDING)])
    db["history_events"].create_index([("waste_type", ASCENDING)])
    print(f"  Seeded {len(events)} history events.")


# ─────────────────────────────────────────────
# 10. REPORT SUMMARY  →  Report / Export Page
# ─────────────────────────────────────────────
def seed_report():
    report = {
        "generated_at":     datetime.utcnow(),
        "report_title":     "SmartSort AI — Weekly Waste Intelligence Report",
        "period":           "18 Mar 2026 – 25 Mar 2026",
        "summary": {
            "total_items":      309,
            "total_kg":         4820.5,
            "plastic_items":    124,
            "paper_items":      77,
            "metal_items":      62,
            "organic_items":    46,
            "contaminations":   8,
            "greencoins_given": 3090,
            "co2_saved_kg":     154.5,
            "avg_confidence":   0.86,
        },
        "top_zone":         "Industrial Park",
        "peak_day":         "Friday",
        "peak_hour":        "14:00",
        "bins_serviced":    6,
        "recommendations": [
            "Increase collection frequency on Fridays due to consistent 40%+ surge.",
            "Deploy contamination detection signage at Downtown Commercial bins.",
            "Expand GreenCoins rewards to boost participation in Suburban South.",
        ],
    }
    db["report_summary"].insert_one(report)
    db["report_summary"].create_index([("generated_at", DESCENDING)])
    print("  Seeded report summary.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════╗")
    print("║   SmartSort AI — Jury Demo Data Seeder   ║")
    print("╚══════════════════════════════════════════╝\n")

    print("▶ Dropping existing data...")
    drop_all()

    print("\n▶ Seeding collections...\n")
    seed_smart_bins()        # Overview + City Bin Map
    seed_waste_detections()  # Overview + Analytics + History
    seed_users()             # City OS Leaderboard
    seed_contamination()     # City OS + AI Insights
    seed_marketplace()       # City OS Circular Economy
    seed_city_analytics()    # City OS DNA + Surge
    seed_impact()            # Impact Page
    seed_ai_insights()       # AI Insights Page
    seed_history()           # History Page
    seed_report()            # Report/Export Page

    print("\n✅  All collections seeded successfully!")
    print("─────────────────────────────────────────")
    print("  Collections created:")
    for col in db.list_collection_names():
        count = db[col].count_documents({})
        print(f"    {col:<30} {count:>4} documents")
    print("─────────────────────────────────────────")
    print("  Ready for jury presentation! 🎯\n")
    client.close()
