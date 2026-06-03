# Streaming LLM Responses

Streaming is the technique of delivering a language model's output incrementally,
token by token, as it is generated, rather than waiting for the full completion.
Because models generate one token at a time, the partial output is available
immediately and can be shown to the user as it arrives.

The main benefit is perceived latency. A long answer might take many seconds to
finish, but with streaming the user sees the first words almost instantly and reads
along as the rest appears. The total time is unchanged, but the experience feels far
faster and more responsive — the difference between a frozen screen and a live one.

Technically, streaming is delivered over a persistent connection, commonly
**Server-Sent Events (SSE)** or chunked HTTP, where the server pushes a sequence of
partial chunks. Provider SDKs expose this as an iterator of deltas; UI frameworks
provide helpers to render a growing string.

In agentic systems, two things can stream. The **final answer** streams its tokens
for responsiveness. Just as valuable, the **reasoning process** can stream: as each
step of an agent runs — routing, retrieving, grading, rewriting, critiquing — the
system emits an event, letting the interface show a live timeline of what the agent
is doing and why. Graph frameworks support this by emitting state updates after
each node executes.

Streaming the reasoning, not just the answer, is what turns an opaque "thinking…"
spinner into a transparent, inspectable process the user can follow and trust.
