"""GovernedConfidenceScorer — thin runtime wrapper with activation and rollback.

Wraps ConfidenceScorer with:
  - Activation mode awareness (ABSENT / SHADOW / ACTIVE)
  - Automatic permanent rollback to heuristic routing when safety thresholds
    are exceeded (via RollbackMonitor)
  - record_outcome() interface for callers to feed back repair success/failure

Rollback is permanent within a single process lifetime.  Re-authorization
requires a new wire_governed_scorer() call with a fresh activation_record.json.
The HealingRouter hard rules (unknown class, sentinel budget, hash mismatch,
OOD, latency, exceptions) are enforced inside ConfidenceScorer._classify_ml()
and continue to operate unchanged regardless of activation mode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .activation_state import ActivationMode
from .activation_criteria import RollbackMonitor
from .confidence_scorer import ConfidenceScore, ConfidenceScorer

if TYPE_CHECKING:
    from .failure_signal import FailureSignal
    from ..types.heal_contract_types import HealClassifierTelemetry


class GovernedConfidenceScorer:
    """Runtime wrapper over ConfidenceScorer with governed activation and rollback.

    Invariants:
      ABSENT   — inner has model=None, shadow_mode=True; no ML inference
      SHADOW   — inner has shadow_mode=True; heuristic routing; ML telemetry only
      ACTIVE   — inner has shadow_mode=False; ML tier drives routing
      ROLLBACK — after latch: permanent heuristic-only regardless of inner mode

    The _heuristic_fallback scorer used after rollback has no telemetry sink to
    avoid double-emission with the inner scorer's sink.
    """

    def __init__(
        self,
        inner: ConfidenceScorer,
        activation_mode: ActivationMode,
        rollback_monitor: RollbackMonitor | None = None,
    ) -> None:
        self._inner = inner
        self._activation_mode = activation_mode
        self._rollback_monitor = rollback_monitor
        self._heuristic_fallback = ConfidenceScorer(model=None, shadow_mode=True)

    def score(self, signal: FailureSignal) -> ConfidenceScore:
        """Score signal.  Falls back to heuristic-only when rollback is latched."""
        if self._rollback_monitor is not None:
            rolled_back, _reason = self._rollback_monitor.should_rollback()
            if rolled_back:
                return self._heuristic_fallback.score(signal)
        return self._inner.score(signal)

    def record_outcome(
        self,
        event: HealClassifierTelemetry,
        repair_succeeded: bool | None = None,
    ) -> None:
        """Feed back an observed outcome to the rollback monitor.

        Callers SHOULD call this for every scored signal so the rollback window
        stays current.  Safe to omit when the outcome is unknown.
        """
        if self._rollback_monitor is not None:
            self._rollback_monitor.record(event, repair_succeeded)

    # ------------------------------------------------------------------
    # State properties for runtime queries and test introspection
    # ------------------------------------------------------------------

    @property
    def activation_mode(self) -> ActivationMode:
        return self._activation_mode

    @property
    def is_rolled_back(self) -> bool:
        """True once the rollback monitor has permanently latched."""
        if self._rollback_monitor is None:
            return False
        return self._rollback_monitor.is_latched

    @property
    def rollback_reason(self) -> str:
        """Human-readable reason for rollback; empty when not rolled back."""
        if self._rollback_monitor is None:
            return ""
        _, reason = self._rollback_monitor.should_rollback()
        return reason

    # Expose inner scorer attributes for external inspection / test assertions
    @property
    def _shadow_mode(self) -> bool:
        return self._inner._shadow_mode

    @property
    def _expected_model_hash(self) -> str:
        return self._inner._expected_model_hash

    @property
    def _model(self):  # type: ignore[return]
        return self._inner._model
