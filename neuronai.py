import streamlit as st
import sqlite3
import os

# 1. CONFIGURATION
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# 2. VALIDATION GOOGLE (Méthode de secours)
# Si Google ne trouve pas le site, vérifie bien que l'URL dans la Search Console 
# est exactement : https://neuron-ai.streamlit.app/
st.markdown('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />', unsafe_allow_html=True)

# 3. INTERFACE VISUELLE
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(LOGO_URL, width=180)
st.markdown("<h1 style='color: black; margin-top: -20px;'>NeuronAI</h1>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 4. MODÉRATION ET GRAMMAIRE
VULGARITES = ["mot1", "mot2", "mot3"] # Ajoute ici les mots à bannir (en minuscules)

def est_propre(texte):
    # Vérifie si un mot interdit est dans la phrase
    for mot in VULGARITES:
        if mot in texte.lower():
            return False
    return True

def corriger_grammaire(texte):
    texte = texte.strip()
    if not texte: return texte
    
    # Liste de déterminants pour vérification
    determinants = ['le', 'la', 'les', 'un', 'une', 'des', 'mon', 'ton', 'son', 'ce', 'cette', 'je', 'tu', 'il', 'elle', "l'"]
    mots = texte.split()
    
    # Si le texte commence par un mot sans déterminant (ex: "Pomme")
    if mots and mots[0].lower() not in determinants:
        # On met au moins une majuscule pour faire propre
        return texte[0].upper() + texte[1:]
    return texte

# 5. BASE DE DONNÉES
def init_db():
    conn = sqlite3.connect('brain_v4.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
    conn.commit()
    conn.close()

init_db()

# 6. CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Discutons proprement..."):
    # Vérification vulgarité entrée utilisateur
    if not est_propre(prompt):
        st.error("Désolé, je ne peux pas traiter ce langage.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            text = prompt.lower().strip()
            
            if st.session_state.temp_q:
                # L'IA apprend une nouvelle réponse
                reponse_propre = corriger_grammaire(prompt)
                conn = sqlite3.connect('brain_v4.db')
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, reponse_propre))
                conn.commit()
                conn.close()
                ans = f"Merci ! J'ai mémorisé : {reponse_propre}"
                st.session_state.temp_q = None
            else:
                # Recherche
                conn = sqlite3.connect('brain_v4.db')
                res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (text,)).fetchone()
                conn.close()
                
                if res:
                    ans = res[0]
                else:
                    ans = f"Je ne connais pas '{prompt}'. Peux-tu m'expliquer ?"
                    st.session_state.temp_q = text

            st.write(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
