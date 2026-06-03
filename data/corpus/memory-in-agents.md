# Memory in LLM Agents

Memory lets an agent stay coherent across a task and across sessions. Because a
language model is stateless between calls and limited by its context window,
durable memory must be managed explicitly by the surrounding system.

Two kinds are usually distinguished. **Short-term (working) memory** is the
information held in the current context window: the conversation so far,
intermediate results, and recently retrieved passages. It is fast to access but
bounded, so it must be curated — often by summarizing older turns to make room.

**Long-term memory** persists beyond the context window in an external store, most
commonly a vector database. Relevant memories are retrieved on demand by embedding
the current situation and searching for similar past entries — the same mechanism
as RAG, applied to the agent's own history. Long-term memory can hold facts the
agent learned, user preferences, and reflections on past successes and failures.

A common pattern is **summarize-and-store**: as the conversation grows, compress
old context into a concise summary that stays in working memory, while archiving
details to long-term storage that can be retrieved if needed later. This keeps the
active context small and cheap while preserving recall.

Memory design involves trade-offs: what to remember, when to retrieve, and how to
avoid polluting context with stale or irrelevant entries. Done well, it is what
separates a one-shot question-answerer from an agent that improves over a long
interaction and carries lessons forward, as in the Reflexion framework.
