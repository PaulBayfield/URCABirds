import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import client
from pages._theme import CSCALE, LAYOUT
from pages._i18n import t, day_map, day_order


def render():
    """Affiche la page d'exploration interactive des détections.

    Propose des filtres par espèce (nom scientifique), par identifiant de capteur
    et par nombre maximum de résultats. Génère ensuite les visualisations suivantes :

    - **Histogramme** des scores de confiance BirdNET.
    - **Barres horizontales** des 10 espèces les plus fréquentes dans le filtre courant.
    - **Heatmap** Heure × Jour de la semaine.
    - **Nuage de points** temporel (Temps × Espèce), coloré par score de confiance.
    - **Tableau** interactif des détections avec formatage des colonnes.
    """
    st.header(t("detections.header"))

    # Filtres de recherche : espèce, capteur et nombre max de résultats
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        species_filter = st.text_input(t("detections.filter.species"), "")
    with col2:
        sensor_filter = st.text_input(t("detections.filter.sensor"), "")
    with col3:
        limit = st.number_input(t("detections.limit"), min_value=10, max_value=500, value=100, step=10)

    # Appel API avec les filtres actifs
    with st.spinner(t("detections.loading")):
        kwargs = {"limit": int(limit)}
        if species_filter:
            kwargs["species"] = species_filter
        if sensor_filter:
            kwargs["sensor_id"] = sensor_filter
        data = client.get_detections(**kwargs)

    detections = data.get("detections", [])
    total = data.get("total", 0)
    st.caption(t("detections.caption", n=len(detections), total=total))

    if not detections:
        st.info(t("detections.empty"))
        return

    # Conversion en DataFrame et parsing des timestamps ISO8601 UTC
    df = pd.DataFrame(detections)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601", utc=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Histogramme de la distribution des scores de confiance (0 → 1)
        fig_conf = px.histogram(
            df, x="confidence",
            title=t("detections.confidence.title"),
            nbins=20,
            color_discrete_sequence=["#4dabf7"],
            labels={"confidence": t("detections.confidence.x")},
        )
        fig_conf.update_layout(bargap=0.05, yaxis_title=t("detections"), **LAYOUT)
        st.plotly_chart(fig_conf, use_container_width=True)

    with col_b:
        # Top 10 espèces les plus fréquentes dans le filtre courant
        sp_counts = df["species"].value_counts().head(10).reset_index()
        sp_counts.columns = ["species", "count"]
        fig_sp = px.bar(
            sp_counts.sort_values("count", ascending=True),
            x="count", y="species", orientation="h",
            title=t("detections.top_species.title"),
            color="count",
            color_continuous_scale=CSCALE,
            labels={"count": t("detections"), "species": ""},
        )
        fig_sp.update_layout(coloraxis_showscale=False, **LAYOUT)
        st.plotly_chart(fig_sp, use_container_width=True)

    # Extraction des colonnes temporelles pour la heatmap
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()
    dm = day_map()
    df["day_label"] = df["day_of_week"].map(dm)
    dorder = day_order()

    # Construction du tableau croisé Heure × Jour pour la heatmap
    hm_data = df.groupby(["day_label", "hour"]).size().reset_index(name="count")
    hm_pivot = hm_data.pivot(index="day_label", columns="hour", values="count").fillna(0)
    # Réordonne les lignes selon l'ordre des jours localisé
    hm_pivot = hm_pivot.reindex([d for d in dorder if d in hm_pivot.index])
    # Complète les heures manquantes pour garantir les 24 colonnes
    for h in range(24):
        if h not in hm_pivot.columns:
            hm_pivot[h] = 0
    hm_pivot = hm_pivot[sorted(hm_pivot.columns)]

    fig_hm = px.imshow(
        hm_pivot,
        title=t("detections.heatmap.title"),
        labels=dict(x=t("hour"), y="", color=t("detections")),
        color_continuous_scale=CSCALE,
        aspect="auto",
    )
    fig_hm.update_xaxes(tickmode="linear", tick0=0, dtick=1)
    fig_hm.update_layout(**LAYOUT)
    st.plotly_chart(fig_hm, use_container_width=True)

    # Nuage de points Temps × Espèce coloré par confiance
    fig_timeline = px.scatter(
        df, x="timestamp", y="species",
        color="confidence",
        title=t("detections.timeline.title"),
        color_continuous_scale=CSCALE,
        labels={"timestamp": t("time"), "species": t("species"), "confidence": t("confidence")},
        hover_data=["sensor_id", "confidence"],
    )
    fig_timeline.update_traces(marker_size=7)
    fig_timeline.update_layout(**LAYOUT)
    st.plotly_chart(fig_timeline, use_container_width=True)

    # Tableau interactif des détections avec formatage des colonnes
    st.subheader(t("detections.table.header"))
    st.dataframe(
        df[["timestamp", "species", "sensor_id", "confidence"]],
        column_config={
            "timestamp": st.column_config.DatetimeColumn(t("detected_at"), format=t("datetime_format")),
            "species": t("species"),
            "sensor_id": t("sensor"),
            # Barre de progression visuelle pour la confiance
            "confidence": st.column_config.ProgressColumn(t("confidence"), min_value=0.0, max_value=1.0),
        },
        hide_index=True,
        use_container_width=True,
    )
