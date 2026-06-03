"""LangGraph state definition for the Ponder agent."""
from __future__ import annotations

from typing import Annotated, List, TypedDict

from ..vectorstore import RetrievedDoc


def _take_last(_old, new):
    """Reducer: last writer wins (used for scalar fields written by parallel-ish nodes)."""
    return new


class PonderState(TypedDict, total=False):
    # Inputs
    question: str          # the user's original question (never mutated)
    query: str             # current search query (may be rewritten)

    # Routing
    route: str

    # Retrieval / grading
    documents: List[RetrievedDoc]
    relevant_docs: List[RetrievedDoc]
    sufficient: bool
    missing: str
    rewrite_count: int

    # Generation / critique
    generation: str
    critique_count: int
    critique_score: float
    critique_issues: str

    # Observability: an append-only timeline of what the agent did.
    trace: Annotated[List[dict], lambda old, new: (old or []) + (new or [])]
