import streamlit as st

# 1. VALIDATION (Placée en haut pour Google et Bing)
st.set_page_config(page_title="NeuronAI")
st.markdown('<meta name="google-site-verification" content="RupwzSf8j4KZ8576pUlcVZhUoix4knzYb9CZd0YPxTY" />', unsafe_allow_html=True)
st.markdown('<meta name="msvalidate.01" content="BA1A2EF4B67CEB856BA0329B7C545711" />', unsafe_allow_html=True)

# 2. INTERFACE
st.title("🧠 NeuronAI")
st.write("Le site est en maintenance pour l'intégration d'une nouvelle API d'IA.")
st.write("Validation en cours...")

# 3. TEST DE CHAT SIMPLE
prompt = st.chat_input("Dites bonjour pour tester")
if prompt:
    st.write(f"Vous avez dit : {prompt}")
