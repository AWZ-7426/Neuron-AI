import streamlit as st
import sqlite3
import uuid
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# Balise Google Verification
st.markdown('<head><meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" /></head>', unsafe_allow_html=True)

# --- 2. AFFICHAGE DU LOGO (CORRECTIF CHEMIN) ---
def show_header():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # On définit le chemin exact par rapport à l'emplacement du script
        # On teste plusieurs variantes pour être sûr de toucher la cible
        current_dir = os.path.dirname(__file__)
        img_path = os.path.join(current_dir, "images", "neuron-ai.png")
        
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        elif os.path.exists("images/neuron-ai.png"):
            st.image("images/neuron-ai.png", use_container_width=True)
        elif os.path.exists("neuron-ai.png"):
            st.image("neuron-ai.png", use_container_width=True)
        else:
            st.error("⚠️ Fichier introuvable. Vérifie que le nom est bien 'neuron-ai.png' (tout en minuscules) dans le dossier 'images'.")
            
    st.markdown("<h1 style='text-align: center;'>NeuronAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>L'intelligence collective qui apprend de vous.</p>", unsafe_allow_html=True)
# --- 3. BASE DE DONNÉES (CORRECTIF ERREUR SQL) ---
def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    # On crée la table
    conn.execute('''CREATE TABLE IF NOT EXISTS brain 
                 (id INTEGER PRIMARY KEY, prompt TEXT UNIQUE, response TEXT, votes INTEGER)''')
    
    # On insère les bases UNIQUEMENT si elles n'existent pas (OR IGNORE évite l'erreur)
    conn.execute("INSERT OR IGNORE INTO brain (prompt, response, votes) VALUES ('bonjour', 'Bonjour ! Je suis NeuronAI. Comment puis-je vous aider ?', 1)")
    conn.execute("INSERT OR IGNORE INTO brain (prompt, response, votes) VALUES ('salut', 'Salut ! Prêt à m''apprendre de nouvelles choses ?', 1)")
    
    conn.commit()
    conn.close()

# On lance l'init proprement
try:
    init_db()
except Exception as e:
    st.error(f"Erreur de base de données : {e}")

# --- 4. SESSION & CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting" not in st.session_state:
    st.session_state.waiting = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Discutons..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        user_text = prompt.lower().strip()
        
        if st.session_state.waiting:
            ans = "Merci ! C'est enregistré."
            conn = sqlite3.connect('neuron_brain.db')
            conn.execute("INSERT OR IGNORE INTO brain (prompt, response, votes) VALUES (?, ?, 1)", (st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            st.session_state.waiting = False
        else:
            conn = sqlite3.connect('neuron_brain.db')
            res = conn.execute("SELECT response FROM brain WHERE prompt LIKE ? LIMIT 1", ('%'+user_text+'%',)).fetchone()
            conn.close()
            
            if res:
                ans = res[0]
            else:
                ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ?"
                st.session_state.waiting = True
                st.session_state.temp_q = user_text

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
