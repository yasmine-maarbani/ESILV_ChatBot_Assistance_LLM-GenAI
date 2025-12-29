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

        # ✅ DEBUG: Check what we're adding
        print(f"[DEBUG VectorStore. add_docs] Adding {len(doc_ids)} documents")
        print(f"[DEBUG] Sample metadata: {metadatas[0] if metadatas else 'None'}")

        self.collection.add(ids=doc_ids, documents=texts, metadatas=metadatas)

        # ✅ Verify documents were added
        count = self.collection.count()
        print(f"[DEBUG] Collection now has {count} documents")

    def query(self, text: str, k: int = 5) -> List[Tuple[str, str, dict]]:
        # ✅ Check collection size before querying
        count = self.collection.count()
        print(f"[DEBUG VectorStore.query] Collection has {count} documents")

        if count == 0:
            print("[WARNING] Collection is empty!  No documents to query.")
            return []

        res = self.collection.query(query_texts=[text], n_results=k)

        # ✅ DEBUG: Check what ChromaDB returned
        print(f"[DEBUG] Query result keys: {res.keys()}")
        print(f"[DEBUG] IDs: {res.get('ids', [[]])[0][:3] if res.get('ids') else 'None'}")
        print(f"[DEBUG] Documents type: {type(res.get('documents'))}")
        print(f"[DEBUG] Metadatas type:  {type(res.get('metadatas'))}")

        docs = []

        # ✅ Safety checks for each field
        if not res.get("ids") or not res["ids"]:
            print("[WARNING] No IDs returned from query")
            return []

        if not res.get("documents") or not res["documents"]:
            print("[WARNING] No documents returned from query")
            return []

        if not res.get("metadatas") or not res["metadatas"]:
            print("[WARNING] No metadatas returned from query")
            return []

        # ✅ Build results with validation
        num_results = len(res["ids"][0])
        print(f"[DEBUG] Processing {num_results} results")

        for i in range(num_results):
            doc_id = res["ids"][0][i]
            text_content = res["documents"][0][i] if i < len(res["documents"][0]) else None
            metadata = res["metadatas"][0][i] if i < len(res["metadatas"][0]) else None

            # ✅ Skip invalid results
            if text_content is None:
                print(f"[WARNING] Skipping doc {doc_id} - text is None")
                continue

            if metadata is None:
                print(f"[WARNING] Doc {doc_id} has None metadata, using default")
                metadata = {"source": "unknown"}

            docs.append((doc_id, text_content, metadata))

        print(f"[DEBUG] Returning {len(docs)} valid documents\n")
        return docs