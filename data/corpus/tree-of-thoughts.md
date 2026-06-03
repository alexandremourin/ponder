# Tree of Thoughts

Tree of Thoughts (ToT) generalizes chain-of-thought reasoning from a single linear
trace into a **search over a tree of partial solutions**. Instead of committing to
one line of reasoning, the model explores several, evaluates them, and pursues the
most promising — with the ability to look ahead and backtrack.

The framework has four ingredients. **Thought decomposition** breaks the problem
into intermediate steps that each form a node. A **thought generator** proposes
several candidate next steps from a given node, branching the tree. A **state
evaluator** scores how promising each partial solution is, often by asking the
model to judge whether a branch can still lead to a solution. A **search
algorithm** — typically breadth-first or depth-first search — decides which nodes
to expand and when to prune or backtrack.

This deliberate, search-based approach helps on problems that require planning,
exploration, or where an early wrong move dooms a purely linear chain. The classic
demonstrations include puzzles like the Game of 24 and creative writing, where ToT
dramatically outperforms single-chain prompting.

The cost is many more model calls — generating and evaluating numerous branches —
so ToT trades compute for reliability on hard problems. Conceptually it reframes
problem-solving as search guided by the model's own evaluations, a theme that
recurs in agentic systems: generate candidates, score them, and keep only the
strong ones rather than trusting a single greedy path.
