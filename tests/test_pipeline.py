"""Testes para o módulo pipeline — orquestrador da pipeline completa."""

from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from judo_data.config import DATASET_NAMES
from judo_data.pipeline import run_pipeline


@pytest.fixture
def mock_fetcher(raw_competitions, raw_contests, raw_athletes):
    """Mock do JudoFetcher com dados de exemplo."""
    fetcher = AsyncMock()
    fetcher.fetch_competitions = AsyncMock(return_value=raw_competitions)
    fetcher.fetch_contests = AsyncMock(return_value=raw_contests)
    fetcher.fetch_athlete = AsyncMock(
        side_effect=lambda aid: next(
            (a for a in raw_athletes if a["id_person"] == aid),
            raw_athletes[0],
        )
    )
    fetcher.fetch_all_athletes = AsyncMock(return_value=raw_athletes)
    fetcher.max_concurrent = 5  # Must be int for Semaphore
    fetcher.delay = 0  # No delay in tests
    return fetcher


@pytest.mark.asyncio
async def test_pipeline_produces_three_datasets(mock_fetcher, tmp_path):
    """Pipeline deve produzir exatamente 3 datasets."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        result = await run_pipeline(year=2024, output_dir=tmp_path)

    assert isinstance(result, dict)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_pipeline_datasets_are_dataframes(mock_fetcher, tmp_path):
    """Todos os datasets retornados devem ser pandas DataFrames."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        result = await run_pipeline(year=2024, output_dir=tmp_path)

    for name, df in result.items():
        assert isinstance(df, pd.DataFrame), f"{name} não é DataFrame"


@pytest.mark.asyncio
async def test_pipeline_creates_output_files(mock_fetcher, tmp_path):
    """Pipeline deve criar arquivos CSV e Parquet no diretório de saída."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        await run_pipeline(year=2024, output_dir=tmp_path)

    # Verifica que os 3 datasets foram exportados em ambos os formatos
    for _, name in DATASET_NAMES.items():
        assert (tmp_path / f"{name}.csv").exists(), f"{name}.csv não existe"
        assert (tmp_path / f"{name}.parquet").exists(), f"{name}.parquet não existe"


@pytest.mark.asyncio
async def test_pipeline_calls_fetcher_with_year(mock_fetcher, tmp_path):
    """Pipeline deve chamar fetch_competitions com o ano correto."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        await run_pipeline(year=2024, output_dir=tmp_path)

    mock_fetcher.fetch_competitions.assert_called_once_with(2024)


@pytest.mark.asyncio
async def test_pipeline_athletes_df_not_empty(mock_fetcher, tmp_path):
    """Dataset de atletas não deve estar vazio quando há dados."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        result = await run_pipeline(year=2024, output_dir=tmp_path)

    athletes_key = DATASET_NAMES["athletes"]
    assert len(result[athletes_key]) > 0


@pytest.mark.asyncio
async def test_pipeline_contests_df_not_empty(mock_fetcher, tmp_path):
    """Dataset de competições não deve estar vazio quando há dados."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        result = await run_pipeline(year=2024, output_dir=tmp_path)

    compt_key = DATASET_NAMES["competitions"]
    assert len(result[compt_key]) > 0


@pytest.mark.asyncio
async def test_pipeline_merged_df_has_role_column(mock_fetcher, tmp_path):
    """Dataset unificado deve conter coluna 'role'."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        result = await run_pipeline(year=2024, output_dir=tmp_path)

    merged_key = DATASET_NAMES["merged"]
    assert "role" in result[merged_key].columns


@pytest.mark.asyncio
async def test_pipeline_creates_selected_output_format(mock_fetcher, tmp_path):
    """Pipeline deve criar apenas arquivos do formato selecionado (ex: excel)."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        await run_pipeline(year=2024, output_dir=tmp_path, formats=["excel"])

    for _, name in DATASET_NAMES.items():
        assert (tmp_path / f"{name}.xlsx").exists(), f"{name}.xlsx não existe"
        assert not (tmp_path / f"{name}.csv").exists()
        assert not (tmp_path / f"{name}.parquet").exists()


@pytest.mark.asyncio
async def test_pipeline_creates_sqlite_output(mock_fetcher, tmp_path):
    """Pipeline deve criar apenas o banco de dados sqlite quando selecionado."""
    with patch("judo_data.pipeline.JudoFetcher", return_value=mock_fetcher):
        await run_pipeline(year=2024, output_dir=tmp_path, formats=["sqlite"])

    assert (tmp_path / "judo_data.db").exists()
    for _, name in DATASET_NAMES.items():
        assert not (tmp_path / f"{name}.csv").exists()
