"""Central configuration for Ponder.

Everything tunable lives here so the rest of the codebase reads cleanly.
Values can be overridden through environment variables (see .env.example).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env once, as early as possible.
load_dotenv()

# --- Paths -------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
CORPUS_DIR = Path(os.getenv("PONDER_CORPUS_DIR", DATA_DIR / "corpus"))
CHROMA_DIR = Path(os.getenv("PONDER_CHROMA_DIR", ROOT_DIR / ".chroma"))
EVAL_FILE = DATA_DIR / "eval.jsonl"
ASSETS_DIR = ROOT_DIR / "assets"

COLLECTION_NAME = "ponder_corpus"


# --- Embeddings (local, free) ------------------------------------------------
# BAAI/bge-small-en-v1.5: 384-dim, fast on CPU, strong retrieval quality.
EMBED_MODEL_NAME = os.getenv("PONDER_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
# bge models recommend prefixing queries (not documents) with this instruction.
EMBED_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


# --- Chunking ----------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("PONDER_CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("PONDER_CHUNK_OVERLAP", "150"))


# --- Retrieval / agentic loop ------------------------------------------------
TOP_K = int(os.getenv("PONDER_TOP_K", "5"))
# Max number of (retrieve -> grade -> rewrite) cycles before we give up improving.
MAX_REWRITES = int(os.getenv("PONDER_MAX_REWRITES", "2"))
# Max number of self-critique driven retries of the full answer.
MAX_CRITIQUE_RETRIES = int(os.getenv("PONDER_MAX_CRITIQUE_RETRIES", "1"))
# A retrieved doc is "relevant enough" if the grader scores it >= this.
RELEVANCE_THRESHOLD = float(os.getenv("PONDER_RELEVANCE_THRESHOLD", "0.5"))


# --- LLM ---------------------------------------------------------------------
# Anthropic is primary; OpenAI is the automatic fallback when only that key is set.
ANTHROPIC_MODEL = os.getenv("PONDER_ANTHROPIC_MODEL", "claude-sonnet-4-6")
OPENAI_MODEL = os.getenv("PONDER_OPENAI_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("PONDER_LLM_TEMPERATURE", "0.0"))
LLM_MAX_TOKENS = int(os.getenv("PONDER_LLM_MAX_TOKENS", "1024"))


# --- Pricing (USD per 1M tokens) for the cost estimate in eval ---------------
# Rough public list prices; override via env if they change.
@dataclass(frozen=True)
class Pricing:
    input_per_mtok: float
    output_per_mtok: float


PRICING: dict[str, Pricing] = {
    "claude-sonnet-4-6": Pricing(3.0, 15.0),
    "claude-3-5-sonnet-latest": Pricing(3.0, 15.0),
    "claude-3-5-haiku-latest": Pricing(0.80, 4.0),
    "gpt-4o-mini": Pricing(0.15, 0.60),
    "gpt-4o": Pricing(2.5, 10.0),
}


def has_llm_key() -> bool:
    """True if at least one usable LLM provider key is present."""
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))


def active_provider() -> str | None:
    """Which provider we will actually use given the available keys."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return None
