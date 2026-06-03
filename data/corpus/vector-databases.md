# Vector Databases

A vector database stores high-dimensional embeddings and answers
**nearest-neighbor** queries: given a query vector, return the stored vectors most
similar to it. They are the storage layer that makes semantic search and RAG
practical at scale.

Exact nearest-neighbor search becomes too slow as a collection grows, so vector
databases use **Approximate Nearest Neighbor (ANN)** indexes that trade a tiny
amount of recall for large speedups. Common index types include HNSW
(graph-based), IVF (inverted file with clustering), and product quantization for
compression.

Beyond raw search, a vector database typically provides: **metadata filtering**,
so a query can be restricted to documents matching structured fields (date,
author, tags); **upserts and deletes**, so the index stays fresh as documents
change; **persistence**, so the index survives restarts; and a choice of distance
metric (cosine, dot product, or Euclidean).

A key design decision is **what to store alongside each vector** — usually the
source text and metadata — so that retrieval returns not just an id but the
passage and its provenance, which the generator needs for citations.

Options range from embedded, file-backed stores such as Chroma and FAISS, ideal
for local development and small to medium corpora, to managed services built for
billions of vectors. For a local, key-free RAG pipeline, an embedded store that
persists to disk is usually the simplest choice that still scales to tens of
thousands of chunks.
