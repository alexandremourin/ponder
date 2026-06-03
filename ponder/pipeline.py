"""High-level entry points: ``ask`` (blocking) and ``stream`` (event generator).

The UI consumes ``stream`` to render the live reasoning timeline and a streaming
answer. ``eval.py`` and the tests use ``ask`` for a single, structured result.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from functools import lru_cache

from .config import active_provider
from .llm import USAGE
from .graph import build_graph
from .vectorstore import RetrievedDoc, VectorStore


@dataclass
class PonderResult:
    question: str
    answer: str
    sources: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    documents: list[RetrievedDoc] = field(default_factory=list)
    latency_s: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


@lru_cache(maxsize=1)
def _graph_and_store():
    store = VectorStore()
    return build_graph(store), store


def _sources_from(docs: list[RetrievedDoc]) -> list[str]:
    seen, out = set(), []
    for d in docs:
        if d.source not in seen:
            seen.add(d.source)
            out.append(d.source)
    return out


def ask(question: str, recursion_limit: int = 25) -> PonderResult:
    """Run the full agent and return a structured result."""
    graph, _ = _graph_and_store()
    USAGE.reset()
    t0 = time.perf_counter()
    final_state = graph.invoke(
        {"question": question}, config={"recursion_limit": recursion_limit}
    )
    latency = time.perf_counter() - t0

    used_docs = final_state.get("relevant_docs") or final_state.get("documents", [])
    return PonderResult(
        question=question,
        answer=final_state.get("generation", ""),
        sources=_sources_from(used_docs),
        trace=final_state.get("trace", []),
        documents=used_docs,
        latency_s=latency,
        input_tokens=USAGE.input_tokens,
        output_tokens=USAGE.output_tokens,
        cost_usd=USAGE.cost_usd,
    )


def stream(question: str, recursion_limit: int = 25):
    """Yield UI events as the agent works.

    Event shapes:
      {"type": "step",  "step": {...}}     # one timeline entry, emitted live
      {"type": "token", "text": "..."}     # a piece of the final answer
      {"type": "final", "result": PonderResult}
    """
    graph, _ = _graph_and_store()
    USAGE.reset()
    t0 = time.perf_counter()

    last_docs: list[RetrievedDoc] = []
    generation = ""

    # stream_mode="updates" hands us each node's state delta the moment it runs,
    # so the timeline appears step by step in real time.
    for update in graph.stream(
        {"question": question},
        stream_mode="updates",
        config={"recursion_limit": recursion_limit},
    ):
        for _node, delta in update.items():
            if not isinstance(delta, dict):
                continue
            for step in delta.get("trace", []):
                yield {"type": "step", "step": step}
            if delta.get("relevant_docs"):
                last_docs = delta["relevant_docs"]
            elif delta.get("documents") and not last_docs:
                last_docs = delta["documents"]
            if delta.get("generation"):
                generation = delta["generation"]

    # The reasoning above is genuinely live. We replay the validated final answer
    # as a token stream so the UI gets a smooth streaming effect.
    for token in _tokenize(generation):
        yield {"type": "token", "text": token}

    latency = time.perf_counter() - t0
    result = PonderResult(
        question=question,
        answer=generation,
        sources=_sources_from(last_docs),
        documents=last_docs,
        latency_s=latency,
        input_tokens=USAGE.input_tokens,
        output_tokens=USAGE.output_tokens,
        cost_usd=USAGE.cost_usd,
    )
    yield {"type": "final", "result": result}


def _tokenize(text: str):
    """Split text into small pieces for a streaming effect (keeps whitespace)."""
    import re

    for piece in re.findall(r"\S+\s*", text):
        yield piece


def provider_label() -> str | None:
    return active_provider()
