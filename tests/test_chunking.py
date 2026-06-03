"""Tests for document loading and chunking."""
from ponder.chunking import Chunk, chunk_text, load_corpus
from ponder.config import CHUNK_SIZE


def _make_text(n_sentences: int) -> str:
    return " ".join(f"This is sentence number {i} about agents and retrieval." for i in range(n_sentences))


def test_chunk_ids_are_unique_and_sourced():
    chunks = chunk_text(_make_text(60), source="doc.md")
    assert len(chunks) >= 2
    assert all(isinstance(c, Chunk) for c in chunks)
    assert all(c.source == "doc.md" for c in chunks)
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))  # unique
    assert ids[0] == "doc.md::0"


def test_chunks_respect_size_budget():
    chunks = chunk_text(_make_text(200), source="doc.md", chunk_size=400, overlap=80)
    # Allow a little slack since we pack whole sentences.
    assert all(len(c.text) <= 400 + 120 for c in chunks)
    assert len(chunks) > 1


def test_overlap_carries_context():
    # With overlap, the end of one chunk should reappear at the start of the next.
    chunks = chunk_text(_make_text(120), source="doc.md", chunk_size=300, overlap=100)
    assert len(chunks) >= 2
    overlaps = 0
    for a, b in zip(chunks, chunks[1:]):
        tail = a.text.split()[-4:]
        if any(word in b.text.split()[:12] for word in tail):
            overlaps += 1
    assert overlaps >= 1


def test_long_sentence_is_hard_split():
    giant = "word " * 1000  # one very long "sentence"
    chunks = chunk_text(giant, source="big.md", chunk_size=500, overlap=50)
    assert len(chunks) > 1
    assert all(len(c.text) <= 500 for c in chunks)


def test_load_corpus_finds_documents():
    chunks = load_corpus()
    assert len(chunks) > 0
    sources = {c.source for c in chunks}
    assert "self-rag.md" in sources
    assert all(c.text.strip() for c in chunks)
