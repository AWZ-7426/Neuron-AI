import streamlit as st
import sqlite3
import random

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

def apply_style():
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        * { color: #000000 !important; font-family: 'Helvetica Neue', Arial, sans-serif; }
        .stChatMessage { 
            background-color: #F7F7F7 !important; 
            border-radius: 20px !important;
            border: 1px solid #EDEDED !important;
            padding: 15px !important;
        }
        .stChatInput textarea {
            background-color: #FFFFFF !important;
            border: 1px solid #DDD !important;
        }
        .stButton button {
            background-color: #000 !important;
            color: #FFF !important;
            border-radius: 20px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

apply_style()

# --- LOGIQUE DU CERVEAU (SQLite) ---
def init_db():
    conn = sqlite3.connect('neuron_brain.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS brain (id INTEGER PRIMARY KEY, prompt TEXT, response TEXT, votes INTEGER)')
    conn.commit()
    conn.close()

def search_memory(text):
    conn = sqlite3.connect('neuron_brain.db')
    res = conn.execute("SELECT response FROM brain WHERE prompt LIKE ? AND votes > 0 ORDER BY votes DESC LIMIT 1", ('%'+text+'%',)).fetchone()
    conn.close()
    return res[0] if res else None

def save_memory(p, r):
    conn = sqlite3.connect('neuron_brain.db')
    c = conn.cursor()
    c.execute("INSERT INTO brain (prompt, response, votes) VALUES (?, ?, 0)", (p, r))
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

# --- GESTION DE LA SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_learning" not in st.session_state:
    st.session_state.waiting_for_learning = False
if "temp_q" not in st.session_state:
    st.session_state.temp_q = ""
if "last_id" not in st.session_state:
    st.session_state.last_id = None

# --- INTERFACE ---
st.markdown("<h1 style='text-align: center;'>NeuronAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>L'intelligence collective qui apprend de vous.</p>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Dites quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        txt = prompt.lower().strip()
        
        # 1. Apprentissage actif
        if st.session_state.waiting_for_learning:
            ans = f"Merci beaucoup ! J'ai bien mémorisé. Pour '{st.session_state.temp_q}', la réponse est : {prompt}"
            save_memory(st.session_state.temp_q, prompt)
            st.session_state.waiting_for_learning = False
        
        # 2. Salutations
        elif any(w in txt for w in ["salut", "bonjour", "hello"]):
            ans = "Bonjour ! Je suis NeuronAI. Posez-moi une question ou apprenez-moi quelque chose de nouveau."
        
        # 3. Recherche
        else:
            knowledge = search_memory(txt)
            if knowledge:
                ans = f"D'après mes connaissances : {knowledge}"
            else:
                ans = "Je ne connais pas encore la réponse. Pourriez-vous m'expliquer ce que c'est ?"
                st.session_state.waiting_for_learning = True
                st.session_state.temp_q = prompt

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})