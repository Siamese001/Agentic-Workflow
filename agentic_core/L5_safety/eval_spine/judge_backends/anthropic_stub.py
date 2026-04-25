"""AnthropicBackend — env-gated stub; real scoring deferred.

Design contract (plan `-d5e8b3` §Q3):

- If ``ANTHROPIC_API_KEY`` is **unset** (or empty), the backend behaves as
  :class:`NullBackend`. This keeps the plugin safe to instantiate in any
  environment.
- If ``ANTHROPIC_API_KEY`` is **set**, the backend's ``__call__`` raises
  :class:`NotImplementedError`. The seam is structural; actual model
  invocation is tracked as a DEFERRED_SCOPE item and requires SVP review
  (rubric-adjacent per parent plan ``-ce683b`` §6).

The two behaviors are chosen at ``__call__`` time, not at construction,
so env changes between startup and runtime are honored.
"""

from __future__ import annotations

import os
from typing import Any, Mapping

from agentic_core.L5_safety.eval_spine.judge_backends.null import NullBackend
from agentic_core.L5_safety.eval_spine.trace_grader import (
    DimensionResult,
    GraderInput,
)

_API_KEY_ENV = "ANTHROPIC_API_KEY"  # guardian: allow-hardcoded-secret -- module-level constant holding the NAME of the env var to read; the secret value itself is never in source


class AnthropicBackend:
    """Stub Anthropic-model judge backend.

    Real wiring is blocked on:
      1. SVP review for judge-rubric / model-swap concerns.
      2. Calibration ledger + cadence rule (ADR-036 §4 invariant 5).
      3. Budget envelope for judge calls (ADR-038).
    """

    __slots__ = ("_null_fallback", "_dim_name")

    def __init__(self, *, dim_name: str | None = None) -> None:
        self._dim_name = dim_name
        self._null_fallback = NullBackend(note="anthropic:no_api_key", dim_name=dim_name)

    def is_active(self) -> bool:
        """Return True iff the API key is present in the environment."""
        value = os.environ.get(_API_KEY_ENV, "").strip()
        return bool(value)

    def __call__(self, inputs: GraderInput, dim_spec: Mapping[str, Any]) -> DimensionResult:
        if not self.is_active():
            return self._null_fallback(inputs, dim_spec)
        # Deliberate: the seam exists but the implementation is not in
        # scope for this plan. Fail loudly so no silent fake scoring
        # leaks into production rubric weights.
        raise NotImplementedError(
            "AnthropicBackend real scoring is deferred — see plan "
            "exit-eval-spine-deferred-closeout-d5e8b3 §Q3 and parent "
            "plan -ce683b §6 (judge rubric / model swap non-touch)."
        )


__all__ = ["AnthropicBackend"]
