"""Testes para o módulo transformer — limpeza e transformação com Pandas."""

import pandas as pd

from judo_data.config import ATHLETE_COLUMNS, CONTEST_COLUMNS
from judo_data.transformer import (
    merge_datasets,
    transform_athletes,
    transform_contests,
)

# === Testes de transform_athletes ===


def test_transform_athletes_returns_dataframe(raw_athletes):
    """transform_athletes deve retornar um pandas DataFrame."""
    result = transform_athletes(raw_athletes)
    assert isinstance(result, pd.DataFrame)


def test_transform_athletes_has_correct_columns(raw_athletes):
    """DataFrame de atletas deve ter todas as colunas definidas no schema."""
    result = transform_athletes(raw_athletes)
    for col in ATHLETE_COLUMNS:
        assert col in result.columns, f"Coluna ausente: {col}"


def test_transform_athletes_maps_fields_correctly(raw_athletes):
    """Campos da API devem ser mapeados para os nomes corretos."""
    result = transform_athletes(raw_athletes)

    # id_person -> athlete_id
    assert 1001 in result["athlete_id"].values

    # family_name -> last_name
    assert "Nagase" in result["last_name"].values

    # given_name -> first_name
    assert "Takanori" in result["first_name"].values


def test_transform_athletes_normalizes_gender(raw_athletes):
    """Gender deve ser normalizado para 'M' ou 'F'."""
    result = transform_athletes(raw_athletes)

    assert set(result["gender"].unique()).issubset({"M", "F"})


def test_transform_athletes_handles_missing_height(raw_athletes):
    """Atletas sem altura devem ter null/NaN na coluna height."""
    result = transform_athletes(raw_athletes)

    # Buchard (id 1004) tem height=None nos mocks
    buchard = result[result["athlete_id"] == 1004]
    assert buchard["height"].isna().all()


def test_transform_athletes_handles_missing_weight(raw_athletes):
    """Atletas sem peso devem ter null/NaN na coluna weight."""
    result = transform_athletes(raw_athletes)

    buchard = result[result["athlete_id"] == 1004]
    assert buchard["weight"].isna().all()


def test_transform_athletes_deduplicates(raw_athletes):
    """Se houver atletas duplicados, deve manter apenas um."""
    duplicated = raw_athletes + [raw_athletes[0]]  # Duplica o primeiro
    result = transform_athletes(duplicated)

    # Deve ter o mesmo número que raw_athletes (sem duplicata)
    assert len(result) == len(raw_athletes)


def test_transform_athletes_country_is_uppercase(raw_athletes):
    """Código do país deve estar em maiúsculas (IOC code)."""
    result = transform_athletes(raw_athletes)

    for country in result["country"]:
        assert country == country.upper()


def test_transform_athletes_empty_input():
    """transform_athletes com lista vazia retorna DataFrame vazio com colunas."""
    result = transform_athletes([])
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
    for col in ATHLETE_COLUMNS:
        assert col in result.columns


# === Testes de transform_contests ===


def test_transform_contests_returns_dataframe(raw_contests):
    """transform_contests deve retornar um pandas DataFrame."""
    result = transform_contests(raw_contests)
    assert isinstance(result, pd.DataFrame)


def test_transform_contests_has_correct_columns(raw_contests):
    """DataFrame de lutas deve ter todas as colunas definidas no schema."""
    result = transform_contests(raw_contests)
    for col in CONTEST_COLUMNS:
        assert col in result.columns, f"Coluna ausente: {col}"


def test_transform_contests_maps_fields_correctly(raw_contests):
    """Campos da API devem ser mapeados para os nomes corretos."""
    result = transform_contests(raw_contests)

    assert 10001 in result["contest_id"].values
    assert 2653 in result["competition_id"].values
    assert 1001 in result["athlete_blue_id"].values
    assert 1002 in result["athlete_white_id"].values


def test_transform_contests_converts_duration_to_seconds(raw_contests):
    """Duração deve ser convertida de 'M:SS' para segundos inteiros."""
    result = transform_contests(raw_contests)

    # "4:00" -> 240 segundos
    row = result[result["contest_id"] == 10001]
    assert row["fight_duration"].values[0] == 240

    # "2:35" -> 155 segundos
    row = result[result["contest_id"] == 10002]
    assert row["fight_duration"].values[0] == 155


def test_duration_to_seconds_robustness():
    """_duration_to_seconds deve lidar de forma robusta com diversos formatos."""
    import numpy as np

    from judo_data.transformer import _duration_to_seconds

    assert _duration_to_seconds("4:00") == 240
    assert _duration_to_seconds("2:35") == 155
    assert _duration_to_seconds(240) == 240
    assert _duration_to_seconds(155.0) == 155
    assert _duration_to_seconds("240") == 240
    assert _duration_to_seconds(None) == 0
    assert _duration_to_seconds(np.nan) == 0
    assert _duration_to_seconds("invalid") == 0
    assert _duration_to_seconds("") == 0


def test_format_score_robustness():
    """_format_score deve formatar placares da API de forma robusta."""
    from judo_data.transformer import _format_score

    assert _format_score("1", "0", "0", "0") == "Ippon"
    assert _format_score("0", "1", "0", "2") == "Waza-ari, 2 Shido"
    assert _format_score("0", "0", "1", "1") == "Yuko, 1 Shido"
    assert _format_score(None, None, None, None) == ""


def test_transform_athletes_fallbacks():
    """Testa fallbacks de país, categorias e peso em transform_athletes."""
    raw = [
        {
            "id_person": 1009,
            "family_name": "Silva",
            "given_name": "Rafael",
            "country_short": "BRA",
            "gender": "male",
            "categories": ["-100", "+100"],
            "height": 195,
        }
    ]
    df = transform_athletes(raw)
    assert df["country"].values[0] == "BRA"
    assert df["weight_category"].values[0] == "-100"
    assert df["weight"].values[0] == 100.0


def test_transform_contests_date_is_datetime(raw_contests):
    """Coluna date deve ser do tipo datetime."""
    result = transform_contests(raw_contests)
    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_transform_contests_handles_null_winner(raw_contests):
    """Lutas sem vencedor devem ter winner_id como NaN."""
    result = transform_contests(raw_contests)

    # Contest 10003 tem id_winner=None no mock
    row = result[result["contest_id"] == 10003]
    assert row["winner_id"].isna().all()


def test_transform_contests_populates_winner_color(raw_contests):
    """winner_color deve ser populado com 'blue', 'white' ou None."""
    result = transform_contests(raw_contests)

    # Contest 10001: winner_id=1001 (athlete_blue_id=1001) -> winner_color='blue'
    row_blue = result[result["contest_id"] == 10001]
    assert row_blue["winner_color"].values[0] == "blue"

    # Contest 10002: winner_id=1004 (athlete_white_id=1004) -> winner_color='white'
    row_white = result[result["contest_id"] == 10002]
    assert row_white["winner_color"].values[0] == "white"

    # Contest 10003: winner_id=None -> winner_color=None/NaN
    row_none = result[result["contest_id"] == 10003]
    assert pd.isna(row_none["winner_color"].values[0])


def test_transform_contests_location_is_string(raw_contests):
    """Location deve ser uma string."""
    result = transform_contests(raw_contests)
    assert result["location"].dtype == object  # string dtype in pandas


def test_transform_contests_empty_input():
    """transform_contests com lista vazia retorna DataFrame vazio com colunas."""
    result = transform_contests([])
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
    for col in CONTEST_COLUMNS:
        assert col in result.columns


# === Testes de merge_datasets ===


def test_merge_datasets_returns_dataframe(sample_athletes_df, sample_contests_df):
    """merge_datasets deve retornar um pandas DataFrame."""
    result = merge_datasets(sample_athletes_df, sample_contests_df)
    assert isinstance(result, pd.DataFrame)


def test_merge_datasets_has_side_by_side_athlete_info(
    sample_athletes_df, sample_contests_df
):
    """DataFrame unificado deve conter informações de ambos os atletas lado a lado."""
    result = merge_datasets(sample_athletes_df, sample_contests_df)

    # Verifica colunas do atleta azul
    assert "blue_first_name" in result.columns
    assert "blue_last_name" in result.columns
    assert "blue_country" in result.columns

    # Verifica colunas do atleta branco
    assert "white_first_name" in result.columns
    assert "white_last_name" in result.columns
    assert "white_country" in result.columns


def test_merge_datasets_keeps_row_count(sample_athletes_df, sample_contests_df):
    """Cada luta deve gerar exatamente 1 linha."""
    result = merge_datasets(sample_athletes_df, sample_contests_df)

    # 2 lutas no mock -> 2 linhas no resultado
    assert len(result) == len(sample_contests_df)


def test_merge_datasets_contains_contest_info(sample_athletes_df, sample_contests_df):
    """Cada linha deve conter informações da luta."""
    result = merge_datasets(sample_athletes_df, sample_contests_df)

    assert "competition_name" in result.columns
    assert "fight_duration" in result.columns
    assert "round" in result.columns


def test_merge_datasets_empty_athletes(sample_contests_df):
    """merge com atletas vazio deve retornar DataFrame vazio."""
    empty_athletes = pd.DataFrame(columns=ATHLETE_COLUMNS)
    result = merge_datasets(empty_athletes, sample_contests_df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_merge_datasets_empty_contests(sample_athletes_df):
    """merge com lutas vazio deve retornar DataFrame vazio."""
    empty_contests = pd.DataFrame(columns=CONTEST_COLUMNS)
    result = merge_datasets(sample_athletes_df, empty_contests)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
