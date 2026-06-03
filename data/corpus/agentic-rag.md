# Agentic RAG

Agentic RAG describes retrieval-augmented systems where an autonomous agent — not
a fixed pipeline — drives the retrieval process. Rather than running a single
"embed, search, generate" pass, the agent reasons about the question, plans how to
gather evidence, and adapts based on what it finds.

The defining traits of agentic RAG are:

- **Routing.** The agent first decides how to handle a query: answer directly,
  retrieve from one corpus, query several sources, or call a tool.
- **Iterative retrieval.** Instead of one search, the agent can search multiple
  times, refining its query as it learns what is missing.
- **Self-evaluation.** The agent grades whether retrieved passages are relevant
  and whether they are sufficient, gating generation on the answer.
- **Query rewriting.** When evidence is weak, the agent rewrites the query —
  adding synonyms, narrowing scope, or targeting the specific gap — and searches
  again.
- **Self-correction.** After drafting an answer, the agent critiques it for
  grounding and completeness and can loop back for another corrective cycle.

These behaviors are usually implemented as a state machine or graph, where nodes
are reasoning steps and edges encode the control flow, including loops back to
retrieval. This makes the agent's decisions explicit and inspectable.

Agentic RAG trades latency and cost (more LLM calls) for reliability: by checking
its own work, the system catches the failure mode of naive RAG — answering
confidently from bad evidence. It shines on complex, multi-hop questions and on
high-stakes domains where a wrong-but-fluent answer is worse than a slower,
verified one.
