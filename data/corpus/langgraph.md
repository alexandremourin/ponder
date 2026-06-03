# LangGraph: Building Agents as Graphs

LangGraph is a library for building stateful, multi-step LLM applications as
**graphs**. Where a simple chain runs steps in a fixed line, a graph can branch,
loop, and revisit earlier steps — exactly the control flow agentic systems need.

The core abstractions are:

- **State.** A typed, shared data structure (often a `TypedDict`) that every node
  reads from and writes to. State channels can have **reducers** that define how
  updates merge — for example appending to a list instead of overwriting it.
- **Nodes.** Plain functions that take the current state and return a partial
  update. A node typically does one job: call the model, run a tool, grade
  results.
- **Edges.** Connections between nodes. **Normal edges** always go from A to B.
  **Conditional edges** call a routing function that inspects the state and
  returns the name of the next node, enabling branching and loops.

A graph is defined by adding nodes and edges, then **compiled** into a runnable.
You start at a special `START` node and finish at `END`.

LangGraph adds production features on top: **checkpointers** persist state so a
run can be paused, resumed, or rewound; **interrupts** let a human approve a step
before it executes; and **streaming** emits state updates as each node runs, which
is what lets a UI show a live reasoning timeline.

Because the control flow is explicit and inspectable, LangGraph is well suited to
corrective and self-reflective agents that loop back to retrieval or regenerate an
answer based on a critique.
