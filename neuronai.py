import streamlit as st
import sqlite3
import spacy
import os

# --- 1. VALIDATION GOOGLE (LA SEULE MÉTHODE QUI MARCHE SUR STREAMLIT) ---
# On utilise st.write avec unsafe_allow_html pour injecter la balise au TOUT DÉBUT
st.set_page_config(page_title="NeuronAI", page_icon="🧠")
st.markdown('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />', unsafe_allow_html=True)

# --- 2. CHARGEMENT DE SPACY ---
@st.cache_resource
def load_nlp():
    return spacy.load("fr_core_news_sm")

nlp = load_nlp()

# --- 3. FONCTIONS D'INTELLIGENCE (VULGARITÉ & GRAMMAIRE) ---
VULGARITES = ["mot1", "mot2"] # Remplace par ta liste

def filtrer_et_corriger(texte):
    doc = nlp(texte.lower().strip())
    
    # Vérification vulgarité
    for token in doc:
        if token.text in VULGARITES or token.lemma_ in VULGARITES:
            return None, "Désolé, je n'apprends pas ce genre de langage."

    # Ajout de déterminant si c'est un nom seul
    if len(doc) == 1 and doc[0].pos_ == "NOUN":
        genre = doc[0].morph.get("Gender")
        if "Fem" in genre:
            return f"La {doc[0].text}", "OK"
        else:
            return f"Le {doc[0].text}", "OK"
    
    # Sinon, on met juste une majuscule
    return texte[0].upper() + texte[1:], "OK"

# --- 4. INTERFACE ---
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"
st.image(LOGO_URL, width=150)
st.title("NeuronAI")

# --- 5. BASE DE DONNÉES ---
conn = sqlite3.connect('brain_v5.db', check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
conn.commit()

# --- 6. CHAT ---
if "temp_q" not in st.session_state: st.session_state.temp_q = None

if prompt := st.chat_input("Dites quelque chose..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        if st.session_state.temp_q:
            reponse_corrigee, statut = filtrer_et_corriger(prompt)
            if statut == "OK":
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, reponse_corrigee))
                conn.commit()
                st.write(f"Merci ! J'ai appris : {reponse_corrigee}")
                st.session_state.temp_q = None
            else:
                st.error(statut)
        else:
            res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (prompt.lower(),)).fetchone()
            if res:
                st.write(res[0])
            else:
                st.write(f"Je ne connais pas '{prompt}'. C'est quoi ?")
                st.session_state.temp_q = prompt.lower()
