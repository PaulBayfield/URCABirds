import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import client
from pages._theme import CSCALE, LAYOUT


def render():
    st.header("Detections Explorer")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        species_filter = st.text_input("Filter by Species (scientific name)", "")
    with col2:
        sensor_filter = st.text_input("Filter by Sensor ID", "")
    with col3:
        limit = st.number_input("Limit", min_value=10, max_value=500, value=100, step=10)

    with st.spinner("Loading detections..."):
        kwargs = {"limit": int(limit)}
        if species_filter:
            kwargs["species"] = species_filter
        if sensor_filter:
            kwargs["sensor_id"] = sensor_filter
        data = client.get_detections(**kwargs)

    detections = data.get("detections", [])
    total = data.get("total", 0)
    st.caption(f"Showing {len(detections)} of {total} total detections")

    if not detections:
        st.info("No detections found matching the current filters.")
        return

    df = pd.DataFrame(detections)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    col_a, col_b = st.columns(2)

    with col_a:
        fig_conf = px.histogram(
            df, x="confidence",
            title="Confidence Score Distribution",
            nbins=20,
            color_discrete_sequence=["#4dabf7"],
            labels={"confidence": "Confidence Score"},
        )
        fig_conf.update_layout(bargap=0.05, yaxis_title="Detections", **LAYOUT)
        st.plotly_chart(fig_conf, use_container_width=True)

    with col_b:
        sp_counts = df["species"].value_counts().head(10).reset_index()
        sp_counts.columns = ["species", "count"]
        fig_sp = px.bar(
            sp_counts.sort_values("count", ascending=True),
            x="count", y="species", orientation="h",
            title="Top Species in Current Filter",
            color="count",
            color_continuous_scale=CSCALE,
            labels={"count": "Detections", "species": ""},
        )
        fig_sp.update_layout(coloraxis_showscale=False, **LAYOUT)
        st.plotly_chart(fig_sp, use_container_width=True)

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hm_data = df.groupby(["day_of_week", "hour"]).size().reset_index(name="count")
    hm_pivot = hm_data.pivot(index="day_of_week", columns="hour", values="count").fillna(0)
    hm_pivot = hm_pivot.reindex([d for d in day_order if d in hm_pivot.index])
    for h in range(24):
        if h not in hm_pivot.columns:
            hm_pivot[h] = 0
    hm_pivot = hm_pivot[sorted(hm_pivot.columns)]

    fig_hm = px.imshow(
        hm_pivot,
        title="Detection Heatmap — Hour of Day × Day of Week",
        labels=dict(x="Hour of Day", y="", color="Detections"),
        color_continuous_scale=CSCALE,
        aspect="auto",
    )
    fig_hm.update_xaxes(tickmode="linear", tick0=0, dtick=1)
    fig_hm.update_layout(**LAYOUT)
    st.plotly_chart(fig_hm, use_container_width=True)

    fig_timeline = px.scatter(
        df, x="timestamp", y="species",
        color="confidence",
        title="Detection Timeline",
        color_continuous_scale=CSCALE,
        labels={"timestamp": "Time", "species": "Species", "confidence": "Confidence"},
        hover_data=["sensor_id", "confidence"],
    )
    fig_timeline.update_traces(marker_size=7)
    fig_timeline.update_layout(**LAYOUT)
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.subheader("Detection Records")
    st.dataframe(
        df[["timestamp", "species", "sensor_id", "confidence"]],
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Detected At", format="MMM DD, YYYY, h:mm a"),
            "species": "Species",
            "sensor_id": "Sensor",
            "confidence": st.column_config.ProgressColumn("Confidence", min_value=0.0, max_value=1.0),
        },
        hide_index=True,
        use_container_width=True,
    )
