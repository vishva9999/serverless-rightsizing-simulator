-- AI Disaster Evacuation & Resource Allocation Command Center
-- Database Initialization Script
-- NOTE: All data represents a simulated test environment.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Schema metadata table for system tracking
CREATE TABLE IF NOT EXISTS system_metadata (
    key VARCHAR(64) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_metadata (key, value)
VALUES 
    ('simulation_mode', 'true'),
    ('emergency_services_integrated', 'false'),
    ('phase', '1_foundation')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;
