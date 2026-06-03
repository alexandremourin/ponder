# Guardrails for LLM Applications

Guardrails are the controls placed around a language model to keep its inputs and
outputs safe, on-topic, and well-formed. Because a model will generate whatever its
prompt leads to, production systems wrap it in checks rather than trusting it
unconditionally.

Guardrails operate at two points. **Input guardrails** inspect the user's request
before it reaches the model: detecting prompt-injection attempts, blocking
off-topic or disallowed requests, redacting sensitive data, and enforcing rate
limits. **Output guardrails** inspect the model's response before it reaches the
user or triggers an action: checking for policy violations, validating that
structured output matches its schema, verifying that claims are grounded in
provided sources, and filtering unsafe content.

Common mechanisms include rule-based filters and regexes, classifier models that
score content for safety or topicality, schema validators for structured output,
and a second LLM acting as a checker. For agents that take actions, a crucial
guardrail is **human-in-the-loop confirmation** for consequential or irreversible
operations.

In RAG, a particularly important guardrail is **groundedness checking**: verifying
that the answer's claims are supported by the retrieved passages and refusing or
flagging when they are not. This is the self-critique step turned into a safety
control, and it directly attacks faithfulness hallucination.

The guiding principle is defense in depth: no single check is perfect, so layering
input filters, output validation, and human oversight produces a system that fails
safe rather than confidently doing the wrong thing.
