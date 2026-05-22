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
pytest
bandit -c pyproject.toml -r producer processor dashboard
pip-audit
```

## CI

Le workflow GitHub Actions execute automatiquement :

- lint
- format check
- tests unitaires
- scan de securite Python

## Ameliorations futures

- Ajouter des tests d'integration avec Kafka via Docker Compose
- Conteneuriser les services Python
- Introduire des variables d'environnement pour la configuration runtime
- Ajouter un deploiement automatise du dashboard
