"""
Module C — Dashboard Streamlit
================================
Objectif : lire le fichier output/stats.json généré par le processeur
et afficher un dashboard avec au minimum 3 graphiques interactifs,
actualisé automatiquement toutes les 5 secondes.

Compétences évaluées :
  - Lecture et parsing d'un fichier JSON
  - Création de graphiques interactifs avec Plotly Express
  - Construction d'une interface Streamlit avec métriques et visualisations
  - Mise en place d'une actualisation automatique
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import time
from pathlib import Path

# ── Configuration (ne pas modifier) ──────────────────────────────────────
STATS_FILE = '../output/stats.json'
REFRESH    = 5   # secondes entre chaque actualisation

# ── Mise en page (ne pas modifier) ───────────────────────────────────────
st.set_page_config(
    page_title='E-Commerce Analytics',
    page_icon='🛒',
    layout='wide',
)
st.title('🛒 E-Commerce Real-Time Analytics')
st.caption('Données : Olist Brazilian E-Commerce — open data Kaggle')


# ── Étape 1 : Fonction de chargement des données ─────────────────────────
def load_data():
    """
    Charger et parser le fichier stats.json.

    TODO : implémenter cette fonction :
      1. Vérifier que le fichier STATS_FILE existe (utiliser pathlib.Path)
         Si non, retourner (None, None)
      2. Ouvrir et lire le fichier JSON avec json.load()
      3. Créer 2 DataFrames pandas :
         - df_cat : depuis la clé 'categories' du JSON
         - df_evo : depuis la clé 'evolution' du JSON
         (utiliser pd.DataFrame() avec .get() pour éviter les KeyError)
      4. Créer un dict 'meta' avec ces clés :
         'mise_a_jour', 'total_commandes', 'ca_global',
         'panier_moyen_global', 'commande_max'
      5. Retourner ((df_cat, df_evo), meta)

    Returns:
        ((df_cat, df_evo), meta) si le fichier existe
        (None, None) sinon
    """
    # TODO : implémenter cette fonction
    pass


# ── Boucle d'actualisation (ne pas modifier) ─────────────────────────────
placeholder = st.empty()

while True:
    result, meta = load_data()

    with placeholder.container():

        # Cas : fichier pas encore créé par le processeur
        if result is None:
            st.warning('⏳ En attente des données... Assurez-vous que processor.py tourne.')
            st.code('cd processor && python3 processor.py')

        else:
            df_cat, df_evo = result

            # ── Étape 2 : Afficher les KPIs ───────────────────────────────
            # TODO : afficher la ligne de métriques en haut du dashboard
            # Créer 5 colonnes avec st.columns(5)
            # Dans chaque colonne, appeler .metric() avec :
            #   col1 : '📦 Commandes'    → meta['total_commandes']
            #   col2 : '💰 CA total (R$)' → meta['ca_global']
            #   col3 : '🛍️ Panier moyen' → meta['panier_moyen_global']
            #   col4 : '🏆 Commande max'  → meta['commande_max']
            #   col5 : '🏷️ Catégories'   → len(df_cat)
            # Afficher aussi la mise_a_jour avec st.caption()

            # TODO : ajouter un st.divider()


            if not df_cat.empty:

                # ── Étape 3 : Graphique 1 — CA par catégorie ──────────────
                # TODO : afficher un graphique en barres horizontales
                # Utiliser px.bar() avec :
                #   - les 10 premières catégories par ca_total (nlargest)
                #   - x='ca_total', y='categorie', orientation='h'
                #   - color='ca_total', color_continuous_scale='Blues'
                # Titre : '💰 CA par catégorie — Top 10'
                # Afficher avec st.plotly_chart(use_container_width=True)


                # ── Étape 4 : Graphique 2 — Répartition des commandes ─────
                # TODO : afficher un graphique en camembert (donut)
                # Utiliser px.pie() avec :
                #   - les 8 premières catégories par nb_commandes (nlargest)
                #   - names='categorie', values='nb_commandes', hole=0.4
                # Titre : '📦 Répartition des commandes'
                # Conseil : placer graphique 1 et 2 côte à côte avec st.columns(2)


                # ── Étape 5 : Graphique 3 — Évolution temporelle ──────────
                # TODO : afficher un graphique d'évolution du CA dans le temps
                # Utiliser df_evo (s'assurer qu'il n'est pas vide et a > 1 ligne)
                # Trier df_evo par la colonne 'heure' avant de tracer
                # Utiliser px.area() ou px.line() avec x='heure', y='ca_total'
                # Titre : '📈 Évolution du CA dans le temps'
                # Si df_evo est trop petit : afficher st.info('Données insuffisantes...')


                # ── BONUS : Graphique 4 — libre ───────────────────────────
                # TODO (bonus) : ajouter un 4ème graphique de votre choix
                # Idées : scatter panier_moyen vs ca_max, classement nb_commandes,
                #         comparaison CA max par catégorie...


                # ── Tableau complet (ne pas modifier) ─────────────────────
                with st.expander('📋 Voir toutes les catégories'):
                    st.dataframe(
                        df_cat.sort_values('ca_total', ascending=False)
                               .reset_index(drop=True),
                        use_container_width=True,
                    )

    # Attendre puis recharger (ne pas modifier)
    time.sleep(REFRESH)
    st.rerun()   # si erreur : utiliser st.experimental_rerun()
