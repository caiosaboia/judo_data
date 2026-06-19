"""Testes para o módulo config."""

from pathlib import Path


def test_base_url_is_string():
    from judo_data.config import BASE_URL

    assert isinstance(BASE_URL, str)
    assert BASE_URL.startswith("https://")


def test_actions_dict_has_required_keys():
    from judo_data.config import ACTIONS

    assert "competitions" in ACTIONS
    assert "contests" in ACTIONS
    assert "competitor" in ACTIONS


def test_data_dir_is_path():
    from judo_data.config import DATA_DIR

    assert isinstance(DATA_DIR, Path)


def test_dataset_names_has_three_entries():
    from judo_data.config import DATASET_NAMES

    assert len(DATASET_NAMES) == 3
    assert "athletes" in DATASET_NAMES
    assert "competitions" in DATASET_NAMES
    assert "merged" in DATASET_NAMES


def test_athlete_columns_completeness():
    from judo_data.config import ATHLETE_COLUMNS

    required = [
        "athlete_id",
        "first_name",
        "last_name",
        "country",
        "gender",
        "weight_category",
        "height",
        "weight",
    ]
    for col in required:
        assert col in ATHLETE_COLUMNS, f"Missing column: {col}"


def test_contest_columns_completeness():
    from judo_data.config import CONTEST_COLUMNS

    required = [
        "contest_id",
        "competition_id",
        "competition_name",
        "date",
        "location",
        "weight_category",
        "athlete_blue_id",
        "athlete_white_id",
        "winner_id",
        "fight_duration",
        "round",
    ]
    for col in required:
        assert col in CONTEST_COLUMNS, f"Missing column: {col}"


def test_export_formats():
    from judo_data.config import EXPORT_FORMATS

    assert "csv" in EXPORT_FORMATS
    assert "parquet" in EXPORT_FORMATS


def test_request_delay_is_positive():
    from judo_data.config import REQUEST_DELAY

    assert REQUEST_DELAY > 0
