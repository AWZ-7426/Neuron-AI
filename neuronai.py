import streamlit as st
import sqlite3
import uuid
import random
import base64
import os

# --- 1. CONFIGURATION ET BALISE GOOGLE ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# Injection de la balise Google (Correction : Utilisation de st.html pour la persistance)
st.components.v1.html(
    """
    <head>
        <meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />
    </head>
    <script>
        var meta = document.createElement('meta');
        meta.name = "google-site-verification";
        meta.content = "RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY";
        parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>
    """,
    height=0,
)

# --- 2. FONCTION POUR LE LOGO (BASE64) ---
def get_base64_logo(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 3. STYLE CSS & EN-TÊTE ---
def apply_ui():
    logo_b64 = get_base64_logo("neuron-ai.png")
    logo_img = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo">' if logo_b64 else ""
    
    st.markdown(f"""
        <style>
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .header-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 20px 0 40px 0;
            animation: fadeIn 1.2s ease-out;
        }}

        .header-logo {{ 
            max-width: 160px; 
            height: auto; 
            margin-bottom: 20px; 
            filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.1));
        }}

        .header-title {{ 
            font-size: 3rem; 
            font-weight: 800; 
            color: #000000 !important;
            margin: 0; 
            letter-spacing: -1.5px; 
        }}

        .header-subtitle {{ 
            color: #8E8E93 !important; 
            font-size: 1.1rem; 
            font-weight: 400;
            margin-top: 5px; 
        }}
        </style>
        
        <div class="header-container">
            {logo_img}
            <div class="header-title">NeuronAI</div>
            <div class="header-subtitle">L'intelligence collective humaine.</div>
        </div>
    """, unsafe_allow_html=True)
    
# --- 4. BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS brain (id INTEGER PRIMARY KEY, user_id TEXT, prompt TEXT, response TEXT, votes INTEGER)')
    conn.commit()
    conn.close()

def search_memory(text):
    conn = sqlite3.connect('neuron_brain.db')
    res = conn.execute("SELECT response FROM brain WHERE prompt LIKE ? AND votes >= 0 ORDER BY votes DESC LIMIT 1", ('%'+text+'%',)).fetchone()
    conn.close()
    return res[0] if res else None

init_db()

# --- 5. SESSION ET HISTORIQUE ---
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting" not in st.session_state:
    st.session_state.waiting = False

with st.sidebar:
    st.title("👤 Ma Session")
    new_id = st.text_input("ID de session :", value=st.session_state.user_id)
    if st.button("Restaurer"):
        st.session_state.user_id = new_id
        st.rerun()
    st.caption("Conservez cet ID pour retrouver vos discussions.")

# --- 6. CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Posez une question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        txt = prompt.lower().strip()
        
        if st.session_state.waiting:
            ans = "Merci ! J'ai bien mémorisé cette réponse dans mon cerveau collectif."
            conn = sqlite3.connect('neuron_brain.db')
            conn.execute("INSERT INTO brain (user_id, prompt, response, votes) VALUES (?, ?, ?, 1)", (st.session_state.user_id, st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            st.session_state.waiting = False
        elif any(w in txt for w in ["salut", "bonjour", "hello"]):
            ans = "Bonjour ! Je suis NeuronAI. Comment puis-je t'aider aujourd'hui ?"
        else:
            knowledge = search_memory(txt)
            if knowledge:
                ans = f"Je sais ça ! {knowledge}."
            else:
                ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ce que c'est ?"
                st.session_state.waiting = True
                st.session_state.temp_q = txt

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
