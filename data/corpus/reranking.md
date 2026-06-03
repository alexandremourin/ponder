# Re-ranking with Cross-Encoders

Re-ranking is a second retrieval stage that re-scores an initial candidate set for
precision. The pattern is **retrieve-then-rerank**: a fast retriever fetches a
broad pool of candidates (say the top 50), and a slower but more accurate model
reorders them so the best few rise to the top before they enter the generator's
context.

The quality gap comes from architecture. The first-stage retriever is a
**bi-encoder**: it embeds the query and each document *independently*, so document
vectors can be precomputed and searched quickly — but the query and document never
directly interact, limiting precision. A **cross-encoder** instead feeds the query
and a candidate document *together* through a transformer and outputs a single
relevance score. Because every query token can attend to every document token, it
judges relevance far more accurately.

The cost is that cross-encoders cannot be precomputed: every query-document pair
must be scored at query time. That is too slow to run over a whole corpus, which is
exactly why re-ranking is applied only to a small candidate set produced by the
fast first stage.

Re-ranking is one of the cheapest reliable ways to improve answer quality, because
it directly raises the relevance of the passages the generator actually sees. It
composes naturally with hybrid search and RAG-Fusion: gather a strong, diverse
candidate pool first, then let the cross-encoder pick the true best passages.
