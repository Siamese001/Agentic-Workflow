"""Deterministic history compressor — EQ-8 (ADR-PROMPT-ASSEMBLY-002 §7, §8).

Rolling-window + oldest-first eviction under a token budget. The
compressor is **deterministic**: same input history + budget produces
byte-identical output across runs. This is the property downstream
replay / cache-key stability depends on.

Feature-flag
------------
Gated by ``USE_DETERMINISTIC_EVICTION=1``. When off, :func:`compress_history`
passes the input through unchanged — legacy callers see zero behavior
change. When on, the compressor enforces the budget.

LLM summarization is explicitly NOT done here (that lands in EQ-15 as a
plug-in strategy). The rule-based compressor stays as the authoritative
deterministic baseline.

Interface
---------
Input: an OpenAI-style messages list of the shape
``[{"role": "...", "content": "..."}]``. Non-dict entries and
non-string contents are passed through verbatim (never crash).

Output: a new list with the same ordering contract (oldest-first).
System messages are NEVER evicted — they are anchoring and typically
carry the S0+D0+I0 payload.
"""

from __future__ import annotations

import os
from typing import Any

from agentic_core.L2_execution.enforcement._token_counter import (
    count_tokens,
)


_FLAG_ENV = "USE_DETERMINISTIC_EVICTION"


def compression_enabled() -> bool:
    """Return True iff ``USE_DETERMINISTIC_EVICTION`` is truthy in the env."""
    return os.getenv(_FLAG_ENV, "").lower() in {"1", "true", "yes", "on"}


def _message_tokens(message: dict[str, Any], provider: str, model: str | None) -> int:
    """Best-effort token count for a single message dict."""
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str):
        return 0
    return count_tokens(content, provider, model)


def compress_history(
    messages: list[dict[str, Any]],
    *,
    budget_tokens: int,
    provider: str,
    model: str | None = None,
    force: bool = False,
) -> list[dict[str, Any]]:
    """Compress ``messages`` to fit ``budget_tokens`` via oldest-first eviction.

    Args:
        messages: Ordered OpenAI-style messages list. System messages
            are preserved at their original positions.
        budget_tokens: Target upper bound on total content tokens.
            Must be >= 0. A value of 0 evicts every non-system message.
        provider: Provider identifier routed to ``count_tokens`` for
            per-provider token accounting.
        model: Optional model identifier (used by tiktoken for OpenAI).
        force: Bypass the ``USE_DETERMINISTIC_EVICTION`` env flag. Use
            in tests and in deliberate bulk-processing scripts. Default
            ``False`` means the env flag rules.

    Returns:
        A NEW list of messages (input is not mutated) with total
        content tokens <= ``budget_tokens``. System messages are never
        evicted. Eviction order is strictly oldest-first; this
        determinism is the replay-stability contract.
    """
    if budget_tokens < 0:
        raise ValueError(f"budget_tokens must be >= 0, got {budget_tokens}")
    if not force and not compression_enabled():
        # Legacy passthrough so callers that haven't opted in see no churn.
        return list(messages)

    # Partition system messages (preserved) from the evictable tail.
    # Oldest-first eviction is applied over the evictable slice only,
    # and the final ordering interleaves the preserved system messages
    # back at their original indexes to keep downstream semantics.
    preserved: list[tuple[int, dict[str, Any]]] = []
    evictable: list[tuple[int, dict[str, Any]]] = []
    for idx, msg in enumerate(messages):
        if isinstance(msg, dict) and msg.get("role") == "system":
            preserved.append((idx, msg))
        else:
            evictable.append((idx, msg))

    preserved_tokens = sum(_message_tokens(m, provider, model) for _, m in preserved)
    remaining_budget = budget_tokens - preserved_tokens

    # Walk evictable newest-first, keeping messages while budget allows.
    # Drop the oldest first (by skipping them from the tail of the
    # accept list). This gives stable, deterministic selection.
    kept_evictable: list[tuple[int, dict[str, Any]]] = []
    consumed = 0
    for idx, msg in reversed(evictable):
        tokens = _message_tokens(msg, provider, model)
        if consumed + tokens > remaining_budget and remaining_budget > 0:
            # No budget left — stop accepting older messages.
            break
        if remaining_budget <= 0:
            break
        kept_evictable.append((idx, msg))
        consumed += tokens
    kept_evictable.reverse()  # restore oldest-first within the kept slice

    # Re-merge preserved + kept_evictable sorted by original index so
    # callers see the same relative ordering they passed in.
    merged = sorted(preserved + kept_evictable, key=lambda pair: pair[0])
    return [msg for _, msg in merged]


__all__ = ["compress_history", "compression_enabled"]
