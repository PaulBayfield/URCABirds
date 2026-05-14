import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import client
from pages._theme import PALETTE, CSCALE, LAYOUT


def render():
    st.header("Overview")

    with st.spinner("Loading dashboard data..."):
        sensors = client.get_sensors()
        species = client.get_species()
        meta = client.get_detections(limit=1)
        recent = client.get_detections(limit=500)

    total_detections = meta.get("total", 0)
    active_sensors = len(sensors)
    total_species = len(species)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Detections", f"{total_detections:,}",
                  help="Total vocalizations detected across all sensors")
    with col2:
        st.metric("Active Sensors", active_sensors,
                  help="Acoustic sensors deployed on campus")
    with col3:
        st.metric("Species Identified", total_species,
                  help="Unique bird species detected by BirdNET")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        if species:
            sp_df = pd.DataFrame(species)
            if "total_detections" in sp_df.columns:
                top10 = sp_df.nlargest(10, "total_detections")
                fig = px.pie(
                    top10, values="total_detections", names="name",
                    title="Top 10 Species Distribution",
                    hole=0.45,
                    color_discrete_sequence=PALETTE,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
                fig.update_layout(showlegend=False, **LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

    with col_b:
        if sensors:
            sen_df = pd.DataFrame(sensors)
            if "total_detections" in sen_df.columns:
                fig = px.bar(
                    sen_df.sort_values("total_detections", ascending=True),
                    x="total_detections", y="name", orientation="h",
                    title="Detections per Sensor",
                    color="total_detections",
                    color_continuous_scale=CSCALE,
                    labels={"total_detections": "Detections", "name": ""},
                )
                fig.update_layout(coloraxis_showscale=False, **LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

    detections_list = recent.get("detections", [])
    if detections_list:
        trend_df = pd.DataFrame(detections_list)
        trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"])
        trend_df["hour"] = trend_df["timestamp"].dt.hour
        trend_df["day_of_week"] = trend_df["timestamp"].dt.day_name()

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data = trend_df.groupby(["day_of_week", "hour"]).size().reset_index(name="count")
        pivot = heatmap_data.pivot(index="day_of_week", columns="hour", values="count").fillna(0)
        pivot = pivot.reindex([d for d in day_order if d in pivot.index])
        for h in range(24):
            if h not in pivot.columns:
                pivot[h] = 0
        pivot = pivot[sorted(pivot.columns)]

        fig_heat = px.imshow(
            pivot,
            title="Activity Heatmap — Hour of Day × Day of Week",
            labels=dict(x="Hour of Day", y="", color="Detections"),
            color_continuous_scale=CSCALE,
            aspect="auto",
        )
        fig_heat.update_xaxes(tickmode="linear", tick0=0, dtick=1)
        fig_heat.update_layout(**LAYOUT)
        st.plotly_chart(fig_heat, use_container_width=True)

        fig_trend = px.histogram(
            trend_df, x="timestamp",
            title=f"Detection Activity Over Time (last {len(detections_list)} records)",
            nbins=40,
            color_discrete_sequence=["#4dabf7"],
            labels={"timestamp": "Time"},
        )
        fig_trend.update_layout(bargap=0.05, yaxis_title="Detections", **LAYOUT)
        st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()
    st.subheader("Recent Activity")
    recent10 = client.get_detections(limit=10)
    df = pd.DataFrame(recent10.get("detections", []))
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
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
    else:
        st.info("No detections recorded yet.")
