from typing import Dict
from rag.vector_store import VectorStore

SYSTEM_PROMPT = """You are the ESILV Retrieval Agent.
Answer ONLY with information explicitly present in the provided context.
Do NOT infer or assume details not stated in the context.
Be concise (one or two sentences).
Do NOT include inline citations, URLs, or a 'Source:' line in your answer.
The UI will add sources separately."""

def _trim(text: str, max_chars: int = 1500) -> str:
    return text if len(text) <= max_chars else text[:max_chars] + "..."

class RetrievalAgent:
    def __init__(self, vector_store: VectorStore, llm_client):
        self.vs = vector_store
        self.llm = llm_client

    def answer(self, question: str) -> Dict:
        docs = self.vs.query(question, k=5)
        context = "\n\n".join([f"[{d[2].get('source','unknown')}]\n{_trim(d[1])}" for d in docs])
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
        ]
        answer = (self.llm.chat(messages) or "").strip()
        if not answer:
            answer = "I don't know based on the provided documents."
        sources = [d[2].get("source", "unknown") for d in docs]
        return {"answer": answer, "sources": sources}