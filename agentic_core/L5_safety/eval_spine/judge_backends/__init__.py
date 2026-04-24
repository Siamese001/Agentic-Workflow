"""LLM-judge backend plugin package (plan `-d5e8b3`).

Backends plug into :class:`agentic_core.L5_safety.eval_spine.trace_grader.TraceGrader`
via ``register_dim_scorer(dim_name, backend)``.

A backend is a callable ``(GraderInput, DimSpec) -> DimensionResult``. It may
return a numeric score in [1, 5] or the sentinel string ``"Unknown"``.

Available backends:
  - :class:`NullBackend` — always returns ``Unknown``. Default safe fallback.
  - :class:`AnthropicBackend` — env-gated stub; real scoring is deferred.

This package intentionally does NOT touch rubric weights or consensus policy
(parent plan ``-ce683b`` §6).
"""

from __future__ import annotations

from agentic_core.L5_safety.eval_spine.judge_backends.base import (
    JudgeBackend,
    backend_name,
)
from agentic_core.L5_safety.eval_spine.judge_backends.null import NullBackend
from agentic_core.L5_safety.eval_spine.judge_backends.anthropic_stub import (
    AnthropicBackend,
)

__all__ = [
    "AnthropicBackend",
    "JudgeBackend",
    "NullBackend",
    "backend_name",
]
