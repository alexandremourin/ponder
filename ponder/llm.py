"""LLM factory + lightweight usage tracking.

Anthropic Claude is the primary provider. If only ``OPENAI_API_KEY`` is set we
fall back to OpenAI automatically. A process-wide ``UsageTracker`` accumulates
token counts so ``eval.py`` can report an honest cost-per-query figure.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from .config import (
    ANTHROPIC_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    OPENAI_MODEL,
    PRICING,
    active_provider,
)


class MissingAPIKey(RuntimeError):
    """Raised when no LLM provider key is configured."""


@dataclass
class UsageTracker:
    """Accumulates token usage and derived cost across LLM calls."""

    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0

    def add(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens += int(input_tokens or 0)
        self.output_tokens += int(output_tokens or 0)
        self.calls += 1

    @property
    def cost_usd(self) -> float:
        price = PRICING.get(self.model)
        if not price:
            return 0.0
        return (
            self.input_tokens / 1_000_000 * price.input_per_mtok
            + self.output_tokens / 1_000_000 * price.output_per_mtok
        )

    def reset(self) -> None:
        self.input_tokens = self.output_tokens = self.calls = 0


# A single shared tracker the whole pipeline reports into.
USAGE = UsageTracker()


def _record_usage(response) -> None:
    """Pull token usage out of a LangChain AIMessage, provider-agnostic."""
    meta = getattr(response, "usage_metadata", None) or {}
    if meta:
        USAGE.add(meta.get("input_tokens", 0), meta.get("output_tokens", 0))
        return
    # Fallback path for providers that stash usage elsewhere.
    rmeta = getattr(response, "response_metadata", {}) or {}
    usage = rmeta.get("usage") or rmeta.get("token_usage") or {}
    USAGE.add(
        usage.get("input_tokens") or usage.get("prompt_tokens", 0),
        usage.get("output_tokens") or usage.get("completion_tokens", 0),
    )


def get_llm(temperature: float | None = None, max_tokens: int | None = None):
    """Return a configured LangChain chat model for the available provider.

    Raises ``MissingAPIKey`` if neither provider key is present so callers can
    show a friendly message instead of crashing deep in a graph node.
    """
    provider = active_provider()
    temp = LLM_TEMPERATURE if temperature is None else temperature
    max_tok = LLM_MAX_TOKENS if max_tokens is None else max_tokens

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        USAGE.model = ANTHROPIC_MODEL
        return ChatAnthropic(
            model=ANTHROPIC_MODEL,
            temperature=temp,
            max_tokens=max_tok,
            timeout=60,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        USAGE.model = OPENAI_MODEL
        return ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=temp,
            max_tokens=max_tok,
            timeout=60,
        )

    raise MissingAPIKey(
        "No LLM key found. Add ANTHROPIC_API_KEY (or OPENAI_API_KEY) to your .env file."
    )


def invoke(llm, messages):
    """Invoke an LLM and record token usage in one place."""
    response = llm.invoke(messages)
    _record_usage(response)
    return response
