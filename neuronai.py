import streamlit as st
import sqlite3
import uuid
import base64
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# Balise Google (Injection propre)
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

# --- 2. LOGO & DESIGN (CORRECTIF HTML) ---
def apply_ui():
    # Encodage du logo en Base64 pour un affichage garanti
    logo_path = "neuron-ai.png" 
    logo_html = ""
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-width: 180px; margin-bottom: 10px;">'

    # LE FIX : On utilise une seule f-string pour tout le bloc HTML/CSS
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
            font-size: 3rem !important;
            font-weight: 800 !important;
            color: #000000 !important;
            margin: 0 !important;
            line-height: 1 !important;
        }}
        .header-subtitle {{
            color: #8E8E93 !important;
            font-size: 1.1rem !important;
            margin-top: 10px !important;
        }}
        /* Style des bulles de chat */
        .stChatMessage {{ 
            background-color: #F2F2F7 !important; 
            border-radius: 20px !important;
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

# Sidebar
with st.sidebar:
    st.title("👤 Session")
    st.code(st.session_state.user_id)
    st.caption("ID unique pour retrouver votre historique.")

# --- 5. CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        txt = prompt.lower().strip()
        
        # Logique simplifiée pour tester le visuel
        if st.session_state.waiting:
            ans = "Merci ! J'ai bien mémorisé cette réponse."
            st.session_state.waiting = False
        else:
            ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ?"
            st.session_state.waiting = True
            
        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
