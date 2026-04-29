"""
RAG Retriever — embeds knowledge base docs and retrieves relevant chunks
using sentence-transformers (local) + FAISS (local vector search).
"""

import os
import glob
from typing import List, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Small, fast, good enough for semantic search
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")


class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.chunks: List[dict] = []   # {"text": ..., "source": ...}
        self.index = None
        self._build_index()

    def _load_docs(self) -> List[dict]:
        """Load all markdown files from knowledge_base/ and split into chunks."""
        docs = []
        pattern = os.path.join(KNOWLEDGE_BASE_DIR, "*.md")
        for filepath in glob.glob(pattern):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            source = os.path.basename(filepath)
            # Split on double newline to get paragraph-level chunks
            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 60]
            for para in paragraphs:
                docs.append({"text": para, "source": source})
        return docs

    def _build_index(self):
        """Embed all chunks and build FAISS index."""
        self.chunks = self._load_docs()
        if not self.chunks:
            raise ValueError("No documents found in knowledge_base/")

        texts = [c["text"] for c in self.chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner product = cosine after normalization
        self.index.add(embeddings)

    def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        """
        Retrieve top_k most relevant chunks for a given query.
        Returns list of {"text": ..., "source": ..., "score": ...}
        """
        query_vec = self.model.encode([query], show_progress_bar=False)
        query_vec = np.array(query_vec, dtype="float32")
        faiss.normalize_L2(query_vec)

        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(score)
            results.append(chunk)

        return results


# Module-level singleton — built once, reused across requests
_retriever_instance = None

def get_retriever() -> Retriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
    return _retriever_instance


def retrieve(query: str, top_k: int = 3) -> List[dict]:
    """Convenience function — retrieve top_k chunks for a query."""
    return get_retriever().retrieve(query, top_k)
