# Function Calling / Tool Use

Function calling (also called tool use) is the mechanism by which a language model
invokes external code in a structured way. The model does not run the function
itself; it emits a structured request — a function name plus JSON arguments — and
the application executes the function and returns the result for the model to use.

The developer supplies a list of available tools, each described by a name, a
purpose, and a **JSON Schema** for its parameters. When the model decides a tool is
needed, it produces arguments conforming to that schema. The runtime calls the
function, appends the result to the conversation, and lets the model continue,
often calling more tools before producing a final answer.

This pattern is what makes models *agentic*: it bridges the gap between a text
predictor and systems that can search, compute, query databases, or take actions.
It also enforces structure — because arguments must match a schema, the model's
output is machine-parseable rather than free text.

Reliable function calling depends on clear tool descriptions and well-specified
schemas; ambiguous descriptions lead to wrong tool choice or malformed arguments.
Models may also call several tools in parallel, or in sequence where each call
depends on the previous result.

Function calling is the low-level primitive beneath higher-level standards: the
Model Context Protocol's *tools* are function calls exposed over a uniform
protocol, and ReAct-style agent loops are essentially repeated function calling
interleaved with reasoning. Structured output — binding a response to a schema
without an external call — uses the same underlying capability.
