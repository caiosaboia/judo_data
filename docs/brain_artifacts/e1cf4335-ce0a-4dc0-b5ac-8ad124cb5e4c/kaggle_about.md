# International Judo Federation (IJF) Match & Athlete Dataset

## Overview
This dataset contains historical records of official judo competitions, individual matches (contests), and detailed athlete profiles extracted directly from the official **International Judo Federation (IJF)** public API (`data.ijf.org`). It is designed for sports analytics, match outcome prediction, athlete profiling, and network/spatial analysis of judo matches worldwide.

---

## Context
Judo is a dynamic, high-intensity martial art and Olympic sport. Matches are decided by complex combinations of scoring techniques (*Ippon*, *Waza-ari*), active tactical elements, and penalties (*Shido*, *Hansoku-make*). This dataset enables researchers, data scientists, and sports analysts to explore the key factors that lead to victory, the influence of physical attributes (height, weight), and the performance dynamics of athletes across weight categories and years.

---

## Dataset Structure
The dataset is structured into three main tables, exported in both **CSV** and **Parquet** formats:

### 1. Athletes Table (`judo_atle`)
Contains demographic and physical profiles of unique judo competitors.
* **`athlete_id`** (Integer): Unique ID of the competitor.
* **`first_name`** (String): Given name.
* **`last_name`** (String): Family name.
* **`country`** (String): Three-letter IOC country code representing the athlete's nation.
* **`gender`** (String): `M` (Male) or `F` (Female).
* **`weight_category`** (String): Athlete's primary weight class (e.g. `-81 kg`, `+100 kg`).
* **`height`** (Float, Nullable): Height of the athlete in centimeters (where available).
* **`weight`** (Float, Nullable): Physical weight estimate in kilograms (derived from category or profile).

### 2. Contests/Matches Table (`judo_compt`)
Contains records of individual fights, scores, penalties, and competition contexts.
* **`contest_id`** (Integer): Unique ID of the match.
* **`competition_id`** (Integer): Unique ID of the tournament.
* **`competition_name`** (String): Name of the tournament (e.g. *Olympic Games*, *Grand Slam*).
* **`date`** (Datetime): The date of the fight.
* **`location`** (String): Venue city and country.
* **`weight_category`** (String): Weight category of the fight.
* **`athlete_blue_id`** (Integer): Athlete ID fighting in the blue judogi.
* **`athlete_white_id`** (Integer): Athlete ID fighting in the white judogi.
* **`winner_id`** (Integer, Nullable): Athlete ID of the winner (null in case of disqualifications/draws).
* **`winner_color`** (String, Nullable): `'blue'`, `'white'`, or `null`.
* **`fight_duration`** (Integer): Match duration in seconds.
* **`score_blue`** / **`score_white`** (String): Formatted text representation of scoring.
* **`blue_ippon`** / **`white_ippon`** (Integer): Count of Ippon scores (typically `0` or `1`).
* **`blue_wazari`** / **`white_wazari`** (Integer): Count of Waza-ari scores.
* **`blue_yuko`** / **`white_yuko`** (Integer): Count of Yuko scores (legacy score format).
* **`blue_shido`** / **`white_shido`** (Integer): Count of tactical penalties received (ranges from `0` to `3`).
* **`blue_hansoukomake`** / **`white_hansoukomake`** (Integer): Direct disqualification status (`1` if penalized, `0` otherwise).
* **`round`** (String): Competition stage (e.g. *Round of 32*, *Semi-Final*, *Final*).

### 3. Consolidated Table (`judo_atle_compt`)
A fully-merged, flat representation combining all matches with side-by-side details of both combatants (prefixed by `blue_` and `white_` respectively). This is the perfect format for training predictive machine learning models.

---

## Inspiration & Research Questions
Here are some interesting analysis projects you can build using this dataset:
1. **Predict Match Outcomes:** Train classification models (like XGBoost, LightGBM, or Neural Networks) using side-by-side attributes to predict the winner (`winner_color` or `winner_id`).
2. **Physical Disparity Impact:** How does a height or estimated weight difference between opponents influence the probability of winning?
3. **Penalty Distribution & Tactical Play:** Analyze the rate of matches won by scoring techniques vs. matches decided by opponent penalties (*Shido* accumulation).
4. **Duration Trends:** Predict match duration based on weight category and competition round. Do heavyweights tend to have shorter or longer matches?
5. **National Performance:** Map the dominance of different nations across time and weight classes (spatial analysis).

---

## Data Source & Attribution
The data is gathered from the publicly accessible API endpoints of the **International Judo Federation (IJF)**:
* **Base API:** `https://data.ijf.org/api/get_json`
* All data remains the property of the International Judo Federation (IJF). This dataset is compiled strictly for educational, research, and non-commercial purposes.
