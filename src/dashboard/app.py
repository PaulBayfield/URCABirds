import streamlit as st
import os

import pages.overview as page_overview
import pages.detections as page_detections
import pages.trends as page_trends
import pages.sensors as page_sensors
import pages.species as page_species
import pages.audio as page_audio

st.set_page_config(
    page_title="URCABirds Dashboard",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { font-family: 'Inter', sans-serif; }
    .metric-card {
        background-color: #212529;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value { font-size: 2.5rem; font-weight: 700; color: #4dabf7; }
    .metric-label { font-size: 1.1rem; color: #ced4da; }
</style>
""", unsafe_allow_html=True)

if "current_view" not in st.session_state:
    st.session_state.current_view = "Overview"

with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "../../assets/logo.png")
    if os.path.exists(logo_path):
        st.logo(logo_path, size="large")

    st.markdown("## URCABirds")
    st.caption("Acoustic Bird Monitoring · Moulin de la Housse")
    st.divider()

    view_options = ["Overview", "Detections", "Trends", "Sensors", "Species", "Audio"]
    st.session_state.current_view = st.radio("Navigation", view_options, label_visibility="collapsed")

    st.divider()
    api_url = os.environ.get("API_URL", "http://localhost:8000")
    st.caption(f"API: {api_url}")

if st.session_state.current_view == "Overview":
    page_overview.render()
elif st.session_state.current_view == "Detections":
    page_detections.render()
elif st.session_state.current_view == "Trends":
    page_trends.render()
elif st.session_state.current_view == "Sensors":
    page_sensors.render()
elif st.session_state.current_view == "Species":
    page_species.render()
elif st.session_state.current_view == "Audio":
    page_audio.render()
