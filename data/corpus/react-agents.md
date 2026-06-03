# ReAct: Reasoning and Acting in Language Models

ReAct is a prompting paradigm that interleaves **reasoning traces** with
**actions**, letting a language model both think and interact with external tools
within a single loop. The name is a contraction of "Reason + Act".

In a classic ReAct loop the model emits a repeating pattern: a **Thought** (free
-form reasoning about what to do next), an **Action** (a call to a tool, such as a
search query), and then receives an **Observation** (the tool's result) which is
appended to the context. The cycle repeats until the model decides it has enough
information and emits a final answer.

The key insight is that reasoning and acting reinforce each other. Pure
chain-of-thought reasoning can drift into hallucination because the model never
checks its assumptions against the world. Pure action without reasoning struggles
to plan multi-step tasks. By alternating the two, ReAct lets the model form a
plan, gather evidence, and revise the plan based on what it observes.

ReAct also improves interpretability and trust: the explicit thought trace shows
*why* the agent took each action, making failures easier to diagnose. On
knowledge-intensive benchmarks, ReAct-style agents that query a search tool
reduce hallucination compared with reasoning-only baselines, because each claim
can be grounded in a retrieved observation.

ReAct is the conceptual ancestor of most modern tool-using agents. Frameworks
that implement an "agent loop" — call a tool, observe, decide, repeat — are
applying the ReAct pattern, even when they wrap it in graph or function-calling
machinery.
