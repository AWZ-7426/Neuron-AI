import streamlit as st
import os
import subprocess
import sys

# --- 1. INSTALLATION AUTOMATIQUE DU MODÈLE FRANÇAIS ---
@st.cache_resource
def install_spacy_model():
    try:
        import spacy
        # On vérifie si le modèle français est déjà là
        if not spacy.util.is_package("fr_core_news_sm"):
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "fr_core_news_sm"])
        return spacy.load("fr_core_news_sm")
    except Exception as e:
        st.error(f"Erreur d'installation : {e}")
        return None

# --- 2. CONFIGURATION & VALIDATION (INDISPENSABLE EN HAUT) ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# Injection des IDs pour Google et Bing
import streamlit.components.v1 as components
components.html(
    """
    <script>
        var head = parent.document.getElementsByTagName('head')[0];
        var g = document.createElement('meta'); g.name="google-site-verification"; g.content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY";
        var b = document.createElement('meta'); b.name="msvalidate.01"; b.content="BA1A2EF4B67CEB856BA0329B7C545711";
        head.appendChild(g); head.appendChild(b);
    </script>
    """, height=0
)

nlp = install_spacy_model()

# --- 3. RESTE DU CODE (DB, CHAT, LOGO) ---
if nlp:
    st.image("https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png", width=150)
    st.title("NeuronAI")
    # ... la suite de ton code habituel
else:
    st.warning("Chargement du cerveau linguistique... rafraîchis la page dans un instant.")
