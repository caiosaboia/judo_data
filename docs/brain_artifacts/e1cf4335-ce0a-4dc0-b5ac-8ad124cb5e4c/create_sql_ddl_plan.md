# Plan: Create SQL DDL Scripts for Judo Output Datasets

This plan outlines the creation of a new `sql/` folder containing SQL DDL scripts for each of the three output tables in the pipeline: `judo_atle`, `judo_compt`, and the consolidated dataset `judo_atle_compt`.

---

## Goal Description
We will create a structured directory named `sql` in the project root containing independent `*.sql` files for each unique output table:
- `sql/judo_atle.sql`: Schema for athlete profiles.
- `sql/judo_compt.sql`: Schema for tournament matches (contests), scores, and durations.
- `sql/judo_atle_compt.sql`: Schema for the consolidated table (containing match and both athletes' side-by-side details). We will offer both a table structure DDL and an alternative dynamic VIEW definition.

The DDL scripts will be written in Standard SQL/PostgreSQL compatible dialect, utilizing `CREATE TABLE IF NOT EXISTS` for safe incremental executions. They will include data types, column comments, primary/foreign keys, and performance-enhancing indexes.

---

## User Review Required
> [!IMPORTANT]
> **Consolidated Table (`judo_atle_compt`):**
> By default, `judo_atle_compt` is modeled as a physical table mirroring the CSV/Parquet export. However, in relational database design, this side-by-side data can be modeled as a dynamic `VIEW` to avoid data duplication.
> In `sql/judo_atle_compt.sql`, we provide **both** options:
> 1. A physical table schema (to copy the pipeline's exact output table).
> 2. A database view definition (using `CREATE VIEW` with joins on `judo_atle`).

---

## Proposed Changes

### Database Schemas Folder
We will create a new `sql/` folder containing:

#### [NEW] `sql/judo_atle.sql`
DDL for the athlete table:
```sql
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
```

---

#### [NEW] `sql/judo_compt.sql`
DDL for the contests/matches table, including foreign keys referencing the athlete table:
```sql
-- DDL for table: judo_compt
-- Represents tournament matches (contests) and detailed scoring/penalties

CREATE TABLE IF NOT EXISTS judo_compt (
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
    fight_duration INTEGER NOT NULL, -- Match duration in seconds
    score_blue VARCHAR(255),
    score_white VARCHAR(255),
    
    -- Score details (Ippon, Wazari, Yuko, Shidos, Disqualification)
    blue_ippon INTEGER DEFAULT 0 NOT NULL,
    blue_wazari INTEGER DEFAULT 0 NOT NULL,
    blue_yuko INTEGER DEFAULT 0 NOT NULL,
    blue_shido INTEGER DEFAULT 0 NOT NULL,
    blue_hansoukomake INTEGER DEFAULT 0 NOT NULL,
    
    white_ippon INTEGER DEFAULT 0 NOT NULL,
    white_wazari INTEGER DEFAULT 0 NOT NULL,
    white_yuko INTEGER DEFAULT 0 NOT NULL,
    white_shido INTEGER DEFAULT 0 NOT NULL,
    white_hansoukomake INTEGER DEFAULT 0 NOT NULL,
    
    round VARCHAR(100) NOT NULL,
    
    -- Foreign Keys
    FOREIGN KEY (athlete_blue_id) REFERENCES judo_atle(athlete_id),
    FOREIGN KEY (athlete_white_id) REFERENCES judo_atle(athlete_id),
    FOREIGN KEY (winner_id) REFERENCES judo_atle(athlete_id)
);

-- Indexes for performance on critical foreign keys and query patterns
CREATE INDEX IF NOT EXISTS idx_judo_compt_blue_athlete ON judo_compt(athlete_blue_id);
CREATE INDEX IF NOT EXISTS idx_judo_compt_white_athlete ON judo_compt(athlete_white_id);
CREATE INDEX IF NOT EXISTS idx_judo_compt_competition ON judo_compt(competition_id);
CREATE INDEX IF NOT EXISTS idx_judo_compt_date ON judo_compt(date);
```

---

#### [NEW] `sql/judo_atle_compt.sql`
DDL for the consolidated table and/or view, linking both opponents side-by-side:
```sql
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
```

---

## Verification Plan

### Manual Verification
1. We will verify the syntax validity of the created DDL scripts by executing them against a local temporary SQLite test database using Python's `sqlite3` module.
2. We will check that the table structures match the output columns in `src/judo_data/config.py` perfectly.
3. We will run the project's test suite to ensure no existing tests are broken.
