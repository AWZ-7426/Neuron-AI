import streamlit as st
import sqlite3
import uuid
import random
import base64
import os

# --- 1. CONFIGURATION ET BALISE GOOGLE ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# Injection de la balise Meta Google via JavaScript
st.components.v1.html(
    """
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
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 3. STYLE CSS (APPLE STYLE - BLANC & NOIR) ---
def apply_custom_style():
    logo_b64 = get_base64_logo("neuron-ai.png")
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo">' if logo_b64 else ""

    st.markdown(f"""
        <style>
        .stApp {{ background-color: #FFFFFF; }}
        * {{ color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }}
        
        /* En-tête avec Logo */
        .header-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 20px 0;
        }}
        .header-logo {{ max-width: 150px; height: auto; margin-bottom: 10px; }}
        .header-title {{ font-size: 2.2rem; font-weight: 800; margin: 0; letter-spacing: -1px; }}
        
        /* Bulles de Chat */
        .stChatMessage {{ 
            background-color: #F2F2F7 !important; 
            border-radius: 20px !important;
            border: none !important;
            padding: 15px !important;
            margin-bottom: 10px !important;
        }}
        
        /* Input */
        .stChatInput textarea {{
            background-color: #FFFFFF !important;
            border: 1px solid #DDD !important;
            border-radius: 25px !important;
        }}

        /* Sidebar */
        .css-1d391kg {{ background-color: #FAFAFA !important; }}
        .stButton button {{
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border-radius: 20px !important;
            border: none !important;
        }}
        </style>
        
        <div class="header-container">
            {logo_html}
            <p class="header-title">NeuronAI</p>
            <p style="color: #8E8E93 !important;">L'intelligence collective humaine.</p>
        </div>
    """, unsafe_allow_html=True)

apply_custom_style()

# --- 4. LOGIQUE DE LA BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS brain 
                 (id INTEGER PRIMARY KEY, user_id TEXT, prompt TEXT, response TEXT, votes INTEGER)''')
    conn.commit()
    conn.close()

def search_memory(text):
    conn = sqlite3.connect('neuron_brain.db')
    res = conn.execute("SELECT response FROM brain WHERE prompt LIKE ? AND votes >= 0 ORDER BY votes DESC LIMIT 1", 
                       ('%'+text+'%',)).fetchone()
    conn.close()
    return res[0] if res else None

def get_suggestions():
    conn = sqlite3.connect('neuron_brain.db')
    res = conn.execute("SELECT prompt FROM brain WHERE votes > 0 ORDER BY RANDOM() LIMIT 2").fetchall()
    conn.close()
    return [r[0] for r in res]

init_db()

# --- 5. GESTION DE LA SESSION ---
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_learning" not in st.session_state:
    st.session_state.waiting_for_learning = False

# Sidebar pour l'ID utilisateur
with st.sidebar:
    st.write("### 👤 Ma Session")
    user_input_id = st.text_input("ID de session :", value=st.session_state.user_id)
    if st.button("Restaurer l'historique"):
        st.session_state.user_id = user_input_id
        st.rerun()
    st.caption("Utilisez cet ID pour retrouver vos discussions sur d'autres appareils.")

# --- 6. INTERFACE DE CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Posez une question ou apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        txt = prompt.lower().strip()
        
        # Scénario Apprentissage (L'IA a posé une question avant)
        if st.session_state.waiting_for_learning:
            ans = random.choice([
                "C'est noté ! Merci de m'avoir aidé à comprendre.",
                "Génial, j'ai enregistré cette information dans mon cerveau.",
                "Merci ! Je saurai quoi répondre maintenant."
            ])
            conn = sqlite3.connect('neuron_brain.db')
            conn.execute("INSERT INTO brain (user_id, prompt, response, votes) VALUES (?, ?, ?, 1)", 
                         (st.session_state.user_id, st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            st.session_state.waiting_for_learning = False
        
        # Scénario Salutations
        elif any(w in txt for w in ["salut", "bonjour", "hello", "coucou"]):
            ans = "Bonjour ! Je suis NeuronAI. De quoi souhaites-tu discuter aujourd'hui ?"
        
        # Scénario Recherche / Proactivité
        else:
            knowledge = search_memory(txt)
            if knowledge:
                ans = f"Je pense savoir : {knowledge}. Est-ce que cela t'aide ?"
            else:
                sugg = get_suggestions()
                if sugg:
                    ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ? (Ou alors, on peut parler de : *{', '.join(sugg)}*)"
                else:
                    ans = "Je ne connais pas encore cela. Peux-tu m'expliquer ce que c'est pour que je l'apprenne ?"
                st.session_state.waiting_for_learning = True
                st.session_state.temp_q = txt

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
