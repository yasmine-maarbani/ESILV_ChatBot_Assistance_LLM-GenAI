# Prompts et construction des messages pour le LLM

SYSTEM_PROMPT = """
Tu es l'assistant du projet ESILV Smart Assistant.
Ton rôle est de répondre aux questions des utilisateurs du site web surle fonctionnement 
et les programmes l'Ecole Supérieure d'Ingénieurs Léonard de Vinci.

Tu réponds toujours de façon claire, structurée et succint.
"""

# Nombre maximum de messages de l'historique à envoyer au modèle
MAX_HISTORY_MESSAGES = 20

def build_messages(history: list[dict]):
    """
    Construit la liste de messages pour le modèle à partir de l'historique.

    history est une liste de dicts de la forme :
    {"role": "user" | "assistant", "content": "texte..."}

    On ajoute le message système au début,
    puis les N derniers messages de l'historique (fenêtre glissante).
    """
    trimmed_history = history[-MAX_HISTORY_MESSAGES:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(trimmed_history)

    return messages
