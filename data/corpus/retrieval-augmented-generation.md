# Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation combines a parametric language model with a
non-parametric memory — typically a searchable document collection — so the model
can ground its answers in external knowledge it was never trained on.

A standard RAG pipeline has two stages. First, **retrieval**: the user's query is
embedded and used to find the most similar passages in a vector store. Second,
**generation**: those passages are placed in the model's context window, and the
model is asked to answer using them. The result is an answer conditioned on
specific, citable evidence rather than on the model's memorized parameters alone.

RAG offers several advantages over relying on the model's weights. Knowledge can
be updated by changing the documents instead of retraining. Answers can cite their
sources, improving trust and verifiability. And smaller models become far more
capable when given the right context, lowering cost.

The classic weakness of naive RAG is that it makes a **single retrieval pass** and
then trusts whatever it found. If the search returns irrelevant or incomplete
passages, the model will often answer confidently anyway, producing a fluent but
wrong response. It has no mechanism to notice that its evidence is weak.

This limitation motivates *agentic* and *self-correcting* variants of RAG, which
add steps to evaluate the retrieved evidence, rewrite the query when results are
poor, and critique the final answer before returning it. RAG remains the dominant
pattern for building question-answering systems over private or fast-changing
data.
