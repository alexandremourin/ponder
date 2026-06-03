# Self-RAG: Self-Reflective Retrieval-Augmented Generation

Self-RAG is a framework that trains a single language model to decide *when* to
retrieve, to *critique* what it retrieves, and to *critique its own output* —
using special **reflection tokens** generated inline during decoding.

Naive RAG always retrieves a fixed number of passages and always uses them, even
when retrieval is unnecessary or unhelpful. Self-RAG makes these decisions
adaptive. The model first predicts a **Retrieve** token deciding whether external
passages are needed for the current step. If so, it retrieves candidates and, for
each one, emits an **IsRelevant** reflection token judging whether the passage
supports the query.

When generating, the model emits **IsSupported** tokens indicating whether each
statement is actually grounded in the cited passage, and **IsUseful** tokens
scoring how well the overall response answers the question. These critique tokens
let the system rank candidate generations and prefer answers that are both
relevant and faithfully supported by evidence.

The payoff is twofold: the model retrieves only when it helps, and it can flag or
suppress claims that its own evidence does not support, reducing hallucination.
Self-RAG outperforms standard RAG and even larger instruction-tuned models on
several open-domain QA and fact-verification tasks.

Conceptually, Self-RAG established the idea that a RAG system should **judge its
own retrieval and generation** rather than trusting them blindly. Pipeline-level
implementations reproduce this with explicit grader and self-critique nodes
instead of trained reflection tokens.
