import streamlit as st
import sqlite3
from groq import Groq

# --- CONFIGURATION (POUR GOOGLE & BING) ---
st.set_page_config(page_title="NeuronAI - Intelligence Collective", page_icon="🧠", layout="wide")

# Balises de validation (Indispensables même avec le domaine)
st.markdown('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />', unsafe_allow_html=True)
st.markdown('<meta name="msvalidate.01" content="BA1A2EF4B67CEB856BA0329B7C545711" />', unsafe_allow_html=True)

# --- INITIALISATION API GROQ ---
# Remplace 'TA_CLE_API_ICI' par ta vraie clé ou utilise les Secrets Streamlit
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "TA_CLE_API_ICI"))

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
    conn.commit()
    return conn

conn = init_db()

# --- FONCTIONS LOGIQUES ---
def get_local_memory(prompt):
    res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (prompt.lower().strip(),)).fetchone()
    return res[0] if res else None

def get_ai_response(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": "Tu es NeuronAI, une IA collaborative."},
                      {"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception:
        return "Je rencontre une petite difficulté technique, mais je reste à l'écoute !"

# --- INTERFACE (SIDEBAR) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png", width=100)
    st.title("Centre de Contrôle")
    count = conn.execute("SELECT count(*) FROM memory").fetchone()[0]
    st.metric("Connaissances locales", count)
    st.write("---")
    if st.button("Effacer l'historique de session"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT INTERFACE ---
st.title("🧠 NeuronAI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Zone de saisie
if prompt := st.chat_input("Posez-moi une question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Vérifier la mémoire locale
        local_res = get_local_memory(prompt)
        
        if local_res:
            response = f"**[Mémoire locale]** : {local_res}"
        else:
            # 2. Utiliser l'IA si inconnu localement
            with st.spinner("Recherche dans le réseau neuronal..."):
                response = get_ai_response(prompt)
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 3. Option d'apprentissage si l'utilisateur veut corriger/ajouter
    if not local_res:
        with st.expander("Enseigner une réponse spécifique à NeuronAI"):
            new_res = st.text_input("Quelle réponse devrais-je donner à l'avenir ?", key=f"learn_{prompt}")
            if st.button("Enregistrer dans ma mémoire"):
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (prompt.lower().strip(), new_res))
                conn.commit()
                st.success("C'est noté ! J'ai enrichi ma base de données.")
