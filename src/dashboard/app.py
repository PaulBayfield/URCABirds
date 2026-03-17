import streamlit as st
import os

from views import render_overview, render_detections, render_sensors, render_species

# App Configuration
st.set_page_config(
    page_title="URCABirds Dashboard",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for UI aesthetics
st.markdown("""
<style>
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background-color: #212529;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4dabf7;
    }
    .metric-label {
        font-size: 1.1rem;
        color: #ced4da;
    }
</style>
""", unsafe_allow_html=True)

# Application state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'Overview'

# Sidebar navigation
with st.sidebar:
    st.title("URCABirds")
    st.caption("Acoustic Monitoring Dashboard")
    st.divider()
    
    view_options = ["Overview", "Detections", "Sensors", "Species"]
    st.session_state.current_view = st.radio("Navigation", view_options)
    
    st.divider()
    st.caption(f"API Connected: {os.environ.get('API_URL', 'http://localhost:8000')}")

# Routing
if st.session_state.current_view == "Overview":
    render_overview()
elif st.session_state.current_view == "Detections":
    render_detections()
elif st.session_state.current_view == "Sensors":
    render_sensors()
elif st.session_state.current_view == "Species":
    render_species()
