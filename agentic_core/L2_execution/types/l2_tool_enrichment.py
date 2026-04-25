"""
Tool-contract enrichment — W3 (gap plan b7c4e2: G4, G5, G10).

Adds three adjacent registries that enrich ``ToolContract`` / ``SafetyProfile``
without modifying the existing frozen dataclasses in ``execution_tool_contract.py``:

* **Thought signatures** (G4) — Google Vertex AI / Gemini 3 pattern:
  "Thought signatures should always be used with function calling for best
  results." Signatures propagate through E3 → E4 heal-replay to guarantee
  a retry runs against the same reasoning context that produced the call.
* **Tool Use Examples** (G5) — Anthropic advanced tool use pattern: few-shot
  parameter calibration attached to each tool for behavioral clarity.
* **Execution markers** (G10) — `parallel_safe` + `idempotent` flags that
  the heal loop and parallel-call planner can read to decide whether a retry
  is safe and whether calls may be issued concurrently.

All three are keyed by ``tool_name`` and live in in-memory registries with
default-safe lookups — tools that have not been enriched are treated as
``parallel_safe=False`` and ``idempotent=False`` (the safest defaults).

Guardian note: no broad exceptions, no subprocess, no filesystem writes.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

__all__ = [
    "ThoughtSignature",
    "ToolUseExample",
    "ExecutionMarkers",
    "register_thought_signature",
    "get_thought_signature",
    "register_tool_examples",
    "get_tool_examples",
    "register_execution_markers",
    "get_execution_markers",
    "DEFAULT_EXECUTION_MARKERS",
    "make_thought_signature",
]


# ---------------------------------------------------------------------------
# Thought signatures (G4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ThoughtSignature:
    """Opaque fingerprint of the reasoning context that produced a tool call.

    Mirrors the Gemini 3 "thought signature" contract: the signature binds
    a specific reasoning turn to the downstream tool call so that heal /
    replay re-runs the *same* call rather than a freshly-generated one.
    """

    signature: str
    trace_id: str
    issued_at: float
    model_hint: str = ""
    turn_index: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "signature": self.signature,
            "trace_id": self.trace_id,
            "issued_at": self.issued_at,
            "model_hint": self.model_hint,
            "turn_index": self.turn_index,
            "metadata": dict(self.metadata),
        }


def make_thought_signature(
    *,
    reasoning_payload: str,
    trace_id: str,
    model_hint: str = "",
    turn_index: int = 0,
) -> ThoughtSignature:
    """Deterministic signature from a reasoning payload + trace identity.

    The signature is SHA-256 of (trace_id | turn_index | reasoning_payload)
    truncated to 32 hex chars. This is NOT cryptographic authentication —
    it is a replay fingerprint. For authenticated scoped credentials, see
    ``capability/scoped_credential_mint.py``.
    """
    if not trace_id:
        raise ValueError("trace_id is required")
    digest_input = f"{trace_id}|{turn_index}|{reasoning_payload}".encode("utf-8")
    sig = hashlib.sha256(digest_input).hexdigest()[:32]
    return ThoughtSignature(
        signature=sig,
        trace_id=trace_id,
        issued_at=time.time(),
        model_hint=model_hint,
        turn_index=turn_index,
    )


_signatures: dict[str, ThoughtSignature] = {}


def register_thought_signature(tool_name: str, signature: ThoughtSignature) -> None:
    """Bind a ``ThoughtSignature`` to a ``tool_name`` for the current step."""
    if not tool_name:
        raise ValueError("tool_name is required")
    _signatures[tool_name] = signature


def get_thought_signature(tool_name: str) -> ThoughtSignature | None:
    """Return the bound signature or ``None`` if not registered."""
    return _signatures.get(tool_name)


# ---------------------------------------------------------------------------
# Tool Use Examples (G5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ToolUseExample:
    """Few-shot calibration example for a tool.

    Per Anthropic guidance: use realistic data (real city names, plausible
    prices — not ``"string"`` or ``"value"``), cover minimal + partial + full
    specification patterns, keep 1-5 examples per tool, focus on ambiguity.
    """

    description: str
    args: Mapping[str, Any]
    expected_shape: Mapping[str, Any] | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "args": dict(self.args),
            "expected_shape": (None if self.expected_shape is None else dict(self.expected_shape)),
            "notes": self.notes,
        }


_examples: dict[str, tuple[ToolUseExample, ...]] = {}


def register_tool_examples(
    tool_name: str,
    examples: Iterable[ToolUseExample],
) -> None:
    """Attach a tuple of 1-5 examples to a tool.

    Raises ``ValueError`` if fewer than 1 or more than 5 are supplied — this
    enforces the Anthropic recommendation that examples stay concise.
    """
    if not tool_name:
        raise ValueError("tool_name is required")
    tup = tuple(examples)
    if not (1 <= len(tup) <= 5):
        raise ValueError(f"tool_name={tool_name!r} must have 1..5 examples, got {len(tup)}")
    _examples[tool_name] = tup


def get_tool_examples(tool_name: str) -> tuple[ToolUseExample, ...]:
    """Return registered examples or an empty tuple."""
    return _examples.get(tool_name, ())


# ---------------------------------------------------------------------------
# Execution markers (G10)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ExecutionMarkers:
    """Safety flags consulted by the heal loop and parallel-call planner.

    Defaults are safest: not parallel-safe, not idempotent, no retry guidance.
    Register opt-in markers for tools that are genuinely safe under each
    condition. Incorrect markers are strictly worse than no markers.
    """

    tool_name: str
    parallel_safe: bool = False
    idempotent: bool = False
    max_retries: int = 0
    retry_backoff_ms: int = 0
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "parallel_safe": self.parallel_safe,
            "idempotent": self.idempotent,
            "max_retries": self.max_retries,
            "retry_backoff_ms": self.retry_backoff_ms,
            "rationale": self.rationale,
        }


DEFAULT_EXECUTION_MARKERS = ExecutionMarkers(
    tool_name="__default__",
    parallel_safe=False,
    idempotent=False,
    max_retries=0,
    retry_backoff_ms=0,
    rationale="safest defaults for unclassified tools",
)


_markers: dict[str, ExecutionMarkers] = {}


def register_execution_markers(markers: ExecutionMarkers) -> None:
    if not markers.tool_name:
        raise ValueError("markers.tool_name is required")
    if markers.max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    if markers.retry_backoff_ms < 0:
        raise ValueError("retry_backoff_ms must be >= 0")
    _markers[markers.tool_name] = markers


def get_execution_markers(tool_name: str) -> ExecutionMarkers:
    """Return registered markers or ``DEFAULT_EXECUTION_MARKERS``."""
    return _markers.get(tool_name, DEFAULT_EXECUTION_MARKERS)


def clear_all_registries() -> None:
    """Test-only helper that resets all W3 registries."""
    _signatures.clear()
    _examples.clear()
    _markers.clear()
