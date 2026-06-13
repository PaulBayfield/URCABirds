import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import client
from pages._theme import CSCALE, LAYOUT
from pages._i18n import t


def render():
    """Affiche la page d'analyse des tendances temporelles des détections.

    Charge les 1 000 détections les plus récentes et produit les graphiques
    suivants :

    - **Courbe quotidienne** du nombre de détections (area chart).
    - **Richesse spécifique** quotidienne (nombre d'espèces uniques par jour).
    - **Diagramme polaire** de l'activité par heure de la journée.
    - **Barres hebdomadaires** colorées par richesse spécifique.
    - **Courbes multi-espèces** des 5 espèces les plus fréquentes (évolution quotidienne).
    """
    st.header(t("trends.header"))

    # Chargement d'un grand lot de détections pour avoir des tendances significatives
    with st.spinner(t("trends.loading")):
        data = client.get_detections(limit=1000)

    detections = data.get("detections", [])
    if not detections:
        st.info(t("trends.empty"))
        return

    # Préparation du DataFrame : extraction des colonnes temporelles utiles
    df = pd.DataFrame(detections)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601", utc=True)
    df["date"] = df["timestamp"].dt.normalize()       # Date sans heure
    df["hour"] = df["timestamp"].dt.hour
    # Début de semaine ISO pour l'agrégation hebdomadaire
    df["week_start"] = df["timestamp"].dt.to_period("W").apply(lambda p: p.start_time)

    # Agrégation quotidienne : volume total + richesse spécifique
    daily_count = df.groupby("date").size().reset_index(name="detections")
    daily_rich = df.groupby("date")["species"].nunique().reset_index(name="unique_species")
    daily = daily_count.merge(daily_rich, on="date")

    # --- Courbe de détections quotidiennes avec zone de remplissage ---
    fig_daily = px.line(
        daily, x="date", y="detections",
        title=t("trends.daily.title"),
        labels={"date": t("date"), "detections": t("detections")},
        color_discrete_sequence=["#4dabf7"],
    )
    # fill="tozeroy" crée l'effet "area chart" sous la courbe
    fig_daily.update_traces(fill="tozeroy", fillcolor="rgba(77,171,247,0.08)", mode="lines+markers", marker_size=4)
    fig_daily.update_layout(**LAYOUT)
    st.plotly_chart(fig_daily, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Richesse spécifique quotidienne (nombre d'espèces uniques par jour)
        fig_rich = px.line(
            daily, x="date", y="unique_species",
            title=t("trends.richness.title"),
            labels={"date": t("date"), "unique_species": t("trends.richness.y")},
            color_discrete_sequence=["#69db7c"],
        )
        fig_rich.update_traces(fill="tozeroy", fillcolor="rgba(105,219,124,0.08)", mode="lines+markers", marker_size=4)
        fig_rich.update_layout(**LAYOUT)
        st.plotly_chart(fig_rich, use_container_width=True)

    with col_b:
        # Diagramme polaire de l'activité horaire (rose des activités diurnes)
        hourly = df.groupby("hour").size().reset_index(name="detections")
        hour_labels = [f"{h:02d}:00" for h in range(24)]
        hourly["hour_label"] = hourly["hour"].apply(lambda h: f"{h:02d}:00")

        fig_dawn = px.bar_polar(
            hourly, r="detections", theta="hour_label",
            title=t("trends.hourly.title"),
            color="detections",
            color_continuous_scale=CSCALE,
            # Assure l'ordre horaire correct sur l'axe angulaire
            category_orders={"hour_label": hour_labels},
        )
        fig_dawn.update_layout(showlegend=False, **LAYOUT)
        st.plotly_chart(fig_dawn, use_container_width=True)

    st.divider()

    # Agrégation hebdomadaire : volume total + richesse pour la coloration
    weekly = (
        df.groupby("week_start")
        .agg(detections=("species", "count"), unique_species=("species", "nunique"))
        .reset_index()
    )
    fmt = t("trends.weekly.x_fmt")
    weekly["week_label"] = weekly["week_start"].dt.strftime(fmt)

    # Barres hebdomadaires colorées par richesse spécifique
    fig_week = px.bar(
        weekly, x="week_label", y="detections",
        title=t("trends.weekly.title"),
        color="unique_species",
        color_continuous_scale=CSCALE,
        labels={"week_label": "", "detections": t("detections"), "unique_species": t("trends.richness.y")},
        text="detections",
    )
    fig_week.update_traces(textposition="outside")
    fig_week.update_layout(coloraxis_colorbar_title=t("trends.weekly.colorbar"), **LAYOUT)
    st.plotly_chart(fig_week, use_container_width=True)

    st.divider()

    # --- Top 5 espèces : évolution quotidienne des détections ---
    top5 = df["species"].value_counts().head(5).index.tolist()
    top5_df = df[df["species"].isin(top5)].copy()
    top5_daily = top5_df.groupby(["date", "species"]).size().reset_index(name="count")

    fig_top5 = px.line(
        top5_daily, x="date", y="count", color="species",
        title=t("trends.top5.title"),
        labels={"date": t("date"), "count": t("detections"), "species": t("species")},
        markers=True,
    )
    fig_top5.update_traces(marker_size=4)
    fig_top5.update_layout(**LAYOUT)
    st.plotly_chart(fig_top5, use_container_width=True)
