import streamlit as st
import sqlite3
import uuid
import random
import os

# --- STYLE INTERFACE HUMAINE AVEC LOGO (SOFT, CLEAN & PROFESSIONNEL) ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="wide")

def apply_enhanced_style():
    # Définition du chemin de l'image (logo)
    # Assurez-vous d'avoir le logo dans un dossier 'images'
    image_path = os.path.join("images", "neuron-ai.png")
    
    # CSS pour le style général et le logo
    st.markdown(f"""
        <style>
        /* Fond de l'application doux */
        .stApp {{ background-color: #FDFDFD; }}
        
        /* Conteneur pour le logo et le titre */
        .header-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 2rem;
            width: 100%;
        }}
        
        /* Style de l'image du logo */
        .header-logo {{
            height: 120px; /* Ajustez la taille selon vos besoins */
            width: auto;
            margin-bottom: 0.5rem;
            border-radius: 10px; /* Optionnel: coins arrondis */
        }}

        /* Style pour le titre principal (moins proéminent que le logo) */
        .header-title {{
            font-size: 1.5rem; /* Réduit la taille par rapport à h1 */
            font-weight: 600;
            color: #222;
            margin: 0;
            letter-spacing: 1.5px;
            font-family: 'Helvetica Neue', sans-serif;
        }}

        /* Style des sous-titres */
        .header-subtitle {{
            color: #777;
            font-weight: 300;
            margin-top: 0.2rem;
            margin-bottom: 2rem;
            font-size: 0.9rem;
        }}
        
        /* Style des messages du chat */
        .stChatMessage {{ 
            background-color: #FFFFFF !important; 
            border-radius: 20px !important;
            padding: 20px !important;
            margin-bottom: 12px !important;
            border: 1px solid #EDEDED !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03); /* Ombre douce */
            color: #1A1A1A !important;
            font-family: 'Helvetica Neue', sans-serif;
        }}
        
        /* Sidebar (menu) */
        .css-1d391kg {{ background-color: #F8F9FA !important; border-right: 1px solid #EEEEEE; }}
        
        /* Boutons arrondis */
        .stButton button {{
            border-radius: 50px !important;
            border: 1px solid #222 !important;
            background-color: #FFFFFF !important;
            color: #222 !important;
            padding: 0.5rem 2rem !important;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .stButton button:hover {{
            background-color: #222 !important;
            color: #FFFFFF !important;
            transform: translateY(-1px); /* Effet de lévitation */
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Inputs texte */
        .stChatInput textarea {{
            background-color: #FFFFFF !important;
            border-radius: 15px !important;
            border: 1px solid #DDDDDD !important;
            padding: 10px !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Affichage du logo et du titre via HTML/CSS injecté
    # (Le texte du titre est inclus dans le conteneur du logo pour un meilleur centrage)
    if os.path.exists(image_path):
        # Utilisation de balise img HTML pour le logo avec une classe CSS pour le centrage
        st.markdown(f'''
            <div class="header-container">
                <img src="app/static/{image_path}" class="header-logo" alt="NeuronAI Logo">
                <p class="header-title">NeuronAI</p>
                <p class="header-subtitle">L'intelligence collective qui apprend de vous.</p>
            </div>
        ''', unsafe_allow_html=True)
    else:
        # Fallback si l'image n'est pas trouvée
        st.markdown('''
            <div class="header-container">
                <p class="header-title">NeuronAI</p>
                <p class="header-subtitle">L'intelligence collective qui apprend de vous.</p>
            </div>
        ''', unsafe_allow_html=True)

apply_enhanced_style()

# --- LOGIQUE DU CERVEAU (SQLite) - INCHAngée ---
# Assurez-vous que cette partie est déjà présente ou ajoutez-la si nécessaire
# (init_db, search_memory, learn, update_vote...)
def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    # Ajout d'une colonne user_id pour l'identifiant unique
    conn.execute('CREATE TABLE IF NOT EXISTS brain (id INTEGER PRIMARY KEY, user_id TEXT, prompt TEXT, response TEXT, votes INTEGER)')
    conn.commit()
    conn.close()

def search_memory(text):
    conn = sqlite3.connect('neuron_brain.db')
    # Utilisation de LIKE pour une recherche plus floue
    res = conn.execute("SELECT response FROM brain WHERE prompt LIKE ? AND votes > 0 ORDER BY votes DESC LIMIT 1", ('%'+text+'%',)).fetchone()
    conn.close()
    return res[0] if res else None

def save_memory(uid, p, r):
    conn = sqlite3.connect('neuron_brain.db')
    c = conn.cursor()
    # On insère l'identifiant unique avec la question et la réponse
    c.execute("INSERT INTO brain (user_id, prompt, response, votes) VALUES (?, ?, ?, 0)", (uid, p, r))
    last_id = c.lastrowid
    conn.commit()
    conn.close()
    return last_id

def update_vote(id, val):
    conn = sqlite3.connect('neuron_brain.db')
    conn.execute("UPDATE brain SET votes = votes + ? WHERE id = ?", (val, id))
    conn.commit()
    conn.close()

init_db()

# --- GESTION DE L'IDENTIFIANT UNIQUE - INCHAngée ---
# Assurez-vous que cette partie est déjà présente ou ajoutez-la
if "user_id" not in st.session_state:
    # On génère un identifiant unique pour cette session (par navigateur)
    st.session_state.user_id = str(uuid.uuid4())

# --- INITIALISATION SESSION ET AFFICHAGE DU CHAT - INCHAngée ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_learning" not in st.session_state:
    st.session_state.waiting_for_learning = False
if "temp_q" not in st.session_state:
    st.session_state.temp_q = ""
if "last_id" not in st.session_state:
    st.session_state.last_id = None

# Affichage des messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- LOGIQUE DU CHAT INPUT - INCHAngée ---
if prompt := st.chat_input("Discutons..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        txt = prompt.lower().strip()
        
        # 1. RÉPONSE À UNE DEMANDE D'EXPLICATION (SCÉNARIO B)
        if st.session_state.waiting_for_learning:
            ans = f"Merci beaucoup ! J'ai bien mémorisé cela dans ma base. Pour '{st.session_state.temp_q}', la réponse est maintenant : {prompt}."
            # On enregistre l'ID unique avec la mémoire
            st.session_state.last_id = save_memory(st.session_state.user_id, st.session_state.temp_q, prompt)
            st.session_state.waiting_for_learning = False
        
        # 2. SALUTATIONS ET PROACTION (SCÉNARIO C / HUMAINE)
        elif any(word in txt for word in ["salut", "bonjour", "hello"]):
            ans = random.choice([
                "Bonjour ! Je suis NeuronAI. Comment puis-je vous aider aujourd'hui ?",
                "Salut ! J'apprends de chaque conversation. Quelle est votre question ?",
                "Bonjour ! Toujours un plaisir de discuter. Qu'aimeriez-vous savoir ?"
            ])
            
        # 3. RECHERCHE EN MÉMOIRE (SCÉNARIO A)
        else:
            knowledge = search_memory(txt)
            if knowledge:
                # Réponse humaine proactive
                ans = random.choice([
                    f"Oh, je connais la réponse ! {knowledge}.",
                    f"D'après mes connaissances actuelles, {knowledge}. Est-ce bien cela ?",
                    f"J'ai déjà appris cela ! La réponse est {knowledge}."
                ])
                #st.session_state.waiting_for_learning = False # Réinitialise l'état
            else:
                # Échec de la recherche : demande d'explication (SCÉNARIO B)
                ans = random.choice([
                    "C'est une excellente question, mais je crains de ne pas encore avoir la réponse. Pourriez-vous m'éclairer ?",
                    "Je ne connais pas encore ce sujet... Auriez-vous la gentillesse de m'expliquer ce que cela signifie ?",
                    "Je suis encore en phase d'apprentissage. Si vous m'expliquez, je m'en souviendrai pour toujours."
                ])
                st.session_state.waiting_for_learning = True
                st.session_state.temp_q = prompt # Mémorise la question

        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- FEEDBACK VOTES (Optionnel, dans la sidebar) ---
with st.sidebar:
    st.write("### Identifiant Unique :")
    st.code(st.session_state.user_id, language=None)
    st.caption("Conservez cet ID pour retrouver votre historique.")

    if st.session_state.last_id:
        st.write("---")
        st.write("Est-ce une bonne réponse ?")
        c1, c2, _ = st.columns([1, 1, 2])
        with c1:
            if st.button("👍"):
                update_vote(st.session_state.last_id, 1)
                st.toast("Appris !")
                st.session_state.last_id = None
        with c2:
            if st.button("👎"):
                update_vote(st.session_state.last_id, -1)
                st.toast("Oublié.")
                st.session_state.last_id = None
