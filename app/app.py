import os
import streamlit as st
from dotenv import load_dotenv
import time
from datetime import datetime
from pathlib import Path
import sys
import subprocess

from configs.config import load_config
from services.llm import LLMClient, LLMConfig, OllamaClient, VertexClient
from rag.vector_store import VectorStore
from agents.orchestrator import Orchestrator
from agents.retrieval_agent import RetrievalAgent
from agents.form_agent import FormAgent, Contact
from admin_panel import admin_panel, get_last_scrape_time  # Admin-only controls

def init_services():
    load_dotenv()
    cfg = load_config()
    conf = LLMConfig(
        provider=cfg["llm"]["provider"],
        ollama_model=cfg["llm"]["ollama_model"],
        vertex_model=cfg["llm"]["vertex_model"],
        gcp_project_id=cfg["llm"].get("gcp_project_id"),
        gcp_location=cfg["llm"].get("gcp_location"),
    )
    if conf.provider == "ollama":
        llm = OllamaClient(conf)
    elif conf.provider == "vertex":
        llm = VertexClient(conf)
    else:
        llm = LLMClient(conf)
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

def auto_scraping(docs_dir, scraping_dir):
    if "app_start_time" not in st.session_state:
        st.session_state.app_start_time = datetime.now()
    
    last_scrape = get_last_scrape_time()
    if last_scrape:
        st.sidebar.caption(f"Dernier scraping : {last_scrape.strftime('%d/%m/%Y à %H:%M:%S')}")
        st.sidebar.caption(f"Time since last scraping: {(st.session_state.app_start_time - last_scrape).days} days.")
        if (st.session_state.app_start_time - last_scrape).days >= 2 :
            st.sidebar.caption("The retrieval database might be obsolete.")
            st.sidebar.caption("Updating the database:")
            try:
                py = sys.executable  # ensure same interpreter/venv as Streamlit
                cmd = [py, "-m", "scraping.scraper", "--raw-dir", scraping_dir, "--parsed-dir", docs_dir]
                with st.sidebar.caption("Collecting data..."):
                    result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    st.sidebar.success("Data collected successfully.")
                    # Signal Chat tab to reload the index automatically
                    st.session_state["needs_index_reload"] = True
                    if result.stdout:
                        st.text(result.stdout)
                else:
                    st.sidebar.error("Scraping failed.")
                    st.sidebar.text(result.stdout or "")
                    st.sidebar.text(result.stderr or "")
            except Exception as e:
                st.sidebar.error(f"Failed to collect data: {e}")
    else:
        st.sidebar.caption("Aucun scraping détecté")


def chat_ui():
    st.set_page_config(
        page_title="ESILV Assistant",
        page_icon="🎓",
        layout="wide"
    )

    st.image("assests/esilv_logo.jpg", width=160)

    st.title("ESILV Smart Assistant")
    st.caption("Factual Q&A, contact collection, and admin tools")

    cfg = st.session_state.cfg

    auto_scraping(
        docs_dir = cfg["rag"]["docs_dir"],
        scraping_dir = cfg["rag"]["scraping_dir"]
    )

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