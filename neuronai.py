import streamlit as st
import sqlite3
import os
import re

# 1. CONFIGURATION (Indispensable en haut)
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# 2. VALIDATION GOOGLE (Correction pour Search Console)
# On injecte la balise de manière à ce qu'elle soit détectable immédiatement
st.markdown(f"""
    <script>
        var meta = document.createElement('meta');
        meta.name = "google-site-verification";
        meta.content = "RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY";
        document.getElementsByTagName('head')[0].appendChild(meta);
    </script>
    <meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />
""", unsafe_allow_html=True)

# 3. INTERFACE VISUELLE
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(LOGO_URL, width=180)
st.markdown("<h1 style='color: black; margin-top: -20px;'>NeuronAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8E8E93;'>L'intelligence collective humaine.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 4. LOGIQUE LINGUISTIQUE (Ajout des déterminants)
def formater_reponse(texte):
    # Liste simplifiée de mots qui ont souvent besoin d'un déterminant
    mots_a_completer = {
        "pomme": "Une pomme", "soleil": "Le soleil", "chat": "Un chat", 
        "chien": "Un chien", "maison": "La maison", "ordinateur": "L'ordinateur"
    }
    
    texte_clean = texte.strip().lower()
    
    # Si la réponse est un seul mot et qu'on le connaît, on l'enrichit
    if texte_clean in mots_a_completer:
        return mots_a_completer[texte_clean]
    
    # Règle automatique simple : si ça commence par une consonne et pas de déterminant
    determinants = ['le', 'la', 'les', 'un', 'une', 'des', 'mon', 'ton', 'son', 'ce', 'cette', 'je', 'tu', 'il', 'elle']
    mots = texte.split()
    
    if mots and mots[0].lower() not in determinants:
        # On peut décider d'ajouter "C'est" ou un article générique
        # Ici on ajoute une majuscule pour faire propre
        return texte[0].upper() + texte[1:]
        
    return texte

# 5. BASE DE DONNÉES
def init_db():
    conn = sqlite3.connect('brain_v4.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
    conn.execute("INSERT OR IGNORE INTO memory VALUES ('bonjour', 'Bonjour ! Ravi de vous voir.')")
    conn.commit()
    conn.close()

init_db()

# 6. SYSTÈME DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        text = prompt.lower().strip()
        
        if st.session_state.temp_q:
            # On formate la réponse de l'utilisateur avant de l'enregistrer
            reponse_formatee = formater_reponse(prompt)
            conn = sqlite3.connect('brain_v4.db')
            conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, reponse_formatee))
            conn.commit()
            conn.close()
            ans = f"Merci ! J'ai appris que pour '{st.session_state.temp_q}', la réponse est : {reponse_formatee}"
            st.session_state.temp_q = None
        else:
            conn = sqlite3.connect('brain_v4.db')
            res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (text,)).fetchone()
            conn.close()
            
            if res:
                ans = res[0]
            else:
                ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ?"
                st.session_state.temp_q = text

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
