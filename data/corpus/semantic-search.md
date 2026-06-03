# Semantic Search

Semantic search retrieves results by **meaning** rather than by exact keyword
overlap. A query and the documents are mapped into the same embedding space, and
the system returns the documents whose vectors are closest to the query's vector.

This differs fundamentally from lexical search. A keyword engine looking for "car"
will miss a document that only says "automobile"; a semantic engine places the two
near each other because they mean the same thing. Semantic search therefore
handles synonyms, paraphrase, and natural-language questions gracefully, which is
why it underpins modern question-answering and RAG.

The pipeline has two phases. **Indexing** (offline): split documents into chunks,
embed each chunk, and store the vectors in a vector database. **Querying**
(online): embed the incoming query and run a nearest-neighbor search to fetch the
top matches. Approximate nearest-neighbor indexes such as HNSW keep this fast even
over large collections.

Semantic search has weaknesses too. It can under-weight rare exact tokens — codes,
identifiers, proper nouns — that a keyword search would nail, and its quality is
capped by the embedding model's understanding of the domain. These gaps are exactly
why hybrid search combines semantic and keyword retrieval.

For most natural-language corpora, semantic search is the right default: it matches
how users actually phrase questions, and it returns passages a generator can use to
produce grounded, citable answers.
