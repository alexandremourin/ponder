# MCP Architecture and Transports

An MCP deployment has three roles. The **host** is the user-facing AI
application that holds the language model and orchestrates everything. The host
spawns **clients**, lightweight connectors that each own a single session with a
server. **Servers** are separate processes that expose capabilities; they can be
local programs or remote services.

Communication runs over JSON-RPC 2.0. MCP defines two standard transports. The
**stdio** transport launches the server as a subprocess and exchanges messages
over standard input and output; it is ideal for local tools because it is simple
and has no network surface. The **streamable HTTP** transport (which superseded
the earlier HTTP+SSE transport) is used for remote servers; the server is reached
over HTTP and can stream multiple messages back to the client using
Server-Sent Events.

The session lifecycle begins with an `initialize` request in which client and
server negotiate protocol version and capabilities. Once initialized, either side
may send requests and notifications. Requests expect a matching response keyed by
an id; notifications are fire-and-forget.

Keeping each client bound to exactly one server connection keeps security
boundaries clear: a host can grant or revoke access per server, and a misbehaving
server cannot reach beyond its own session. This isolation, combined with the
stdio option for purely local tools, is a core reason MCP is considered safe to
adopt inside enterprises.
