"""Testes para o módulo exporter — exportação de datasets em CSV e Parquet."""

import pandas as pd
import pytest

from judo_data.exporter import (
    export_all,
    export_csv,
    export_excel,
    export_parquet,
    export_sqlite,
)


@pytest.fixture
def sample_df():
    """DataFrame simples para testes de exportação."""
    return pd.DataFrame(
        {
            "athlete_id": [1, 2, 3],
            "first_name": ["Alice", "Bob", "Charlie"],
            "country": ["BRA", "JPN", "FRA"],
        }
    )


@pytest.fixture
def output_dir(tmp_path):
    """Diretório temporário para output."""
    return tmp_path / "output"


# === Testes de export_csv ===


def test_export_csv_creates_file(sample_df, tmp_path):
    """export_csv deve criar um arquivo .csv no path especificado."""
    filepath = tmp_path / "test.csv"
    export_csv(sample_df, filepath)
    assert filepath.exists()


def test_export_csv_content_is_readable(sample_df, tmp_path):
    """Arquivo CSV criado deve ser legível pelo pandas."""
    filepath = tmp_path / "test.csv"
    export_csv(sample_df, filepath)

    loaded = pd.read_csv(filepath)
    assert len(loaded) == 3
    assert "athlete_id" in loaded.columns


def test_export_csv_preserves_data(sample_df, tmp_path):
    """Dados no CSV devem corresponder ao DataFrame original."""
    filepath = tmp_path / "test.csv"
    export_csv(sample_df, filepath)

    loaded = pd.read_csv(filepath)
    assert loaded["first_name"].tolist() == ["Alice", "Bob", "Charlie"]


# === Testes de export_parquet ===


def test_export_parquet_creates_file(sample_df, tmp_path):
    """export_parquet deve criar um arquivo .parquet no path especificado."""
    filepath = tmp_path / "test.parquet"
    export_parquet(sample_df, filepath)
    assert filepath.exists()


def test_export_parquet_content_is_readable(sample_df, tmp_path):
    """Arquivo Parquet criado deve ser legível pelo pandas."""
    filepath = tmp_path / "test.parquet"
    export_parquet(sample_df, filepath)

    loaded = pd.read_parquet(filepath)
    assert len(loaded) == 3
    assert "athlete_id" in loaded.columns


def test_export_parquet_preserves_data(sample_df, tmp_path):
    """Dados no Parquet devem corresponder ao DataFrame original."""
    filepath = tmp_path / "test.parquet"
    export_parquet(sample_df, filepath)

    loaded = pd.read_parquet(filepath)
    assert loaded["country"].tolist() == ["BRA", "JPN", "FRA"]


# === Testes de export_all ===


def test_export_all_creates_csv_and_parquet(sample_df, output_dir):
    """export_all deve criar arquivos CSV e Parquet para cada dataset."""
    datasets = {"test_dataset": sample_df}
    export_all(datasets, output_dir, formats=["csv", "parquet"])

    assert (output_dir / "test_dataset.csv").exists()
    assert (output_dir / "test_dataset.parquet").exists()


def test_export_all_creates_output_directory(sample_df, output_dir):
    """export_all deve criar o diretório de output se não existir."""
    assert not output_dir.exists()

    datasets = {"test_dataset": sample_df}
    export_all(datasets, output_dir, formats=["csv"])

    assert output_dir.exists()


def test_export_all_multiple_datasets(sample_df, output_dir):
    """export_all deve exportar múltiplos datasets."""
    datasets = {
        "dataset_a": sample_df,
        "dataset_b": sample_df,
        "dataset_c": sample_df,
    }
    export_all(datasets, output_dir, formats=["csv", "parquet"])

    assert (output_dir / "dataset_a.csv").exists()
    assert (output_dir / "dataset_b.csv").exists()
    assert (output_dir / "dataset_c.csv").exists()
    assert (output_dir / "dataset_a.parquet").exists()
    assert (output_dir / "dataset_b.parquet").exists()
    assert (output_dir / "dataset_c.parquet").exists()


def test_export_all_csv_only(sample_df, output_dir):
    """export_all com formats=['csv'] deve criar apenas CSV."""
    datasets = {"test_dataset": sample_df}
    export_all(datasets, output_dir, formats=["csv"])

    assert (output_dir / "test_dataset.csv").exists()
    assert not (output_dir / "test_dataset.parquet").exists()


def test_export_all_parquet_only(sample_df, output_dir):
    """export_all com formats=['parquet'] deve criar apenas Parquet."""
    datasets = {"test_dataset": sample_df}
    export_all(datasets, output_dir, formats=["parquet"])

    assert not (output_dir / "test_dataset.csv").exists()
    assert (output_dir / "test_dataset.parquet").exists()


def test_export_excel_creates_file(sample_df, tmp_path):
    """export_excel deve criar um arquivo .xlsx no path especificado."""
    filepath = tmp_path / "test.xlsx"
    export_excel(sample_df, filepath)
    assert filepath.exists()


def test_export_excel_content_is_readable(sample_df, tmp_path):
    """Arquivo Excel criado deve ser legível pelo pandas."""
    filepath = tmp_path / "test.xlsx"
    export_excel(sample_df, filepath)

    loaded = pd.read_excel(filepath)
    assert len(loaded) == 3
    assert "athlete_id" in loaded.columns
    assert loaded["first_name"].tolist() == ["Alice", "Bob", "Charlie"]


def test_export_sqlite_creates_file_with_tables(sample_df, tmp_path):
    """export_sqlite deve criar um arquivo .db e gravar as tabelas."""
    import sqlite3

    filepath = tmp_path / "test.db"
    datasets = {"athletes": sample_df, "competitions": sample_df}
    export_sqlite(datasets, filepath)
    assert filepath.exists()

    with sqlite3.connect(filepath) as conn:
        for table in ["athletes", "competitions"]:
            loaded = pd.read_sql(f"SELECT * FROM {table}", conn)
            assert len(loaded) == 3
            assert "athlete_id" in loaded.columns
            assert loaded["first_name"].tolist() == ["Alice", "Bob", "Charlie"]


def test_export_all_creates_excel_and_sqlite(sample_df, output_dir):
    """export_all deve suportar e criar arquivos nos formatos excel e sqlite."""
    datasets = {"test_dataset": sample_df}
    export_all(datasets, output_dir, formats=["excel", "sqlite"])

    assert (output_dir / "test_dataset.xlsx").exists()
    assert (output_dir / "judo_data.db").exists()


def test_export_empty_dataframe(tmp_path):
    """Exportar DataFrame vazio deve funcionar sem erro nos 4 formatos."""
    empty_df = pd.DataFrame(columns=["a", "b", "c"])

    csv_path = tmp_path / "empty.csv"
    export_csv(empty_df, csv_path)
    assert csv_path.exists()

    parquet_path = tmp_path / "empty.parquet"
    export_parquet(empty_df, parquet_path)
    assert parquet_path.exists()

    excel_path = tmp_path / "empty.xlsx"
    export_excel(empty_df, excel_path)
    assert excel_path.exists()

    db_path = tmp_path / "empty.db"
    export_sqlite({"empty_table": empty_df}, db_path)
    assert db_path.exists()
