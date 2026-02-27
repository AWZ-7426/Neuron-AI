import streamlit as st
import sqlite3
import uuid
import base64
import os

# 1. Configuration de la page
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# 2. Injection Google (Méthode invisible)
st.components.v1.html(f'<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />', height=0)

# 3. Affichage du Logo et Titre (SANS HTML COMPLEXE)
def show_header():
    # Centrage via colonnes Streamlit (plus robuste)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("neuron-ai.png"):
            st.image("neuron-ai.png", use_container_width=True)
        st.markdown("<h1 style='text-align: center;'>NeuronAI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>L'intelligence collective humaine.</p>", unsafe_allow_html=True)

show_header()

# 4. Base de données
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

# 5. Session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# 6. Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Dites quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # Logique de recherche simple
        conn = sqlite3.connect('neuron_brain.db')
        res = conn.execute("SELECT response FROM brain WHERE prompt LIKE ? LIMIT 1", ('%'+prompt.lower()+'%',)).fetchone()
        conn.close()
        
        ans = res[0] if res else f"Je ne connais pas '{prompt}'. Peux-tu m'expliquer ?"
        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
