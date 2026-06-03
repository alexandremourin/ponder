"""Tests for the vector store and retrieval.

These run fully offline with local BGE embeddings (no API key). The model is
downloaded once and cached by sentence-transformers.
"""
import pytest

from ponder.chunking import Chunk
from ponder.vectorstore import VectorStore


@pytest.fixture(scope="module")
def store(tmp_path_factory):
    persist = tmp_path_factory.mktemp("chroma_test")
    vs = VectorStore(persist_dir=persist, collection_name="test_collection")
    vs.reset()
    chunks = [
        Chunk(text="The stdio transport runs an MCP server as a subprocess over stdin and stdout.", source="mcp.md", chunk_index=0),
        Chunk(text="Reciprocal Rank Fusion scores documents as one over k plus rank, summed across lists.", source="fusion.md", chunk_index=0),
        Chunk(text="Self-RAG uses reflection tokens to decide when to retrieve and to critique its output.", source="selfrag.md", chunk_index=0),
        Chunk(text="HNSW is a graph-based approximate nearest neighbor index used by vector databases.", source="hnsw.md", chunk_index=0),
    ]
    vs.add_chunks(chunks)
    return vs


def test_index_counts_all_chunks(store):
    assert store.count() == 4


def test_search_returns_most_relevant_first(store):
    hits = store.search("How does an MCP server run as a subprocess?", k=2)
    assert hits, "expected at least one hit"
    assert hits[0].source == "mcp.md"
    assert 0.0 <= hits[0].similarity <= 1.0


def test_search_ranks_by_similarity(store):
    hits = store.search("reflection tokens in Self-RAG", k=4)
    assert hits[0].source == "selfrag.md"
    sims = [h.similarity for h in hits]
    assert sims == sorted(sims, reverse=True)  # descending


def test_empty_query_safe_on_empty_store(tmp_path):
    vs = VectorStore(persist_dir=tmp_path / "empty", collection_name="empty_col")
    vs.reset()
    assert vs.count() == 0
    assert vs.search("anything", k=3) == []
