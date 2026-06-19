"""Módulo exporter — exportação de DataFrames para CSV e Parquet."""

from pathlib import Path

import pandas as pd


def export_csv(df: pd.DataFrame, path: Path) -> None:
    """Salva o DataFrame como CSV no path especificado.

    Args:
        df: DataFrame a ser exportado.
        path: Caminho do arquivo CSV de saída.
    """
    df.to_csv(path, index=False)


def export_parquet(df: pd.DataFrame, path: Path) -> None:
    """Salva o DataFrame como Parquet no path especificado.

    Args:
        df: DataFrame a ser exportado.
        path: Caminho do arquivo Parquet de saída.
    """
    df.to_parquet(path, engine="pyarrow")


def export_all(
    datasets: dict[str, pd.DataFrame],
    output_dir: Path,
    formats: list[str],
) -> None:
    """Exporta múltiplos datasets nos formatos solicitados.

    Cria o diretório de saída caso não exista e itera sobre cada dataset,
    gerando os arquivos nos formatos indicados.

    Args:
        datasets: Dicionário {nome: DataFrame} com os datasets a exportar.
        output_dir: Diretório onde os arquivos serão criados.
        formats: Lista de formatos desejados ('csv' e/ou 'parquet').
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, df in datasets.items():
        if "csv" in formats:
            export_csv(df, output_dir / f"{name}.csv")
        if "parquet" in formats:
            export_parquet(df, output_dir / f"{name}.parquet")
