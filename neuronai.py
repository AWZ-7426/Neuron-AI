import streamlit as st
import sqlite3
import os

# 1. CONFIGURATION
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# 2. VALIDATION GOOGLE
st.markdown('<head><meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" /></head>', unsafe_allow_html=True)

# 3. INTERFACE VISUELLE
# On garde le chemin qui a fonctionné pour ton logo
logo_path = "images/neuron-ai.png"

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
if os.path.exists(logo_path):
    st.image(logo_path, width=200)
st.markdown("<h1 style='margin-top: -20px;'>NeuronAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: gray;'>L'intelligence collective humaine.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 4. BASE DE DONNÉES (VERSION SÉCURISÉE V4)
def init_db():
    try:
        # On change le nom pour 'brain_v4.db' pour repartir sur un fichier propre
        conn = sqlite3.connect('brain_v4.db', check_same_thread=False)
        conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
        # On utilise INSERT OR IGNORE pour ne jamais planter si les données existent déjà
        conn.execute("INSERT OR IGNORE INTO memory VALUES ('bonjour', 'Bonjour ! Ravi de vous voir.')")
        conn.execute("INSERT OR IGNORE INTO memory VALUES ('salut', 'Salut ! On apprend quoi aujourd''hui ?')")
        conn.commit()
        conn.close()
    except Exception as e:
        # Si la DB bloque, on affiche l'erreur mais on ne stoppe pas l'appli
        st.warning(f"Note : Mode lecture seule activé ({e})")

init_db()

# 5. CHAT
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
        
        try:
            if st.session_state.temp_q:
                conn = sqlite3.connect('brain_v4.db')
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, prompt))
                conn.commit()
                conn.close()
                ans = f"Merci ! J'ai appris que pour '{st.session_state.temp_q}', la réponse est : {prompt}"
                st.session_state.temp_q = None
            else:
                conn = sqlite3.connect('brain_v4.db')
                res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (text,)).fetchone()
                conn.close()
                
                if res:
                    ans = res[0]
                else:
                    ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ce que c'est ?"
                    st.session_state.temp_q = text
        except:
            ans = "Oups, ma mémoire rencontre un petit souci technique, mais je vous écoute !"

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
