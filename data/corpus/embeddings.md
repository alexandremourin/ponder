# Text Embeddings

A text embedding is a dense vector of floating-point numbers that represents the
meaning of a piece of text. Texts with similar meaning map to nearby vectors, so
semantic similarity becomes a geometry problem: find the vectors closest to the
query's vector.

Modern embeddings come from neural encoders — typically transformer models
fine-tuned with contrastive learning, where the model is trained to pull
paraphrases together and push unrelated texts apart. The output dimensionality is
fixed (for example 384, 768, or 1536), regardless of input length.

Similarity between two embeddings is usually measured with **cosine similarity**,
the cosine of the angle between the vectors. If the vectors are L2-normalized to
unit length, cosine similarity equals the dot product, and Euclidean distance
becomes a monotonic function of it — so normalization makes the choice of metric
largely cosmetic.

Embedding quality is what ultimately limits a retrieval system: if the encoder
does not capture the distinctions that matter for your domain, no amount of clever
search will recover the right passages. This is why domain-appropriate models and
good chunking matter.

Embeddings can run locally with open models such as the BGE and E5 families, which
removes per-call API cost and keeps data on-premises, or through hosted APIs.
Local sentence-transformer models are small enough to run on CPU and are a common
choice for cost-free, private retrieval pipelines.
