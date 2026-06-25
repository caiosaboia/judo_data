# GEMINI.md — Judo Data Pipeline

## Visão Geral
Pipeline Python para extração, limpeza e exportação de dados de competições de judô.
Fonte: API pública da IJF (International Judo Federation) em `data.ijf.org`.

## Stack Tecnológica
- **Python 3.12+** — linguagem principal
- **UV** — gerenciador de pacotes e projeto
- **httpx** — HTTP client async para chamadas à API
- **pandas** — limpeza e transformação de dados
- **pyarrow** — engine para exportação Parquet
- **pytest + pytest-asyncio + respx** — testes com mocks async

## Fonte de Dados
- **API Base URL:** `https://data.ijf.org/api/get_json`
- **Endpoints (via parâmetro `action`):**
  - `competition.get_list` — lista de competições
  - `contest.get_list` — lutas de uma competição
  - `competitor.get_list` / perfil de atleta — dados individuais
- **Autenticação:** Nenhuma (API pública)
- **Rate Limiting:** Delay de 0.5s entre requests para evitar bloqueio
- **Fallback:** Se a API direta falhar, usar a lib `judobase` (pip install judobase)

## Datasets Finais (3 conjuntos)

### 1. `judo_atle` — Atletas
| Coluna | Tipo | Obrigatório |
|--------|------|:-----------:|
| athlete_id | int | ✅ |
| first_name | str | ✅ |
| last_name | str | ✅ |
| country | str (IOC code) | ✅ |
| gender | str (M/F) | ✅ |
| weight_category | str | ✅ |
| height | float | ❌ (pode ser null) |
| weight | float | ❌ (pode ser null) |

### 2. `judo_compt` — Competições/Lutas
| Coluna | Tipo | Obrigatório |
|--------|------|:-----------:|
| contest_id | int | ✅ |
| competition_id | int | ✅ |
| competition_name | str | ✅ |
| date | date | ✅ |
| location | str | ✅ |
| weight_category | str | ✅ |
| athlete_blue_id | int | ✅ |
| athlete_white_id | int | ✅ |
| winner_id | int | ❌ (null se empate/desclassificação) |
| winner_color | str | ❌ (lado do vencedor: 'blue', 'white' ou null) |
| fight_duration | int (segundos) | ✅ |
| score_blue | str | ❌ |
| score_white | str | ❌ |
| round | str | ✅ |

### 3. `judo_atle_compt` — União dos dois
Merge de `judo_atle` + `judo_compt` via `athlete_id`.
Cada luta gera exatamente 1 linha contendo as informações da luta e de ambos os atletas lado a lado (com colunas prefixadas por `blue_` e `white_`).

## Estrutura do Projeto
```
judo_data/
├── pyproject.toml
├── README.md
├── GEMINI.md                   ← ESTE ARQUIVO
├── src/
│   └── judo_data/
│       ├── __init__.py
│       ├── config.py           # Constantes e configuração
│       ├── fetcher.py          # Extração de dados da API
│       ├── transformer.py      # Limpeza com Pandas
│       ├── exporter.py         # Export CSV/Parquet
│       └── pipeline.py         # Orquestrador
├── tests/
│   ├── conftest.py             # Fixtures e mocks
│   ├── test_config.py
│   ├── test_fetcher.py
│   ├── test_transformer.py
│   ├── test_exporter.py
│   └── test_pipeline.py
└── data/                       # Output dos datasets
```

## Decisões de Design
1. **API direta com httpx** — preferido sobre lib `judobase` para controle total
2. **Abordagem TDD** — testes escritos ANTES da implementação
3. **Pandas para transformação** — padrão da indústria para ETL em Python
4. **Parquet + CSV** — formatos mais comuns para datasets
5. **Async para fetcher** — performance ao buscar muitos registros
6. **Rate limiting manual** — 0.5s entre requests, evita bloqueio pela IJF

## Pipeline Flow
```
Usuário informa ano
    → fetch_competitions(year)
    → fetch_contests(competition_ids)
    → fetch_athletes(athlete_ids)
    → transform_athletes() → judo_atle
    → transform_contests() → judo_compt
    → merge() → judo_atle_compt
    → export(csv + parquet)
```

## Comandos Úteis
```powershell
# Rodar pipeline
uv run python -m judo_data.pipeline

# Rodar testes
uv run pytest tests/ -v

# Rodar testes com coverage
uv run pytest tests/ -v --cov=src/judo_data
```

## Notas Importantes
- Dados da IJF são propriedade da International Judo Federation
- Uso apenas educacional e não-comercial
- Altura e peso dos atletas nem sempre estão disponíveis na API
- A API não tem documentação oficial — endpoints foram descobertos via reverse engineering
- NUNCA APAGUE OS TESTES!
