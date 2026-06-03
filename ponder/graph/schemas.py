"""Structured-output schemas for the agent's decision nodes."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    """Where to send the question first."""

    route: str = Field(
        description="Either 'retrieve' (needs the document corpus) or "
        "'direct' (a greeting, small talk, or a question about Ponder itself)."
    )
    reasoning: str = Field(description="One short sentence explaining the choice.")


class GradeDecision(BaseModel):
    """Relevance grading of the retrieved passages."""

    relevant_indices: List[int] = Field(
        default_factory=list,
        description="0-based indices of passages that actually help answer the question.",
    )
    sufficient: bool = Field(
        description="True if the relevant passages contain enough to answer well."
    )
    missing: str = Field(
        default="",
        description="If not sufficient, what information is still missing (used to rewrite).",
    )


class CritiqueDecision(BaseModel):
    """Self-critique of a drafted answer."""

    grounded: bool = Field(
        description="True if every claim is supported by the provided passages."
    )
    complete: bool = Field(
        description="True if the answer actually addresses the user's question."
    )
    score: float = Field(description="Overall answer quality from 0.0 to 1.0.")
    issues: str = Field(
        default="", description="If weak, what is wrong or missing (used to retry)."
    )
