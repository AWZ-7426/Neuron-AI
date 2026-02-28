import streamlit as st
import sqlite3

# --- 1. CONFIGURATION & VALIDATION (PRIORITÉ ABSOLUE) ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# Ces lignes sont injectées directement pour Google et Bing
st.markdown('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />', unsafe_allow_html=True)
st.markdown('<meta name="msvalidate.01" content="BA1A2EF4B67CEB856BA0329B7C545711" />', unsafe_allow_html=True)

# --- 2. LOGIQUE LINGUISTIQUE LÉGÈRE (SANS SPACY) ---
def corriger_texte(texte):
    # Liste simple de vulgarités à filtrer
    VULGARITES =  ["connard","connasse","abruti","gros con","con","salope","va te faire foutre","casse-toi","bordel","putain","connard","taré","degenere","chieur","connard"] 
    if any(m in texte.lower() for m in VULGARITES):
        return None, "🚫 Propos non autorisés."
    
    # Correction simple des déterminants
    mots = texte.strip().split()
    if len(mots) == 1:
        mot = mots[0].lower()
        # Liste manuelle rapide pour tester
        feminin = ["pomme", "maison", "voiture", "idée"]
        masculin = ["soleil", "chat", "chien", "ordinateur"]
        
        if mot in feminin: return f"La {mot}", "OK"
        if mot in masculin: return f"Le {mot}", "OK"
    
    return texte[0].upper() + texte[1:] if texte else texte, "OK"

# --- 3. INTERFACE ---
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"
st.image(LOGO_URL, width=150)
st.title("NeuronAI")

# --- 4. BASE DE DONNÉES ---
conn = sqlite3.connect('brain_v6.db', check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
conn.commit()

# --- 5. CHAT ---
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

if prompt := st.chat_input("Dites quelque chose..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        if st.session_state.temp_q:
            reponse, statut = corriger_texte(prompt)
            if statut == "OK":
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, reponse))
                conn.commit()
                st.write(f"Merci ! J'ai appris : {reponse}")
                st.session_state.temp_q = None
            else:
                st.error(statut)
        else:
            res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (prompt.lower().strip(),)).fetchone()
            if res:
                st.write(res[0])
            else:
                st.write(f"Je ne connais pas '{prompt}'. C'est quoi ?")
                st.session_state.temp_q = prompt.lower().strip()
