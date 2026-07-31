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
