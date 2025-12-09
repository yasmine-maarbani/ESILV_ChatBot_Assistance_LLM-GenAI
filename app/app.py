import os
import streamlit as st
from dotenv import load_dotenv
import time

from logo_utils import resolve_logo_path
from configs.config import load_config
from services.llm import LLMClient, LLMConfig
from rag.vector_store import VectorStore
from agents.orchestrator import Orchestrator
from agents.retrieval_agent import RetrievalAgent
from agents.form_agent import FormAgent, Contact
from admin_panel import admin_panel  # Admin-only controls

def init_services():
    load_dotenv()
    cfg = load_config()
    llm = LLMClient(LLMConfig(
        provider=cfg["llm"]["provider"],
        ollama_model=cfg["llm"]["ollama_model"],
        vertex_model=cfg["llm"]["vertex_model"],
        gcp_project_id=cfg["llm"].get("gcp_project_id"),
        gcp_location=cfg["llm"].get("gcp_location"),
    ))
    vs = VectorStore(cfg["rag"]["index_dir"])
    return cfg, llm, vs

def _ensure_services():
    if "cfg" not in st.session_state or "llm" not in st.session_state or "vs" not in st.session_state:
        cfg, llm, vs = init_services()
        st.session_state.cfg = cfg
        st.session_state.llm = llm
        st.session_state.vs = vs
        st.session_state.orch = Orchestrator(llm)
        st.session_state.retrieval = RetrievalAgent(vs, llm)
        st.session_state.form = FormAgent(llm)

def _reload_index():
    cfg = st.session_state.cfg
    st.session_state.vs = VectorStore(cfg["rag"]["index_dir"])
    st.session_state.retrieval = RetrievalAgent(st.session_state.vs, st.session_state.llm)
    st.success("Index reloaded in app.")

def _sanitize_answer(text: str) -> str:
    if not text:
        return ""
    lines = []
    for line in text.splitlines():
        l = line.strip()
        if l.lower().startswith("source:") or l.lower().startswith("sources:"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def chat_ui():
    st.set_page_config(page_title="ESILV Assistant", page_icon="🎓", layout="wide")
    _ensure_services()

    cfg = st.session_state.cfg
    llm = st.session_state.llm
    # Resolve logo path robustly
    raw_logo = cfg["app"].get("logo_path")  # ensure your config uses 'logo_path'
    app_dir = os.path.dirname(__file__)
    logo_path = resolve_logo_path(raw_logo, app_dir)

    # Header
    cols = st.columns([1, 4])
    with cols[0]:
        try:
            if logo_path:
                # use width instead of deprecated use_column_width
                st.image(logo_path, width=160)
            else:
                # Fallback to a URL placeholder
                st.image("https://via.placeholder.com/160x48?text=ESILV+Logo", width=160)
        except Exception:
            st.image("https://via.placeholder.com/160x48?text=ESILV+Logo", width=160)

    with cols[1]:
        st.title("ESILV Smart Assistant")
        st.caption("Factual Q&A, contact collection, and admin tools")


    tab_home, tab_chat, tab_admin = st.tabs(["Home", "Chat", "Admin"])

    with tab_home:
        st.subheader("Overview")
        c1, c2, c3 = st.columns(3)
        with c1:
            docs_dir = cfg["rag"]["docs_dir"]
            st.metric("Docs", len(os.listdir(docs_dir)) if os.path.exists(docs_dir) else 0)
        with c2:
            st.metric("Index Path", cfg["rag"]["index_dir"])
        with c3:
            st.metric("Provider", cfg["llm"]["provider"])

    with tab_chat:
        st.subheader("Chat")

        # Auto-reload index if Admin rebuild signaled
        if st.session_state.get("needs_index_reload"):
            _reload_index()
            st.session_state["needs_index_reload"] = False

        # Mode selector
        st.selectbox("Mode", ["auto", "retrieval", "form"], key="chat_mode_select")

        # Chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "transcript" not in st.session_state:
            st.session_state.transcript = ""

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        user_input = st.chat_input("Ask about ESILV or share your contact details…", key="chat_input_box")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.transcript += f"\nUser: {user_input}"
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.spinner("Le modèle réfléchit..."):
                start_time = time.time()
                intent = st.session_state.get("chat_mode_select", "auto")
                if intent == "auto":
                    route = st.session_state.orch.route(user_input)
                    intent = route.get("intent", "retrieval")

                if intent == "retrieval":
                    res = st.session_state.retrieval.answer(user_input)
                    assistant_msg = _sanitize_answer(res["answer"])
                    unique_sources = list(dict.fromkeys(res["sources"]))
                    if unique_sources:
                        assistant_msg += "\n\nSources:\n- " + "\n- ".join(unique_sources[:3])
                else:
                    assistant_msg = st.session_state.form.next(st.session_state.transcript)
                response_time = time.time() - start_time
                st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
                with st.chat_message("assistant"):
                    st.markdown(assistant_msg)
                    st.caption(f"⏱️ Temps de réponse : {response_time:.2f} secondes")

    with tab_admin:
        st.subheader("Admin")
        admin_panel(cfg)

if __name__ == "__main__":
    chat_ui()