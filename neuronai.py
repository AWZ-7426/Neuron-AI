import streamlit as st
import sqlite3
import os

# 1. CONFIGURATION (Indispensable en haut)
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# 2. VALIDATION GOOGLE (Invisible pour l'utilisateur, visible pour Google)
st.markdown(f'<head><meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" /></head>', unsafe_allow_html=True)

# 3. INTERFACE VISUELLE "APPLE STYLE"
# Utilisation de l'URL RAW de ton GitHub pour le logo
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(LOGO_URL, width=180)
st.markdown("<h1 style='color: black; margin-top: -20px; font-size: 3rem;'>NeuronAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8E8E93; font-size: 1.2rem;'>L'intelligence collective humaine.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 4. BASE DE DONNÉES (SÉCURISÉE)
def init_db():
    conn = sqlite3.connect('neuron_brain_final.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS brain (prompt TEXT PRIMARY KEY, response TEXT)')
    # Réponses de base
    conn.execute("INSERT OR IGNORE INTO brain VALUES ('bonjour', 'Bonjour ! Je suis NeuronAI, ravi de faire votre connaissance.')")
    conn.execute("INSERT OR IGNORE INTO brain VALUES ('salut', 'Salut ! Prêt à m\'apprendre quelque chose de nouveau ?')")
    conn.commit()
    conn.close()

init_db()

# 5. SYSTÈME DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

# Affichage des messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# Entrée utilisateur
if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        text = prompt.lower().strip()
        
        # Si on est en train d'apprendre
        if st.session_state.temp_q:
            conn = sqlite3.connect('neuron_brain_final.db')
            conn.execute("INSERT OR REPLACE INTO brain VALUES (?, ?)", (st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            ans = f"Merci ! J'ai bien mémorisé que pour '{st.session_state.temp_q}', la réponse est : {prompt}"
            st.session_state.temp_q = None
        else:
            # Recherche dans le cerveau
            conn = sqlite3.connect('neuron_brain_final.db')
            res = conn.execute("SELECT response FROM brain WHERE prompt = ?", (text,)).fetchone()
            conn.close()
            
            if res:
                ans = res[0]
            else:
                ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ce que c'est ?"
                st.session_state.temp_q = text

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
