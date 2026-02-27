import streamlit as st

# 1. CONFIGURATION (Doit être la toute première commande)
st.set_page_config(page_title="NeuronAI", page_icon="🧠")

# 2. VALIDATION GOOGLE (Le robot de Google doit voir ça)
st.html('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />')

# 3. INTERFACE VISUELLE SIMPLE
# On utilise l'URL directe de ton image GitHub
LOGO_URL = "https://github.com/AWZ-7426/Neuron-AI/blob/main/Neuron-AI/images/neuron-ai.png?raw=true"

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(LOGO_URL, width=200)
st.markdown("<h1>NeuronAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: gray;'>L'intelligence collective humaine.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 4. CHAT SIMPLIFIÉ (SANS BASE DE DONNÉES POUR L'INSTANT)
# On teste d'abord si l'affichage fonctionne
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Je suis enfin en ligne. Testez-moi !"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Dites bonjour..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    response = "Je vous reçois ! Une fois que Google aura validé le site, je remettrai ma mémoire SQL."
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
