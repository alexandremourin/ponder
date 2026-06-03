# Corrective RAG (CRAG)

Corrective Retrieval-Augmented Generation (CRAG) adds a lightweight safety net to
RAG: a **retrieval evaluator** that scores how relevant the retrieved documents
are, followed by corrective actions when that confidence is low.

After retrieval, CRAG runs a small evaluator that assigns each retrieved document
a confidence score and then maps the overall result to one of three states:

- **Correct** — at least one document is clearly relevant. The system refines the
  retrieved text, decomposing it and keeping the key strips of information while
  discarding noise, then generates the answer.
- **Incorrect** — no document is relevant. The system discards the retrieved set
  entirely and instead performs a **web search** to find better external
  knowledge before generating.
- **Ambiguous** — the evaluator is unsure. CRAG hedges by combining both the
  refined internal documents and web-search results.

A recurring technique in CRAG is **decompose-then-recompose**: rather than feeding
whole noisy documents to the generator, it filters down to the relevant fragments,
which improves faithfulness.

CRAG is **plug-and-play**: it wraps around an existing RAG pipeline without
retraining the generator, and it can sit on top of both standard RAG and
Self-RAG. Its central lesson is that a RAG system should *measure its own
retrieval quality* and take corrective action — rewriting the query, searching
elsewhere, or filtering — instead of blindly trusting the first results. This
query-correction loop is the heart of "agentic" RAG.
