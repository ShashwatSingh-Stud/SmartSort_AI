
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

-- 1. Smart Bins Data
INSERT INTO smart_bins (bin_id, location_name, latitude, longitude, zone, bin_type, capacity_liters, current_fill_percent, last_collected, sensor_status, temperature) VALUES
('BIN_100', 'Palasia Square', 22.719078, 75.853032, 'Palasia', 'plastic', 100, 58, '2026-03-26 12:36:30', 'active', 35.6),
('BIN_101', '56 Dukan', 22.736390, 75.881335, 'Nipania', 'glass', 100, 37, '2026-03-27 19:36:30', 'active', 33.2),
('BIN_102', 'Apollo Premier', 22.685400, 75.854842, 'Super Corridor', 'plastic', 200, 95, '2026-03-27 12:36:30', 'maintenance', 36.7),
('BIN_103', 'C21 Mall', 22.679505, 75.843023, 'Vijay Nagar', 'metal', 200, 29, '2026-03-26 08:36:30', 'maintenance', 31.1),
('BIN_104', 'Rajwada Palace', 22.733969, 75.856367, 'Bhawarkuan', 'plastic', 200, 76, '2026-03-26 02:36:30', 'active', 37.5),
('BIN_105', 'Khajrana Temple', 22.718071, 75.826776, 'Vijay Nagar', 'metal', 200, 61, '2026-03-26 20:36:30', 'active', 25.6),
('BIN_106', 'Holkar Stadium', 22.736636, 75.897138, 'Bhawarkuan', 'metal', 100, 92, '2026-03-27 03:36:30', 'maintenance', 34.7),
('BIN_107', 'Bhawarkuan Square', 22.701610, 75.884771, 'Bhawarkuan', 'plastic', 500, 54, '2026-03-26 23:36:30', 'maintenance', 26.0),
('BIN_108', 'IT Park', 22.721901, 75.863356, 'Rajwada', 'organic', 500, 22, '2026-03-26 09:36:30', 'active', 29.8),
('BIN_109', 'Super Corridor TCS', 22.706660, 75.845977, 'Nipania', 'plastic', 500, 46, '2026-03-27 18:36:30', 'maintenance', 25.2),
('BIN_110', 'Rau Circle', 22.689408, 75.810636, 'Nipania', 'organic', 200, 49, '2026-03-26 19:36:30', 'active', 36.0),
('BIN_111', 'Silicon City', 22.700254, 75.882436, 'Palasia', 'glass', 200, 73, '2026-03-27 15:36:30', 'active', 25.5),
('BIN_112', 'Nipania Bypass', 22.717493, 75.853644, 'Rau', 'glass', 100, 52, '2026-03-27 08:36:30', 'active', 28.6),
('BIN_113', 'Bombay Hospital', 22.698519, 75.904415, 'Bhawarkuan', 'organic', 100, 58, '2026-03-26 06:36:30', 'active', 29.4),
('BIN_114', 'Geeta Bhawan Square', 22.695180, 75.893510, 'Nipania', 'metal', 500, 47, '2026-03-26 11:36:30', 'active', 25.5),
('BIN_115', 'MY Hospital', 22.710069, 75.883499, 'Bhawarkuan', 'plastic', 100, 68, '2026-03-26 06:36:30', 'active', 29.6),
('BIN_116', 'LIG Square', 22.694104, 75.816256, 'Bhawarkuan', 'plastic', 200, 72, '2026-03-27 19:36:30', 'active', 29.1),
('BIN_117', 'SGSITS College', 22.719932, 75.904597, 'Nipania', 'metal', 500, 56, '2026-03-27 11:36:30', 'active', 29.8),
('BIN_118', 'Pheonix Citadel', 22.746089, 75.862142, 'Geeta Bhawan', 'metal', 200, 57, '2026-03-26 17:36:30', 'active', 38.5),
('BIN_119', 'Brilliant Convention', 22.728091, 75.818068, 'Bhawarkuan', 'plastic', 200, 88, '2026-03-27 17:36:30', 'active', 30.9);
