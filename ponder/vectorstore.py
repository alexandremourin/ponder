"""Thin Chroma wrapper: build the index and run similarity search.

We use chromadb directly (PersistentClient) rather than the LangChain Chroma
integration so the persistence story is explicit and we control scoring.
Distances are cosine; we convert them to a 0..1 similarity for grading.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chunking import Chunk
from .config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from .embeddings import LocalEmbeddings


@dataclass
class RetrievedDoc:
    """A search hit returned to the agent."""

    text: str
    source: str
    chunk_id: str
    similarity: float  # 0..1, higher is better

    def cite(self) -> str:
        return self.source


class VectorStore:
    def __init__(
        self,
        persist_dir: Path = CHROMA_DIR,
        collection_name: str = COLLECTION_NAME,
        embeddings: LocalEmbeddings | None = None,
    ):
        import chromadb

        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings = embeddings or LocalEmbeddings()
        self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection_name = collection_name
        # cosine space so similarity = 1 - distance.
        self._collection = self._client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    # --- Indexing ------------------------------------------------------------
    def reset(self) -> None:
        """Drop and recreate the collection (used by a clean re-ingest)."""
        try:
            self._client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: list[Chunk], batch_size: int = 128) -> int:
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            embeddings = self.embeddings.embed_documents([c.text for c in batch])
            self._collection.add(
                ids=[c.id for c in batch],
                documents=[c.text for c in batch],
                embeddings=embeddings,
                metadatas=[{"source": c.source, "chunk_index": c.chunk_index} for c in batch],
            )
        return len(chunks)

    def count(self) -> int:
        return self._collection.count()

    # --- Retrieval -----------------------------------------------------------
    def search(self, query: str, k: int = TOP_K) -> list[RetrievedDoc]:
        if self.count() == 0:
            return []
        query_vec = self.embeddings.embed_query(query)
        res = self._collection.query(
            query_embeddings=[query_vec],
            n_results=min(k, self.count()),
            include=["documents", "metadatas", "distances"],
        )
        docs: list[RetrievedDoc] = []
        ids = res["ids"][0]
        documents = res["documents"][0]
        metadatas = res["metadatas"][0]
        distances = res["distances"][0]
        for cid, text, meta, dist in zip(ids, documents, metadatas, distances):
            docs.append(
                RetrievedDoc(
                    text=text,
                    source=meta.get("source", "unknown"),
                    chunk_id=cid,
                    similarity=max(0.0, 1.0 - float(dist)),
                )
            )
        return docs
