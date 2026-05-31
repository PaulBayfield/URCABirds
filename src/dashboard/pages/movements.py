import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta

from api_client import client
from pages._theme import CSCALE, LAYOUT
from pages._i18n import t


def _infer_movements(df: pd.DataFrame, window_minutes: int) -> pd.DataFrame:
    if len(df) < 2:
        return pd.DataFrame()

    df = df.sort_values("timestamp").reset_index(drop=True)
    window = timedelta(minutes=window_minutes)

    movements = []
    for i in range(len(df) - 1):
        a = df.iloc[i]
        b = df.iloc[i + 1]
        delta = b["timestamp"] - a["timestamp"]
        if delta <= window and a["sensor_id"] != b["sensor_id"]:
            movements.append({
                "from_sensor": a["sensor_id"],
                "to_sensor": b["sensor_id"],
                "from_time": a["timestamp"],
                "to_time": b["timestamp"],
                "delta_minutes": round(delta.total_seconds() / 60, 1),
                "species": a["species"],
            })

    return pd.DataFrame(movements)


def render():
    st.header(t("movements.header"))
    st.caption(t("movements.caption"))

    with st.spinner(t("movements.loading")):
        species_list = client.get_species()
        sensors = client.get_sensors()

    if not species_list:
        st.info(t("movements.no_species"))
        return
    if not sensors:
        st.info(t("movements.no_sensors"))
        return

    sensors_df = pd.DataFrame(sensors)
    sensor_map = {}
    if "sensor_id" in sensors_df.columns:
        for _, row in sensors_df.iterrows():
            sensor_map[row["sensor_id"]] = {
                "name": row.get("name", row["sensor_id"]),
                "lat": row.get("latitude"),
                "lon": row.get("longitude"),
            }

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        species_names = [s["name"] for s in species_list]
        selected_species = st.selectbox(t("movements.select.species"), species_names)
    with col2:
        window_minutes = st.slider(t("movements.slider.window"), min_value=5, max_value=240, value=60, step=5)
    with col3:
        fetch_limit = st.number_input(t("movements.input.limit"), min_value=100, max_value=1000, value=500, step=100)

    with st.spinner(t("movements.loading.species", species=selected_species)):
        data = client.get_detections(limit=int(fetch_limit), species=selected_species)

    detections = data.get("detections", [])
    if not detections:
        st.info(t("movements.no_detections", species=selected_species))
        return

    df = pd.DataFrame(detections)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["sensor_name"] = df["sensor_id"].map(lambda sid: sensor_map.get(sid, {}).get("name", sid))

    n_sensors = df["sensor_id"].nunique()
    st.caption(t("movements.detections.caption", n=len(df), k=n_sensors))

    movements_df = _infer_movements(df, window_minutes)

    st.subheader(t("movements.timeline.header"))
    fig_timeline = px.scatter(
        df.sort_values("timestamp"),
        x="timestamp",
        y="sensor_name",
        color="confidence",
        color_continuous_scale=CSCALE,
        title=t("movements.timeline.title", species=selected_species),
        labels={"timestamp": t("time"), "sensor_name": t("movements.timeline.y"), "confidence": t("confidence")},
        hover_data=["sensor_id", "confidence"],
    )
    if not movements_df.empty:
        for _, mv in movements_df.iterrows():
            from_name = sensor_map.get(mv["from_sensor"], {}).get("name", mv["from_sensor"])
            to_name = sensor_map.get(mv["to_sensor"], {}).get("name", mv["to_sensor"])
            fig_timeline.add_shape(
                type="line",
                x0=mv["from_time"], y0=from_name,
                x1=mv["to_time"], y1=to_name,
                line=dict(color="rgba(255,107,53,0.6)", width=2, dash="dot"),
            )
    fig_timeline.update_traces(marker_size=8)
    fig_timeline.update_layout(**LAYOUT)
    st.plotly_chart(fig_timeline, use_container_width=True)

    valid_sensors = [
        sid for sid in df["sensor_id"].unique()
        if sensor_map.get(sid, {}).get("lat") is not None
    ]
    map_available = (
        len(valid_sensors) > 0
        and "latitude" in sensors_df.columns
        and "longitude" in sensors_df.columns
    )

    if map_available:
        st.subheader(t("movements.map.header"))
        fig_map = go.Figure()

        if not movements_df.empty:
            mv_counts = movements_df.groupby(["from_sensor", "to_sensor"]).size().reset_index(name="count")
            max_count = mv_counts["count"].max()
            for _, row in mv_counts.iterrows():
                s_from = sensor_map.get(row["from_sensor"], {})
                s_to = sensor_map.get(row["to_sensor"], {})
                if not s_from.get("lat") or not s_to.get("lat"):
                    continue
                line_width = 2 + 5 * (row["count"] / max_count)
                fig_map.add_trace(go.Scattermapbox(
                    lat=[s_from["lat"], s_to["lat"]],
                    lon=[s_from["lon"], s_to["lon"]],
                    mode="lines",
                    line=dict(width=line_width, color="#ff6b35"),
                    hoverinfo="text",
                    text=t("movements.map.hover", from_=s_from["name"], to_=s_to["name"], count=row["count"]),
                    showlegend=False,
                ))

        map_sensors = sensors_df[sensors_df["sensor_id"].isin(valid_sensors)].dropna(
            subset=["latitude", "longitude"]
        )
        if not map_sensors.empty:
            det_counts = df.groupby("sensor_id").size().reset_index(name="det_count")
            map_sensors = map_sensors.merge(det_counts, on="sensor_id", how="left").fillna({"det_count": 0})
            max_det = map_sensors["det_count"].max() or 1
            fig_map.add_trace(go.Scattermapbox(
                lat=map_sensors["latitude"],
                lon=map_sensors["longitude"],
                mode="markers+text",
                marker=dict(
                    size=14 + (map_sensors["det_count"] / max_det * 16),
                    color="#4dabf7",
                    opacity=0.9,
                ),
                text=map_sensors["name"],
                textposition="top right",
                hovertext=map_sensors.apply(
                    lambda r: f"{r['name']}<br>{int(r['det_count'])} {t('detections').lower()}", axis=1
                ),
                hoverinfo="text",
                name=t("movements.sensors_label"),
            ))

        center_lat = sensors_df["latitude"].dropna().mean()
        center_lon = sensors_df["longitude"].dropna().mean()
        fig_map.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": center_lat, "lon": center_lon},
            mapbox_zoom=14,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=450,
            showlegend=False,
        )
        st.plotly_chart(fig_map, use_container_width=True)

    st.divider()
    if movements_df.empty:
        st.info(t("movements.no_movements", window=window_minutes))
        return

    st.subheader(t("movements.table.header", n=len(movements_df)))
    movements_df["from_name"] = movements_df["from_sensor"].map(
        lambda s: sensor_map.get(s, {}).get("name", s)
    )
    movements_df["to_name"] = movements_df["to_sensor"].map(
        lambda s: sensor_map.get(s, {}).get("name", s)
    )

    col_sum, col_detail = st.columns([1, 2])
    with col_sum:
        summary = (
            movements_df.groupby(["from_name", "to_name"])
            .agg(count=("delta_minutes", "count"), avg_minutes=("delta_minutes", "mean"))
            .reset_index()
            .round({"avg_minutes": 1})
        )
        summary.columns = [
            t("movements.col.from"),
            t("movements.col.to"),
            t("movements.col.count"),
            t("movements.col.avg_dt"),
        ]
        st.dataframe(summary, hide_index=True, use_container_width=True)

    with col_detail:
        display = movements_df[["from_time", "from_name", "to_name", "delta_minutes"]].copy()
        display.columns = [
            t("movements.col.departure"),
            t("movements.col.from"),
            t("movements.col.to"),
            t("movements.col.dt"),
        ]
        departure_col = t("movements.col.departure")
        st.dataframe(
            display,
            column_config={
                departure_col: st.column_config.DatetimeColumn(departure_col, format=t("movements.departure_fmt")),
            },
            hide_index=True,
            use_container_width=True,
        )
