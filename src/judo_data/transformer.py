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
    "ippon_b": "blue_ippon",
    "waza_b": "blue_wazari",
    "yuko_b": "blue_yuko",
    "penalty_b": "blue_shido",
    "hsk_b": "blue_hansoukomake",
    "ippon_w": "white_ippon",
    "waza_w": "white_wazari",
    "yuko_w": "white_yuko",
    "penalty_w": "white_shido",
    "hsk_w": "white_hansoukomake",
    "round": "round",
}

_GENDER_MAP = {
    "male": "M",
    "female": "F",
}


def _duration_to_seconds(duration) -> int:
    """Converte duração no formato 'HH:MM:SS', 'M:SS' ou numérico para segundos.

    Exemplos:
        '00:04:00' → 240
        '4:00' → 240
        '2:35' → 155
        240 → 240
        None/NaN → 0
    """
    if pd.isna(duration) or duration is None:
        return 0

    if isinstance(duration, (int, float)):
        return max(0, int(duration))

    duration_str = str(duration).strip()
    if not duration_str:
        return 0

    if ":" in duration_str:
        try:
            parts = duration_str.split(":")
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return max(0, hours * 3600 + minutes * 60 + seconds)
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                return max(0, minutes * 60 + seconds)
            return 0
        except (ValueError, IndexError):
            return 0
    else:
        try:
            return max(0, int(float(duration_str)))
        except ValueError:
            return 0


def _format_score(ippon, waza, yuko, penalty) -> str:
    """Monta uma string descritiva do placar a partir dos valores da API."""
    parts = []
    if ippon and str(ippon) != "0":
        parts.append("Ippon")
    if waza and str(waza) != "0":
        parts.append("Waza-ari")
    if yuko and str(yuko) != "0":
        parts.append("Yuko")
    if penalty and str(penalty) != "0":
        parts.append(f"{penalty} Shido")
    return ", ".join(parts) if parts else ""


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

        # Fallback para país (API real usa country_short, mocks usam country)
        if "country" not in entry:
            record["country"] = entry.get("country_short")

        # Fallback para categoria (API usa 'categories' list,
        # mocks usam 'weight_category')
        if "weight_category" not in entry:
            cats = entry.get("categories")
            if cats and isinstance(cats, list) and len(cats) > 0:
                record["weight_category"] = cats[0]

        # Fallback para peso (API real não tem o campo, extraímos de weight_category)
        if "weight" not in entry:
            w_cat = record.get("weight_category")
            if w_cat:
                try:
                    cleaned = (
                        str(w_cat)
                        .replace("kg", "")
                        .replace("-", "")
                        .replace("+", "")
                        .strip()
                    )
                    record["weight"] = float(cleaned)
                except ValueError:
                    pass

        records.append(record)

    df = pd.DataFrame(records, columns=ATHLETE_COLUMNS)

    # Normaliza gênero: 'male' → 'M', 'female' → 'F'
    df["gender"] = df["gender"].str.lower().map(_GENDER_MAP)

    # Country code sempre em maiúsculas (IOC)
    df["country"] = df["country"].str.upper()

    # Converte athlete_id, height e weight para numérico
    df["athlete_id"] = pd.to_numeric(df["athlete_id"], errors="coerce").astype("Int64")
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

        # Fallback para campo de data (API real usa date_raw/competition_date)
        if not record.get("date"):
            record["date"] = (
                entry.get("date_raw")
                or entry.get("competition_date")
                or entry.get("date")
            )

        # Fallback para scores (API real usa ippon_b, waza_b, etc.)
        if not record.get("score_blue"):
            ippon_b = entry.get("ippon_b")
            waza_b = entry.get("waza_b")
            yuko_b = entry.get("yuko_b")
            penalty_b = entry.get("penalty_b")
            record["score_blue"] = _format_score(ippon_b, waza_b, yuko_b, penalty_b)

        if not record.get("score_white"):
            ippon_w = entry.get("ippon_w")
            waza_w = entry.get("waza_w")
            yuko_w = entry.get("yuko_w")
            penalty_w = entry.get("penalty_w")
            record["score_white"] = _format_score(ippon_w, waza_w, yuko_w, penalty_w)

        records.append(record)

    df = pd.DataFrame(records, columns=CONTEST_COLUMNS)

    # Garante que as colunas de ID sejam numéricas para evitar erro no merge
    df["contest_id"] = pd.to_numeric(df["contest_id"], errors="coerce").astype("Int64")
    df["competition_id"] = pd.to_numeric(df["competition_id"], errors="coerce").astype(
        "Int64"
    )
    df["athlete_blue_id"] = pd.to_numeric(
        df["athlete_blue_id"], errors="coerce"
    ).astype("Int64")
    df["athlete_white_id"] = pd.to_numeric(
        df["athlete_white_id"], errors="coerce"
    ).astype("Int64")
    df["winner_id"] = pd.to_numeric(df["winner_id"], errors="coerce").astype("Int64")

    # Determina o lado/cor do vencedor da luta
    df["winner_color"] = None
    is_blue_winner = df["winner_id"] == df["athlete_blue_id"]
    is_white_winner = df["winner_id"] == df["athlete_white_id"]
    df.loc[is_blue_winner, "winner_color"] = "blue"
    df.loc[is_white_winner, "winner_color"] = "white"

    # Garante que location é object dtype (compatibilidade com pandas StringDtype)
    df["location"] = df["location"].astype(object)

    # Converte duração para segundos com fallback para fight_duration do JSON bruto
    durations = []
    for idx, entry in enumerate(raw_data):
        duration_val = df.loc[idx, "fight_duration"]
        seconds = _duration_to_seconds(duration_val)
        if seconds == 0:
            raw_fight_dur = entry.get("fight_duration")
            if raw_fight_dur is not None:
                seconds = _duration_to_seconds(raw_fight_dur)
        durations.append(seconds)
    df["fight_duration"] = durations

    # Converte coluna date para datetime
    df["date"] = pd.to_datetime(df["date"])

    # Garante que as colunas de placar detalhado sejam numéricas (int)
    score_cols = [
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
    ]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


def merge_datasets(
    athletes: pd.DataFrame,
    contests: pd.DataFrame,
) -> pd.DataFrame:
    """Gera o dataset unificado judo_atle_compt.

    Cada luta produz 1 linha contendo as informações de ambos os atletas.

    Args:
        athletes: DataFrame de atletas (judo_atle).
        contests: DataFrame de lutas (judo_compt).

    Returns:
        DataFrame mesclado com colunas de ambos os atletas lado a lado.
    """
    if athletes.empty or contests.empty:
        from judo_data.config import MERGED_COLUMNS

        return pd.DataFrame(columns=MERGED_COLUMNS)

    athlete_cols = [
        "athlete_id",
        "first_name",
        "last_name",
        "country",
        "gender",
        "weight_category",
        "height",
        "weight",
    ]
    athletes_blue = athletes[athlete_cols].copy()
    athletes_blue = athletes_blue.rename(
        columns={
            "first_name": "blue_first_name",
            "last_name": "blue_last_name",
            "country": "blue_country",
            "gender": "blue_gender",
            "weight_category": "blue_weight_category",
            "height": "blue_height",
            "weight": "blue_weight",
        }
    )

    merged = contests.merge(
        athletes_blue,
        left_on="athlete_blue_id",
        right_on="athlete_id",
        how="left",
    )
    if "athlete_id" in merged.columns:
        merged = merged.drop(columns=["athlete_id"])

    athletes_white = athletes[athlete_cols].copy()
    athletes_white = athletes_white.rename(
        columns={
            "first_name": "white_first_name",
            "last_name": "white_last_name",
            "country": "white_country",
            "gender": "white_gender",
            "weight_category": "white_weight_category",
            "height": "white_height",
            "weight": "white_weight",
        }
    )

    merged = merged.merge(
        athletes_white,
        left_on="athlete_white_id",
        right_on="athlete_id",
        how="left",
    )
    if "athlete_id" in merged.columns:
        merged = merged.drop(columns=["athlete_id"])

    from judo_data.config import MERGED_COLUMNS

    return merged.reindex(columns=MERGED_COLUMNS)
