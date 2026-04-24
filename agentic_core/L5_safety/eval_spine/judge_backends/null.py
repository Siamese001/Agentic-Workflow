"""NullBackend — deterministic Unknown-returning judge backend.

This is the safe fallback used whenever no LLM backend is configured or
when a real backend fails its own preflight. Returning ``Unknown`` for
every dim pushes the grader toward the ``unknown_budget`` ceiling, which
the orchestrator then escalates via ``reason_code=grader.unknown_budget_exceeded``.
"""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.L5_safety.eval_spine.trace_grader import (
    DimensionResult,
    GraderInput,
)


class NullBackend:
    """Always reports ``Unknown`` for every dimension.

    Parameters
    ----------
    note:
        Optional short reason attached to each DimensionResult for
        telemetry. Keeps the distinction between "no backend configured"
        vs "backend preflight failed" vs "model returned Unknown" visible.
    """

    __slots__ = ("_note", "_dim_name")

    def __init__(
        self, note: str | None = None, *, dim_name: str | None = None
    ) -> None:
        self._note = note
        self._dim_name = dim_name

    def __call__(
        self, _inputs: GraderInput, dim_spec: Mapping[str, Any]
    ) -> DimensionResult:
        # Prefer explicit dim_name passed at construction; fall back to
        # the spec key ``name`` if the grader injects it; last resort is
        # a sentinel that callers can detect.
        name = self._dim_name or str(dim_spec.get("name", "unknown_dim"))
        return DimensionResult(
            name=name, score="Unknown", verdict="unknown", notes=self._note
        )


__all__ = ["NullBackend"]
