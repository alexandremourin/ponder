# HNSW: Hierarchical Navigable Small World Graphs

HNSW is one of the most widely used algorithms for **approximate nearest-neighbor
(ANN)** search and powers the indexes inside many vector databases. It delivers
high recall with logarithmic-scale query time, which is why it has become a
default.

The structure is a multi-layer graph. Each stored vector is a node connected to a
few of its nearest neighbors. Upper layers contain a sparse subset of nodes with
long-range links; lower layers are denser, and the bottom layer contains every
node. Searching starts at an entry point in the top layer and **greedily hops**
toward the query, descending a layer each time it can no longer get closer. The
sparse upper layers let the search cover large distances quickly, while the dense
bottom layer refines to the true neighbors — the same idea as a skip list applied
to a proximity graph.

Two parameters dominate behavior. **M** controls how many neighbors each node
keeps, affecting graph connectivity and memory. **ef** (search breadth) controls
how many candidates are explored at query time: higher ef means better recall but
slower queries. A separate `ef_construction` governs index build quality.

HNSW's trade-offs: it is memory-resident and insertion is incremental but
relatively expensive, while queries are very fast and accurate. For the corpus
sizes typical of a local RAG system — thousands to hundreds of thousands of chunks
— HNSW comfortably returns the right passages in milliseconds, making it a
practical default index.
