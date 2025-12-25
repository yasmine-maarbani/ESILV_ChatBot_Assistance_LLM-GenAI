import os, uuid, argparse, pathlib
from typing import List
from pathlib import Path
from tqdm import tqdm
import shutil

# Conditional import for web crawl
try:
    from bs4 import BeautifulSoup
    import requests

    CRAWL_AVAILABLE = True
except ImportError:
    CRAWL_AVAILABLE = False

try:
    from pypdf import PdfReader

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from .vector_store import VectorStore

SUPPORTED_EXTENSIONS = {".txt", ".md"}
if PDF_AVAILABLE:
    SUPPORTED_EXTENSIONS.add(".pdf")

def _read_text_file(path: Path) -> str:
    """Read text file (txt / md) in UTF-8."""
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf_file(path: Path) -> str:
    """Read pdf file and aggregate text from all pages"""
    if not PDF_AVAILABLE:
        raise RuntimeError("pypdf not installed; cannot read PDF")
    reader = PdfReader(str(path))
    texts: List[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        texts.append(page_text)
    return "\n".join(texts)


def load_local_docs(docs_dir: str):
    texts, metas, ids = [], [], []
    base = pathlib.Path(docs_dir)
    base.mkdir(parents=True, exist_ok=True)
    for p in base.glob("**/*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                if p.suffix.lower() in {".txt", ".md"}:
                    t = _read_text_file(p)
                elif p.suffix.lower() == ".pdf":
                    t = _read_pdf_file(p)
                else:
                    continue
                texts.append(t)
                metas.append({"source": str(p.relative_to(base))})
                ids.append(str(uuid.uuid4()))
            except Exception as e:
                print(f"Failed to read {p}:  {e}")
    return ids, texts, metas


def crawl_urls(urls):
    if not CRAWL_AVAILABLE:
        raise RuntimeError("bs4/requests not installed; cannot crawl URLs")
    texts, metas, ids = [], [], []
    for url in tqdm(urls, desc="Crawling URLs"):
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            texts.append(text)
            metas.append({"source": url})
            ids.append(str(uuid.uuid4()))
        except Exception as e:
            print(f"Failed to crawl {url}: {e}")
    return ids, texts, metas

def main(docs_dir: str, index_dir: str, urls=None):
    # Clear existing index before rebuild
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
        print(f"Cleared existing index at {index_dir}")

    vs = VectorStore(index_dir)
    ids, texts, metas = load_local_docs(docs_dir)
    print(f"Loaded {len(texts)} local documents from {docs_dir}")

    if urls:
        uids, utxts, umetas = crawl_urls(urls)
        ids += uids
        texts += utxts
        metas += umetas
        print(f"Crawled {len(uids)} URLs")

    if texts:
        vs.add_docs(ids, texts, metas)
        print(f"SUCCESS: Indexed {len(texts)} documents into {index_dir}")
    else:
        print("WARNING: No documents found to index.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build/update RAG index from local docs and optional URLs")
    ap.add_argument("--docs-dir", required=True, help="Directory containing . txt/.md/. pdf files")
    ap.add_argument("--index-dir", required=True, help="Directory to store the vector index")
    ap.add_argument("--urls", nargs="*", default=None, help="Optional list of URLs to crawl and index")
    args = ap.parse_args()
    main(args.docs_dir, args.index_dir, args.urls)