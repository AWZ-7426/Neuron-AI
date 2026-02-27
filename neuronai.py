import streamlit as st
import sqlite3
import os

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# 2. VALIDATION GOOGLE (CRUCIAL)
# On utilise st.html pour injecter la balise directement sans perturber le reste
st.html(f'<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />')

# 3. INTERFACE VISUELLE
# Utilisation de l'URL brute GitHub pour le logo (méthode la plus stable)
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(LOGO_URL, width=200)
st.markdown("<h1 style='margin-top: -20px;'>NeuronAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: gray;'>L'intelligence collective humaine.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 4. BASE DE DONNÉES (MODE SÉCURISÉ)
def init_db():
    try:
        # On utilise un nouveau nom pour repartir de zéro
        conn = sqlite3.connect('final_brain.db', check_same_thread=False)
        conn.execute('CREATE TABLE IF NOT EXISTS brain (prompt TEXT PRIMARY KEY, response TEXT)')
        conn.execute("INSERT OR IGNORE INTO brain VALUES ('bonjour', 'Bonjour ! Je suis NeuronAI.')")
        conn.execute("INSERT OR IGNORE INTO brain VALUES ('salut', 'Salut ! Prêt à apprendre ?')")
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Erreur DB : {e}")

init_db()

# 5. SYSTÈME DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "learning_mode" not in st.session_state:
    st.session_state.learning_mode = None

# Affichage de l'historique
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# Entrée utilisateur
if prompt := st.chat_input("Dites quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        text = prompt.lower().strip()
        
        if st.session_state.learning_mode:
            # Enregistrement de l'apprentissage
            conn = sqlite3.connect('final_brain.db')
            conn.execute("INSERT OR REPLACE INTO brain VALUES (?, ?)", (st.session_state.learning_mode, prompt))
            conn.commit()
            conn.close()
            ans = f"Merci ! J'ai appris que pour '{st.session_state.learning_mode}', la réponse est : {prompt}"
            st.session_state.learning_mode = None
        else:
            # Recherche de réponse
            conn = sqlite3.connect('final_brain.db')
            res = conn.execute("SELECT response FROM brain WHERE prompt = ?", (text,)).fetchone()
            conn.close()
            
            if res:
                ans = res[0]
            else:
                ans = f"Je ne connais pas '{prompt}'. Peux-tu m'expliquer ce que c'est ?"
                st.session_state.learning_mode = text

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
