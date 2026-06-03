"""Document loading and chunking.

The corpus is a folder of plain-text / Markdown files. We split each file into
overlapping, sentence-aware chunks small enough to embed precisely but large
enough to stay self-contained.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import CHUNK_OVERLAP, CHUNK_SIZE, CORPUS_DIR

SUPPORTED_SUFFIXES = {".md", ".txt", ".markdown"}


@dataclass
class Chunk:
    """A retrievable unit of text plus where it came from."""

    text: str
    source: str  # file name, e.g. "react-agents.md"
    chunk_index: int
    metadata: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.source}::{self.chunk_index}"


def _split_sentences(text: str) -> list[str]:
    """Cheap, dependency-free sentence splitter.

    Splits on sentence punctuation and on blank lines so we never glue two
    paragraphs together. Good enough for chunking; we are not parsing prose.
    """
    # Normalise whitespace but keep paragraph breaks as explicit separators.
    parts = re.split(r"\n\s*\n", text.strip())
    sentences: list[str] = []
    for para in parts:
        para = para.strip()
        if not para:
            continue
        # Keep headings / list items whole; split long paragraphs on . ! ?
        pieces = re.split(r"(?<=[.!?])\s+", para)
        sentences.extend(p.strip() for p in pieces if p.strip())
    return sentences


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Pack sentences into ~chunk_size character windows with overlap.

    Overlap is applied by carrying the tail sentences of the previous chunk into
    the next one, which preserves context across boundaries.
    """
    sentences = _split_sentences(text)
    chunks: list[Chunk] = []
    current: list[str] = []
    current_len = 0
    idx = 0

    def flush():
        nonlocal current, current_len, idx
        if not current:
            return
        chunk_str = " ".join(current).strip()
        if chunk_str:
            chunks.append(Chunk(text=chunk_str, source=source, chunk_index=idx))
            idx += 1

    for sentence in sentences:
        s_len = len(sentence)
        # A single huge sentence: hard-split it.
        if s_len > chunk_size:
            flush()
            for start in range(0, s_len, chunk_size - overlap):
                piece = sentence[start : start + chunk_size]
                chunks.append(Chunk(text=piece, source=source, chunk_index=idx))
                idx += 1
            current, current_len = [], 0
            continue

        if current_len + s_len > chunk_size and current:
            flush()
            # Carry overlap: keep trailing sentences until we hit the overlap budget.
            carried: list[str] = []
            carried_len = 0
            for prev in reversed(current):
                if carried_len + len(prev) > overlap:
                    break
                carried.insert(0, prev)
                carried_len += len(prev)
            current = carried
            current_len = carried_len

        current.append(sentence)
        current_len += s_len

    flush()
    return chunks


def load_corpus(corpus_dir: Path = CORPUS_DIR) -> list[Chunk]:
    """Load and chunk every supported file in the corpus directory."""
    corpus_dir = Path(corpus_dir)
    if not corpus_dir.exists():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    all_chunks: list[Chunk] = []
    files = sorted(
        p for p in corpus_dir.rglob("*") if p.suffix.lower() in SUPPORTED_SUFFIXES
    )
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not text.strip():
            continue
        all_chunks.extend(chunk_text(text, source=path.name))
    return all_chunks
