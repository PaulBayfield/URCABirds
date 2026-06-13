import streamlit as st
import os

# Import de chaque page du dashboard
import pages.overview as page_overview
import pages.detections as page_detections
import pages.trends as page_trends
import pages.sensors as page_sensors
import pages.species as page_species
import pages.movements as page_movements
import pages.audio as page_audio
from pages._i18n import t, LANGUAGES

# Configuration globale de l'application Streamlit (titre, icône, mise en page)
st.set_page_config(
    page_title="URCABirds Dashboard",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personnalisé : police globale et style des cartes de métriques
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

# Affichage du logo si le fichier existe dans le dossier assets
logo_path = os.path.join(os.path.dirname(__file__), "../../assets/logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path, size="large")

# Langue par défaut au premier chargement (stockée dans la session Streamlit)
if "lang" not in st.session_state:
    st.session_state["lang"] = "Français"

# Déclaration de la navigation multi-pages avec icônes et chemins URL
pg = st.navigation([
    st.Page(page_overview.render,   title=t("nav.overview"),   icon="📊", url_path="overview",   default=True),
    st.Page(page_movements.render,  title=t("nav.movements"),  icon="🗺️", url_path="movements"),
    st.Page(page_detections.render, title=t("nav.detections"), icon="🔍", url_path="detections"),
    st.Page(page_trends.render,     title=t("nav.trends"),     icon="📈", url_path="trends"),
    st.Page(page_sensors.render,    title=t("nav.sensors"),    icon="📡", url_path="sensors"),
    st.Page(page_species.render,    title=t("nav.species"),    icon="🦜", url_path="species"),
    st.Page(page_audio.render,      title=t("nav.audio"),      icon="🎵", url_path="audio"),
])

# Contenu de la barre latérale : titre, sous-titre, sélecteur de langue et URL de l'API
with st.sidebar:
    st.markdown("## URCABirds")
    st.caption(t("app.subtitle"))
    st.divider()
    # Sélecteur de langue — met à jour st.session_state["lang"] automatiquement
    st.selectbox(
        t("app.lang_label"),
        options=LANGUAGES,
        key="lang",
        label_visibility="collapsed",
    )
    st.divider()
    # Affiche l'URL de l'API configurée (variable d'environnement API_URL)
    api_url = os.environ.get("API_URL", "http://localhost:8000")
    st.caption(f"{t('app.api_label')} {api_url}")

# Lance le routeur de pages — affiche la page correspondant à l'URL courante
pg.run()
