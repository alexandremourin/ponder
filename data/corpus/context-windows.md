# Context Windows

The context window is the maximum amount of text — measured in tokens — that a
language model can attend to at once, spanning both the input prompt and the
generated output. It is a hard budget: everything the model "knows" during a single
call must fit inside it.

Context windows have grown from a few thousand tokens to hundreds of thousands, but
larger is not a free lunch. Cost and latency scale with the number of tokens
processed, so stuffing a huge context is expensive. More subtly, models exhibit a
**"lost in the middle"** effect: they attend most reliably to information at the
beginning and end of a long context and can overlook material buried in the
middle. Simply dumping more text does not guarantee the model will use it.

These realities shape RAG design. Rather than feeding an entire corpus, RAG
retrieves only the most relevant passages and places them in the window — keeping
the prompt small, cheap, and focused. Re-ranking matters because the few best
passages should occupy the most-attended positions. Chunking matters because it
controls how much of the budget each retrieved unit consumes.

For long conversations, the window also forces **context management**: older turns
are summarized or dropped to make room, and details are offloaded to external
memory that can be retrieved on demand.

The practical principle is that context is a scarce resource to be curated, not
filled. A focused, well-ordered context of relevant evidence usually beats a larger
but noisier one — even when the larger one would technically fit.
