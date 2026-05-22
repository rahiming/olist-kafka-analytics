# Kafka TP Project

Mini projet d'analyse e-commerce en temps reel avec Kafka, un processeur Python et un dashboard Streamlit.

## Architecture

- `producer/producer.py` charge et transforme les CSV Olist puis publie une commande par message Kafka.
- `processor/processor.py` consomme le topic Kafka, calcule des agregats et ecrit `output/stats.json`.
- `dashboard/dashboard.py` lit `output/stats.json` et affiche les metriques dans Streamlit.
- `docker-compose.yml` demarre Kafka et la console d'inspection.

## Prerequis

- Python 3.10+
- Docker + Docker Compose

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Donnees

Les CSV de travail ne sont pas versions dans Git. Place-les dans `data/` avec ces noms :

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`

## Demarrage local

1. Demarrer Kafka :

```bash
docker compose up -d
```

2. Lancer le producteur :

```bash
python producer/producer.py
```

3. Lancer le processeur :

```bash
python processor/processor.py
```

4. Lancer le dashboard :

```bash
streamlit run dashboard/dashboard.py
```

## Qualite

```bash
ruff check .
ruff format --check .
black --check producer processor dashboard tests
pytest
bandit -c pyproject.toml -r producer processor dashboard
pip-audit
```

## Hook pre-push local

Le depot contient un hook Git `pre-push` versionne qui bloque un push si un controle echoue.

Installation locale :

```bash
powershell -ExecutionPolicy Bypass -File scripts/install-git-hooks.ps1
```

Execution manuelle du workflow local :

```bash
powershell -ExecutionPolicy Bypass -File scripts/pre-push-check.ps1
```

Le hook lance :

- `ruff check .`
- `ruff format --check .`
- `black --check producer processor dashboard tests` en controle consultatif
- `bandit -c pyproject.toml -r producer processor dashboard`
- `python -m pytest tests -q`

## CI

Le workflow GitHub Actions est decoupe en jobs distincts :

- `structure-check`
- `lint`
- `format`
- `unit-tests`
- `security-scan`
- `dependency-vulnerability`

Ces controles tournent en parallele. Ensuite la pipeline enchaine de facon sequentielle :

- `build-producer-image`
- `build-processor-image`
- `build-dashboard-image`
- `deploy-staging`

Le deploiement `staging` est conditionnel et s'active seulement si les secrets suivants existent :

- `STAGING_HOST`
- `STAGING_USER`
- `STAGING_SSH_KEY`
- `STAGING_GHCR_USERNAME`
- `STAGING_GHCR_TOKEN`
- `STAGING_DEPLOY_PATH`

## Ameliorations futures

- Ajouter des tests d'integration avec Kafka via Docker Compose
- Conteneuriser les services Python
- Introduire des variables d'environnement pour la configuration runtime
- Ajouter un deploiement automatise du dashboard
