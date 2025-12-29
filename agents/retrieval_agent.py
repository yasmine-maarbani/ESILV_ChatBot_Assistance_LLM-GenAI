from typing import Dict
from rag.vector_store import VectorStore

SYSTEM_PROMPT = """You are the ESILV Retrieval Agent. 
Answer ONLY with information explicitly present in the provided context.
Do NOT infer or assume details not stated in the context. 
Provide complete and accurate answers with all relevant details (amounts, percentages, eligibility, deadlines, names).
Use bullet points or structured format when listing multiple items.
Do NOT truncate names, abbreviate, or omit information.
Do NOT include inline citations, URLs, or a 'Source:' line in your answer.
The UI will add sources separately."""

def _trim(text: str, max_chars: int = 5000) -> str:
    if text is None:
        return ""
    return text if len(text) <= max_chars else text[:max_chars] + "..."

class RetrievalAgent:
    def __init__(self, vector_store: VectorStore, llm_client):
        self.vs = vector_store
        self.llm = llm_client

    def answer(self, question: str) -> Dict:
        docs = self.vs.query(question, k=8)

        if not docs:
            return {
                "answer": "Aucune information pertinente trouvée dans les documents.",
                "sources": []
            }

        context_parts = []
        for d in docs:
            # d is tuple:  (id, text, metadata)
            doc_id, text, metadata = d

            # Handle None or missing metadata
            if metadata and isinstance(metadata, dict):
                source = metadata.get('source', 'unknown')
            else:
                source = 'unknown'

            context_parts.append(f"[{source}]\n{_trim(text)}")

        context = "\n\n".join(context_parts)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
        ]

        answer = (self.llm.chat(messages) or "").strip()
        if not answer:
            answer = "I don't know based on the provided documents."

        sources = []
        for d in docs:
            metadata = d[2]
            if metadata and isinstance(metadata, dict):
                sources.append(metadata.get("source", "unknown"))
            else:
                sources.append("unknown")

        return {"answer": answer, "sources": sources}