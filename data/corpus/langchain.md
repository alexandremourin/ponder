# LangChain

LangChain is a framework for developing applications powered by language models.
It provides standard interfaces and composable building blocks so developers can
swap models, vector stores, and tools without rewriting their application logic.

Its key abstractions include **chat models** (a uniform interface over providers
like Anthropic and OpenAI), **prompts** and prompt templates, **output parsers**
and structured output (binding a model's response to a schema), **retrievers**
(anything that returns relevant documents for a query), and **tools** (functions
the model can call).

LangChain popularized the idea of expressing pipelines declaratively. Components
share a common runnable interface so they can be piped together, batched, and
streamed consistently. A retriever can be combined with a prompt and a model to
produce a basic RAG chain in a few lines.

For simple, linear flows — embed, retrieve, stuff context, generate — a LangChain
chain is often enough. For anything with branching, looping, or self-correction,
the ecosystem points to LangGraph, which models the application as a stateful
graph rather than a straight line.

LangChain also provides integrations for observability and evaluation, document
loaders for many file formats, and text splitters for chunking. Its breadth makes
it a common starting point, while its standard interfaces make it easy to migrate
individual pieces — for example switching embedding models or vector stores — as
requirements change.
