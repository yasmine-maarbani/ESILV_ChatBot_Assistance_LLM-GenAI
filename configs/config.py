import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    return {
        "llm": {
            "provider": os.getenv("LLM_PROVIDER", "ollama"),
            "ollama_model": os.getenv("OLLAMA_MODEL", "mistral"),
            "vertex_model": os.getenv("VERTEX_MODEL", "gemini-1.5-flash"),
            "gcp_project_id": os.getenv("GCP_PROJECT_ID", ""),
            "gcp_location": os.getenv("GCP_LOCATION", "us-central1"),
        },
        "rag": {
            "docs_dir": os.getenv("DOCS_DIR", "data/docs"),
            "index_dir": os.getenv("INDEX_DIR", "data/index"),
        },
        "app": {
            "persist_contacts_path": os.getenv("PERSIST_CONTACTS_PATH", "data/contacts.jsonl"),
            "logo_path": os.getenv("LOGO_PATH", "assets/esilv_logo.jpg"),
        },
    }