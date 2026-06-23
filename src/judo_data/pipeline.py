"""Pipeline principal — orquestra extração, transformação e exportação.

Fluxo:
    1. Busca competições do ano informado
    2. Para cada competição, busca as lutas
    3. Extrai IDs de atletas únicos
    4. Busca informações dos atletas
    5. Transforma dados brutos em DataFrames limpos
    6. Gera o dataset unificado (merge)
    7. Exporta os 3 datasets em CSV e Parquet
"""

import asyncio
import logging
from pathlib import Path

import pandas as pd
from tqdm.asyncio import tqdm

from judo_data.config import DATA_DIR, DATASET_NAMES, EXPORT_FORMATS
from judo_data.exporter import export_all
from judo_data.fetcher import JudoFetcher
from judo_data.transformer import merge_datasets, transform_athletes, transform_contests

logger = logging.getLogger(__name__)


async def run_pipeline(
    year: int,
    output_dir: Path | None = None,
    formats: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Executa a pipeline completa de extração de dados de judô.

    Parameters
    ----------
    year : int
        Ano até o qual captar dados de competições.
    output_dir : Path, optional
        Diretório de saída para os datasets. Usa ``config.DATA_DIR`` se não informado.
    formats : list[str], optional
        Lista de formatos para exportação (e.g., ['parquet'], ['csv'], etc.).
        Se não informado, usa EXPORT_FORMATS da config.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dicionário com os 3 datasets: judo_atle, judo_compt, judo_atle_compt.
    """
    if output_dir is None:
        output_dir = DATA_DIR

    if formats is None:
        formats = EXPORT_FORMATS

    fetcher = JudoFetcher()

    # --- 1. Buscar competições ---
    logger.info("Buscando competições do ano %d...", year)
    raw_competitions = await fetcher.fetch_competitions(year)
    logger.info("Encontradas %d competições.", len(raw_competitions))

    # --- 2. Buscar lutas de cada competição ---
    all_raw_contests: list[dict] = []
    for comp in raw_competitions:
        raw_comp_id = comp.get("id_competition")
        comp_name = comp.get("name", "Desconhecida")
        if not raw_comp_id:
            continue
        comp_id = int(raw_comp_id)
        logger.info("Buscando lutas de '%s' (ID: %d)...", comp_name, comp_id)
        contests = await fetcher.fetch_contests(comp_id)
        # Enriquece cada luta com dados da competição (caso não venham da API)
        for contest in contests:
            contest.setdefault("id_competition", comp_id)
            contest.setdefault("competition_name", comp_name)
            venue = contest.get("venue", "")
            if not venue:
                city = comp.get("city", "")
                country = comp.get("country", "")
                contest["venue"] = f"{city}, {country}" if city else country
        all_raw_contests.extend(contests)

    logger.info("Total de lutas coletadas: %d", len(all_raw_contests))

    # --- 3. Extrair IDs de atletas únicos ---
    athlete_ids: set[int] = set()
    for contest in all_raw_contests:
        blue_id = contest.get("id_person_blue")
        white_id = contest.get("id_person_white")
        if blue_id is not None:
            athlete_ids.add(int(blue_id))
        if white_id is not None:
            athlete_ids.add(int(white_id))

    logger.info("Atletas únicos encontrados: %d", len(athlete_ids))

    # --- 4. Buscar informações dos atletas ---
    logger.info(
        "Buscando informações dos atletas "
        "(isso pode demorar devido ao rate limit da API)..."
    )

    semaphore = asyncio.Semaphore(fetcher.max_concurrent)

    async def worker_with_progress(athlete_id: int, index: int) -> dict:
        """Worker que busca um atleta e atualiza a barra de progresso."""
        async with semaphore:
            if fetcher.delay > 0:
                await asyncio.sleep(index * fetcher.delay / fetcher.max_concurrent)
            return await fetcher.fetch_athlete(athlete_id)

    athlete_ids_list = list(athlete_ids)
    tasks = [worker_with_progress(aid, idx) for idx, aid in enumerate(athlete_ids_list)]
    raw_athletes = await tqdm.gather(
        *tasks,
        desc="Capturando atletas",
        total=len(athlete_ids_list),
        unit="atleta",
    )
    # Filtra atletas que retornaram dados vazios
    raw_athletes = [a for a in raw_athletes if a]
    logger.info("Atletas com dados obtidos: %d", len(raw_athletes))

    # --- 5. Transformar dados ---
    logger.info("Transformando dados...")
    athletes_df = transform_athletes(raw_athletes)
    contests_df = transform_contests(all_raw_contests)

    # --- 6. Gerar dataset unificado ---
    merged_df = merge_datasets(athletes_df, contests_df)

    # --- 7. Montar dicionário de resultados ---
    datasets = {
        DATASET_NAMES["athletes"]: athletes_df,
        DATASET_NAMES["competitions"]: contests_df,
        DATASET_NAMES["merged"]: merged_df,
    }

    # --- 8. Exportar ---
    logger.info("Exportando datasets para %s...", output_dir)
    export_all(datasets, output_dir, formats)
    logger.info("Pipeline concluída com sucesso!")

    for name, df in datasets.items():
        logger.info("  %s: %d linhas x %d colunas", name, len(df), len(df.columns))

    return datasets


def main():
    """Entry point para execução via CLI."""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    print("=" * 60)
    print("  JUDO DATA PIPELINE")
    print("  Extração de dados de competições de judô (IJF)")
    print("=" * 60)
    print()

    try:
        year_input = input("Até qual ano deseja captar os dados? ")
        year = int(year_input.strip())
    except (ValueError, EOFError):
        print("Erro: informe um ano válido (ex: 2024)")
        sys.exit(1)

    print("\nEscolha o formato de exportação:")
    print("  1. parquet (Padrão)")
    print("  2. csv")
    print("  3. excel")
    print("  4. banco de dados (SQLite)")
    try:
        format_input = input("Opção (1-4): ").strip()
    except EOFError:
        format_input = "1"

    if format_input == "2":
        selected_format = "csv"
    elif format_input == "3":
        selected_format = "excel"
    elif format_input == "4":
        selected_format = "sqlite"
    else:
        selected_format = "parquet"

    print(
        f"\nIniciando pipeline para o ano {year} "
        f"com exportação em formato '{selected_format}'..."
    )
    print()

    datasets = asyncio.run(run_pipeline(year=year, formats=[selected_format]))

    print()
    print("=" * 60)
    print("  RESULTADO")
    print("=" * 60)
    for name, df in datasets.items():
        print(f"  {name}: {len(df)} linhas x {len(df.columns)} colunas")
    print()
    if selected_format == "sqlite":
        print(f"Banco de dados SQLite salvo em: {DATA_DIR}/judo_data.db")
    else:
        print(f"Arquivos salvos em: {DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
