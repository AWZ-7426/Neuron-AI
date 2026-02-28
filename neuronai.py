import streamlit as st
import sqlite3
import spacy

# --- 1. CONFIGURATION & VALIDATION (PRIORITÉ GOOGLE/BING) ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# Ces lignes sont lues immédiatement par les robots Google et Bing
st.markdown('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />', unsafe_allow_html=True)
st.markdown('<meta name="msvalidate.01" content="BA1A2EF4B67CEB856BA0329B7C545711" />', unsafe_allow_html=True)

# --- 2. CHARGEMENT DU MODÈLE ---
@st.cache_resource
def load_nlp():
    # Puisque le modèle est dans requirements.txt, il est déjà là !
    return spacy.load("fr_core_news_sm")

nlp = load_nlp()

# --- 3. INTERFACE ---
LOGO_URL = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"
st.image(LOGO_URL, width=150)
st.title("NeuronAI")
st.write("L'intelligence collective humaine est prête.")

# --- 4. BASE DE DONNÉES ---
conn = sqlite3.connect('brain_v5.db', check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
conn.commit()

# --- 5. LOGIQUE DU CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Posez-moi une question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Réponse simple pour tester si ça marche
    with st.chat_message("assistant"):
        st.write("Je vous écoute et j'apprends !")
