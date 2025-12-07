import os
from typing import List, Tuple
import chromadb
from chromadb.utils import embedding_functions

class VectorStore:
    def __init__(self, index_dir: str):
        os.makedirs(index_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=index_dir)
        emb_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="esilv_docs",
            embedding_function=emb_fn
        )

    def add_docs(self, doc_ids: List[str], texts: List[str], metadatas: List[dict]):
        if not texts:
            return
        self.collection.add(ids=doc_ids, documents=texts, metadatas=metadatas)

    def query(self, text: str, k: int = 5) -> List[Tuple[str, str, dict]]:
        res = self.collection.query(query_texts=[text], n_results=k)
        docs = []
        if res["ids"]:
            for i in range(len(res["ids"][0])):
                docs.append((
                    res["ids"][0][i],
                    res["documents"][0][i],
                    res["metadatas"][0][i],
                ))
        return docs