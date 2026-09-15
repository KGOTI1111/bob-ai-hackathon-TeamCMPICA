-- Sample Data for Supply Chain Optimizer

USE supply_chain_db;

-- Sample Shipments
INSERT INTO shipments (shipment_id, origin, destination, cargo_description, cargo_value, is_cold_chain, status, current_location, planned_delivery, estimated_delivery, carrier, container_id) VALUES
('SHIP-001', 'Chicago, IL', 'Miami, FL', 'Vaccines (Pfizer)', 500000.00, TRUE, 'in_transit', 'Atlanta, GA', '2024-01-15', '2024-01-14', 'ColdChain Express', 'CONT-001'),
('SHIP-002', 'Newark, NJ', 'Los Angeles, CA', 'Perishable Fruits', 75000.00, TRUE, 'in_transit', 'St. Louis, MO', '2024-01-18', '2024-01-20', 'FreshTransit', 'CONT-002'),
('SHIP-003', 'Houston, TX', 'New York, NY', 'Medical Equipment', 250000.00, FALSE, 'pending', 'Houston, TX', '2024-01-20', '2024-01-20', 'LogisticsNow', 'CONT-003'),
('SHIP-004', 'San Francisco, CA', 'Seattle, WA', 'Electronics', 150000.00, FALSE, 'in_transit', 'Portland, OR', '2024-01-12', '2024-01-11', 'FastFreight', 'CONT-004'),
('SHIP-005', 'Miami, FL', 'Orlando, FL', 'Seafood', 120000.00, TRUE, 'in_transit', 'Miami, FL', '2024-01-10', '2024-01-10', 'ColdChain Express', 'CONT-005');

-- Sample Disruptions
INSERT INTO disruptions (disruption_id, title, description, disruption_type, affected_region, severity, start_time, estimated_resolution, affected_shipments_count, is_active) VALUES
('DISR-001', 'Port of Miami Strike', 'Dock workers strike affecting cargo handling', 'strike', 'Miami, FL', 'high', '2024-01-08 06:00:00', '2024-01-12 18:00:00', 2, TRUE),
('DISR-002', 'Winter Storm - Northeast', 'Major winter storm impacting highways', 'weather', 'New York, NY', 'critical', '2024-01-09 12:00:00', '2024-01-11 00:00:00', 3, TRUE),
('DISR-003', 'Port Congestion - LA', 'Container vessel backlog at Port of LA', 'geopolitical', 'Los Angeles, CA', 'medium', '2024-01-07 00:00:00', '2024-01-25 00:00:00', 1, TRUE);

-- Sample Fleet Assets
INSERT INTO fleet_assets (asset_id, asset_type, status, current_location, capacity_tons, is_cold_chain_capable, current_shipment, available_from) VALUES
('TRUCK-001', 'truck', 'idle', 'Atlanta, GA', 20.0, TRUE, NULL, NOW()),
('TRUCK-002', 'truck', 'in_transit', 'Chicago, IL', 18.0, FALSE, 'SHIP-003', '2024-01-15'),
('TRUCK-003', 'truck', 'maintenance', 'Memphis, TN', 22.0, TRUE, NULL, '2024-01-12'),
('CONT-A001', 'container', 'idle', 'Newark, NJ', 30.0, TRUE, NULL, NOW()),
('CONT-A002', 'container', 'in_transit', 'Houston, TX', 30.0, FALSE, 'SHIP-003', '2024-01-16'),
('VESSEL-001', 'vessel', 'in_transit', 'Atlantic Ocean', 500.0, TRUE, 'SHIP-001', '2024-01-20'),
('VESSEL-002', 'vessel', 'idle', 'Port of Charleston', 480.0, FALSE, NULL, NOW());

-- Sample Cold Chain Sensors
INSERT INTO cold_chain_sensors (sensor_id, shipment_id, container_id, latitude, longitude, temperature, humidity, timestamp) VALUES
('SENSOR-001', 'SHIP-001', 'CONT-001', 33.7490, -84.3880, 5.2, 45.0, '2024-01-10 08:00:00'),
('SENSOR-001', 'SHIP-001', 'CONT-001', 33.7490, -84.3880, 5.8, 46.0, '2024-01-10 09:00:00'),
('SENSOR-001', 'SHIP-001', 'CONT-001', 33.7490, -84.3880, 8.5, 47.0, '2024-01-10 10:00:00'),  -- Excursion
('SENSOR-002', 'SHIP-002', 'CONT-002', 38.5816, -92.1723, 3.5, 50.0, '2024-01-10 08:30:00'),
('SENSOR-002', 'SHIP-002', 'CONT-002', 38.5816, -92.1723, 4.2, 52.0, '2024-01-10 09:30:00'),
('SENSOR-005', 'SHIP-005', 'CONT-005', 25.7617, -80.1918, 2.8, 65.0, '2024-01-10 07:00:00'),
('SENSOR-005', 'SHIP-005', 'CONT-005', 25.7617, -80.1918, 3.5, 64.0, '2024-01-10 08:00:00');

-- Sample Temperature Alerts
INSERT INTO temperature_alerts (alert_id, shipment_id, sensor_id, temperature_recorded, expected_min, expected_max, duration_minutes, severity, regulatory_impact, timestamp, acknowledged) VALUES
('ALERT-001', 'SHIP-001', 'SENSOR-001', 8.5, 2.0, 8.0, 60, 'warning', 'FDA WARNING: Temperature excursion may affect vaccine potency. Requires QA review before distribution.', '2024-01-10 10:00:00', FALSE),
('ALERT-002', 'SHIP-005', 'SENSOR-005', 1.2, 2.0, 8.0, 45, 'critical', 'CRITICAL: Temperature below minimum. FDA 21 CFR 211.42 violation likely. Seafood quality compromised. Product destruction may be required.', '2024-01-10 07:30:00', FALSE);

-- Sample Route Recommendations
INSERT INTO route_recommendations (shipment_id, disruption_id, original_route, recommended_route, alternative_carrier, cost_impact, time_impact_hours, risk_score, implemented) VALUES
('SHIP-001', 'DISR-001', 'Chicago -> Miami (Port)', 'Chicago -> Jacksonville (Port)', 'ColdChain Express', 5000.00, 6, 25.0, FALSE),
('SHIP-002', 'DISR-002', 'Newark -> LA via I-80', 'Newark -> LA via I-40 (Southern Route)', 'FreshTransit', 3500.00, 12, 45.0, FALSE),
('SHIP-005', 'DISR-001', 'Miami -> Orlando (Direct)', 'Miami -> Tampa -> Orlando (Bypass)', 'Alternative Carrier', 2000.00, 3, 30.0, FALSE);
