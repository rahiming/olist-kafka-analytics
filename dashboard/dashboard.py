import json
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

STATS_FILE = Path(__file__).resolve().parents[1] / "output" / "stats.json"
REFRESH = 5


def load_data(stats_file: Path = STATS_FILE):
    """Load dashboard data from the processor output JSON file."""
    if not stats_file.exists():
        return None, None

    try:
        with stats_file.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except json.JSONDecodeError:
        return (pd.DataFrame(), pd.DataFrame()), {
            "mise_a_jour": "Calcul en cours...",
            "total_commandes": 0,
            "ca_global": 0,
            "panier_moyen_global": 0,
            "commande_max": 0,
        }

    df_cat = pd.DataFrame(raw.get("categories", []))
    df_evo = pd.DataFrame(raw.get("evolution", []))
    meta = {
        "mise_a_jour": raw.get("mise_a_jour", "-"),
        "total_commandes": raw.get("total_commandes", 0),
        "ca_global": raw.get("ca_global", 0),
        "panier_moyen_global": raw.get("panier_moyen_global", 0),
        "commande_max": raw.get("commande_max", 0),
    }
    return (df_cat, df_evo), meta


def render_dashboard() -> None:
    st.set_page_config(
        page_title="E-Commerce Analytics",
        page_icon=":shopping_trolley:",
        layout="wide",
    )

    st.markdown(
        """
        <style>
            [data-testid="metric-container"] {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 16px 20px;
            }
            [data-testid="metric-container"] label {
                color: #64748b !important;
                font-size: 0.85rem !important;
            }
            [data-testid="metric-container"] [data-testid="stMetricValue"] {
                color: #1e293b !important;
                font-size: 1.6rem !important;
                font-weight: 700 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("E-Commerce Real-Time Analytics")
    st.caption("Source: Olist Brazilian E-Commerce data - refresh every 5 seconds")

    placeholder = st.empty()

    while True:
        result, meta = load_data()

        with placeholder.container():
            if result is None or meta is None:
                st.warning("Waiting for data. Start the processor first.")
                st.code("python processor/processor.py")
            else:
                df_cat, df_evo = result

                st.caption(f"Last update: **{meta['mise_a_jour']}**")
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Orders", f"{meta['total_commandes']:,}")
                c2.metric("Revenue (R$)", f"{meta['ca_global']:,.0f}")
                c3.metric("Avg basket (R$)", f"{meta['panier_moyen_global']:.2f}")
                c4.metric("Max order (R$)", f"{meta['commande_max']:.2f}")
                c5.metric("Active categories", str(len(df_cat)))

                st.divider()

                if not df_cat.empty:
                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.subheader("Revenue by category - Top 10")
                        top10 = df_cat.nlargest(10, "ca_total")
                        fig1 = px.bar(
                            top10,
                            x="ca_total",
                            y="categorie",
                            orientation="h",
                            color="ca_total",
                            color_continuous_scale="Blues",
                            labels={"ca_total": "Revenue (R$)", "categorie": "Category"},
                            text="ca_total",
                        )
                        fig1.update_traces(texttemplate="R$%{text:,.0f}", textposition="outside")
                        fig1.update_layout(
                            showlegend=False,
                            coloraxis_showscale=False,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            yaxis={"categoryorder": "total ascending"},
                        )
                        st.plotly_chart(fig1, use_container_width=True)

                    with col_b:
                        st.subheader("Order split - Top 8")
                        top8 = df_cat.nlargest(8, "nb_commandes")
                        fig2 = px.pie(top8, names="categorie", values="nb_commandes", hole=0.45)
                        fig2.update_traces(textposition="inside", textinfo="percent+label")
                        fig2.update_layout(
                            showlegend=False,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                    st.subheader("Revenue over time")
                    if not df_evo.empty and len(df_evo) > 1:
                        df_evo_sorted = df_evo.sort_values("heure")
                        fig3 = px.area(
                            df_evo_sorted,
                            x="heure",
                            y="ca_total",
                            labels={"heure": "Hour", "ca_total": "Revenue (R$)"},
                            color_discrete_sequence=["#3b82f6"],
                        )
                        fig3.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            xaxis_tickangle=-45,
                        )
                        st.plotly_chart(fig3, use_container_width=True)
                    else:
                        st.info("Not enough history yet to render the time series.")

                    st.subheader("Avg basket vs max order by category")
                    fig4 = px.scatter(
                        df_cat,
                        x="panier_moyen",
                        y="ca_max",
                        size="nb_commandes",
                        color="categorie",
                        hover_name="categorie",
                        hover_data={
                            "nb_commandes": True,
                            "ca_total": True,
                            "categorie": False,
                        },
                        labels={
                            "panier_moyen": "Avg basket (R$)",
                            "ca_max": "Max order (R$)",
                            "nb_commandes": "Orders",
                        },
                    )
                    fig4.update_layout(
                        showlegend=False,
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig4, use_container_width=True)

                    with st.expander("Show all categories"):
                        st.dataframe(
                            df_cat.sort_values("ca_total", ascending=False).reset_index(drop=True),
                            use_container_width=True,
                            column_config={
                                "categorie": "Category",
                                "nb_commandes": "Orders",
                                "ca_total": st.column_config.NumberColumn(
                                    "Revenue (R$)", format="R$%.2f"
                                ),
                                "panier_moyen": st.column_config.NumberColumn(
                                    "Avg basket (R$)", format="R$%.2f"
                                ),
                                "ca_max": st.column_config.NumberColumn(
                                    "Max order (R$)", format="R$%.2f"
                                ),
                            },
                        )

        time.sleep(REFRESH)
        st.rerun()


if __name__ == "__main__":
    render_dashboard()
