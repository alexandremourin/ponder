"""Build the Chroma index from the corpus folder.

Run as a module:  python -m ponder.ingest [--reset]
"""
from __future__ import annotations

import argparse
import time

from .chunking import load_corpus
from .config import CORPUS_DIR
from .vectorstore import VectorStore


def ingest(reset: bool = True) -> dict:
    """Load corpus -> chunk -> embed -> store. Returns simple stats."""
    t0 = time.perf_counter()
    chunks = load_corpus(CORPUS_DIR)
    if not chunks:
        raise RuntimeError(f"No documents found in {CORPUS_DIR}")

    store = VectorStore()
    if reset:
        store.reset()
    store.add_chunks(chunks)
    elapsed = time.perf_counter() - t0

    sources = {c.source for c in chunks}
    stats = {
        "documents": len(sources),
        "chunks": len(chunks),
        "indexed": store.count(),
        "seconds": round(elapsed, 2),
    }
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest the Ponder corpus into Chroma.")
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Append to the existing index instead of rebuilding it.",
    )
    args = parser.parse_args()

    print(f"Ingesting corpus from {CORPUS_DIR} ...")
    stats = ingest(reset=not args.no_reset)
    print(
        f"Done in {stats['seconds']}s — {stats['documents']} documents, "
        f"{stats['chunks']} chunks, {stats['indexed']} vectors indexed."
    )


if __name__ == "__main__":
    main()
