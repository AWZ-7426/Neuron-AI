import streamlit as st
import sqlite3
import os

# 1. Configuration de base
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# 2. Validation Google (Méthode simple)
st.markdown('<head><meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" /></head>', unsafe_allow_html=True)

# 3. Logo et Titre
# On utilise le logo directement via son URL GitHub pour éviter les problèmes de dossiers
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(LOGO_URL, use_container_width=True)
    st.markdown("<h1 style='text-align: center; margin-top: -30px;'>NeuronAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>L'intelligence collective humaine.</p>", unsafe_allow_html=True)

# 4. Base de données simplifiée
def init_db():
    conn = sqlite3.connect('brain_v3.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
    # On pré-remplit le cerveau
    conn.execute("INSERT OR IGNORE INTO memory VALUES ('bonjour', 'Bonjour ! Ravi de vous voir.')")
    conn.execute("INSERT OR IGNORE INTO memory VALUES ('salut', 'Salut ! On apprend quoi aujourd\'hui ?')")
    conn.commit()
    conn.close()

init_db()

# 5. Session et Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Dites quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        text = prompt.lower().strip()
        
        # Si on attendait une explication
        if st.session_state.temp_q:
            conn = sqlite3.connect('brain_v3.db')
            conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            ans = f"Merci ! J'ai appris que pour '{st.session_state.temp_q}', la réponse est : {prompt}"
            st.session_state.temp_q = None
        else:
            # Recherche
            conn = sqlite3.connect('brain_v3.db')
            res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (text,)).fetchone()
            conn.close()
            
            if res:
                ans = res[0]
            else:
                ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ce que c'est ?"
                st.session_state.temp_q = text

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
