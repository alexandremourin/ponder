# BGE Embedding Models

BGE (BAAI General Embedding) is a family of open-source text-embedding models from
the Beijing Academy of Artificial Intelligence. They are widely used for
retrieval because they offer strong quality at small sizes and can run locally for
free.

The family spans several sizes. **bge-small-en-v1.5** produces 384-dimensional
vectors and is fast enough to run comfortably on CPU; **bge-base** and
**bge-large** produce 768- and 1024-dimensional vectors with higher quality at the
cost of speed and memory. The "v1.5" releases improved similarity-score
distribution over the originals.

A practical detail specific to BGE: for retrieval you should prepend a short
**instruction prefix to the query** — "Represent this sentence for searching
relevant passages:" — while leaving the documents unprefixed. This asymmetry
matches how the models were trained and measurably improves retrieval. Embeddings
are typically L2-normalized so that cosine similarity reduces to a dot product.

BGE models integrate cleanly with the sentence-transformers library: load the
model by name, call `encode` on a list of texts, and request normalized
embeddings. Because everything runs on-device, there is no API key, no per-token
cost, and no data leaving the machine — attractive properties for private corpora
and for keeping a demo runnable out of the box.

For most retrieval workloads bge-small offers the best quality-per-millisecond,
making it a sensible default before reaching for larger or hosted models.
