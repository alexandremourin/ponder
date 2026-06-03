# Fine-Tuning vs. RAG

Fine-tuning and retrieval-augmented generation are two ways to adapt a base model
to a specific domain, and they solve different problems. Choosing well — or
combining them — depends on whether the challenge is *knowledge* or *behavior*.

**RAG injects knowledge at inference time.** Facts live in an external store and
are retrieved into the prompt as needed. Its strengths: knowledge updates instantly
by editing documents (no retraining), answers can cite sources, and it is cheaper
to maintain. Its limits: it depends on retrieval quality, consumes context-window
space, and adds retrieval latency. RAG is the right tool when the knowledge is
large, changes often, or must be attributable.

**Fine-tuning bakes patterns into the weights.** By training on examples, you shift
the model's behavior — its format, tone, style, or skill at a narrow task — and can
teach domain vocabulary. Its strengths: no retrieval step at inference and reliable
adherence to a desired output style. Its limits: knowledge is frozen at training
time, updates require retraining, it risks forgetting general abilities, and it
offers no citations. Fine-tuning is the right tool when you need consistent
*behavior* rather than fresh *facts*.

The two are complementary, not rivals. A common production recipe fine-tunes a
model for the desired format and domain style, then uses RAG to supply current,
citable facts at query time. As a rule of thumb: use RAG for what the model should
*know*, and fine-tuning for how the model should *act*.
