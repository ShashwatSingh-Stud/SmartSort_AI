import os
import json
import random
from datetime import datetime, timedelta

def setup_dirs():
    os.makedirs('database', exist_ok=True)
    os.makedirs('mock_data', exist_ok=True)

zones = [
    {"id": 1, "name": "Palasia"},
    {"id": 2, "name": "Vijay Nagar"},
    {"id": 3, "name": "Rajwada"},
    {"id": 4, "name": "Bhawarkuan"},
    {"id": 5, "name": "Super Corridor"},
    {"id": 6, "name": "Rau"},
    {"id": 7, "name": "Nipania"},
    {"id": 8, "name": "Geeta Bhawan"}
]

bin_types = ["organic", "plastic", "glass", "metal"]
collectors = ["Ramesh K.", "Suresh M.", "Anil S.", "Mohit D.", "Deepak T."]

def generate_bins_sql():
    # 20 Smart Waste Bins across Indore
    locations = [
        "Palasia Square", "56 Dukan", "Apollo Premier", "C21 Mall", 
        "Rajwada Palace", "Khajrana Temple", "Holkar Stadium", 
        "Bhawarkuan Square", "IT Park", "Super Corridor TCS",
        "Rau Circle", "Silicon City", "Nipania Bypass", "Bombay Hospital",
        "Geeta Bhawan Square", "MY Hospital", "LIG Square", "SGSITS College",
        "Pheonix Citadel", "Brilliant Convention"
    ]
    
    bins = []
    sql_inserts = "-- 1. Smart Bins Data\nINSERT INTO smart_bins (bin_id, location_name, latitude, longitude, zone, bin_type, capacity_liters, current_fill_percent, last_collected, sensor_status, temperature) VALUES\n"
    
    # Base coords roughly for Indore: 22.7196, 75.8577
    base_lat = 22.7196
    base_lon = 75.8577
    
    for i in range(20):
        b_id = f"BIN_{100 + i}"
        loc = locations[i]
        z = random.choice(zones)["name"]
        b_type = random.choice(bin_types)
        cap = random.choice([100, 200, 500])
        fill = random.randint(10, 95)
        # Random time within last 2 days
        last_col = (datetime.now() - timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%d %H:%M:%S')
        status = random.choice(["active", "active", "active", "maintenance"])
        temp = round(random.uniform(25.0, 40.0), 1)
        
        lat = base_lat + random.uniform(-0.05, 0.05)
        lon = base_lon + random.uniform(-0.05, 0.05)
        
        bins.append({"bin_id": b_id, "location_name": loc, "zone": z, "type": b_type, "capacity": cap})
        
        sep = ";\n" if i == 19 else ",\n"
        sql_inserts += f"('{b_id}', '{loc}', {lat:.6f}, {lon:.6f}, '{z}', '{b_type}', {cap}, {fill}, '{last_col}', '{status}', {temp}){sep}"
        
    return bins, sql_inserts

def generate_collection_logs(bins):
    logs = []
    end_date = datetime.now()
    
    # 50 rows of events last 30 days
    for i in range(1, 51):
        # randomly pick a bin
        bz = random.choice(bins)
        
        # generate a random date in last 30 days
        days_ago = random.randint(0, 30)
        col_date = end_date - timedelta(days=days_ago)
        
        # Weekend spikes
        is_weekend = col_date.weekday() >= 5
        fill_modifier = 1.3 if is_weekend else 1.0
        
        weight = round(random.uniform(20, 80) * fill_modifier, 2)
        carbon = round(weight * 0.5, 2) # simplified logic
        
        logs.append({
            "log_id": f"LOG_{1000 + i}",
            "bin_id": bz["bin_id"],
            "collected_at": col_date.strftime('%Y-%m-%d %H:%M:%S'),
            "collector_name": random.choice(collectors),
            "weight_kg": weight,
            "waste_type": bz["type"],
            "truck_id": f"TRK_IND_{random.randint(1, 10)}",
            "route_name": f"Route_{bz['zone'].replace(' ', '')}",
            "carbon_saved_kg": carbon
        })
    return logs

def generate_gamification_users():
    users = []
    names = ["Amit Sharma", "Neha Gupta", "Priya Singh", "Rahul Verma", "Karan Patel", 
             "Swati Jain", "Vivek Joshi", "Ankita Rao", "Sachin Yadav", "Pooja Mishra",
             "Vikram Chaudhary", "Riya Desai", "Arjun Reddy", "Kavita Tiwari", "Manish Sen"]
    
    for i in range(15):
        green_coins = random.randint(50, 2000)
        c_sorts = random.randint(10, 500)
        inc_sorts = random.randint(1, 50)
        comp_score = min(100, round((c_sorts / (c_sorts + inc_sorts)) * 100, 1))
        
        users.append({
            "user_id": f"USR_{200 + i}",
            "name": names[i],
            "zone": random.choice(zones)["name"],
            "green_coins_earned": green_coins,
            "correct_sorts": c_sorts,
            "incorrect_sorts": inc_sorts,
            "compliance_score": comp_score,
            "monthly_rank": 0, # compute later
            "waste_reduced_kg": round(c_sorts * 0.2, 1) # simple logic
        })
        
    # Rank them
    users.sort(key=lambda x: x["green_coins_earned"], reverse=True)
    for idx, u in enumerate(users):
        u["monthly_rank"] = idx + 1
        
    return users

def generate_predictive_analytics(bins):
    analytics = []
    # 5 bins, 30 days, every 6 hours = 4 records/day * 30 days = 120 records per bin
    selected_bins = bins[:5]
    start_date = datetime.now() - timedelta(days=30)
    
    for b in selected_bins:
        current_fill = random.randint(5, 20)
        for d in range(30):
            current_date = start_date + timedelta(days=d)
            is_weekend = current_date.weekday() >= 5
            
            for h in range(4): # 00:00, 06:00, 12:00, 18:00
                ts = current_date.replace(hour=h*6, minute=0, second=0)
                
                # Fill logic
                increase = random.randint(2, 8) if not is_weekend else random.randint(5, 15)
                current_fill += increase
                
                if current_fill >= 100:
                    current_fill = random.randint(0, 5) # reset (collected)
                    
                analytics.append({
                    "bin_id": b["bin_id"],
                    "timestamp": ts.strftime('%Y-%m-%d %H:%M:%S'),
                    "fill_percent": current_fill,
                    "temperature": round(random.uniform(25.0, 42.0), 1),
                    "humidity": round(random.uniform(30.0, 80.0), 1)
                })
    return analytics

def generate_zone_summary():
    z_summary = []
    for z in zones:
        tb = random.randint(10, 50)
        avg_fill = round(random.uniform(35.0, 75.0), 1)
        comp = round(random.uniform(70.0, 98.0), 1)
        m_waste = random.randint(500, 3000)
        z_summary.append({
            "zone_id": f"ZON_{z['id']}",
            "zone_name": z["name"],
            "total_bins": tb,
            "avg_fill_percent": avg_fill,
            "compliance_score": comp,
            "monthly_waste_kg": m_waste,
            "recycled_percent": round(comp * 0.9, 1),
            "carbon_offset_kg": round(m_waste * 0.4, 1),
            "overflow_incidents": random.randint(0, 12),
            "active_alerts": random.randint(0, 3)
        })
    return z_summary

def main():
    setup_dirs()
    
    # Schema Generation
    schema_sql = """
CREATE DATABASE IF NOT EXISTS smartsort_ai;
USE smartsort_ai;

CREATE TABLE zones (
    zone_id VARCHAR(20) PRIMARY KEY,
    zone_name VARCHAR(100) NOT NULL
);

CREATE TABLE waste_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    base_carbon_offset FLOAT NOT NULL
);

CREATE TABLE smart_bins (
    bin_id VARCHAR(20) PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    zone VARCHAR(100),
    bin_type VARCHAR(50),
    capacity_liters INT,
    current_fill_percent INT,
    last_collected DATETIME,
    sensor_status VARCHAR(50),
    temperature FLOAT
);

CREATE TABLE collection_logs (
    log_id VARCHAR(20) PRIMARY KEY,
    bin_id VARCHAR(20),
    collected_at DATETIME,
    collector_name VARCHAR(100),
    weight_kg FLOAT,
    waste_type VARCHAR(50),
    truck_id VARCHAR(50),
    route_name VARCHAR(100),
    carbon_saved_kg FLOAT,
    FOREIGN KEY (bin_id) REFERENCES smart_bins(bin_id)
);

CREATE TABLE users_greencoins (
    user_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    zone VARCHAR(100),
    green_coins_earned INT,
    correct_sorts INT,
    incorrect_sorts INT,
    compliance_score FLOAT,
    monthly_rank INT,
    waste_reduced_kg FLOAT
);

CREATE TABLE alerts_notifications (
    alert_id VARCHAR(20) PRIMARY KEY,
    bin_id VARCHAR(20),
    alert_type VARCHAR(50),
    message TEXT,
    created_at DATETIME,
    resolved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (bin_id) REFERENCES smart_bins(bin_id)
);

-- Seed Waste Categories
INSERT INTO waste_categories (name, base_carbon_offset) VALUES
('organic', 0.2), ('plastic', 1.5), ('glass', 0.8), ('metal', 2.0);

-- Seed Zones
INSERT INTO zones (zone_id, zone_name) VALUES
('ZON_1', 'Palasia'), ('ZON_2', 'Vijay Nagar'), ('ZON_3', 'Rajwada'),
('ZON_4', 'Bhawarkuan'), ('ZON_5', 'Super Corridor'), ('ZON_6', 'Rau'),
('ZON_7', 'Nipania'), ('ZON_8', 'Geeta Bhawan');

"""
    
    bins, sql_inserts = generate_bins_sql()
    schema_sql += sql_inserts
    
    with open('database/smartsort_schema.sql', 'w') as f:
        f.write(schema_sql)
        
    # Write JSON files
    with open('mock_data/collection_logs.json', 'w') as f:
        json.dump(generate_collection_logs(bins), f, indent=4)
        
    with open('mock_data/gamification_users.json', 'w') as f:
        json.dump(generate_gamification_users(), f, indent=4)
        
    with open('mock_data/predictive_analytics.json', 'w') as f:
        json.dump(generate_predictive_analytics(bins), f, indent=4)
        
    with open('mock_data/zone_summary.json', 'w') as f:
        json.dump(generate_zone_summary(), f, indent=4)
        
    with open('mock_data/smart_bins.json', 'w') as f:
        json.dump(bins, f, indent=4)

if __name__ == "__main__":
    main()
