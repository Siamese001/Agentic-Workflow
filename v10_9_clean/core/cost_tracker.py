"""
Cost and latency tracking for v10_9 runtime.

Tracks:
  • Execution spans (wall time)
  • Token usage per call (prompt, completion, total)
  • Aggregated workflow cost summaries
  • Safety-friendly snapshots for state metadata

Does not perform any network or provider logic; this module is purely
responsible for measurement and reporting.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


# ======================================================================
# DATA STRUCTURE
# ======================================================================

@dataclass
class SpanRecord:
    """Represents a single timed execution span."""
    start: float
    end: Optional[float] = None

    def duration_ms(self) -> float:
        if self.end is None:
            return 0.0
        return max((self.end - self.start) * 1000.0, 0.0)


@dataclass
class TokenRecord:
    """Represents token usage statistics for a segment."""
    prompt: int = 0
    completion: int = 0

    @property
    def total(self) -> int:
        return self.prompt + self.completion


# ======================================================================
# COST TRACKER (MAIN)
# ======================================================================

@dataclass
class CostTracker:
    """
    Aggregates:
      • timing spans
      • token counts
      • per-span cost summaries
    """

    spans: Dict[str, SpanRecord] = field(default_factory=dict)
    tokens: Dict[str, TokenRecord] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # SPAN MANAGEMENT
    # ------------------------------------------------------------------

    def start_span(self, name: str) -> None:
        """Begin a timed segment."""
        self.spans[name] = SpanRecord(start=time.perf_counter())

    def end_span(self, name: str) -> None:
        """End a timed segment."""
        span = self.spans.get(name)
        if span and span.end is None:
            span.end = time.perf_counter()

    # ------------------------------------------------------------------
    # TOKEN MANAGEMENT
    # ------------------------------------------------------------------

    def add_tokens(
        self,
        name: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> None:
        """Increment token usage for a given segment."""
        record = self.tokens.get(name, TokenRecord())
        record.prompt += max(prompt_tokens, 0)
        record.completion += max(completion_tokens, 0)
        self.tokens[name] = record

    # ------------------------------------------------------------------
    # SNAPSHOTS (FOR L3/L4/L5)
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Produce a structured snapshot for state metadata.
        Guaranteed deterministic ordering.
        """

        span_entries = []
        for name in sorted(self.spans.keys()):
            span = self.spans[name]
            span_entries.append(
                {
                    "name": name,
                    "duration_ms": span.duration_ms(),
                }
            )

        token_entries = []
        for name in sorted(self.tokens.keys()):
            t = self.tokens[name]
            token_entries.append(
                {
                    "name": name,
                    "prompt_tokens": t.prompt,
                    "completion_tokens": t.completion,
                    "total_tokens": t.total,
                }
            )

        return {
            "spans": span_entries,
            "tokens": token_entries,
        }

    # ------------------------------------------------------------------
    # AGGREGATE HELPERS
    # ------------------------------------------------------------------

    def total_tokens(self) -> int:
        """Sum of all tokens across all segments."""
        return sum(record.total for record in self.tokens.values())

    def total_duration_ms(self) -> float:
        """Sum of all recorded durations across spans."""
        return sum(span.duration_ms() for span in self.spans.values())
