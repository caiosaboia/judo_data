"""Módulo fetcher — extração de dados da API IJF.

Usa httpx.AsyncClient para chamadas HTTP assíncronas com rate limiting
e tratamento de erros (HTTP errors, timeouts).
"""

import asyncio
import logging

import httpx

from judo_data.config import ACTIONS, BASE_URL, REQUEST_DELAY, REQUEST_TIMEOUT, MAX_CONCURRENT_REQUESTS

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

class JudoFetcher:
    """Cliente para buscar dados de judô na API pública da IJF.

    Parameters
    ----------
    base_url : str, optional
        URL base da API. Usa ``config.BASE_URL`` se não informado.
    delay : float, optional
        Delay em segundos entre requests consecutivos para rate limiting.
        Usa ``config.REQUEST_DELAY`` se não informado.
    max_concurrent : int, optional
        Número máximo de requisições concorrentes.
        Usa ``config.MAX_CONCURRENT_REQUESTS`` se não informado.
    """

    def __init__(
        self,
        base_url: str | None = None,
        delay: float | None = None,
        max_concurrent: int | None = None,
    ) -> None:
        self.base_url = base_url or BASE_URL
        self.delay = delay if delay is not None else REQUEST_DELAY
        self.max_concurrent = max(1, max_concurrent if max_concurrent is not None else MAX_CONCURRENT_REQUESTS)

    # ------------------------------------------------------------------
    # Competitions
    # ------------------------------------------------------------------

    async def fetch_competitions(self, year: int) -> list[dict]:
        """Busca lista de competições para um determinado ano.

        Parameters
        ----------
        year : int
            Ano das competições a buscar.

        Returns
        -------
        list[dict]
            Lista de competições. Retorna lista vazia em caso de erro.
        """
        params = {
            "params[action]": ACTIONS["competitions"],
            "params[year]": str(year),
        }
        return await self._get_list(params)

    # ------------------------------------------------------------------
    # Contests
    # ------------------------------------------------------------------

    async def fetch_contests(self, competition_id: int) -> list[dict]:
        """Busca lista de lutas de uma competição específica.

        Parameters
        ----------
        competition_id : int
            ID da competição na API IJF.

        Returns
        -------
        list[dict]
            Lista de lutas. Retorna lista vazia em caso de erro.
        """
        params = {
            "params[action]": ACTIONS["contests"],
            "params[id_competition]": str(competition_id),
        }
        return await self._get_list(params)

    # ------------------------------------------------------------------
    # Athletes
    # ------------------------------------------------------------------

    async def fetch_athlete(self, athlete_id: int) -> dict:
        """Busca dados de um atleta individual.

        Parameters
        ----------
        athlete_id : int
            ID do atleta (``id_person``) na API IJF.

        Returns
        -------
        dict
            Dados do atleta. Retorna dict vazio em caso de erro.
        """
        params = {
            "params[action]": ACTIONS["competitor"],
            "params[id_person]": str(athlete_id),
        }
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict):
                    data["id_person"] = int(athlete_id)
                return data
        except httpx.TimeoutException:
            logger.error("Timeout ao buscar atleta %s", athlete_id)
            return {}
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Erro HTTP %s ao buscar atleta %s", exc.response.status_code, athlete_id
            )
            return {}
        except httpx.HTTPError as exc:
            logger.error("Erro HTTP ao buscar atleta %s: %s", athlete_id, exc)
            return {}

    async def fetch_all_athletes(self, athlete_ids: list[int]) -> list[dict]:
        """Busca dados de múltiplos atletas concorrentemente usando um semáforo.

        Faz chamadas concorrentes limitadas pelo semáforo, respeitando o delay
        configurado entre as requisições por meio de uma estratégia de staggering.

        Parameters
        ----------
        athlete_ids : list[int]
            Lista de IDs de atletas a buscar.

        Returns
        -------
        list[dict]
            Lista de dicts com dados dos atletas. Atletas que falharam
            são incluídos como dicts vazios.
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def worker(athlete_id: int, index: int) -> dict:
            async with semaphore:
                if self.delay > 0:
                    # Distribui o início das requisições ao longo do tempo para evitar surtos
                    await asyncio.sleep(index * self.delay / self.max_concurrent)
                return await self.fetch_athlete(athlete_id)

        tasks = [worker(aid, idx) for idx, aid in enumerate(athlete_ids)]
        return list(await asyncio.gather(*tasks))

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    async def _get_list(self, params: dict) -> list[dict]:
        """Helper genérico para endpoints que retornam listas.

        Parameters
        ----------
        params : dict
            Parâmetros de query para a request HTTP.

        Returns
        -------
        list[dict]
            Dados retornados pela API, ou lista vazia em caso de erro.
        """
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "contests" in data and isinstance(data["contests"], list):
                    return data["contests"]
                return []
        except httpx.TimeoutException:
            logger.error("Timeout na request para %s", params)
            return []
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Erro HTTP %s na request para %s",
                exc.response.status_code,
                params,
            )
            return []
        except httpx.HTTPError as exc:
            logger.error("Erro HTTP na request: %s", exc)
            return []
