-- DDL for table: judo_atle
-- Represents unique competitors extracted from the IJF API

CREATE TABLE IF NOT EXISTS judo_atle (
    athlete_id BIGINT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    country VARCHAR(3) NOT NULL, -- IOC Country Code (e.g. BRA, JPN)
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    weight_category VARCHAR(20),
    height REAL, -- Athlete height in cm (nullable)
    weight REAL  -- Athlete weight in kg (nullable)
);

-- Index to optimize searches/filtering by country
CREATE INDEX IF NOT EXISTS idx_judo_atle_country ON judo_atle(country);

-- Index to optimize searches/filtering by weight category
CREATE INDEX IF NOT EXISTS idx_judo_atle_weight_category ON judo_atle(weight_category);
