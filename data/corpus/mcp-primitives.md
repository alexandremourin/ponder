# MCP Primitives: Tools, Resources, and Prompts

MCP servers expose three core primitives, plus two client-side features.

**Tools** are functions the model can invoke to take an action or fetch live
data — querying a database, calling an API, sending a message. Each tool has a
name, a human-readable description, and a JSON Schema describing its arguments.
Tools are *model-controlled*: the language model decides when to call them, much
like classic function calling.

**Resources** are read-only pieces of context the server makes available, such as
files, database rows, or documents. Each resource is identified by a URI.
Resources are *application-controlled*: the host decides which ones to load into
context, rather than the model invoking them.

**Prompts** are reusable, parameterized message templates the server offers — for
example a "summarize this ticket" template. Prompts are *user-controlled*: they
typically surface as slash commands or menu items the user picks.

On the client side, MCP defines **sampling**, which lets a server ask the host's
model to generate a completion (enabling agentic servers without their own LLM
key), and **roots**, which tell a server the file-system or URI boundaries it is
allowed to operate within.

The distinction of who controls each primitive — model, application, or user — is
deliberate. It keeps dangerous actions gated and makes the system predictable:
the model can request actions through tools, but humans and the host application
retain control over what context is exposed and what the server may touch.
