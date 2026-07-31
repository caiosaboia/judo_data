-- DDL for table: judo_atle_compt
-- Option 1: Physical table structure mirroring the consolidated CSV/Parquet output

CREATE TABLE IF NOT EXISTS judo_atle_compt (
    contest_id BIGINT PRIMARY KEY,
    competition_id BIGINT NOT NULL,
    competition_name VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    location VARCHAR(255),
    weight_category VARCHAR(20) NOT NULL,
    athlete_blue_id BIGINT NOT NULL,
    athlete_white_id BIGINT NOT NULL,
    winner_id BIGINT,
    winner_color VARCHAR(10) CHECK (winner_color IN ('blue', 'white')),
    fight_duration INTEGER NOT NULL,
    score_blue VARCHAR(255),
    score_white VARCHAR(255),
    
    -- Blue scores
    blue_ippon INTEGER DEFAULT 0 NOT NULL,
    blue_wazari INTEGER DEFAULT 0 NOT NULL,
    blue_yuko INTEGER DEFAULT 0 NOT NULL,
    blue_shido INTEGER DEFAULT 0 NOT NULL,
    blue_hansoukomake INTEGER DEFAULT 0 NOT NULL,
    
    -- White scores
    white_ippon INTEGER DEFAULT 0 NOT NULL,
    white_wazari INTEGER DEFAULT 0 NOT NULL,
    white_yuko INTEGER DEFAULT 0 NOT NULL,
    white_shido INTEGER DEFAULT 0 NOT NULL,
    white_hansoukomake INTEGER DEFAULT 0 NOT NULL,
    
    round VARCHAR(100) NOT NULL,
    
    -- Blue Athlete Side-by-Side Details
    blue_first_name VARCHAR(100),
    blue_last_name VARCHAR(100),
    blue_country VARCHAR(3),
    blue_gender CHAR(1),
    blue_weight_category VARCHAR(20),
    blue_height REAL,
    blue_weight REAL,
    
    -- White Athlete Side-by-Side Details
    white_first_name VARCHAR(100),
    white_last_name VARCHAR(100),
    white_country VARCHAR(3),
    white_gender CHAR(1),
    white_weight_category VARCHAR(20),
    white_height REAL,
    white_weight REAL,
    
    -- Foreign Keys
    FOREIGN KEY (athlete_blue_id) REFERENCES judo_atle(athlete_id),
    FOREIGN KEY (athlete_white_id) REFERENCES judo_atle(athlete_id),
    FOREIGN KEY (winner_id) REFERENCES judo_atle(athlete_id)
);


-- Option 2: Dynamic database VIEW (highly recommended for actual databases)
-- To execute this alternative view version:
-- 
-- CREATE VIEW view_judo_atle_compt AS
-- SELECT
--     c.*,
--     b.first_name AS blue_first_name,
--     b.last_name AS blue_last_name,
--     b.country AS blue_country,
--     b.gender AS blue_gender,
--     b.weight_category AS blue_weight_category,
--     b.height AS blue_height,
--     b.weight AS blue_weight,
--     w.first_name AS white_first_name,
--     w.last_name AS white_last_name,
--     w.country AS white_country,
--     w.gender AS white_gender,
--     w.weight_category AS white_weight_category,
--     w.height AS white_height,
--     w.weight AS white_weight
-- FROM judo_compt c
-- LEFT JOIN judo_atle b ON c.athlete_blue_id = b.athlete_id
-- LEFT JOIN judo_atle w ON c.athlete_white_id = w.athlete_id;
