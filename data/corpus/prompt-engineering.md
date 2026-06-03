# Prompt Engineering

Prompt engineering is the practice of designing the text given to a language model
so it produces the desired output reliably. Because a model's behavior is steered
almost entirely by its input, small changes in wording, structure, and examples can
make a large difference in quality.

Core techniques include:

- **Clear instructions and role-setting.** State the task, the desired format, and
  any constraints explicitly. A system prompt that assigns a role ("you are a
  careful research assistant") sets consistent behavior.
- **Few-shot examples.** Showing a handful of input–output pairs teaches the
  format and the standard better than description alone.
- **Chain-of-thought.** Asking the model to reason step by step before answering
  improves accuracy on multi-step problems.
- **Decomposition.** Breaking a complex task into smaller, separately prompted
  steps is more reliable than one giant instruction.
- **Output constraints.** Requesting a specific structure — JSON, a schema, a
  fixed set of labels — makes results parseable and reduces drift.

Good prompts also handle failure: instruct the model on what to do when it is
unsure (for example, "say you don't know rather than guess"), which is critical for
grounded, low-hallucination RAG answers.

In agentic systems, prompts define each node's job: the router's classification
rules, the grader's relevance criteria, the generator's citation requirements, the
critic's evaluation rubric. Well-scoped, single-purpose prompts per step are easier
to tune and debug than one sprawling prompt trying to do everything at once.
