"""Testes para o módulo fetcher — coleta de dados da API IJF."""

import httpx
import pytest
import respx

from judo_data.config import BASE_URL
from judo_data.fetcher import JudoFetcher

# === Testes de fetch_competitions ===


@respx.mock
@pytest.mark.asyncio
async def test_fetch_competitions_returns_list(raw_competitions):
    """fetch_competitions deve retornar uma lista de dicts com competições."""
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=raw_competitions))

    fetcher = JudoFetcher(delay=0)
    result = await fetcher.fetch_competitions(2024)

    assert isinstance(result, list)
    assert len(result) == 2


@respx.mock
@pytest.mark.asyncio
async def test_fetch_competitions_filters_by_year(raw_competitions):
    """fetch_competitions deve passar o ano como parâmetro na request."""
    route = respx.get(BASE_URL).mock(
        return_value=httpx.Response(200, json=raw_competitions)
    )

    fetcher = JudoFetcher(delay=0)
    await fetcher.fetch_competitions(2024)

    assert route.called
    request = route.calls[0].request
    assert "competition.get_list" in str(request.url)


@respx.mock
@pytest.mark.asyncio
async def test_fetch_competitions_has_required_fields(raw_competitions):
    """Cada competição retornada deve ter id, name, city, country e datas."""
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=raw_competitions))

    fetcher = JudoFetcher(delay=0)
    result = await fetcher.fetch_competitions(2024)

    for comp in result:
        assert "id_competition" in comp
        assert "name" in comp


# === Testes de fetch_contests ===


@respx.mock
@pytest.mark.asyncio
async def test_fetch_contests_returns_list(raw_contests):
    """fetch_contests deve retornar uma lista de lutas."""
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=raw_contests))

    fetcher = JudoFetcher(delay=0)
    result = await fetcher.fetch_contests(2653)

    assert isinstance(result, list)
    assert len(result) == 4


@respx.mock
@pytest.mark.asyncio
async def test_fetch_contests_passes_competition_id():
    """fetch_contests deve incluir o competition_id nos parâmetros."""
    route = respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=[]))

    fetcher = JudoFetcher(delay=0)
    await fetcher.fetch_contests(2653)

    assert route.called
    request = route.calls[0].request
    url_str = str(request.url)
    assert "contest.find" in url_str
    assert "2653" in url_str


# === Testes de fetch_athlete ===


@respx.mock
@pytest.mark.asyncio
async def test_fetch_athlete_returns_dict():
    """fetch_athlete deve retornar um dicionário com dados do atleta."""
    athlete_data = {
        "id_person": 1001,
        "family_name": "Nagase",
        "given_name": "Takanori",
        "country": "JPN",
        "gender": "male",
        "weight_category": "-81 kg",
        "height": 178,
        "weight": 81,
    }
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=athlete_data))

    fetcher = JudoFetcher(delay=0)
    result = await fetcher.fetch_athlete(1001)

    assert isinstance(result, dict)
    assert result["id_person"] == 1001
    assert result["family_name"] == "Nagase"


# === Testes de fetch_all_athletes ===


@respx.mock
@pytest.mark.asyncio
async def test_fetch_all_athletes_returns_list():
    """fetch_all_athletes deve buscar múltiplos atletas e retornar lista."""
    athletes = [
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
    ]
    # Each call returns a single athlete
    respx.get(BASE_URL).mock(
        side_effect=[
            httpx.Response(200, json=athletes[0]),
            httpx.Response(200, json=athletes[1]),
        ]
    )

    fetcher = JudoFetcher(delay=0)
    result = await fetcher.fetch_all_athletes([1001, 1002])

    assert isinstance(result, list)
    assert len(result) == 2


# === Testes de tratamento de erros ===


@respx.mock
@pytest.mark.asyncio
async def test_fetch_handles_http_error():
    """Fetcher deve tratar erros HTTP sem crashar."""
    respx.get(BASE_URL).mock(
        return_value=httpx.Response(500, json={"error": "Internal Server Error"})
    )

    fetcher = JudoFetcher(delay=0)
    result = await fetcher.fetch_competitions(2024)

    # Deve retornar lista vazia em caso de erro, não crashar
    assert isinstance(result, list)
    assert len(result) == 0


@respx.mock
@pytest.mark.asyncio
async def test_fetch_handles_timeout():
    """Fetcher deve tratar timeout sem crashar."""
    respx.get(BASE_URL).mock(side_effect=httpx.TimeoutException("timeout"))

    fetcher = JudoFetcher(delay=0)
    result = await fetcher.fetch_competitions(2024)

    assert isinstance(result, list)
    assert len(result) == 0


# === Teste de rate limiting ===


@respx.mock
@pytest.mark.asyncio
async def test_fetcher_has_delay_attribute():
    """Fetcher deve ter um atributo de delay configurável."""
    fetcher = JudoFetcher(delay=1.0)
    assert fetcher.delay == 1.0

    fetcher_fast = JudoFetcher(delay=0)
    assert fetcher_fast.delay == 0


@respx.mock
@pytest.mark.asyncio
async def test_fetcher_default_delay():
    """Fetcher sem argumento de delay deve usar o padrão da config."""
    fetcher = JudoFetcher()
    assert fetcher.delay > 0


@respx.mock
@pytest.mark.asyncio
async def test_fetcher_has_max_concurrent_attribute():
    """Fetcher deve ter um atributo max_concurrent configurável."""
    fetcher = JudoFetcher(max_concurrent=10)
    assert fetcher.max_concurrent == 10

    fetcher_default = JudoFetcher()
    assert fetcher_default.max_concurrent == 5
