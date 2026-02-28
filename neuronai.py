import streamlit as st
import sqlite3
import os

# 1. CONFIGURATION (Toujours en premier)
st.set_page_config(page_title="NeuronAI", page_icon="🧠", layout="centered")

# 2. VALIDATION GOOGLE (Double sécurité)
# Cette balise doit être présente pour que Google Search Console valide le site
st.markdown('<head><meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" /></head>', unsafe_allow_html=True)
st.html('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />')

# 3. INTERFACE VISUELLE
# On essaie de trouver le logo par tous les moyens possibles
def show_logo():
    # URL directe GitHub (la plus fiable)
    logo_url = "https://raw.githubusercontent.com/AWZ-7426/Neuron-AI/main/Neuron-AI/images/neuron-ai.png"
    # Chemins locaux possibles
    local_paths = ["images/neuron-ai.png", "neuron-ai.png", "Neuron-AI/images/neuron-ai.png"]
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_displayed = False
        # 1er essai : URL Directe
        try:
            st.image(logo_url, use_container_width=True)
            logo_displayed = True
        except:
            # 2ème essai : Chemins locaux si l'URL échoue
            for path in local_paths:
                if os.path.exists(path):
                    st.image(path, use_container_width=True)
                    logo_displayed = True
                    break
        
        if not logo_displayed:
            st.write("🧠") # Icone de secours si l'image ne charge vraiment pas

show_logo()

st.markdown("<h1 style='text-align: center; margin-top: -20px;'>NeuronAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>L'intelligence collective humaine.</p>", unsafe_allow_html=True)

# 4. BASE DE DONNÉES (On garde ta version qui marche !)
def init_db():
    conn = sqlite3.connect('brain_v4.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS memory (prompt TEXT PRIMARY KEY, response TEXT)')
    conn.execute("INSERT OR IGNORE INTO memory VALUES ('bonjour', 'Bonjour ! Ravi de vous voir.')")
    conn.execute("INSERT OR IGNORE INTO memory VALUES ('salut', 'Salut ! On apprend quoi aujourd''hui ?')")
    conn.commit()
    conn.close()

init_db()

# 5. SYSTÈME DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "temp_q" not in st.session_state:
    st.session_state.temp_q = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Apprenez-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        text = prompt.lower().strip()
        
        if st.session_state.temp_q:
            conn = sqlite3.connect('brain_v4.db')
            conn.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (st.session_state.temp_q, prompt))
            conn.commit()
            conn.close()
            ans = f"Merci ! J'ai appris que pour '{st.session_state.temp_q}', la réponse est : {prompt}"
            st.session_state.temp_q = None
        else:
            conn = sqlite3.connect('brain_v4.db')
            res = conn.execute("SELECT response FROM memory WHERE prompt = ?", (text,)).fetchone()
            conn.close()
            
            if res:
                ans = res[0]
            else:
                ans = f"Je ne connais pas encore '{prompt}'. Peux-tu m'expliquer ?"
                st.session_state.temp_q = text

        st.write(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
