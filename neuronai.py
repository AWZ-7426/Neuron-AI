import streamlit as st
import sqlite3
import uuid
import os

# --- 1. CONFIGURATION ET GOOGLE VERIFICATION ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# Cette ligne injecte ta balise Google de façon invisible mais efficace
st.markdown(f'<head><meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" /></head>', unsafe_allow_html=True)

# --- 2. AFFICHAGE DU LOGO ET TITRE (MÉTHODE SIMPLE) ---
def show_header():
    # On centre avec des colonnes Streamlit (plus de texte brut !)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("neuron-ai.png"):
            st.image("neuron-ai.png", use_container_width=True)
        else:
            st.write("Logo introuvable : vérifie le nom du fichier sur GitHub")
            
    # Titre et sous-titre centrés proprement
    st.markdown("<h1 style='text-align: center; color: black;'>NeuronAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>L'intelligence collective qui apprend de vous.</p>", unsafe_allow_html=True)

show_header()

# --- 3. BASE DE DONNÉES ET MÉMOIRE ---
def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS brain 
                 (id INTEGER PRIMARY KEY, prompt TEXT, response TEXT, votes INTEGER)''')
    # On insère les bases si elles n'existent pas pour qu'il ne les oublie jamais
    cursor = conn.execute("SELECT count(*) FROM brain WHERE prompt = 'bonjour'")
    if cursor.fetchone()[0] == 0:
        conn.execute("INSERT INTO brain (prompt, response, votes) VALUES ('bonjour', 'Bonjour ! Je suis NeuronAI. Comment puis-je vous aider ?', 1)")
        conn.execute("INSERT INTO brain (prompt, response, votes) VALUES ('salut', 'Salut ! Prêt à m'apprendre de nouvelles choses ?', 1)")
    conn.commit()
    conn.close()

init_db()

# --- 4. GESTION DE LA SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_learning" not in st.session_state:
    st.session_state.waiting_for_learning = False

# --- 5. AFFICHAGE DU CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# --- 6. LOGIQUE DE RÉPONSE ---
if prompt := st.chat_input("Dites quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        user_text = prompt.lower().strip()
        
        if st.session_state.waiting_for_learning:
            ans = "Merci ! J'ai bien enregistré cela dans ma mémoire."
            conn = sqlite3.connect('neuron_brain.db')
            conn.execute("INSERT INTO brain (prompt, response, votes) VALUES (?, ?, 1)", (st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            st.session_state.waiting_for_learning = False
        else:
            # Recherche en base de données
            conn = sqlite3.connect('neuron_brain.db')
            res = conn.execute("SELECT response FROM brain WHERE prompt LIKE ? ORDER BY votes DESC LIMIT 1", ('%'+user_text+'%',)).fetchone()
            conn.close()
            
            if res:
                ans = res[0]
            else:
                ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ce que c'est ?"
                st.session_state.waiting_for_learning = True
                st.session_state.temp_q = user_text

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
