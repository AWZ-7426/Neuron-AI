import webview

# Remplace par l'URL de ton site une fois déployé
url = "https://neuron-ai.streamlit.app" 

# Crée la fenêtre de l'application
window = webview.create_window('NeuronAI', url, width=1000, height=800)

# Lance l'application
webview.start()