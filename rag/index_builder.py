import os, uuid, argparse, pathlib
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from .vector_store import VectorStore

def load_local_docs(docs_dir: str):
    texts, metas, ids = [], [], []
    base = pathlib.Path(docs_dir)
    base.mkdir(parents=True, exist_ok=True)
    for p in base.glob("**/*"):
        if p.is_file() and p.suffix.lower() in {".txt", ".md"}:
            try:
                t = p.read_text(encoding="utf-8", errors="ignore")
                texts.append(t)
                metas.append({"source": str(p)})
                ids.append(str(uuid.uuid4()))
            except Exception as e:
                print(f"Failed to read {p}: {e}")
    return ids, texts, metas

def crawl_urls(urls):
    texts, metas, ids = [], [], []
    for url in tqdm(urls):
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(separator="\n")
            texts.append(text)
            metas.append({"source": url})
            ids.append(str(uuid.uuid4()))
        except Exception as e:
            print(f"Failed to crawl {url}: {e}")
    return ids, texts, metas

def main(docs_dir: str, index_dir: str, urls=None):
    vs = VectorStore(index_dir)
    ids, texts, metas = load_local_docs(docs_dir)
    if urls:
        uids, utxts, umetas = crawl_urls(urls)
        ids += uids; texts += utxts; metas += umetas
    if texts:
        vs.add_docs(ids, texts, metas)
        print(f"Indexed {len(texts)} documents into {index_dir}")
    else:
        print("No documents found.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-dir", required=True)
    ap.add_argument("--index-dir", required=True)
    ap.add_argument("--urls", nargs="*", default=None)
    args = ap.parse_args()
    main(args.docs_dir, args.index_dir, args.urls)