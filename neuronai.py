import streamlit as st
import sqlite3
from groq import Groq

# --- CONFIGURATION (POUR GOOGLE & BING) ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="wide")

# Balises de validation DNS/Meta
st.markdown('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />', unsafe_allow_html=True)
st.markdown('<meta name="msvalidate.01" content="BA1A2EF4B67CEB856BA0329B7C545711" />', unsafe_allow_html=True)

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
    conn.commit()
    return conn

conn = init_db()

# --- BARRE LATÉRALE (GESTION DE LA CLÉ) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png", width=100)
    st.title("Configuration")
    
    # Zone de saisie sécurisée pour la clé API
    user_api_key = st.text_input(
        "Clé API Groq", 
        type="password", 
        help="Obtenez une clé gratuite sur console.groq.com. Votre clé n'est pas enregistrée sur nos serveurs.",
        placeholder="gsk_..."
    )
    
    if user_api_key:
        st.success("Clé activée ! ✅")
    else:
        st.warning("⚠️ Entrez une clé pour activer l'IA générative.")
    
    st.write("---")
    count = conn.execute("SELECT count(*) FROM memory").fetchone()[0]
    st.metric("Mémoire collective", f"{count} faits")

# --- INITIALISATION CLIENT GROQ ---
def get_ai_response(prompt, api_key):
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Tu es NeuronAI, une IA collaborative qui complète sa mémoire locale."},
                {"role": "user", "content": prompt}
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur API : Assurez-vous que votre clé est valide. ({str(e)})"

# --- INTERFACE DE CHAT ---
st.title("🧠 NeuronAI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Entrée utilisateur
if prompt := st.chat_input("Posez une question ou apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Priorité à la mémoire locale (SQLite)
        res_sql = conn.execute("SELECT response FROM memory WHERE prompt = ?", (prompt.lower().strip(),)).fetchone()
        
        if res_sql:
            full_response = f"**[Mémoire collective]** : {res_sql[0]}"
            st.markdown(full_response)
        
        # 2. Appel à l'IA si la clé est présente
        elif user_api_key:
            with st.spinner("L'IA réfléchit..."):
                full_response = get_ai_response(prompt, user_api_key)
                st.markdown(full_response)
        
        # 3. Message si rien n'est disponible
        else:
            full_response = "Je ne connais pas la réponse et aucune clé API n'est configurée pour me permettre de chercher plus loin."
            st.info(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Zone d'apprentissage (Expander)
    with st.expander("Enseigner la réponse à NeuronAI"):
        learn_val = st.text_input("Réponse souhaitée :", key=f"input_{prompt}")
        if st.button("Mémoriser"):
            if learn_val:
                conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (prompt.lower().strip(), learn_val))
                conn.commit()
                st.success("Merci ! Cette information est maintenant gravée dans ma mémoire collective.")
            else:
                st.error("Veuillez entrer une réponse.")
