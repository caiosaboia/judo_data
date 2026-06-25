"""Configurações e constantes do projeto judo_data."""

from pathlib import Path

# === API Configuration ===
BASE_URL = "https://data.ijf.org/api/get_json"

# Endpoints da API IJF (parâmetro `action`)
ACTIONS = {
    "competitions": "competition.get_list",
    "contests": "contest.find",
    "competitor": "competitor.info",
}

# Rate limiting: delay entre requests (em segundos)
REQUEST_DELAY = 0.5

# Concorrência máxima para requisições
MAX_CONCURRENT_REQUESTS = 5

# Timeout para requests HTTP (em segundos)
REQUEST_TIMEOUT = 30.0

# === Paths ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# === Export ===
EXPORT_FORMATS = ["csv", "parquet"]

DATASET_NAMES = {
    "athletes": "judo_atle",
    "competitions": "judo_compt",
    "merged": "judo_atle_compt",
}

# === Schema: colunas esperadas nos datasets ===
ATHLETE_COLUMNS = [
    "athlete_id",
    "first_name",
    "last_name",
    "country",
    "gender",
    "weight_category",
    "height",
    "weight",
]

CONTEST_COLUMNS = [
    "contest_id",
    "competition_id",
    "competition_name",
    "date",
    "location",
    "weight_category",
    "athlete_blue_id",
    "athlete_white_id",
    "winner_id",
    "winner_color",
    "fight_duration",
    "score_blue",
    "score_white",
    "blue_ippon",
    "blue_wazari",
    "blue_yuko",
    "blue_shido",
    "blue_hansoukomake",
    "white_ippon",
    "white_wazari",
    "white_yuko",
    "white_shido",
    "white_hansoukomake",
    "round",
]

BLUE_ATHLETE_COLUMNS = [
    "blue_first_name",
    "blue_last_name",
    "blue_country",
    "blue_gender",
    "blue_weight_category",
    "blue_height",
    "blue_weight",
]

WHITE_ATHLETE_COLUMNS = [
    "white_first_name",
    "white_last_name",
    "white_country",
    "white_gender",
    "white_weight_category",
    "white_height",
    "white_weight",
]

MERGED_COLUMNS = CONTEST_COLUMNS + BLUE_ATHLETE_COLUMNS + WHITE_ATHLETE_COLUMNS
