"""Testes para o módulo transformer — limpeza e transformação com Pandas."""

import pytest
import pandas as pd
import numpy as np

from judo_data.transformer import (
    transform_athletes,
    transform_contests,
    merge_datasets,
)
from judo_data.config import ATHLETE_COLUMNS, CONTEST_COLUMNS


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
    """transform_athletes com lista vazia deve retornar DataFrame vazio com colunas corretas."""
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


def test_transform_contests_location_is_string(raw_contests):
    """Location deve ser uma string."""
    result = transform_contests(raw_contests)
    assert result["location"].dtype == object  # string dtype in pandas


def test_transform_contests_empty_input():
    """transform_contests com lista vazia deve retornar DataFrame vazio com colunas corretas."""
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


def test_merge_datasets_has_role_column(sample_athletes_df, sample_contests_df):
    """DataFrame unificado deve ter coluna 'role' com valores 'blue'/'white'."""
    result = merge_datasets(sample_athletes_df, sample_contests_df)
    assert "role" in result.columns
    assert set(result["role"].unique()).issubset({"blue", "white"})


def test_merge_datasets_doubles_rows(sample_athletes_df, sample_contests_df):
    """Cada luta deve gerar 2 linhas (uma por atleta)."""
    result = merge_datasets(sample_athletes_df, sample_contests_df)

    # 2 lutas no mock -> 4 linhas (2 por luta)
    assert len(result) == 4


def test_merge_datasets_contains_athlete_info(sample_athletes_df, sample_contests_df):
    """Cada linha deve conter informações do atleta."""
    result = merge_datasets(sample_athletes_df, sample_contests_df)

    assert "first_name" in result.columns
    assert "last_name" in result.columns
    assert "country" in result.columns


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


def test_merge_datasets_empty_contests(sample_athletes_df):
    """merge com lutas vazio deve retornar DataFrame vazio."""
    empty_contests = pd.DataFrame(columns=CONTEST_COLUMNS)
    result = merge_datasets(sample_athletes_df, empty_contests)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
