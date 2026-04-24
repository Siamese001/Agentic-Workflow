"""LLM-based conversation summarizer — EQ-15 (ADR-PROMPT-ASSEMBLY-002 §7).

Pluggable backend for the EQ-8 compressor. When ``USE_LLM_SUMMARIZER=1``
is set, the compressor's call site may replace an evicted block of
messages with an LLM-generated summary instead of discarding them
outright.

Feature-flag gated and default-off. The rule-based EQ-8 compressor
remains the deterministic authority. Any failure in the LLM path
(``GatewayError``, timeout, bad response) falls back to rule-based
compression silently — the contract is "summarization is a best-
effort optimization, never a correctness hinge".

Architecture
------------
- :class:`Summarizer` is the protocol implementers must satisfy.
- :class:`NullSummarizer` returns a deterministic fixed string and is
  used when the LLM path is not available. Tests use it by default.
- :func:`summarize_or_fallback` is the safe-entry helper: it catches
  any exception from the injected summarizer and yields a fallback
  string. Callers never see raised errors from this module.
"""

from __future__ import annotations

import logging
import os
from typing import Protocol


_LOG = logging.getLogger(__name__)
_FLAG_ENV = "USE_LLM_SUMMARIZER"


def summarizer_enabled() -> bool:
    """True iff ``USE_LLM_SUMMARIZER`` is truthy in the environment."""
    return os.getenv(_FLAG_ENV, "").lower() in {"1", "true", "yes", "on"}


class Summarizer(Protocol):
    """Protocol for pluggable summarizer backends."""

    def summarize(self, messages: list[dict]) -> str:
        """Produce a single summary string for a block of messages."""
        ...


class NullSummarizer:
    """Default summarizer. Returns a deterministic placeholder."""

    name = "null"

    def summarize(self, messages: list[dict]) -> str:
        n = len(messages)
        return f"[summary placeholder — {n} message(s) elided]"


def summarize_or_fallback(
    messages: list[dict],
    *,
    summarizer: Summarizer | None = None,
    fallback: str = "[summary unavailable]",
) -> str:
    """Summarize ``messages`` via the injected backend, or fall back safely.

    Args:
        messages: Block of messages to summarize.
        summarizer: Optional backend. Defaults to :class:`NullSummarizer`
            which emits a deterministic placeholder — useful in tests
            and when LLM credentials are absent.
        fallback: String to return if the summarizer raises any
            exception. Default "[summary unavailable]".

    Returns:
        A string describing the content of ``messages``. Never raises.
    """
    if not summarizer_enabled():
        # Flag off — do not even invoke the backend. Callers get a
        # short tag so downstream code can still produce a valid
        # messages list if it wants to inline the summary.
        return "[summarizer disabled]"
    backend = summarizer or NullSummarizer()
    try:
        return backend.summarize(messages)
    except Exception as exc:  # noqa: BLE001 -- guardian: allow-broad-exception -- summarizer is a pluggable backend; contract guarantees summarize_or_fallback never raises, so ANY backend exception logs and returns the fallback string
        _LOG.warning("Summarizer backend failed (%s); falling back.", exc)
        return fallback


__all__ = [
    "Summarizer",
    "NullSummarizer",
    "summarize_or_fallback",
    "summarizer_enabled",
]
