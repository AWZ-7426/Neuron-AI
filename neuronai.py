import streamlit as st
import sqlite3
import uuid
import base64
import os

# --- 1. CONFIGURATION & VALIDATION GOOGLE ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# Cette partie injecte ta balise meta directement dans le HEAD invisible du site
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

# --- 2. GESTION DU LOGO ---
def get_base64_logo(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 3. INTERFACE VISUELLE (FIX HTML) ---
def apply_ui():
    logo_b64 = get_base64_logo("neuron-ai.png")
    logo_img = f'<img src="data:images/png;base64,{logo_b64}" class="header-logo">' if logo_b64 else ""
    
    # Utilisation de st.markdown avec unsafe_allow_html=True pour tout le bloc
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #FFFFFF !important; }}
        
        .header-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 20px 0 40px 0;
        }}
        
        .header-logo {{ 
            max-width: 200px; 
            height: auto; 
            margin-bottom: 20px;
            border-radius: 20px;
        }}

        .header-title {{ 
            font-size: 3.5rem !important; 
            font-weight: 800 !important; 
            color: #000000 !important;
            margin: 0 !important; 
            letter-spacing: -2px !important;
            line-height: 1 !important;
        }}

        .header-subtitle {{ 
            color: #8E8E93 !important; 
            font-size: 1.2rem !important; 
            margin-top: 10px !important;
        }}
        
        /* Style Apple pour les messages */
        .stChatMessage {{ 
            background-color: #F2F2F7 !important; 
            border-radius: 20px !important;
            border: none !important;
            color: #000 !important;
        }}
        </style>
        
        <div class="header-container">
            {logo_img}
            <h1 class="header-title">NeuronAI</h1>
            <p class="header-subtitle">L'intelligence collective humaine.</p>
        </div>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. BASE DE DONNÉES ---
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

# --- 5. SESSION ---
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
    st.caption("ID unique pour votre historique.")

# --- 6. CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        txt = prompt.lower().strip()
        
        if st.session_state.waiting:
            ans = "Merci ! J'ai bien mémorisé cette réponse."
            conn = sqlite3.connect('neuron_brain.db')
            conn.execute("INSERT INTO brain (user_id, prompt, response, votes) VALUES (?, ?, ?, 1)", 
                         (st.session_state.user_id, st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            st.session_state.waiting = False
        else:
            # Recherche en base
            conn = sqlite3.connect('neuron_brain.db')
            res = conn.execute("SELECT response FROM brain WHERE prompt LIKE ? ORDER BY votes DESC LIMIT 1", ('%'+txt+'%',)).fetchone()
            conn.close()
            
            if res:
                ans = f"Je sais ça ! {res[0]}"
            else:
                ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ?"
                st.session_state.waiting = True
                st.session_state.temp_q = txt

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
