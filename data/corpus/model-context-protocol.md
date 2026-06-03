# The Model Context Protocol (MCP)

The Model Context Protocol (MCP) is an open standard that lets AI applications
connect to external tools and data sources through a single, uniform interface.
Instead of writing a bespoke integration for every data source, an application
speaks one protocol and any compliant server can plug in. MCP is often described
as "a USB-C port for AI applications": one connector, many peripherals.

MCP follows a client–server design built on JSON-RPC 2.0. The **host** is the AI
application (for example a desktop assistant or an IDE). Inside the host runs one
or more **clients**, and each client maintains a one-to-one connection to a
**server**. A server exposes capabilities — tools to call, resources to read,
and prompt templates to reuse — and the client requests them on the model's
behalf.

The protocol defines a capability negotiation handshake at startup. The client
and server exchange the features they support so neither side assumes
functionality that is not present. After initialization, messages flow as
JSON-RPC requests, responses, and notifications.

MCP matters because it decouples model providers from tool builders. A company
can ship one MCP server for its internal knowledge base, and every MCP-aware
assistant can use it without custom glue code. This standardization is what makes
agentic systems composable: tools become reusable building blocks rather than
one-off plumbing. The specification is maintained as an open project with SDKs in
several languages, including Python and TypeScript.
