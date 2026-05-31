import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import client
from pages._theme import CSCALE, LAYOUT
from pages._i18n import t


def render():
    st.header(t("species.header"))

    with st.spinner(t("species.loading")):
        species = client.get_species()

    if not species:
        st.info(t("species.empty"))
        return

    df = pd.DataFrame(species)
    if "last_detection" in df.columns:
        df["last_detection"] = pd.to_datetime(df["last_detection"])

    total_obs = int(df["total_detections"].sum()) if "total_detections" in df.columns else 0
    st.caption(t("species.caption", n=len(df), total=f"{total_obs:,}"))

    if "total_detections" in df.columns:
        st.subheader(t("species.treemap.header"))
        fig_tree = px.treemap(
            df, path=["name"], values="total_detections",
            title=t("species.treemap.title"),
            color="total_detections",
            color_continuous_scale=CSCALE,
        )
        fig_tree.update_traces(textinfo="label+value")
        fig_tree.update_layout(**LAYOUT)
        st.plotly_chart(fig_tree, use_container_width=True)

    st.divider()
    st.subheader(t("species.top.header"))

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
