import streamlit as st

# Configuration minimale
st.set_page_config(page_title="NeuronAI")

# Titre en texte pur (impossible à rater)
st.title("NeuronAI")
st.write("L'intelligence collective humaine.")

# Balise Google en texte simple pour qu'elle soit dans le code source
st.markdown("", unsafe_allow_html=True)

# Un champ de texte simple
user_input = st.text_input("Dis quelque chose pour tester :")
if user_input:
    st.write(f"Tu as dit : {user_input}")

