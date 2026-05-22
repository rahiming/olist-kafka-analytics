"""
Module A — Producteur Kafka
============================
Objectif : lire les 3 fichiers CSV Olist, les joindre, nettoyer les données,
et publier chaque commande comme un message JSON dans le topic Kafka.

Compétences évaluées :
  - Chargement et manipulation de données avec pandas
  - Jointure de plusieurs DataFrames
  - Sérialisation JSON et publication Kafka avec confluent-kafka
"""

import pandas as pd
import json
import time
from confluent_kafka import Producer

# ── Configuration (ne pas modifier) ──────────────────────────────────────
BOOTSTRAP = 'localhost:9092'
TOPIC     = 'ecommerce-orders'
DATA_DIR  = '../data'
DELAY     = 0.05   # secondes entre chaque message

# ── Étape 1 : Charger les 3 fichiers CSV ─────────────────────────────────
# TODO : charger les 3 fichiers suivants avec pd.read_csv() :
#   - olist_orders_dataset.csv
#   - olist_order_items_dataset.csv
#   - olist_products_dataset.csv
# Afficher le nombre de lignes de chaque fichier avec print()

# orders   = ...
# items    = ...
# products = ...


# ── Étape 2 : Joindre les 3 DataFrames ───────────────────────────────────
# TODO : réaliser 2 jointures successives avec .merge() :
#   1. Joindre orders et items sur la colonne 'order_id'
#   2. Joindre le résultat avec products sur la colonne 'product_id'
#      (ne garder que les colonnes 'product_id' et 'product_category_name' de products)
# Utiliser how='left' pour les deux jointures.

# df = ...


# ── Étape 3 : Nettoyer les données ────────────────────────────────────────
# TODO :
#   1. Garder uniquement les commandes dont order_status == 'delivered'
#   2. Supprimer les lignes où la colonne 'price' est NaN (dropna)
#   3. Remplacer les valeurs NaN de 'product_category_name' par la chaîne 'autre'



# ── Étape 4 : Agréger par commande ────────────────────────────────────────
# TODO : une commande peut avoir plusieurs articles (plusieurs lignes dans items).
# Grouper par 'order_id' et agréger avec .groupby().agg() :
#   - 'order_purchase_timestamp' : prendre la première valeur ('first')
#   - 'customer_id'              : prendre la première valeur ('first')
#   - 'order_status'             : prendre la première valeur ('first')
#   - 'product_category_name'    : prendre la première valeur ('first')
#   - 'price'                    : sommer toutes les valeurs ('sum')
#   - 'freight_value'            : sommer toutes les valeurs ('sum')
# Puis créer une nouvelle colonne 'total' = price + freight_value

# df = df.groupby(...).agg({...}).reset_index()
# df['total'] = ...

print(f'[INFO] ... commandes prêtes à publier')


# ── Étape 5 : Créer le producteur Kafka ──────────────────────────────────
# TODO : instancier un Producer confluent-kafka avec bootstrap.servers

# producer = Producer({...})

def on_delivery(err, msg):
    """Callback appelé après chaque envoi — ne pas modifier."""
    if err:
        print(f'[ERREUR] Livraison échouée : {err}')


# ── Étape 6 : Publier chaque commande ────────────────────────────────────
# TODO : itérer sur les lignes du DataFrame avec .iterrows()
# Pour chaque ligne, construire un dictionnaire 'message' avec ces 8 clés :
#   'order_id', 'customer_id', 'status', 'category',
#   'price', 'freight', 'total', 'timestamp'
# Puis appeler producer.produce() avec :
#   - topic = TOPIC
#   - key   = order_id (string)
#   - value = json.dumps(message)
#   - on_delivery = on_delivery
# Appeler producer.poll(0) après chaque produce()
# Afficher la progression tous les 500 messages
# Attendre DELAY secondes entre chaque message (time.sleep)

nb = 0
for _, row in df.iterrows():
    # TODO : construire le message et le publier
    pass

# TODO : appeler producer.flush() pour s'assurer que tous les messages sont envoyés
print(f'[INFO] ✅ {nb} commandes publiées dans {TOPIC}')
