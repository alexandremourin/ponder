"""Assemble the Ponder agent graph.

Topology (a Corrective-RAG + Self-RAG hybrid):

    START
      -> route_question
           -> direct_answer -> END                      (small talk)
           -> retrieve
                -> grade_documents
                     -> generate            (passages sufficient)
                     -> rewrite_query -> retrieve ...    (corrective loop)
      generate -> self_critique
                     -> END                 (answer is grounded & complete)
                     -> rewrite_query -> retrieve ...    (self-correction loop)

Two bounded feedback loops give the agent a chance to fix bad retrieval
(driven by the document grader) and bad answers (driven by self-critique).
"""
from __future__ import annotations

from functools import partial

from langgraph.graph import END, START, StateGraph

from ..config import MAX_CRITIQUE_RETRIES, MAX_REWRITES
from ..vectorstore import VectorStore
from . import nodes
from .state import PonderState


def _route_after_question(state: PonderState) -> str:
    return "direct_answer" if state.get("route") == "direct" else "retrieve"


def _decide_after_grade(state: PonderState) -> str:
    """Generate if we have enough; otherwise rewrite — unless we've tried enough."""
    if state.get("sufficient"):
        return "generate"
    if state.get("rewrite_count", 0) >= MAX_REWRITES:
        # Out of retries: answer with what we have rather than loop forever.
        return "generate"
    return "rewrite_query"


def _decide_after_critique(state: PonderState) -> str:
    """End if the answer passed; otherwise loop back through a corrective rewrite."""
    passed = not state.get("critique_issues")
    if passed:
        return "end"
    if state.get("critique_count", 0) > MAX_CRITIQUE_RETRIES:
        return "end"
    return "rewrite_query"


def build_graph(store: VectorStore | None = None):
    """Compile and return the agent graph. Requires a built vector store."""
    store = store or VectorStore()

    g = StateGraph(PonderState)

    g.add_node("route_question", nodes.route_question)
    g.add_node("retrieve", partial(nodes.retrieve, store=store))
    g.add_node("grade_documents", nodes.grade_documents)
    g.add_node("rewrite_query", nodes.rewrite_query)
    g.add_node("generate", nodes.generate)
    g.add_node("direct_answer", nodes.direct_answer)
    g.add_node("self_critique", nodes.self_critique)

    g.add_edge(START, "route_question")
    g.add_conditional_edges(
        "route_question",
        _route_after_question,
        {"direct_answer": "direct_answer", "retrieve": "retrieve"},
    )
    g.add_edge("direct_answer", END)
    g.add_edge("retrieve", "grade_documents")
    g.add_conditional_edges(
        "grade_documents",
        _decide_after_grade,
        {"generate": "generate", "rewrite_query": "rewrite_query"},
    )
    g.add_edge("rewrite_query", "retrieve")
    g.add_edge("generate", "self_critique")
    g.add_conditional_edges(
        "self_critique",
        _decide_after_critique,
        {"end": END, "rewrite_query": "rewrite_query"},
    )

    return g.compile()
