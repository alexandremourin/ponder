"""The agent's nodes.

Each node does one job, appends a human-readable step to ``trace`` (this is what
the UI renders as a live timeline), and returns a small state delta.
"""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from ..config import MAX_REWRITES, RELEVANCE_THRESHOLD, TOP_K
from ..llm import get_llm, invoke
from ..vectorstore import RetrievedDoc, VectorStore
from . import prompts
from .schemas import CritiqueDecision, GradeDecision, RouteDecision
from .state import PonderState


def _format_passages(docs: list[RetrievedDoc]) -> str:
    """Number passages so the grader/critique can refer to them by index."""
    blocks = []
    for i, d in enumerate(docs):
        blocks.append(f"[{i}] (source: {d.source}, sim={d.similarity:.2f})\n{d.text}")
    return "\n\n".join(blocks) if blocks else "(no passages)"


def _step(node: str, title: str, detail: str = "", **data) -> dict:
    return {"node": node, "title": title, "detail": detail, **data}


# --- Nodes -------------------------------------------------------------------
def route_question(state: PonderState) -> dict:
    """Classify the question: does it need the corpus, or is it small talk?"""
    llm = get_llm(temperature=0).with_structured_output(RouteDecision)
    decision: RouteDecision = llm.invoke(
        [
            SystemMessage(content=prompts.router_prompt()),
            HumanMessage(content=state["question"]),
        ]
    )
    return {
        "route": decision.route,
        "query": state["question"],
        "rewrite_count": 0,
        "critique_count": 0,
        "trace": [
            _step(
                "route",
                f"Routed to '{decision.route}'",
                decision.reasoning,
            )
        ],
    }


def retrieve(state: PonderState, store: VectorStore) -> dict:
    """Top-k similarity search for the current query."""
    docs = store.search(state["query"], k=TOP_K)
    detail = ", ".join(f"{d.source} ({d.similarity:.2f})" for d in docs) or "no hits"
    return {
        "documents": docs,
        "trace": [
            _step(
                "retrieve",
                f"Retrieved top-{len(docs)} passages",
                detail,
                query=state["query"],
                hits=[{"source": d.source, "similarity": round(d.similarity, 3)} for d in docs],
            )
        ],
    }


def grade_documents(state: PonderState) -> dict:
    """Filter by similarity, then have the LLM judge relevance + sufficiency."""
    docs = state.get("documents", [])
    # Cheap pre-filter: drop clearly off-topic hits before spending an LLM call.
    prefiltered = [d for d in docs if d.similarity >= RELEVANCE_THRESHOLD]
    candidates = prefiltered or docs  # if nothing passes, still let the LLM look

    if not candidates:
        return {
            "relevant_docs": [],
            "sufficient": False,
            "missing": "No passages were retrieved at all.",
            "trace": [_step("grade", "No passages to grade", "Retrieval returned nothing.")],
        }

    llm = get_llm(temperature=0).with_structured_output(GradeDecision)
    decision: GradeDecision = llm.invoke(
        [
            SystemMessage(content=prompts.grader_prompt()),
            HumanMessage(
                content=(
                    f"Question:\n{state['question']}\n\n"
                    f"Passages:\n{_format_passages(candidates)}"
                )
            ),
        ]
    )
    relevant = [candidates[i] for i in decision.relevant_indices if 0 <= i < len(candidates)]
    # If the grader marked it sufficient but selected nothing, fall back to candidates.
    if decision.sufficient and not relevant:
        relevant = candidates

    detail = (
        f"{len(relevant)}/{len(candidates)} relevant — "
        f"{'sufficient' if decision.sufficient else 'insufficient'}"
    )
    if not decision.sufficient and decision.missing:
        detail += f". Missing: {decision.missing}"
    return {
        "relevant_docs": relevant,
        "sufficient": decision.sufficient,
        "missing": decision.missing,
        "trace": [_step("grade", "Graded passage relevance", detail)],
    }


def rewrite_query(state: PonderState) -> dict:
    """Corrective step: rewrite the query toward what the grader said was missing."""
    llm = get_llm(temperature=0.2)
    note = state.get("missing") or state.get("critique_issues") or "previous results were weak"
    response = invoke(
        llm,
        [
            SystemMessage(content=prompts.rewrite_prompt()),
            HumanMessage(
                content=(
                    f"Original question:\n{state['question']}\n\n"
                    f"What was missing/wrong:\n{note}\n\n"
                    f"Previous query:\n{state['query']}"
                )
            ),
        ],
    )
    new_query = response.content.strip().strip('"')
    return {
        "query": new_query,
        "rewrite_count": state.get("rewrite_count", 0) + 1,
        "trace": [
            _step(
                "rewrite",
                f"Rewrote the query (attempt {state.get('rewrite_count', 0) + 1})",
                f"'{state['query']}' -> '{new_query}'",
            )
        ],
    }


def generate(state: PonderState) -> dict:
    """Draft an answer grounded in the relevant passages, with inline citations."""
    docs = state.get("relevant_docs") or state.get("documents", [])
    llm = get_llm()
    response = invoke(
        llm,
        [
            SystemMessage(content=prompts.generate_prompt()),
            HumanMessage(
                content=(
                    f"Question:\n{state['question']}\n\n"
                    f"Passages:\n{_format_passages(docs)}"
                )
            ),
        ],
    )
    return {
        "generation": response.content,
        "trace": [
            _step(
                "generate",
                "Drafted a grounded answer",
                f"Using {len(docs)} passage(s).",
            )
        ],
    }


def direct_answer(state: PonderState) -> dict:
    """Answer greetings / meta questions without touching the corpus."""
    llm = get_llm()
    response = invoke(
        llm,
        [
            SystemMessage(content=prompts.direct_prompt()),
            HumanMessage(content=state["question"]),
        ],
    )
    return {
        "generation": response.content,
        "relevant_docs": [],
        "trace": [_step("direct", "Answered directly", "No retrieval needed.")],
    }


def self_critique(state: PonderState) -> dict:
    """Self-RAG style check: is the draft grounded and complete?"""
    docs = state.get("relevant_docs") or state.get("documents", [])
    llm = get_llm(temperature=0).with_structured_output(CritiqueDecision)
    decision: CritiqueDecision = llm.invoke(
        [
            SystemMessage(content=prompts.critique_prompt()),
            HumanMessage(
                content=(
                    f"Question:\n{state['question']}\n\n"
                    f"Passages:\n{_format_passages(docs)}\n\n"
                    f"Draft answer:\n{state['generation']}"
                )
            ),
        ]
    )
    verdict = "passed" if (decision.grounded and decision.complete) else "needs work"
    detail = f"grounded={decision.grounded}, complete={decision.complete}, score={decision.score:.2f}"
    if verdict == "needs work" and decision.issues:
        detail += f". Issues: {decision.issues}"
    return {
        "critique_score": decision.score,
        "critique_issues": decision.issues if verdict == "needs work" else "",
        "critique_count": state.get("critique_count", 0)
        + (0 if (decision.grounded and decision.complete) else 1),
        "missing": decision.issues if verdict == "needs work" else state.get("missing", ""),
        "trace": [_step("critique", f"Self-critique {verdict}", detail)],
    }
