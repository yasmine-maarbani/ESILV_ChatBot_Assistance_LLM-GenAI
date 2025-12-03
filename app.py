import streamlit as st

# Import du wrapper LLM et des helpers
import source
from source.llm_client import OllamaClient
from source.prompts import build_messages
from source.config import OLLAMA_MODEL


# Configuration de la page
st.set_page_config(page_title="ESILV Smart Assistant", page_icon="icon.png")

# Titre principal
st.title("🤖 ESILV Smart Assistant")
st.write("Prototype minimal : un message → une réponse (pas encore de mémoire).")

# Initialisation du client LLM
client = OllamaClient(model=OLLAMA_MODEL)

# Zone de chat Streamlit
user_input = st.chat_input("Écris ton message ici...")

if user_input:
    # Afficher le message de l'utilisateur
    with st.chat_message("user"):
        st.write(user_input)

    # Construire les messages pour le modèle
    messages = build_messages(user_input)

    # Appel au modèle
    with st.chat_message("assistant"):
        with st.spinner("Le modèle réfléchit..."):
            try:
                response = client.generate(messages)
                st.write(response)
            except Exception as e:
                st.error(f"Erreur lors de l'appel au modèle : {e}")
