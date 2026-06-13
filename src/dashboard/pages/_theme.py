import plotly.express as px

# Palette de couleurs qualitative utilisée pour les graphiques multi-séries (camembert, etc.)
PALETTE = px.colors.qualitative.Plotly

# Échelle de couleur séquentielle pour les heatmaps et cartes choroplèthes
CSCALE = "Blues"

# Paramètres de mise en page Plotly communs à tous les graphiques :
# fonds transparents pour s'intégrer au thème sombre Streamlit, police cohérente
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif"),
    title_font=dict(size=16),
)
