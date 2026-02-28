import streamlit as st
import sqlite3
import time
from groq import Groq

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="NeuronAI", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour une interface plus moderne
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 20px; }
    .api-box { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('neuron_brain_v2.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    return conn

conn = init_db()

# --- 3. BARRE LATÉRALE (UX AMÉLIORÉE) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png", width=120)
    st.title("Configuration")
    
    with st.expander("🔑 Aide : Obtenir une clé API", expanded=False):
        st.write("""
        1. Allez sur [Groq Cloud](https://console.groq.com/keys).
        2. Connectez-vous et cliquez sur **Create API Key**.
        3. Copiez-collez la clé ici. 
        *C'est gratuit et instantané !*
        """)
    
    user_api_key = st.text_input("Clé API Groq", type="password", placeholder="gsk_...")
    
    st.divider()
    
    # Statistiques visuelles
    count = conn.execute("SELECT count(*) FROM memory").fetchone()[0]
    st.metric(label="Connaissances stockées", value=count, delta="Collectif")
    
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

# --- 4. LOGIQUE DE RÉPONSE ---
def get_ai_response(prompt, api_key):
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": "Tu es NeuronAI. Sois concis et utile."},
                      {"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur : Clé invalide ou problème réseau. ({e})"

# --- 5. INTERFACE PRINCIPALE ---
st.title("🧠 NeuronAI")
st.caption("L'IA qui apprend grâce à vous. Chaque question sans réponse est une opportunité d'apprentissage.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Je suis NeuronAI. Posez-moi une question ou apprenez-moi quelque chose de nouveau."}]

# Affichage fluide des messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Entrée utilisateur
if prompt := st.chat_input("Que voulez-vous savoir ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Recherche locale
        res_sql = conn.execute("SELECT response FROM memory WHERE prompt = ?", (prompt.lower().strip(),)).fetchone()
        
        if res_sql:
            response = f"💡 **Mémoire collective :** {res_sql[0]}"
            st.markdown(response)
        elif user_api_key:
            with st.spinner("🧠 NeuronAI réfléchit via le réseau neuronal..."):
                response = get_ai_response(prompt, user_api_key)
                st.write_stream((m for m in response.split(" "))) # Effet d'écriture en direct
        else:
            response = "🤷 Je ne connais pas encore la réponse et aucune clé API n'est configurée."
            st.info(response)
            
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Option d'enseignement (plus élégante)
    if not res_sql:
        with st.chat_message("assistant", avatar="🎓"):
            st.write("Voulez-vous m'apprendre la réponse pour la prochaine fois ?")
            new_info = st.text_input("Réponse à enregistrer :", key=f"learn_{time.time()}")
            if st.button("Enregistrer le savoir"):
                if new_info:
                    conn.execute("INSERT OR REPLACE INTO memory (prompt, response) VALUES (?, ?)", (prompt.lower().strip(), new_info))
                    conn.commit()
                    st.success("Savoir mémorisé ! Merci pour votre contribution.")
                    st.balloons() # Petit effet de fête pour l'engagement
