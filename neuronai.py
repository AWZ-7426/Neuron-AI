import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import os

# 1. CONFIGURATION (Doit être la toute première commande)
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# 2. INJECTION CRUCIALE DANS LE <HEAD> 
# Cette fonction force l'insertion AVANT le body pour Google
components.html(
    """
    <script>
        var meta = document.createElement('meta');
        meta.name = "google-site-verification";
        meta.content = "RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY";
        parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>
    """,
    height=0,
)

# 3. FILTRE DE VULGARITÉ ET GRAMMAIRE
# Ajoutez vos mots interdits ici
MOTS_INTERDITS = ["connard","connasse","abruti","gros con","con","salope","va te faire foutre","casse-toi","bordel","putain","connard","taré","degenere","chieur","connard"]


def est_propre(texte):
    for mot in MOTS_INTERDITS:
        if mot in texte.lower():
            return False
    return True

def ajouter_determinant(texte):
    texte = texte.strip()
    if not texte: return texte
    
    # Liste de base des déterminants et pronoms
    protections = ['le', 'la', 'les', 'un', 'une', 'des', 'ce', 'cette', 'je', 'tu', 'il', 'elle', "l'"]
    mots = texte.split()
    
    # Si le texte est un mot seul sans déterminant, on tente une correction simple
    if len(mots) == 1 and mots[0].lower() not in protections:
        # Par défaut, on met une majuscule. 
        # Pour une IA plus complexe, il faudrait une bibliothèque comme Spacy
        return texte.capitalize()
    
    return texte[0].upper() + texte[1:] if texte else texte

# 4. INTERFACE VISUELLE
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(LOGO_URL, width=180)
st.header("NeuronAI")
st.markdown("</div>", unsafe_allow_html=True)

# 5. BASE DE DONNÉES
def init_db():
    conn = sqlite3.connect('brain_v4.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
    conn.commit()
    conn.close()

init_db()

# 6. LOGIQUE DU CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    if not est_propre(prompt):
        st.error("Ce message contient des mots non autorisés.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            text = prompt.lower().strip()
            
            if st.session_state.temp_q:
                # Application de la grammaire avant enregistrement
                reponse_propre = ajouter_determinant(prompt)
                conn = sqlite3.connect('brain_v4.db')
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, reponse_propre))
                conn.commit()
                conn.close()
                ans = f"Merci ! J'ai bien retenu : {reponse_propre}"
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
