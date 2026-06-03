# Chain-of-Thought Prompting

Chain-of-thought (CoT) prompting elicits step-by-step reasoning from a language
model by encouraging it to "think out loud" before giving a final answer. On
multi-step problems — arithmetic, logic, commonsense reasoning — generating
intermediate steps substantially improves accuracy over answering directly.

The mechanism is simple but effective. A model asked to jump straight to an answer
must compute everything in a single forward pass. By emitting intermediate steps,
the model spreads the computation across many tokens, with each step conditioning
the next. The reasoning trace becomes a scratchpad.

CoT can be triggered in two ways. **Few-shot CoT** includes a handful of worked
examples in the prompt that show the reasoning format. **Zero-shot CoT** simply
appends a cue such as "Let's think step by step", which is enough to unlock
reasoning in capable models without any examples.

An important finding is that CoT is an **emergent ability**: it helps large models
but can actually hurt very small ones, which produce plausible-looking but flawed
reasoning. The benefit grows with model scale.

CoT also improves interpretability, since the trace shows how the model reached
its conclusion — though the stated reasoning is not always a faithful account of
the true computation. CoT is the foundation that later methods build on:
self-consistency samples many chains and votes; tree-of-thoughts explores chains
as a search tree; and ReAct interleaves reasoning with tool actions.
