# Wrapper simple autour du client Python Ollama

import ollama

class OllamaClient:
    def __init__(self, model: str):
        self.model = model

    def generate(self, messages: list[dict]) -> str:
        """
        Appelle le modèle via ollama.chat() et retourne uniquement le texte.
        """
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            return response["message"]["content"]

        except Exception as e:
            raise RuntimeError(
                f"Erreur lors de l'appel au modèle Ollama ({self.model}) : {e}"
            )
