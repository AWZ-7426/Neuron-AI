import streamlit as st
import sqlite3
import uuid
import base64
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# --- 2. LOGO & DESIGN (LE CORRECTIF) ---
def apply_ui():
    # Encodage du logo pour qu'il soit visible partout
    logo_path = "neuron-ai.png" 
    logo_html = ""
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-width: 180px; margin-bottom: 10px; border-radius: 15px;">'

    # LE SECRET : On met tout dans un SEUL bloc markdown avec unsafe_allow_html=True
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #FFFFFF !important; }}
        .header-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 20px 0;
            width: 100%;
        }}
        .header-title {{
            font-size: 3.2rem !important;
            font-weight: 800 !important;
            color: #000000 !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.1 !important;
            letter-spacing: -1.5px !important;
        }}
        .header-subtitle {{
            color: #8E8E93 !important;
            font-size: 1.2rem !important;
            margin-top: 10px !important;
            font-weight: 400 !important;
        }}
        /* Style des bulles de chat pour le look Apple */
        .stChatMessage {{ 
            background-color: #F2F2F7 !important; 
            border-radius: 20px !important;
            border: none !important;
        }}
        </style>
        
        <div class="header-container">
            {logo_html}
            <h1 class="header-title">NeuronAI</h1>
            <p class="header-subtitle">L'intelligence collective humaine.</p>
        </div>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. BASE DE DONNÉES ---
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
if "waiting" not in st.session_state:
    st.session_state.waiting = False

# Sidebar propre
with st.sidebar:
    st.markdown("### 👤 Session")
    st.code(st.session_state.user_id)
    st.caption("ID unique pour retrouver votre historique.")

# --- 5. LOGIQUE DU CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # Ici on simule la réponse pour tester l'affichage
        ans = f"Je vous entends ! Je suis en train d'analyser '{prompt}'."
        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
