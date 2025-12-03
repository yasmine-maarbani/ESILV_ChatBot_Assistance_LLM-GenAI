import streamlit as st

from source.llm_client import OllamaClient
from source.prompts import build_messages
from source.config import OLLAMA_MODEL

# Config de la page
st.set_page_config(page_title="ESILV Smart Assistant - V0", page_icon="icon.png")

st.title("ESILV Smart Assistant")
st.write(
    "Chat avec mémoire de session : l'assistant se souvient de la conversation "
    "tant que la page reste ouverte."
)

# Initialisation de la mémoire de conversation dans la session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bouton pour réinitialiser la conversation
if st.button("🔄 Réinitialiser la conversation"):
    st.session_state.messages = []

# Affichage de l'historique existant
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role):
        st.sidebar.write("Historique")
        st.write(content)

# Initialisation du client LLM
client = OllamaClient(model=OLLAMA_MODEL)

# Zone de saisie utilisateur
user_input = st.chat_input("Écris ton message ici...")

if user_input:
    # 1. Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. Afficher le message utilisateur
    with st.chat_message("user"):
        st.sidebar.write("Question")
        st.markdown(user_input)

    # 3. Construire les messages à envoyer au modèle à partir de l'historique
    messages = build_messages(st.session_state.messages)

    # 4. Appeler le modèle et ajouter la réponse à l'historique
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = ""

        with st.spinner("Le modèle réfléchit..."):
            try:
                response = client.generate(messages)
                st.sidebar.write("Réponse")
                message_placeholder.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                error_msg = f"Erreur lors de l'appel au modèle : {e}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
