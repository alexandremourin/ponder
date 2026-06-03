"""Local embedding model wrapper (sentence-transformers / BGE).

We implement the tiny LangChain ``Embeddings`` interface ourselves instead of
pulling an extra integration package. This keeps the dependency surface small
and lets us apply the BGE query-side instruction prefix correctly.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_core.embeddings import Embeddings

from .config import EMBED_MODEL_NAME, EMBED_QUERY_PREFIX


@lru_cache(maxsize=1)
def _load_model(name: str):
    # Imported lazily: sentence-transformers (and torch) are heavy.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(name)


class LocalEmbeddings(Embeddings):
    """BGE embeddings running fully on-device — no API key, no per-call cost."""

    def __init__(self, model_name: str = EMBED_MODEL_NAME):
        self.model_name = model_name
        self._model = _load_model(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        # BGE expects an instruction prefix on the query side only.
        vector = self._model.encode(
            EMBED_QUERY_PREFIX + text, normalize_embeddings=True, show_progress_bar=False
        )
        return vector.tolist()
