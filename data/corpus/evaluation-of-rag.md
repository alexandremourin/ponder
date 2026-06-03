# Evaluating RAG Systems

A RAG system has two stages to evaluate — **retrieval** and **generation** — and
measuring them separately is essential, because a great generator cannot rescue bad
retrieval and good retrieval is wasted by a careless generator.

**Retrieval metrics** judge whether the right passages were fetched. They need a
labeled set of queries with their relevant documents (the "gold" set).

- **Recall@k** measures the fraction of relevant documents that appear in the top
  k results. It answers: did we surface the evidence at all? High recall@k is the
  precondition for a correct answer.
- **Precision@k** measures how many of the top k results are actually relevant.
- **MRR** (mean reciprocal rank) and **nDCG** reward placing relevant documents
  higher in the ranking, not just including them.

**Generation metrics** judge the answer given the retrieved context.

- **Faithfulness / groundedness**: are the answer's claims supported by the
  retrieved passages, with no hallucination?
- **Answer relevance / correctness**: does the answer actually address the
  question, and does it match a reference answer?

Because these qualities are hard to score with string matching, **LLM-as-a-judge**
is widely used to rate faithfulness and correctness. Frameworks such as RAGAS
package these metrics together.

Beyond quality, production evaluation tracks **operational metrics**: latency per
query and cost per query (driven by token usage and the number of LLM calls). A
self-correcting agent improves quality by making more calls, so reporting latency
and cost alongside accuracy is the only honest way to show the trade-off.
