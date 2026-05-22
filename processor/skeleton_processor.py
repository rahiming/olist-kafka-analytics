"""
Module B — Processeur Kafka
============================
Objectif : consommer les messages du topic ecommerce-orders,
calculer des agrégats en mémoire (par catégorie et par heure),
et écrire les résultats dans output/stats.json toutes les 50 commandes.

Compétences évaluées :
  - Configuration et utilisation d'un Consumer confluent-kafka
  - Logique d'agrégation (compteurs, sommes, moyennes)
  - Sérialisation JSON et écriture de fichier
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from confluent_kafka import Consumer, KafkaError

# ── Configuration (ne pas modifier) ──────────────────────────────────────
BOOTSTRAP   = 'localhost:9092'
TOPIC       = 'ecommerce-orders'
OUTPUT      = '../output/stats.json'
FLUSH_EVERY = 50   # sauvegarder toutes les 50 commandes


# ── Étape 1 : Créer le consommateur Kafka ────────────────────────────────
# TODO : instancier un Consumer confluent-kafka avec ces 3 paramètres :
#   - 'bootstrap.servers' : adresse du broker
#   - 'group.id'          : identifiant du groupe ('processeur-ecommerce')
#   - 'auto.offset.reset' : relire depuis le début ('earliest')
# Puis appeler consumer.subscribe() avec la liste des topics à écouter.

# consumer = Consumer({...})
# consumer.subscribe([...])


# ── Étape 2 : Définir les structures d'agrégation ────────────────────────
# TODO : créer 2 defaultdict pour stocker les agrégats en mémoire :
#
# stats_cat   : agrégation PAR CATÉGORIE
#   Chaque entrée doit avoir : 'nb_commandes', 'ca_total', 'ca_max'
#
# stats_heure : agrégation PAR HEURE (clé = '2017-10-02 10', les 13 premiers caractères du timestamp)
#   Chaque entrée doit avoir : 'nb_commandes', 'ca_total'
#
# Utiliser defaultdict(lambda: {...}) pour initialiser automatiquement les valeurs.

# stats_cat   = defaultdict(lambda: {...})
# stats_heure = defaultdict(lambda: {...})

# Compteurs globaux
total_traite = 0
ca_global    = 0.0
commande_max = 0.0


# ── Étape 3 : Fonction de sauvegarde ─────────────────────────────────────
def save_stats():
    """
    Sérialiser toutes les statistiques et écrire dans OUTPUT (stats.json).

    TODO : construire le dictionnaire de sortie avec ces clés :
      - 'mise_a_jour'         : heure actuelle (datetime.now().strftime('%H:%M:%S'))
      - 'total_commandes'     : nombre total de commandes traitées
      - 'ca_global'           : CA total arrondi à 2 décimales
      - 'panier_moyen_global' : ca_global / total_traite (attention division par zéro)
      - 'commande_max'        : valeur maximale d'une commande
      - 'categories'          : liste de dicts par catégorie, triée par ca_total décroissant
                                Chaque dict : categorie, nb_commandes, ca_total,
                                              panier_moyen (= ca_total / nb_commandes), ca_max
      - 'evolution'           : liste de dicts par heure, triée chronologiquement
                                Chaque dict : heure, nb_commandes, ca_total

    Créer le dossier output/ si nécessaire (os.makedirs avec exist_ok=True).
    Écrire le JSON dans le fichier OUTPUT avec json.dump().
    """
    # TODO : implémenter cette fonction
    pass


# ── Étape 4 : Boucle de consommation ─────────────────────────────────────
os.makedirs('../output', exist_ok=True)
print(f'[INFO] Processeur démarré — écoute {TOPIC} — Ctrl+C pour arrêter')

try:
    while True:
        # Attendre un message (max 1 seconde)
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue   # pas de message dans ce cycle

        if msg.error():
            # _PARTITION_EOF est normal, les autres codes sont des erreurs
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f'[ERREUR] {msg.error()}')
            continue

        # ── TODO : traiter le message ─────────────────────────────────────
        # 1. Décoder la valeur du message (bytes → string → dict JSON)
        #    Indice : msg.value().decode('utf-8') puis json.loads()
        #
        # 2. Extraire les champs utiles :
        #    - category : data.get('category', 'autre')
        #    - total    : float(data.get('total', 0.0))
        #    - heure    : les 13 premiers caractères du timestamp
        #                 ex: '2017-10-02 10:56:33' → '2017-10-02 10'
        #
        # 3. Mettre à jour stats_cat[category] :
        #    - incrémenter nb_commandes
        #    - ajouter total à ca_total
        #    - mettre à jour ca_max si total est plus grand
        #
        # 4. Mettre à jour stats_heure[heure] :
        #    - incrémenter nb_commandes
        #    - ajouter total à ca_total
        #
        # 5. Mettre à jour les compteurs globaux :
        #    total_traite, ca_global, commande_max
        #
        # 6. Appeler save_stats() tous les FLUSH_EVERY messages

        pass   # à remplacer par votre implémentation

except KeyboardInterrupt:
    print('\n[INFO] Arrêt — sauvegarde finale...')
    save_stats()
finally:
    consumer.close()
    print('[INFO] ✅ Consommateur fermé.')
