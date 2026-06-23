"""Fixtures e dados mock compartilhados para os testes."""

import pandas as pd
import pytest

# === Mock data: respostas simuladas da API IJF ===


@pytest.fixture
def raw_competitions():
    """Resposta simulada de competition.get_list."""
    return [
        {
            "id_competition": 2653,
            "name": "Olympic Games Paris 2024",
            "date_from": "2024-07-27",
            "date_to": "2024-08-03",
            "city": "Paris",
            "country": "France",
        },
        {
            "id_competition": 2600,
            "name": "World Championships 2024",
            "date_from": "2024-05-18",
            "date_to": "2024-05-25",
            "city": "Abu Dhabi",
            "country": "United Arab Emirates",
        },
    ]


@pytest.fixture
def raw_contests():
    """Resposta simulada de contest.get_list para uma competição."""
    return [
        {
            "id_fight": 10001,
            "id_competition": 2653,
            "competition_name": "Olympic Games Paris 2024",
            "date": "2024-07-27",
            "venue": "Paris, FRA",
            "weight": "-60",
            "id_person_blue": 1001,
            "id_person_white": 1002,
            "id_winner": 1001,
            "duration": "4:00",
            "score_blue": "Ippon",
            "score_white": "",
            "round": "Final",
        },
        {
            "id_fight": 10002,
            "id_competition": 2653,
            "competition_name": "Olympic Games Paris 2024",
            "date": "2024-07-27",
            "venue": "Paris, FRA",
            "weight": "-48",
            "id_person_blue": 1003,
            "id_person_white": 1004,
            "id_winner": 1004,
            "duration": "2:35",
            "score_blue": "Waza-ari",
            "score_white": "Ippon",
            "round": "Semi-Final",
        },
        {
            "id_fight": 10003,
            "id_competition": 2653,
            "competition_name": "Olympic Games Paris 2024",
            "date": "2024-07-28",
            "venue": "Paris, FRA",
            "weight": "-66",
            "id_person_blue": 1005,
            "id_person_white": 1006,
            "id_winner": None,
            "duration": "1:15",
            "score_blue": "Hansoku-make",
            "score_white": "",
            "round": "Quarter-Final",
        },
        {
            "id_fight": 10004,
            "id_competition": 2653,
            "competition_name": "Olympic Games Paris 2024",
            "date": "2024-07-28",
            "venue": "Paris, FRA",
            "weight": "-52",
            "id_person_blue": 1007,
            "id_person_white": 1008,
            "id_winner": 1007,
            "duration": "6:30",
            "score_blue": "Waza-ari",
            "score_white": "",
            "round": "Final",
        },
    ]


@pytest.fixture
def raw_athletes():
    """Resposta simulada de dados de atletas individuais."""
    return [
        {
            "id_person": 1001,
            "family_name": "Nagase",
            "given_name": "Takanori",
            "country": "JPN",
            "gender": "male",
            "weight_category": "-81 kg",
            "height": 178,
            "weight": 81,
        },
        {
            "id_person": 1002,
            "family_name": "Silva",
            "given_name": "Rafael",
            "country": "BRA",
            "gender": "male",
            "weight_category": "+100 kg",
            "height": 195,
            "weight": 130,
        },
        {
            "id_person": 1003,
            "family_name": "Abe",
            "given_name": "Uta",
            "country": "JPN",
            "gender": "female",
            "weight_category": "-52 kg",
            "height": 158,
            "weight": 52,
        },
        {
            "id_person": 1004,
            "family_name": "Buchard",
            "given_name": "Amandine",
            "country": "FRA",
            "gender": "female",
            "weight_category": "-52 kg",
            "height": None,
            "weight": None,
        },
        {
            "id_person": 1005,
            "family_name": "Lombardo",
            "given_name": "Manuel",
            "country": "ITA",
            "gender": "male",
            "weight_category": "-73 kg",
            "height": 175,
            "weight": 73,
        },
        {
            "id_person": 1006,
            "family_name": "An",
            "given_name": "Baul",
            "country": "KOR",
            "gender": "male",
            "weight_category": "-66 kg",
            "height": 170,
            "weight": 66,
        },
    ]


@pytest.fixture
def sample_athletes_df():
    """DataFrame de atletas já transformado (judo_atle)."""
    return pd.DataFrame(
        {
            "athlete_id": [1001, 1002, 1003, 1004],
            "first_name": ["Takanori", "Rafael", "Uta", "Amandine"],
            "last_name": ["Nagase", "Silva", "Abe", "Buchard"],
            "country": ["JPN", "BRA", "JPN", "FRA"],
            "gender": ["M", "M", "F", "F"],
            "weight_category": ["-81 kg", "+100 kg", "-52 kg", "-52 kg"],
            "height": [178.0, 195.0, 158.0, None],
            "weight": [81.0, 130.0, 52.0, None],
        }
    )


@pytest.fixture
def sample_contests_df():
    """DataFrame de lutas já transformado (judo_compt)."""
    return pd.DataFrame(
        {
            "contest_id": [10001, 10002],
            "competition_id": [2653, 2653],
            "competition_name": [
                "Olympic Games Paris 2024",
                "Olympic Games Paris 2024",
            ],
            "date": pd.to_datetime(["2024-07-27", "2024-07-27"]),
            "location": ["Paris, France", "Paris, France"],
            "weight_category": ["-60 kg", "-60 kg"],
            "athlete_blue_id": [1001, 1003],
            "athlete_white_id": [1002, 1004],
            "winner_id": [1001, 1004],
            "fight_duration": [240, 155],
            "score_blue": ["10 - 0", "0 - 1"],
            "score_white": ["0 - 0", "1 - 0"],
            "round": ["Final", "Semi-Final"],
        }
    )
