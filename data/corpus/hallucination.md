# Hallucination in Language Models

A hallucination is content a language model produces that is fluent and confident
but factually wrong or unsupported. Because models are trained to predict
plausible text, they will happily fill gaps with invented details rather than admit
uncertainty.

It helps to distinguish two types. **Factuality hallucination** is output that
contradicts real-world facts. **Faithfulness hallucination** is output that
contradicts or is unsupported by the *provided source* — the central risk in RAG,
where the model may stray from the retrieved passages and assert things they do not
say.

Causes include gaps in training data, over-generalization, outdated parametric
knowledge, and prompts that pressure the model to answer even when it lacks
grounds. In RAG specifically, hallucination spikes when retrieval returns
irrelevant or insufficient passages but the model answers anyway.

Mitigations fall into a few families. **Grounding** with retrieval gives the model
real evidence to cite. **Instructions to abstain** — telling the model to say "I
don't know" when the context lacks the answer — reduce confident guessing.
**Citations** force claims to be tied to sources and make errors auditable.
**Self-verification**, where the model or a separate critic checks each claim
against the evidence, catches unsupported statements before they reach the user.

Self-correcting RAG attacks the problem at both ends: grading retrieved passages so
the generator works from relevant evidence, and critiquing the draft answer for
groundedness so unsupported claims trigger a retry rather than a confident,
wrong response.
