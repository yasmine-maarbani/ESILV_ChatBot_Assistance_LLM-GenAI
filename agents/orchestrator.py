import json
import re
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are an intent classifier for ESILV chatbot queries. 

Classify the user's query into ONE of these intents:
- "retrieval": User is asking factual questions about ESILV (programs, admissions, tuition, scholarships, calendar, etc.)
- "form": User wants to be contacted, provide contact details, speak with someone, or requests a callback

Examples of RETRIEVAL: 
- "What scholarships are offered?"
- "When does the semester start?"
- "What are the tuition fees?"
- "Tell me about the engineering program"

Examples of FORM:
- "Contact me about admissions"
- "Can someone call me?"
- "I want to speak with an advisor"
- "Email me more information"
- "My email is yasmine@example.com"
-"Je voudrais recevoir plus d'informations sur les admissions

IMPORTANT:  Respond with ONLY valid JSON in this exact format:
{"intent": "retrieval"} 
OR 
{"intent": "form"}

Do NOT add explanations, notes, or any other text."""


class Orchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client

    def route(self, user_input: str) -> Dict:
        """Route user input to the appropriate agent."""

        # First, try keyword-based routing (fast fallback)
        intent = self._keyword_route(user_input)
        if intent:
            logging.info(f"[Orchestrator] Keyword route: {intent}")
            return {"intent": intent, "notes": "keyword-based"}

        # If no clear keywords, use LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]

        try:
            resp = self.llm.chat(messages, max_tokens=50).strip()
            logging.info(f"[Orchestrator] LLM response: {resp}")

            # Try to extract JSON (handle cases where LLM adds markdown or extra text)
            json_match = re.search(r'\{[^}]+\}', resp)
            if json_match:
                data = json.loads(json_match.group(0))
                intent_value = data.get("intent", "retrieval")

                # Validate intent
                if intent_value in ["retrieval", "form"]:
                    logging.info(f"[Orchestrator] LLM route:  {intent_value}")
                    return {"intent": intent_value, "notes": "llm-based"}

            # If parsing fails, log and fallback
            logging.warning(f"[Orchestrator] Failed to parse JSON from:  {resp}")

        except Exception as e:
            logging.error(f"[Orchestrator] LLM call failed: {e}")

        # Final fallback to keyword routing
        fallback_intent = self._keyword_route(user_input, strict=False)
        logging.info(f"[Orchestrator] Fallback route: {fallback_intent}")
        return {"intent": fallback_intent, "notes": "fallback"}

    def _keyword_route(self, text: str, strict: bool = True) -> str | None:
        """Simple keyword-based routing as fallback."""
        text_lower = text.lower()

        # Strong form indicators
        form_keywords_strong = [
            "contact me", "call me", "email me", "speak with", "talk to",
            "reach out", "get in touch", "my email", "my phone", "my number"
        ]

        # Weak form indicators
        form_keywords_weak = [
            "contact", "appel", "téléphone", "rendez-vous", "advisor",
            "conseiller", "parler", "discuter"
        ]

        # Check strong form keywords
        if any(kw in text_lower for kw in form_keywords_strong):
            return "form"

        # Check weak form keywords (only if strict=False)
        if not strict and any(kw in text_lower for kw in form_keywords_weak):
            # Avoid false positives:  if user asks "How do I contact admissions?" -> retrieval
            if any(q in text_lower for q in ["comment", "how", "qui", "who", "quel", "what"]):
                return "retrieval"
            return "form"

        # Check if likely retrieval (question words)
        retrieval_indicators = ["? ", "quel", "quand", "comment", "pourquoi", "où",
                                "what", "when", "how", "why", "where", "who"]
        if any(ind in text_lower for ind in retrieval_indicators):
            return "retrieval"

        # Default
        return "retrieval" if strict else None