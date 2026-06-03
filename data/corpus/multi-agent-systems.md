# Multi-Agent Systems

A multi-agent system coordinates several specialized LLM agents to solve a task
that would be unwieldy for one. Each agent has a focused role, and their
interaction produces the final result. The bet is that decomposition plus
specialization beats a single generalist agent juggling everything in one context.

Common organizational patterns include:

- **Supervisor / orchestrator.** A central agent decomposes the task and delegates
  sub-tasks to worker agents, then integrates their outputs. Control is
  hierarchical and easy to reason about.
- **Pipeline.** Agents are arranged in a sequence, each transforming the previous
  one's output — for example research, then draft, then critique.
- **Debate / collaboration.** Multiple agents propose and challenge each other's
  answers, surfacing errors that a single agent might miss.

Specialization helps for several reasons: each agent's prompt and tools can be
tuned for its narrow job, contexts stay smaller and cheaper, and roles like
"critic" or "verifier" naturally catch mistakes — echoing the self-critique idea
at the level of separate agents.

The costs are real: more agents mean more LLM calls (higher latency and price),
coordination overhead, and new failure modes where agents miscommunicate or loop.
Clear interfaces between agents, bounded interaction rounds, and a single
integrator for the final answer keep these systems manageable.

A RAG pipeline with distinct router, grader, and critique steps can be viewed as a
lightweight multi-agent system: each step is a specialist, even if they share one
underlying model.
