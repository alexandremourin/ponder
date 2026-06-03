# Chroma: An Embedded Vector Store

Chroma is an open-source vector database designed to be simple to embed directly
in an application. It is a popular choice for local development and for small to
medium RAG systems because it requires no separate server to get started.

The central concept in Chroma is a **collection**: a named set of documents, each
stored with an id, the original text, an embedding vector, and an optional
metadata dictionary. You add records with `add` (supplying your own embeddings or
letting Chroma compute them) and query with `query`, which returns the nearest
records along with their documents, metadata, and distances.

Chroma can run purely in memory or as a **PersistentClient** that writes the
index to a directory on disk, so the collection survives process restarts without
re-embedding. The distance metric is configurable; for normalized embeddings,
cosine space is typical, and the returned distance can be converted to a 0-to-1
similarity as `1 - distance`.

Metadata stored with each chunk — such as the source file name and chunk index —
is what lets a retrieval layer return citable provenance rather than anonymous
text. Metadata can also be used to filter queries.

Because the API is small and the persistence story is explicit, Chroma fits the
"runs out of the box, no infrastructure" requirement of local agentic RAG demos,
while still scaling to tens of thousands of chunks on a laptop.
