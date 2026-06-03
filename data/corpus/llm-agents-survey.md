# LLM Agents: An Overview

An LLM agent is a system that uses a language model as its reasoning engine to
pursue a goal over multiple steps, deciding for itself which actions to take rather
than following a fixed script. A common decomposition describes an agent in terms
of four cooperating components.

**Profile / role.** The agent is given an identity, objective, and constraints —
usually via a system prompt — that shape how it behaves.

**Planning.** The agent breaks a goal into steps. Planning can be a single
upfront decomposition, or it can be iterative, with the agent re-planning as it
learns. Reflection techniques let the agent critique and revise its plan.

**Memory.** Short-term memory is the working context of the current task;
long-term memory persists facts and past experiences across tasks, typically in an
external store retrieved on demand. Memory is what lets an agent stay coherent
over long horizons.

**Tools / action.** The agent acts on the world through tools — search, code
execution, APIs, retrieval. Tool use turns a text predictor into something that
can gather information and cause effects.

The dominant execution pattern is a loop: observe the current state, reason about
what to do, take an action, observe the result, and repeat until the goal is met or
a limit is reached — the ReAct pattern.

Agents are powerful but introduce challenges: they can loop unproductively,
accumulate errors over long trajectories, and incur high cost from many model
calls. Bounding iterations, evaluating intermediate results, and keeping a human in
the loop for consequential actions are standard mitigations.
