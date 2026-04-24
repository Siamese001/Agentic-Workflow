"""Thinking-token billing ledger — EQ-16 (ADR-PROMPT-ASSEMBLY-002 §11).

Observability-only. Records provider-reported thinking-token counts per
trace so callers can reconcile against the ``AgentRoutingSpec.thinking_budget``
hint from EQ-11.

Provider field translation
--------------------------

- OpenAI (o-series / GPT-5): ``usage.completion_tokens_details.reasoning_tokens``
- Anthropic: usage includes ``thinking`` block tokens in
  ``usage.cache_creation_input_tokens`` / dedicated thinking fields on
  newer SDKs.
- Gemini: ``usage_metadata.thought_token_count``.

This module does not import any provider SDK — it takes already-extracted
numbers and records them in a thread-safe in-process ledger.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ThinkingRecord:
    """A single thinking-token observation."""

    trace_id: str
    provider: str
    thinking_tokens: int
    budget_tokens: int | None
    model: str | None


class ThinkingTokenLedger:
    """Thread-safe in-process ledger of thinking-token observations.

    Used for telemetry only — never on a hot path where it would affect
    generation behavior. A process-wide default instance is exposed via
    :func:`get_default_ledger` but callers can construct their own for
    test isolation.
    """

    def __init__(self) -> None:
        self._records: list[ThinkingRecord] = []
        self._lock = threading.Lock()

    def record(
        self,
        *,
        trace_id: str,
        provider: str,
        thinking_tokens: int,
        budget_tokens: int | None = None,
        model: str | None = None,
    ) -> None:
        """Append a single observation. ``thinking_tokens=0`` is a valid no-op entry."""
        if thinking_tokens < 0:
            raise ValueError(
                f"thinking_tokens must be >= 0, got {thinking_tokens}"
            )
        record = ThinkingRecord(
            trace_id=trace_id,
            provider=provider,
            thinking_tokens=thinking_tokens,
            budget_tokens=budget_tokens,
            model=model,
        )
        with self._lock:
            self._records.append(record)

    def records_for(self, trace_id: str) -> list[ThinkingRecord]:
        with self._lock:
            return [r for r in self._records if r.trace_id == trace_id]

    def total_for(self, trace_id: str) -> int:
        return sum(r.thinking_tokens for r in self.records_for(trace_id))

    def reconcile(self, trace_id: str) -> dict[str, Any]:
        """Diff actual thinking-token usage vs requested budget.

        Returns a dict with ``actual`` (sum across records for the trace),
        ``budget`` (latest non-None budget observation), and ``delta``
        (``actual - budget`` when budget is known; otherwise None).
        """
        records = self.records_for(trace_id)
        actual = sum(r.thinking_tokens for r in records)
        # Latest-wins for budget so retries inherit the most recent cap.
        latest_budget: int | None = None
        for r in records:
            if r.budget_tokens is not None:
                latest_budget = r.budget_tokens
        delta = None if latest_budget is None else actual - latest_budget
        return {"actual": actual, "budget": latest_budget, "delta": delta}

    def clear(self) -> None:
        """Drop all records. Intended for tests and long-running process resets."""
        with self._lock:
            self._records.clear()


_DEFAULT_LEDGER: ThinkingTokenLedger | None = None


def get_default_ledger() -> ThinkingTokenLedger:
    """Return the process-wide ledger (lazily instantiated)."""
    global _DEFAULT_LEDGER
    if _DEFAULT_LEDGER is None:
        _DEFAULT_LEDGER = ThinkingTokenLedger()
    return _DEFAULT_LEDGER


def reset_default_ledger() -> None:
    """Test helper — replace the default ledger with a fresh empty one."""
    global _DEFAULT_LEDGER
    _DEFAULT_LEDGER = ThinkingTokenLedger()


__all__ = [
    "ThinkingRecord",
    "ThinkingTokenLedger",
    "get_default_ledger",
    "reset_default_ledger",
]
