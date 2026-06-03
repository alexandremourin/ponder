# RAG-Fusion and Reciprocal Rank Fusion

RAG-Fusion improves retrieval by generating **multiple query variations** from a
single user question, retrieving for each, and then merging the ranked result
lists into one. The intuition is that any single phrasing of a query may miss
relevant passages, but a diverse set of phrasings collectively covers the
information need far better.

The merge step uses **Reciprocal Rank Fusion (RRF)**, a simple and robust
algorithm for combining ranked lists. Each document receives a score of the form
1 / (k + rank) summed across every list in which it appears, where rank is the
document's position in that list and k is a small constant (commonly 60). RRF
rewards documents that rank highly across *several* queries, so passages that
consistently surface rise to the top while one-off hits sink.

RRF is attractive because it needs no score calibration: it works on ranks alone,
so it can fuse results from heterogeneous retrievers — for example a dense vector
search and a keyword search — that produce incomparable raw scores.

RAG-Fusion is especially helpful for vague or under-specified questions, where the
"right" phrasing is unclear. The cost is extra LLM calls to generate the query
variants and extra retrieval calls, so it is a latency-for-recall trade. It pairs
naturally with re-ranking: fuse first to gather a strong candidate pool, then
re-rank with a cross-encoder for final precision.
