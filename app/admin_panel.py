import os
import sys
import subprocess
import streamlit as st
from datetime import datetime
from pathlib import Path

def list_docs(docs_dir:  str):
    files = []
    for root, _, filenames in os.walk(docs_dir):
        for fn in filenames:
            if fn.lower().endswith((".md", ".txt", ".pdf")):
                files.append(os.path.relpath(os.path.join(root, fn), docs_dir))
    return sorted(files)

SCRAPE_META_FILE = Path("data/last_scrape.txt")
def get_last_scrape_time():
    if SCRAPE_META_FILE.exists():
        return datetime.fromisoformat(SCRAPE_META_FILE.read_text())
    return None

def admin_panel(cfg):
    docs_dir = cfg["rag"]["docs_dir"]
    index_dir = cfg["rag"]["index_dir"]
    scraping_dir = cfg["rag"]["scraping_dir"]

    # Button to launch scraping
    st.markdown("### Collect data from the website :")
    last_scrape = get_last_scrape_time()
    if last_scrape:
        st.caption(f"Last run : {last_scrape.strftime('%d/%m/%Y à %H:%M:%S')}")
        st.caption(f"Time since last scraping: {(st.session_state.app_start_time - last_scrape).days} days.")
    if st.button("Launch collect", key="admin_scraping_btn"):
        try:
            py = sys.executable  # ensure same interpreter/venv as Streamlit
            cmd = [py, "-m", "scraping.scraper", "--raw-dir", scraping_dir, "--parsed-dir", docs_dir]
            with st.spinner("Collecting data..."):
                result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                st.success("Data collected successfully.")
                # Signal Chat tab to reload the index automatically
                st.session_state["needs_index_reload"] = True
                if result.stdout:
                    st.text(result.stdout)
            else:
                st.error("Scraping failed.")
                st.text(result.stdout or "")
                st.text(result.stderr or "")
        except Exception as e:
            st.error(f"Failed to collect data: {e}")

    st.markdown("---")

    # Upload documents
    st.markdown("### Upload new documents and update old ones :")

    st.write(f"Documents directory: {docs_dir}")
    os.makedirs(docs_dir, exist_ok=True)

    # Upload docs
    st.write("Upload documents for indexing (.txt/.md):")
    uploaded = st.file_uploader(
        "Upload .txt/.md/.pdf files",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
        help="Files are saved immediately to the docs directory.",
        key="admin_upload_docs",
    )
    if uploaded:
        saved = 0
        overwritten = 0
        for f in uploaded:
            path = os.path.join(docs_dir, f.name)
            if os.path.exists(path):
                overwritten += 1
            with open(path, "wb") as out:
                out.write(f.read())
            saved += 1
        st.success(f"Saved {saved} files to {docs_dir} (overwritten: {overwritten}).")

    # Show current docs
    st.write("Current documents:")
    docs = list_docs(docs_dir)
    if docs:
        st.code("\n".join(docs), language="text")
    else:
        st.info("No .md/.txt documents in the docs directory.")

    # Rebuild index button
    st.write("Index:")
    st.caption(f"Index directory: {index_dir}")

    if st.button("Rebuild Index", key="rebuild_btn"):
        docs_dir = cfg["rag"]["docs_dir"]
        index_dir = cfg["rag"]["index_dir"]

        st.info("Releasing index and rebuilding...")

        try:
            # Close and delete all references to the index
            if "vs" in st.session_state:
                del st.session_state.vs

            if "retrieval" in st.session_state:
                del st.session_state.retrieval

            # Force garbage collection
            import gc
            gc.collect()

            # Wait for file handles to close
            import time
            time.sleep(2)

            st.info("Starting rebuild (this may take up to 30 seconds)...")

            # Run rebuild subprocess
            py = sys.executable
            cmd = [py, "-m", "rag.index_builder", "--docs-dir", docs_dir, "--index-dir", index_dir]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                st.success(" Index rebuild successful!")
                st.session_state["needs_index_reload"] = True
                if result.stdout:
                    st.text(result.stdout)
            else:
                st.error(" Index rebuild failed.")
                st.text(result.stdout or "")
                st.text(result.stderr or "")

        except Exception as e:
            st.error(f"Failed to rebuild index: {e}")