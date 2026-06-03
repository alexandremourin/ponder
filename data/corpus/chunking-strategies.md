# Chunking Strategies

Chunking is the process of splitting documents into smaller passages before
embedding them. It is a quiet but critical decision: chunks are the unit of
retrieval, so their size and boundaries shape what the system can find.

The core tension is **precision vs. context**. Small chunks embed tightly and
match queries precisely, but a single small chunk may not contain enough to answer
a question. Large chunks carry more context but dilute the embedding — the
relevant sentence is averaged together with surrounding noise, lowering similarity
and wasting context-window space.

Common strategies:

- **Fixed-size with overlap.** Split into windows of N characters or tokens with a
  partial overlap between consecutive chunks. The overlap prevents an answer from
  being split across a boundary. Simple and robust.
- **Sentence- or paragraph-aware.** Respect natural boundaries so a chunk never
  cuts a sentence in half, which keeps each chunk readable and self-contained.
- **Recursive splitting.** Try to split on large separators (headings, blank
  lines) first, falling back to smaller ones only when a piece is still too big.
- **Parent–child / small-to-big.** Embed small chunks for precise matching but, on
  a hit, return the larger parent passage to the generator for context.

A practical default is sentence-aware, fixed-size chunks of a few hundred to
roughly a thousand characters with a 10–20% overlap. Whatever the scheme, storing
the source file and position with each chunk is essential so retrieval can cite
its provenance.
