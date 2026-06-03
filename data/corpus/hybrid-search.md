# Hybrid Search

Hybrid search combines **dense** (vector) retrieval with **sparse** (keyword)
retrieval to get the strengths of both. Each method fails in ways the other
covers, so fusing them is more robust than either alone.

Dense retrieval matches on **meaning**: it finds passages that are semantically
similar to the query even when they share no words, which is great for synonyms
and paraphrase. Its weakness is exact terms — rare identifiers, product codes,
acronyms, or proper nouns — which can be smoothed away in the embedding.

Sparse retrieval, classically **BM25**, matches on **terms**: it ranks documents
by weighted word overlap, rewarding rare query terms and penalizing very common
ones. It nails exact-match needs like error codes or specific names but misses
synonyms and rephrasings entirely.

Hybrid search runs both and merges the results. A common, calibration-free merge
is **Reciprocal Rank Fusion**, which combines the two ranked lists using rank
positions rather than incomparable raw scores. Alternatively, scores can be
normalized and linearly weighted.

The practical takeaway: for queries dominated by natural language, dense retrieval
usually wins; for queries containing exact tokens that must appear, keyword
retrieval is essential. Many production RAG systems default to hybrid because real
user queries mix both. Hybrid retrieval is frequently paired with a re-ranking
stage that re-scores the merged candidate pool for final precision.
