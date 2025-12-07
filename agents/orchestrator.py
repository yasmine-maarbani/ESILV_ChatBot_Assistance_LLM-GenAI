import json
from typing import Dict

SYSTEM_PROMPT = """You are the Orchestrator. Decide intent and provide a structured plan.
Intents:
- retrieval: factual ESILV question answer from docs
- form: collect contact details
Rules:
- If user asks about ESILV info or policies -> retrieval
- If user wants to be contacted or provides personal info -> form
Return JSON with keys: intent (retrieval|form), notes."""

class Orchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def route(self, user_input: str) -> Dict:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
        resp = self.llm.chat(messages).strip()
        try:
            data = json.loads(resp)
        except Exception:
            data = {"intent": "retrieval", "notes": "fallback"}
        return data