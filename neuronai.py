import streamlit as st
import sqlite3
import uuid
import base64
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# Balise Google
st.components.v1.html(
    """
    <script>
    var meta = document.createElement('meta');
    meta.name = "google-site-verification";
    meta.content = "RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY";
    parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>
    """, height=0
)

# --- 2. LOGO & DESIGN ---
def apply_ui():
    # On vérifie le nom du fichier image (doit être identique sur GitHub)
    logo_path = "neuron-ai.png" 
    logo_html = ""
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-width: 150px; margin-bottom: 20px; border-radius: 10px;">'

    st.markdown(f"""
        <style>
        .stApp {{ background-color: #FFFFFF; color: #000000; }}
        .header-container {{
            display: flex; flex-direction: column; align-items: center; 
            text-align: center; padding: 30px 0;
        }}
        .header-title {{ font-size: 2.5rem; font-weight: 800; color: #000 !important; margin: 0; }}
        .header-subtitle {{ color: #8E8E93 !important; font-size: 1rem; }}
        </style>
        <div class="header-container">
            {logo_html}
            <div class="header-title">NeuronAI</div>
            <div class="header-subtitle">L'intelligence collective humaine.</div>
        </div>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. BASE DE DONNÉES (Version Robuste) ---
# On utilise pysqlite3 pour Streamlit Cloud
try:
    from pysqlite3 import dbapi2 as sqlite3
except ImportError:
    import sqlite3

def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS brain (id INTEGER PRIMARY KEY, user_id TEXT, prompt TEXT, response TEXT, votes INTEGER)')
    conn.commit()
    conn.close()

init_db()

# --- 4. SESSION ---
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. CHAT ---
# Affichage des messages existants
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# Entrée utilisateur
if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Réponse simple pour tester si ça s'affiche
    with st.chat_message("assistant"):
        response = "Je vous reçois cinq sur cinq ! Mon système est opérationnel."
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
