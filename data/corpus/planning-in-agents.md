# Planning in LLM Agents

Planning is how an agent turns a high-level goal into an ordered set of steps it
can execute. The quality of planning largely determines whether an agent can
handle tasks that require more than one action.

Approaches fall on a spectrum. **Decomposition-first** planning generates the full
plan up front, then executes it step by step; this is simple and cheap but brittle
when the world does not match the plan. **Interleaved** planning alternates
planning and acting, so the agent adjusts its next step based on what it just
observed — the ReAct style. **Plan-and-solve** sits between them: draft a plan,
then execute while allowing revision.

Several techniques strengthen planning. **Task decomposition** splits a goal into
sub-goals that can be solved independently and recombined. **Reflection** lets the
agent critique its progress and revise the plan when it stalls. **Tree search**
(as in Tree of Thoughts) explores multiple plans and prunes weak ones. Some
systems separate a dedicated *planner* model from one or more *executor* models.

The hardest problems are **error recovery** and **long horizons**: small mistakes
compound across many steps, and the agent must notice when a plan is failing and
re-plan rather than pushing on. Self-evaluation — checking whether a step actually
achieved its sub-goal — is what makes recovery possible.

In retrieval settings, planning shows up as deciding what to search for, in what
order, and when enough evidence has been gathered to answer — the same loop a
corrective RAG agent runs when it grades results and rewrites its query.
