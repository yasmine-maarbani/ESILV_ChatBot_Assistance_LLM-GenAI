# Prompts et construction des messages pour le LLM

SYSTEM_PROMPT = """
Tu es l'assistant du projet ESILV Smart Assistant.
Ton rôle est d'aider les étudiants à comprendre, structurer et implémenter
un assistant intelligent basé sur des modèles de langue.

Tu réponds toujours de façon claire, structurée et pédagogique.
"""

def build_messages(user_input: str):
    """
    Construit la liste de messages pour le modèle.
    V0 : pas de mémoire → seulement système + utilisateur.
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]
