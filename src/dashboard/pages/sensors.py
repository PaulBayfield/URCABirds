import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import client
from pages._theme import PALETTE, CSCALE, LAYOUT
from pages._i18n import t


def render():
    """Affiche la page de gestion et de visualisation du réseau de capteurs.

    Charge la liste des capteurs depuis l'API et présente :

    - **Carte géographique** des capteurs (uniquement si les colonnes ``latitude``
      et ``longitude`` sont disponibles), avec taille des points proportionnelle
      au nombre de détections.
    - **Barres horizontales** du volume de détections par capteur.
    - **Camembert** de la part relative de chaque capteur.
    - **Tableau** récapitulatif avec horodatages de connexion et de dernière détection.
    """
    st.header(t("sensors.header"))

    with st.spinner(t("sensors.loading")):
        sensors = client.get_sensors()

    if not sensors:
        st.info(t("sensors.empty"))
        return

    df = pd.DataFrame(sensors)

    # --- Carte géographique des capteurs (uniquement si les coordonnées GPS sont disponibles) ---
    if "latitude" in df.columns and "longitude" in df.columns:
        map_df = df.dropna(subset=["latitude", "longitude"])
        if not map_df.empty:
            st.subheader(t("sensors.map.header"))
            # La taille des points est proportionnelle au nombre de détections si la colonne existe
            has_size = "total_detections" in map_df.columns and map_df["total_detections"].sum() > 0
            # Colonnes affichées dans l'infobulle au survol
            hover_cols = {c: True for c in ["sensor_id", "total_detections", "description"] if c in map_df.columns}
            fig_map = px.scatter_mapbox(
                map_df,
                lat="latitude", lon="longitude",
                hover_name="name",
                hover_data=hover_cols,
                color="total_detections" if "total_detections" in map_df.columns else None,
                size="total_detections" if has_size else None,
                size_max=30,
                color_continuous_scale=CSCALE,
                zoom=15,
                height=450,
            )
            fig_map.update_layout(
                mapbox_style="open-street-map",
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
            )
            st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        # Barres horizontales du volume de détections par capteur
        if "total_detections" in df.columns:
            fig_bar = px.bar(
                df.sort_values("total_detections", ascending=True),
                x="total_detections", y="name", orientation="h",
                title=t("sensors.bar.title"),
                color="total_detections",
                color_continuous_scale=CSCALE,
                labels={"total_detections": t("detections"), "name": ""},
            )
            fig_bar.update_layout(coloraxis_showscale=False, **LAYOUT)
            st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        # Camembert de la part relative de chaque capteur dans le total des détections
        if "total_detections" in df.columns and df["total_detections"].sum() > 0:
            fig_pie = px.pie(
                df, values="total_detections", names="name",
                title=t("sensors.pie.title"),
                color_discrete_sequence=PALETTE,
                hole=0.3,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(showlegend=False, **LAYOUT)
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- Tableau récapitulatif de tous les capteurs ---
    st.subheader(t("sensors.table.header"))
    # Conversion des colonnes de dates ISO8601 en objets datetime UTC
    for col in ["first_registered", "last_connection", "last_detection"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="ISO8601", utc=True)
    # Sélection des colonnes disponibles uniquement (robustesse si l'API évolue)
    display_cols = [c for c in ["name", "sensor_id", "description", "total_detections", "last_connection"] if c in df.columns]
    st.dataframe(df[display_cols], hide_index=True, use_container_width=True)
