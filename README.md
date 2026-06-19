# Judo Data Pipeline

Uma pipeline em Python para extrair, limpar e exportar dados de competições de judô a partir da API pública da International Judo Federation (IJF).

## Visão Geral

Este projeto realiza o processo de ETL (Extract, Transform, Load) dos dados da IJF:
1. **Extração:** Busca informações sobre competições, lutas e atletas na API pública (`data.ijf.org`).
2. **Transformação:** Limpa e estrutura os dados usando `pandas`, gerando três conjuntos principais:
    - `judo_atle`: Dados dos atletas (nome, país, gênero, altura, peso, etc.).
    - `judo_compt`: Dados das lutas/competições.
    - `judo_atle_compt`: Dataset unificado.
3. **Carga (Exportação):** Salva os datasets em formatos populares para análise de dados (`.csv` e `.parquet`).

## Requisitos

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Recomendado) ou `pip` com ambiente virtual tradicional

## Instalação

### Opção 1: Com `uv` (Recomendado)

1. Clone ou faça o download deste projeto.
2. Sincronize as dependências usando o `uv`:

```powershell
uv sync
```

### Opção 2: Sem `uv` (Tradicional)

1. Clone ou faça o download deste projeto.
2. Crie e ative um ambiente virtual:

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv .venv
.venv\Scripts\activate.bat

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências de produção:

```powershell
pip install -r requirements.txt
```

> [!TIP]
> Caso queira rodar os testes ou contribuir para o desenvolvimento, instale as dependências de desenvolvimento em vez disso:
> 
> ```powershell
> pip install -r requirements-dev.txt
> ```

## Como Executar

### Com `uv`:

Para iniciar a pipeline, execute:

```powershell
uv run python main.py
```

### Sem `uv` (Com ambiente virtual ativo):

Para iniciar a pipeline, execute:

```powershell
python main.py
```

Ao executar o comando, digite o ano desejado no prompt. A pipeline começará a coletar os dados, aplicar as transformações e gerar os arquivos no diretório `data/`.

## Datasets Gerados

Os dados são exportados para a pasta `data/` nos formatos `.csv` e `.parquet`.

- `judo_atle`
- `judo_compt`
- `judo_atle_compt`

## Como Executar os Testes

O projeto segue a metodologia TDD (Test-Driven Development) e possui testes cobrindo todas as fases.

### Com `uv`:

```powershell
uv run pytest tests/ -v
```

### Sem `uv` (Com ambiente virtual ativo e dependências de desenvolvimento instaladas):

```powershell
pytest tests/ -v
```

## Tecnologias
- `httpx`: Cliente HTTP assíncrono para consumir a API.
- `pandas`: Processamento e limpeza dos dados.
- `pyarrow`: Engine de suporte para exportar em formato Parquet.
- `pytest` / `pytest-asyncio` / `respx`: Testes unitários e mocks da API.
