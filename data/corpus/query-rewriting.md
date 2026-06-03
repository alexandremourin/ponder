# Query Rewriting for Retrieval

Query rewriting transforms a user's raw question into one or more queries that
retrieve better passages. It is one of the highest-leverage steps in a RAG
pipeline because retrieval quality caps the quality of every downstream answer.

Several rewriting strategies are common:

- **Normalization.** Fix spelling, expand abbreviations, and strip conversational
  filler so the query contains clean keywords and named entities.
- **Contextualization.** Resolve follow-up questions ("what about its pricing?")
  into self-contained queries using the conversation history, so retrieval does
  not depend on prior turns.
- **Decomposition.** Split a multi-part question into separate sub-queries, each
  retrieved independently, then combine the evidence.
- **Expansion / HyDE.** Add synonyms and related terms, or generate a hypothetical
  answer document and embed *that* to find similar real passages.
- **Feedback-driven rewriting.** The most powerful variant: after a retrieval
  attempt is judged insufficient, rewrite the query to target exactly what was
  missing, then search again. This closes a loop between evaluation and retrieval.

The first four happen up front, before any search. Feedback-driven rewriting is
*reactive*: it uses signal from a grader about why the last results were weak. A
blind upfront rewrite has no such signal and can only guess; a feedback-driven
rewrite is corrective and tends to converge faster on the right passages.

Bounding the number of rewrite cycles is essential to keep latency and cost under
control and to guarantee the loop terminates.
