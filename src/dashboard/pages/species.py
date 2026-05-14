import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import client
from pages._theme import CSCALE, LAYOUT


def render():
    st.header("Species Statistics")

    with st.spinner("Loading species data..."):
        species = client.get_species()

    if not species:
        st.info("No species detected yet.")
        return

    df = pd.DataFrame(species)
    if "last_detection" in df.columns:
        df["last_detection"] = pd.to_datetime(df["last_detection"])

    total_obs = int(df["total_detections"].sum()) if "total_detections" in df.columns else 0
    st.caption(f"{len(df)} species identified · {total_obs:,} total detections")

    if "total_detections" in df.columns:
        st.subheader("Species Diversity Treemap")
        fig_tree = px.treemap(
            df, path=["name"], values="total_detections",
            title="Species Diversity — area proportional to detection count",
            color="total_detections",
            color_continuous_scale=CSCALE,
        )
        fig_tree.update_traces(textinfo="label+value")
        fig_tree.update_layout(**LAYOUT)
        st.plotly_chart(fig_tree, use_container_width=True)

    st.divider()
    st.subheader("Most Detected Species")

    top_n = st.slider("Show top N species", min_value=5, max_value=min(50, len(df)), value=min(15, len(df)))
    top = df.nlargest(top_n, "total_detections")

    fig_bar = px.bar(
        top.sort_values("total_detections", ascending=True),
        x="total_detections", y="name", orientation="h",
        title=f"Top {top_n} Species by Detection Count",
        color="total_detections",
        color_continuous_scale=CSCALE,
        labels={"total_detections": "Total Detections", "name": ""},
    )
    fig_bar.update_layout(coloraxis_showscale=False, **LAYOUT)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.subheader("All Species")
    st.dataframe(
        df.sort_values("total_detections", ascending=False),
        column_config={
            "name": "Scientific Name",
            "total_detections": st.column_config.NumberColumn("Total Detections"),
            "last_detection": st.column_config.DatetimeColumn("Last Detected", format="MMM DD, YYYY, h:mm a"),
        },
        hide_index=True,
        use_container_width=True,
    )
