"""Ponder — Streamlit chat UI.

Shows the agent's reasoning as a live timeline (route -> retrieve -> grade ->
rewrite -> generate -> self-critique) and streams the final, cited answer.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from ponder.config import (
    ANTHROPIC_MODEL,
    OPENAI_MODEL,
    active_provider,
    has_llm_key,
)
from ponder.vectorstore import VectorStore

st.set_page_config(page_title="Ponder", page_icon="●", layout="centered")

# --- Minimal, professional styling -------------------------------------------
st.markdown(
    """
    <style>
      .ponder-title { font-size: 2.4rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom:0; }
      .ponder-sub { color: #6b7280; margin-top: 0.1rem; }
      .step-tag {
        display:inline-block; font-size:0.70rem; font-weight:700; letter-spacing:0.05em;
        padding:2px 8px; border-radius:6px; background:#f3eddf; color:#8a6d2f; margin-right:8px;
        vertical-align:middle;
      }
      .step-title { font-weight:600; }
      .step-detail { color:#6b7280; font-size:0.85rem; margin:2px 0 10px 0; }
      .source-card { border:1px solid #ececec; border-radius:8px; padding:10px 12px; margin-bottom:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

STEP_LABELS = {
    "route": "ROUTE",
    "retrieve": "RETRIEVE",
    "grade": "GRADE",
    "rewrite": "REWRITE",
    "generate": "GENERATE",
    "direct": "ANSWER",
    "critique": "CRITIQUE",
}


def render_step(container, step: dict) -> None:
    tag = STEP_LABELS.get(step.get("node", ""), step.get("node", "").upper())
    title = step.get("title", "")
    detail = step.get("detail", "")
    html = f'<div><span class="step-tag">{tag}</span><span class="step-title">{title}</span></div>'
    if detail:
        html += f'<div class="step-detail">{detail}</div>'
    container.markdown(html, unsafe_allow_html=True)


# --- Header ------------------------------------------------------------------
st.markdown('<div class="ponder-title">Ponder</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ponder-sub">An agentic RAG that checks its own work — and shows you how.</div>',
    unsafe_allow_html=True,
)
st.write("")

# --- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.subheader("Status")
    store = VectorStore()
    n_vectors = store.count()
    if n_vectors == 0:
        st.warning("Index is empty. Run `make ingest` (or `python -m ponder.ingest`).")
    else:
        st.success(f"Index ready — {n_vectors} chunks.")

    provider = active_provider()
    if provider == "anthropic":
        st.success(f"LLM: Anthropic ({ANTHROPIC_MODEL})")
    elif provider == "openai":
        st.success(f"LLM: OpenAI fallback ({OPENAI_MODEL})")
    else:
        st.error("No LLM key found.")
    st.caption("Retrieval runs locally (BGE embeddings) — no key needed.")

# --- Guard: no key -----------------------------------------------------------
if not has_llm_key():
    st.error(
        "**No LLM API key found.**\n\n"
        "Add your own key to a `.env` file at the project root:\n\n"
        "```\nANTHROPIC_API_KEY=sk-ant-...\n```\n\n"
        "Then restart the app. (You can also use `OPENAI_API_KEY` as a fallback.)"
    )
    st.stop()

if store.count() == 0:
    st.stop()

# --- Chat history ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(msg["sources"]))

# --- Chat input --------------------------------------------------------------
prompt = st.chat_input("Ask about LLM agents, RAG, MCP, or agent frameworks…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Import here so the page still loads if heavy deps are slow.
    from ponder.pipeline import stream

    with st.chat_message("assistant"):
        timeline = st.expander("Reasoning timeline", expanded=True)
        answer_box = st.empty()
        meta_box = st.empty()

        answer_text = ""
        final_result = None

        for event in stream(prompt):
            if event["type"] == "step":
                render_step(timeline, event["step"])
            elif event["type"] == "token":
                answer_text += event["text"]
                answer_box.markdown(answer_text + "▌")
            elif event["type"] == "final":
                final_result = event["result"]

        answer_box.markdown(answer_text)

        sources = final_result.sources if final_result else []
        if sources:
            with st.expander(f"Sources ({len(sources)})", expanded=True):
                for d in (final_result.documents or [])[:6]:
                    st.markdown(
                        f'<div class="source-card"><b>{d.source}</b> '
                        f'<span style="color:#9ca3af">· similarity {d.similarity:.2f}</span><br>'
                        f'<span style="color:#4b5563;font-size:0.85rem">{d.text[:280].strip()}…</span></div>',
                        unsafe_allow_html=True,
                    )
        if final_result:
            meta_box.caption(
                f"{final_result.latency_s:.1f}s · "
                f"{final_result.input_tokens + final_result.output_tokens} tokens · "
                f"≈ ${final_result.cost_usd:.4f}"
            )

    st.session_state.messages.append(
        {"role": "assistant", "content": answer_text, "sources": sources}
    )
