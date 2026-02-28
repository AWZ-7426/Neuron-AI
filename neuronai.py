import streamlit as st
import sqlite3
import spacy
import streamlit.components.v1 as components

# 1. CHARGEMENT DU MODÈLE LINGUISTIQUE
@st.cache_resource
def load_nlp():
    try:
        return spacy.load("fr_core_news_sm")
    except:
        # Commande de secours si le modèle n'est pas encore installé
        os.system("python -m spacy download fr_core_news_sm")
        return spacy.load("fr_core_news_sm")

nlp = load_nlp()

# 2. CONFIGURATION & VALIDATION GOOGLE (SECTION HEAD)
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# Injection forcée pour Google Search Console
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

# 3. LOGIQUE AVANCÉE AVEC SPACY
def enrichir_phrase(texte):
    doc = nlp(texte.strip())
    if len(doc) == 0: return texte
    
    premier_token = doc[0]
    
    # Si le premier mot est un NOM sans déterminant
    if premier_token.pos_ == "NOUN":
        # On récupère le genre (Masculin/Féminin)
        genre = premier_token.morph.get("Gender")
        if "Fem" in genre:
            return f"La {texte}"
        else:
            return f"Le {texte}"
            
    # Met une majuscule si nécessaire
    return texte[0].upper() + texte[1:]

def est_propre(texte):
    mots_interdits = ["vulgaire1", "vulgaire2"] # À compléter
    doc = nlp(texte.lower())
    for token in doc:
        if token.text in mots_interdits or token.lemma_ in mots_interdits:
            return False
    return True

# 4. INTERFACE & CHAT
st.image("https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png", width=150)
st.title("NeuronAI")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

# Affichage des messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    if not est_propre(prompt):
        st.warning("Langage non autorisé.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            if st.session_state.temp_q:
                # Utilisation de spaCy pour formater l'apprentissage
                reponse_finale = enrichir_phrase(prompt)
                
                conn = sqlite3.connect('brain_v4.db')
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, reponse_finale))
                conn.commit()
                conn.close()
                
                ans = f"Merci ! J'ai appris que : {reponse_finale}"
                st.session_state.temp_q = None
            else:
                conn = sqlite3.connect('brain_v4.db')
                res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (prompt.lower(),)).fetchone()
                conn.close()
                
                if res:
                    ans = res[0]
                else:
                    ans = f"Je ne connais pas '{prompt}'. C'est quoi ?"
                    st.session_state.temp_q = prompt.lower()

            st.write(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
