"""Tests for the agent graph wiring and routing logic.

The routing/decision functions are pure, so we can verify the agent's control
flow (the corrective and self-correction loops) without any LLM calls.
"""
from ponder.config import MAX_CRITIQUE_RETRIES, MAX_REWRITES
from ponder.graph.build import (
    _decide_after_critique,
    _decide_after_grade,
    _route_after_question,
    build_graph,
)


def test_router_sends_small_talk_to_direct():
    assert _route_after_question({"route": "direct"}) == "direct_answer"
    assert _route_after_question({"route": "retrieve"}) == "retrieve"
    assert _route_after_question({}) == "retrieve"  # default


def test_grade_generates_when_sufficient():
    assert _decide_after_grade({"sufficient": True, "rewrite_count": 0}) == "generate"


def test_grade_rewrites_when_insufficient():
    assert _decide_after_grade({"sufficient": False, "rewrite_count": 0}) == "rewrite_query"


def test_grade_stops_rewriting_at_limit():
    # Out of retries -> generate with what we have, never loop forever.
    state = {"sufficient": False, "rewrite_count": MAX_REWRITES}
    assert _decide_after_grade(state) == "generate"


def test_critique_ends_when_answer_passes():
    assert _decide_after_critique({"critique_issues": ""}) == "end"


def test_critique_retries_when_answer_weak():
    state = {"critique_issues": "missing the definition", "critique_count": 1}
    assert _decide_after_critique(state) == "rewrite_query"


def test_critique_stops_at_retry_limit():
    state = {"critique_issues": "still weak", "critique_count": MAX_CRITIQUE_RETRIES + 1}
    assert _decide_after_critique(state) == "end"


def test_graph_compiles_with_expected_nodes():
    graph = build_graph()
    node_names = set(graph.get_graph().nodes.keys())
    for expected in [
        "route_question",
        "retrieve",
        "grade_documents",
        "rewrite_query",
        "generate",
        "direct_answer",
        "self_critique",
    ]:
        assert expected in node_names
