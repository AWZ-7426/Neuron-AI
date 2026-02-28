import streamlit as st
import sqlite3
import spacy
import os
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ET VALIDATION (GOOGLE & BING) ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# Injection combinée pour Google et Bing dans le head du site
# Cette méthode est la plus robuste pour que les robots trouvent les IDs sur la page d'accueil
components.html(
    """
    <script>
        var head = parent.document.getElementsByTagName('head')[0];
        
        // Balise Google
        var googleMeta = document.createElement('meta');
        googleMeta.name = "google-site-verification";
        googleMeta.content = "RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY";
        head.appendChild(googleMeta);
        
        // Balise Bing
        var bingMeta = document.createElement('meta');
        bingMeta.name = "msvalidate.01";
        bingMeta.content = "BA1A2EF4B67CEB856BA0329B7C545711";
        head.appendChild(bingMeta);
    </script>
    """,
    height=0,
)

# --- 2. CHARGEMENT DE SPACY (MODÈLE FRANÇAIS) ---
@st.cache_resource
def load_nlp():
    try:
        return spacy.load("fr_core_news_sm")
    except:
        # Secours si le modèle n'est pas lié correctement
        return spacy.blank("fr")

nlp = load_nlp()

# --- 3. LOGIQUE LINGUISTIQUE ET MODÉRATION ---
# Liste de mots vulgaires (à compléter selon tes besoins)
VULGARITES = ["insulte1", "insulte2", "grosmot"] 

def traiter_texte(texte):
    doc = nlp(texte.lower().strip())
    
    # Vérification vulgarité (vérifie le mot exact et sa racine/lemme)
    for token in doc:
        if token.text in VULGARITES or token.lemma_ in VULGARITES:
            return None, "🚫 Désolé, je ne peux pas enregistrer de propos vulgaires."

    # Ajout intelligent de déterminant (Grammaire)
    # Si c'est un nom seul (ex: "pomme"), on détecte le genre avec spaCy
    if len(doc) == 1 and doc[0].pos_ == "NOUN":
        genre = doc[0].morph.get("Gender")
        if "Fem" in genre:
            return f"La {doc[0].text}", "OK"
        else:
            return f"Le {doc[0].text}", "OK"
    
    # Sinon, on retourne le texte avec une majuscule
    return texte[0].upper() + texte[1:], "OK"

# --- 4. INTERFACE VISUELLE ---
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"
st.image(LOGO_URL, width=150)
st.title("NeuronAI")
st.write("---")

# --- 5. BASE DE DONNÉES ---
conn = sqlite3.connect('brain_v5.db', check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
conn.commit()

# --- 6. SYSTÈME DE CHAT ---
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        # Phase d'apprentissage
        if st.session_state.temp_q:
            reponse_propre, statut = traiter_texte(prompt)
            if statut == "OK":
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, reponse_propre))
                conn.commit()
                st.success(f"Merci ! J'ai bien mémorisé : {reponse_propre}")
                st.session_state.temp_q = None
            else:
                st.error(statut)
        
        # Phase de réponse
        else:
            res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (prompt.lower().strip(),)).fetchone()
            if res:
                st.write(res[0])
            else:
                st.write(f"Je ne connais pas encore la réponse pour '{prompt}'. Qu'est-ce que c'est ?")
                st.session_state.temp_q = prompt.lower().strip()
