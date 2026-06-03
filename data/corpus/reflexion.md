# Reflexion: Agents That Learn From Their Mistakes

Reflexion is a framework that gives language-model agents a form of **verbal
reinforcement learning**. Instead of updating model weights, the agent improves by
writing reflective feedback about its own failures and storing that feedback in
memory to guide future attempts.

The loop works in three parts. An **Actor** attempts a task and produces a
trajectory of actions. An **Evaluator** scores the outcome — this can be an exact
-match check, a unit test, or a heuristic. A **Self-Reflection** module then reads
the failed trajectory and the evaluation signal and writes a short natural-language
critique: what went wrong and what to try differently. This critique is appended
to an episodic memory buffer.

On the next attempt the agent sees its previous reflections, so it can avoid
repeating mistakes. Because the feedback is verbal rather than a gradient, no
fine-tuning is required and the lessons are human-readable.

Reflexion shows large gains on tasks with a clear success signal, such as coding
problems where unit tests provide ground truth, and decision-making environments
where the agent can retry. The approach is most effective when reflections are
specific and actionable rather than vague.

Reflexion popularized the idea that an agent's **self-critique can be a first
-class component** of the loop. Many later systems, including self-correcting RAG
pipelines, borrow this pattern: generate, evaluate, reflect, and retry with the
lessons learned carried forward.
