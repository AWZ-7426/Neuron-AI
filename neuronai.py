import streamlit as st
import sqlite3
import uuid
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# Injection de la balise Google (obligatoire pour la validation)
st.markdown(
    f'<head><meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" /></head>', 
    unsafe_allow_html=True
)

# --- 2. LOGO ET TITRE ---
def show_header():
    # On définit le chemin relatif : puisque neuronai.py est dans Neuron-AI/
    # le logo est dans images/
    logo_path = "images/neuron-ai.png"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            # Sécurité si le chemin change encore
            st.info("Recherche du logo...")
            if os.path.exists("neuron-ai.png"):
                st.image("neuron-ai.png", use_container_width=True)

    st.markdown("""
        <h1 style='text-align: center; color: black; margin-top: -20px;'>NeuronAI</h1>
        <p style='text-align: center; color: #8E8E93; font-size: 1.2rem;'>L'intelligence collective humaine.</p>
    """, unsafe_allow_html=True)

show_header()

# --- 3. BASE DE DONNÉES (VERSION ANTI-CRASH) ---
def init_db():
    # On utilise un nouveau nom de fichier pour éviter les erreurs de verrouillage précédentes
    conn = sqlite3.connect('neuron_v2.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS brain 
                 (prompt TEXT PRIMARY KEY, response TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 4. GESTION DE LA MÉMOIRE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting" not in st.session_state:
    st.session_state.waiting = False

def get_ai_response(user_input):
    text = user_input.lower().strip()
    
    # Réponses prioritaires (Mémoire flash)
    fast_responses = {
        "bonjour": "Bonjour ! Je suis NeuronAI. Je suis prêt à apprendre de vous.",
        "salut": "Salut ! Qu'allez-vous m'enseigner aujourd'hui ?",
        "hello": "Hello ! Posez-moi une question ou apprenez-moi une info.",
        "qui es-tu": "Je suis NeuronAI, une intelligence collective qui grandit grâce à vos messages.",
        "qui es-tu ?": "Je suis NeuronAI, une intelligence collective qui grandit grâce à vos messages."
    }
    
    if text in fast_responses:
        return fast_responses[text], False

    # Recherche en base de données
    try:
        conn = sqlite3.connect('neuron_v2.db')
        res = conn.execute("SELECT response FROM brain WHERE prompt = ?", (text,)).fetchone()
        conn.close()
        if res:
            return res[0], False
    except:
        pass

    # Si on ne sait pas
    return f"Je ne connais pas encore la réponse pour '{user_input}'. Pourriez-vous m'expliquer ce que c'est ?", True

# --- 5. INTERFACE DE CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    # Affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Logique de réponse
    with st.chat_message("assistant"):
        if st.session_state.waiting:
            # On enregistre ce que l'utilisateur vient de dire comme réponse au prompt précédent
            conn = sqlite3.connect('neuron_v2.db')
            conn.execute("INSERT OR REPLACE INTO brain (prompt, response) VALUES (?, ?)", 
                         (st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            
            ans = f"Merci beaucoup ! J'ai bien mémorisé. Pour '{st.session_state.temp_q}', la réponse est : {prompt}"
            st.session_state.waiting = False
        else:
            ans, is_missing = get_ai_response(prompt)
            if is_missing:
                st.session_state.waiting = True
                st.session_state.temp_q = prompt.lower().strip()
        
        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
