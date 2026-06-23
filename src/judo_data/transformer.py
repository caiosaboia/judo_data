"""Transformação de dados brutos da API IJF em DataFrames limpos."""

import pandas as pd

from judo_data.config import ATHLETE_COLUMNS, CONTEST_COLUMNS

# Mapeamento de campos da API → schema do projeto
_ATHLETE_FIELD_MAP = {
    "id_person": "athlete_id",
    "given_name": "first_name",
    "family_name": "last_name",
    "country": "country",
    "gender": "gender",
    "weight_category": "weight_category",
    "height": "height",
    "weight": "weight",
}

_CONTEST_FIELD_MAP = {
    "id_fight": "contest_id",
    "id_competition": "competition_id",
    "competition_name": "competition_name",
    "date": "date",
    "venue": "location",
    "weight": "weight_category",
    "id_person_blue": "athlete_blue_id",
    "id_person_white": "athlete_white_id",
    "id_winner": "winner_id",
    "duration": "fight_duration",
    "score_blue": "score_blue",
    "score_white": "score_white",
    "round": "round",
}

_GENDER_MAP = {
    "male": "M",
    "female": "F",
}


def _duration_to_seconds(duration: str) -> int:
    """Converte duração no formato 'M:SS' para segundos inteiros.

    Exemplos:
        '4:00' → 240
        '2:35' → 155
    """
    parts = duration.split(":")
    minutes = int(parts[0])
    seconds = int(parts[1])
    return minutes * 60 + seconds


def transform_athletes(raw_data: list[dict]) -> pd.DataFrame:
    """Transforma dados brutos de atletas em DataFrame limpo.

    Mapeamento de campos, normalização de gênero, deduplicação
    e tratamento de valores nulos (height, weight).

    Args:
        raw_data: Lista de dicts vindos da API IJF.

    Returns:
        DataFrame com colunas definidas em ATHLETE_COLUMNS.
    """
    if not raw_data:
        return pd.DataFrame(columns=ATHLETE_COLUMNS)

    # Seleciona e renomeia apenas os campos que interessam
    records = []
    for entry in raw_data:
        record = {}
        for api_field, schema_field in _ATHLETE_FIELD_MAP.items():
            record[schema_field] = entry.get(api_field)
        records.append(record)

    df = pd.DataFrame(records, columns=ATHLETE_COLUMNS)

    # Normaliza gênero: 'male' → 'M', 'female' → 'F'
    df["gender"] = df["gender"].str.lower().map(_GENDER_MAP)

    # Country code sempre em maiúsculas (IOC)
    df["country"] = df["country"].str.upper()

    # Converte athlete_id, height e weight para numérico
    df["athlete_id"] = pd.to_numeric(df["athlete_id"], errors="coerce")
    df["height"] = pd.to_numeric(df["height"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    # Deduplicação por athlete_id, mantém a primeira ocorrência
    return df.drop_duplicates(subset="athlete_id", keep="first").reset_index(drop=True)


def transform_contests(raw_data: list[dict]) -> pd.DataFrame:
    """Transforma dados brutos de lutas em DataFrame limpo.

    Mapeamento de campos, conversão de duração 'M:SS' → segundos,
    parsing de data e tratamento de winner_id nulo.

    Args:
        raw_data: Lista de dicts vindos da API IJF.

    Returns:
        DataFrame com colunas definidas em CONTEST_COLUMNS.
    """
    if not raw_data:
        return pd.DataFrame(columns=CONTEST_COLUMNS)

    records = []
    for entry in raw_data:
        record = {}
        for api_field, schema_field in _CONTEST_FIELD_MAP.items():
            record[schema_field] = entry.get(api_field)
        records.append(record)

    df = pd.DataFrame(records, columns=CONTEST_COLUMNS)

    # Garante que as colunas de ID sejam numéricas para evitar erro no merge
    df["contest_id"] = pd.to_numeric(df["contest_id"], errors="coerce")
    df["competition_id"] = pd.to_numeric(df["competition_id"], errors="coerce")
    df["athlete_blue_id"] = pd.to_numeric(df["athlete_blue_id"], errors="coerce")
    df["athlete_white_id"] = pd.to_numeric(df["athlete_white_id"], errors="coerce")
    df["winner_id"] = pd.to_numeric(df["winner_id"], errors="coerce")

    # Garante que location é object dtype (compatibilidade com pandas StringDtype)
    df["location"] = df["location"].astype(object)

    # Converte duração 'M:SS' → int (segundos)
    df["fight_duration"] = df["fight_duration"].apply(_duration_to_seconds)

    # Converte coluna date para datetime
    df["date"] = pd.to_datetime(df["date"])

    return df


def merge_datasets(
    athletes: pd.DataFrame,
    contests: pd.DataFrame,
) -> pd.DataFrame:
    """Gera o dataset unificado judo_atle_compt.

    Cada luta produz 2 linhas: uma para o atleta azul (role='blue')
    e outra para o atleta branco (role='white').

    Args:
        athletes: DataFrame de atletas (judo_atle).
        contests: DataFrame de lutas (judo_compt).

    Returns:
        DataFrame mesclado com coluna 'role'.
    """
    if athletes.empty or contests.empty:
        return pd.DataFrame()

    # Merge para atletas azuis
    blue = contests.merge(
        athletes,
        left_on="athlete_blue_id",
        right_on="athlete_id",
        how="left",
    )
    blue["role"] = "blue"

    # Merge para atletas brancos
    white = contests.merge(
        athletes,
        left_on="athlete_white_id",
        right_on="athlete_id",
        how="left",
    )
    white["role"] = "white"

    return pd.concat([blue, white], ignore_index=True)
