# LLM-as-a-Judge

LLM-as-a-judge uses a capable language model to evaluate text outputs that are hard
to score automatically — answer correctness, helpfulness, faithfulness, style —
where exact-match metrics fail because there are many valid phrasings of a good
answer.

Three common setups exist. **Pointwise (reference-free) scoring** asks the judge to
rate a single output against a rubric. **Reference-based scoring** gives the judge a
gold answer to compare against, which is more reliable for factual correctness.
**Pairwise comparison** shows the judge two candidate outputs and asks which is
better, useful for ranking systems or models.

For RAG, a typical judge prompt provides the question, the retrieved context, the
gold answer, and the system's answer, then asks for a correctness or faithfulness
verdict — often as a discrete label or a 1–5 score with a short justification.
Requesting a structured verdict makes results easy to aggregate.

LLM judges correlate reasonably well with human ratings at far lower cost, which is
why they dominate RAG evaluation. But they have known biases: a **position bias**
(favoring the first option in pairwise tests), a **verbosity bias** (preferring
longer answers), and **self-preference** (favoring text from the same model
family). Mitigations include randomizing option order, giving an explicit rubric,
asking for reasoning before the verdict, and using a strong, neutral judge model.

Despite the caveats, LLM-as-a-judge is the practical default for measuring answer
quality at scale, especially when paired with a small human-checked sample to
validate the judge.
