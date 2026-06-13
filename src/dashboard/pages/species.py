import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import client
from pages._theme import CSCALE, LAYOUT
from pages._i18n import t


def render():
    """Affiche la page de statistiques par espèce.

    Charge la liste des espèces depuis l'API et présente :

    - **Treemap** de la diversité des espèces (surface proportionnelle au nombre
      de détections).
    - **Barres horizontales** des N espèces les plus détectées, avec un curseur
      permettant d'ajuster N dynamiquement.
    - **Tableau** complet de toutes les espèces, trié par volume décroissant,
      avec la date de dernière détection.
    """
    st.header(t("species.header"))

    with st.spinner(t("species.loading")):
        species = client.get_species()

    if not species:
        st.info(t("species.empty"))
        return

    df = pd.DataFrame(species)
    # Conversion de la date de dernière détection en datetime UTC
    if "last_detection" in df.columns:
        df["last_detection"] = pd.to_datetime(df["last_detection"], format="ISO8601", utc=True)

    # Calcul du total de toutes les détections pour la légende
    total_obs = int(df["total_detections"].sum()) if "total_detections" in df.columns else 0
    st.caption(t("species.caption", n=len(df), total=f"{total_obs:,}"))

    # --- Treemap : diversité des espèces (surface ∝ détections) ---
    if "total_detections" in df.columns:
        st.subheader(t("species.treemap.header"))
        fig_tree = px.treemap(
            df, path=["name"], values="total_detections",
            title=t("species.treemap.title"),
            color="total_detections",
            color_continuous_scale=CSCALE,
        )
        # Affiche le nom et le comptage dans chaque cellule du treemap
        fig_tree.update_traces(textinfo="label+value")
        fig_tree.update_layout(**LAYOUT)
        st.plotly_chart(fig_tree, use_container_width=True)

    # --- Barres horizontales des N espèces les plus détectées ---
    st.divider()
    st.subheader(t("species.top.header"))

    # Slider permettant à l'utilisateur de choisir le nombre d'espèces affichées
    top_n = st.slider(t("species.slider"), min_value=5, max_value=min(50, len(df)), value=min(15, len(df)))
    top = df.nlargest(top_n, "total_detections")

    fig_bar = px.bar(
        top.sort_values("total_detections", ascending=True),
        x="total_detections", y="name", orientation="h",
        title=t("species.bar.title", n=top_n),
        color="total_detections",
        color_continuous_scale=CSCALE,
        labels={"total_detections": t("species.bar.x"), "name": ""},
    )
    fig_bar.update_layout(coloraxis_showscale=False, **LAYOUT)
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Tableau complet de toutes les espèces triées par volume décroissant ---
    st.divider()
    st.subheader(t("species.all.header"))
    st.dataframe(
        df.sort_values("total_detections", ascending=False),
        column_config={
            "name": t("species.col.name"),
            "total_detections": st.column_config.NumberColumn(t("species.col.total")),
            "last_detection": st.column_config.DatetimeColumn(t("species.col.last"), format=t("datetime_format")),
        },
        hide_index=True,
        use_container_width=True,
    )
