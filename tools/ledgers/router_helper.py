"""tools.ledgers.router_helper — Generic closed-loop wiring for any router.

Constitutional §29 — closed-loop-router-enforcement.md — requires every router
in the 10-router matrix (and any new router) to:

1. Emit a ``ROUTER_DECISION:`` marker on every routing decision
2. Persist the prediction to its per-router ledger (``router_<layer>_<router>``)
3. Bind the outcome to the same row when the dispatched action completes
4. Optionally consult a posterior over (decision_class, cell) before deciding

This module DRY-ifies that pattern. The ``RouterClosedLoopHelper`` is the
high-leverage façade: instantiate once per router, call ``record_decision()``
to capture predictions, ``bind_outcome()`` to attach outcomes, and
``get_posterior()`` to consult accumulated evidence.

Reference implementation: ``agentic_core/L2_execution/healers/healing_router.py``
(W1+W2 of plan ``l2-cascade-router-closed-loop-wiring-c4d8a1``). The L2
exemplar inlined ~150 LOC; with this helper the same wiring is ~30 LOC.

Design rules:

- **Pure adapter** — depends on ``hook_helpers`` (writes) + ``posterior_reader``
  (reads). No direct ``import sqlite3``. No router business logic.
- **Stdlib only**.
- **Fail-soft on every error path** — returns sentinel ``RouterDecisionHandle``
  with empty ``ledger_event_id`` and the routing continues unaffected.
- **Idempotent** — reusing the same ``decision_id`` is the caller's
  responsibility for retry semantics; the helper itself does not dedupe.
- **Layer/router pair is the routing key** — every helper instance is bound
  to exactly one ledger.

Plan: ``.codex/plans/_archive/windsurf_legacy_plans/closed-loop-router-fleet-rollout-d8f2a3.md``
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

# Constitutional §29 promotion gate floor. The same floor is the routing
# posterior's "use-this-not-the-heuristic" threshold so promotion and routing
# share calibration semantics.
DEFAULT_POSTERIOR_N_FLOOR: int = 30

# Beta(1, 1) uniform prior. Posterior mean = (1+k) / (2+n).
_BETA_PRIOR_ALPHA: float = 1.0
_BETA_PRIOR_BETA: float = 1.0


# =========================================================================== #
# Public dataclasses
# =========================================================================== #
@dataclass(frozen=True)
class RouterDecisionHandle:
    """The receipt returned by ``record_decision``.

    Carries everything ``bind_outcome`` needs to attach the outcome to its
    prediction row, plus telemetry fields the router itself wants to stamp.

    Empty ``ledger_event_id`` signals the ledger write was skipped (bypass /
    error). Outcome binding silently no-ops in that case so the dispatch path
    is never broken by telemetry failures.
    """

    decision_id: str
    ledger_event_id: str
    fingerprint: str
    predicted_p_success: float
    eu_score: float
    selected: str
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PosteriorVerdict:
    """The verdict returned by ``get_posterior``."""

    posterior_mean: float
    n: int
    successes: int
    used: bool
    fallback_reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "posterior_mean": float(self.posterior_mean),
            "n": int(self.n),
            "successes": int(self.successes),
            "used": bool(self.used),
            "fallback_reason": self.fallback_reason,
        }


# =========================================================================== #
# Helpers — stable cell fingerprint + Brier component + score band
# =========================================================================== #
def cell_fingerprint(cell: Mapping[str, Any]) -> str:
    """Return a 12-hex-char SHA-256 prefix identifying a routing cell.

    The cell is a dict of feature-name → value pairs that uniquely identify
    the situation the router faced (e.g.
    ``{"failure_class": "TIMEOUT", "source_layer": "L2", "retry_band": "r0"}``).
    Keys are sorted before hashing so dict order is irrelevant.
    """
    items = sorted((str(k), str(v)) for k, v in cell.items())
    raw = "\x00".join(f"{k}={v}" for k, v in items)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def brier_component(predicted_p: float, actual_success: bool) -> float:
    """Return ``(predicted_p - actual)^2`` for one Bernoulli outcome."""
    p = max(0.0, min(1.0, float(predicted_p)))
    actual = 1.0 if actual_success else 0.0
    diff = p - actual
    return diff * diff


def score_band_for(predicted_p: float, actual_success: bool, threshold: float = 0.5) -> str:
    """Return one of ``tp|fp|tn|fn`` for a (predicted, actual) pair."""
    predicted_success = predicted_p >= threshold
    if predicted_success and actual_success:
        return "tp"
    if predicted_success and not actual_success:
        return "fp"
    if not predicted_success and actual_success:
        return "fn"
    return "tn"


# =========================================================================== #
# RouterClosedLoopHelper — the façade
# =========================================================================== #
class RouterClosedLoopHelper:
    """Closed-loop wiring façade for one router.

    Instantiate once per router (typically as a class attribute or in
    ``__init__``); reuse for every routing decision.
    """

    def __init__(
        self,
        *,
        layer: str,
        router: str,
        ledger_name: str,
        repo_area: str,
        constitutional_rule: str = "§29",
    ) -> None:
        self.layer = str(layer)
        self.router = str(router)
        self.ledger_name = str(ledger_name)
        self.repo_area = str(repo_area)
        self.constitutional_rule = str(constitutional_rule)

    def record_decision(
        self,
        *,
        selected: str,
        cell: Mapping[str, Any],
        predicted_p_success: float,
        eu_score: float = 0.0,
        prediction_extras: Mapping[str, Any] | None = None,
        metadata_extras: Mapping[str, Any] | None = None,
        trace_id: str | None = None,
        route_id: str | None = None,
        decision_id: str | None = None,
    ) -> RouterDecisionHandle:
        """Record a routing decision and return a binding handle.

        Returns ``RouterDecisionHandle`` carrying decision_id + ledger_event_id.
        Empty ``ledger_event_id`` when the ledger write was suppressed.
        """
        did = decision_id or uuid.uuid4().hex
        fp = cell_fingerprint(cell)
        clamped_p = max(0.0, min(1.0, float(predicted_p_success)))
        eu = float(eu_score)
        sel = str(selected)
        tid = trace_id or did
        rid = route_id or f"{self.layer}/{self.router}"

        prediction: dict[str, Any] = {
            "decision_id": did,
            "selected": sel,
            "fingerprint": fp,
            "cell": dict(cell),
            "predicted_p_success": clamped_p,
            "eu_score": eu,
            "trace_id": tid,
            "route_id": rid,
        }
        if prediction_extras:
            prediction.update(prediction_extras)

        self._emit_marker(
            decision_id=did,
            trace_id=tid,
            route_id=rid,
            selected=sel,
            predicted_p=clamped_p,
            eu_score=eu,
        )

        event_id = self._write_decision_row(
            prediction=prediction,
            metadata_extras=metadata_extras,
        )

        return RouterDecisionHandle(
            decision_id=did,
            ledger_event_id=event_id,
            fingerprint=fp,
            predicted_p_success=clamped_p,
            eu_score=eu,
            selected=sel,
            extra=dict(prediction_extras) if prediction_extras else {},
        )

    def bind_outcome(
        self,
        handle: RouterDecisionHandle,
        *,
        success: bool,
        latency_ms: int = 0,
        outcome_extras: Mapping[str, Any] | None = None,
        score_threshold: float = 0.5,
    ) -> None:
        """Bind a dispatch outcome to its prediction row.

        Computes Brier component and TP/FP/TN/FN band. Fail-soft: any error
        leaves the prediction in ``status='predicted'`` for later sweeps.
        """
        if not handle.ledger_event_id:
            return

        outcome: dict[str, Any] = {
            "success": bool(success),
            "latency_ms": int(latency_ms),
        }
        if outcome_extras:
            outcome.update(outcome_extras)

        try:
            brier = brier_component(handle.predicted_p_success, bool(success))
            band = score_band_for(handle.predicted_p_success, bool(success), threshold=score_threshold)
        except (TypeError, ValueError):
            brier = None
            band = None

        try:
            from tools.ledgers.hook_helpers import bind_ledger_outcome  # noqa: PLC0415

            bind_ledger_outcome(
                ledger=self.ledger_name,
                event_id=handle.ledger_event_id,
                outcome=outcome,
                score_band=band,
                score_numeric=brier,
                latency_ms=int(latency_ms),
            )
            _LOGGER.info(
                "ROUTER_OUTCOME: layer=%s router=%s decision_id=%s success=%s band=%s brier=%s latency_ms=%d",
                self.layer,
                self.router,
                handle.decision_id,
                bool(success),
                band,
                f"{brier:.4f}" if brier is not None else "n/a",
                int(latency_ms),
            )
        except (
            ImportError,
            AttributeError,
            TypeError,
            ValueError,
            RuntimeError,
            OSError,
        ):  # guardian: allow-log-and-swallow -- outcome binding is best-effort; dispatch must not fail
            _LOGGER.debug("router_helper outcome bind failed", exc_info=True)

    def get_posterior(
        self,
        *,
        selected: str,
        cell: Mapping[str, Any],
        n_floor: int = DEFAULT_POSTERIOR_N_FLOOR,
        alpha: float = _BETA_PRIOR_ALPHA,
        beta: float = _BETA_PRIOR_BETA,
        ledger_path: str | None = None,
    ) -> PosteriorVerdict:
        """Aggregate bound rows for (selected, cell) and return posterior verdict."""
        try:
            from tools.ledgers.posterior_reader import aggregate_router_cell  # noqa: PLC0415
            from tools.ledgers.schema_registry import get as _get_spec  # noqa: PLC0415
        except (
            ImportError
        ):  # guardian: allow-log-and-swallow -- adapter import failure must not break routing
            _LOGGER.debug("router_helper get_posterior import failed", exc_info=True)
            prior_mean = alpha / (alpha + beta)
            return PosteriorVerdict(
                posterior_mean=prior_mean,
                n=0,
                successes=0,
                used=False,
                fallback_reason="error",
            )

        if ledger_path is None:
            try:
                spec = _get_spec(self.ledger_name)
                path = str(spec.db_path)
            except (KeyError, AttributeError):
                path = ""
        else:
            path = str(ledger_path)

        if not path:
            prior_mean = alpha / (alpha + beta)
            return PosteriorVerdict(
                posterior_mean=prior_mean,
                n=0,
                successes=0,
                used=False,
                fallback_reason="ledger_unavailable",
            )

        agg = aggregate_router_cell(
            ledger_path=path,
            tier_name=str(selected),
            fingerprint_hex=cell_fingerprint(cell),
            n_floor=int(n_floor),
            alpha=alpha,
            beta=beta,
            selected_field="selected",
        )
        return PosteriorVerdict(
            posterior_mean=agg.posterior_mean,
            n=agg.n,
            successes=agg.successes,
            used=agg.used,
            fallback_reason=agg.fallback_reason,
        )

    def _emit_marker(
        self,
        *,
        decision_id: str,
        trace_id: str,
        route_id: str,
        selected: str,
        predicted_p: float,
        eu_score: float,
    ) -> None:
        _LOGGER.info(
            "ROUTER_DECISION: layer=%s router=%s decision_id=%s trace_id=%s "
            "route_id=%s selected=%s eu_score=%.4f brier_score=pending "
            "confidence=%.4f",
            self.layer,
            self.router,
            decision_id,
            trace_id,
            route_id,
            selected,
            eu_score,
            predicted_p,
        )

    def _write_decision_row(
        self,
        *,
        prediction: Mapping[str, Any],
        metadata_extras: Mapping[str, Any] | None,
    ) -> str:
        metadata: dict[str, Any] = {
            "router": f"{self.layer}/{self.router}",
            "constitutional_rule": self.constitutional_rule,
        }
        if metadata_extras:
            metadata.update(metadata_extras)

        try:
            from tools.ledgers.hook_helpers import emit_ledger_event  # noqa: PLC0415

            event_id = emit_ledger_event(
                ledger=self.ledger_name,
                event_kind="route_decision",
                prediction=dict(prediction),
                outcome=None,
                score_band="unbound",
                score_numeric=None,
                repo_area=self.repo_area,
                metadata=metadata,
            )
            return event_id or ""
        except (
            ImportError,
            AttributeError,
            TypeError,
            ValueError,
            RuntimeError,
            OSError,
        ):  # guardian: allow-log-and-swallow -- ledger write is best-effort; routing must not break
            _LOGGER.debug("router_helper ledger emit failed", exc_info=True)
            return ""


__all__ = [
    "DEFAULT_POSTERIOR_N_FLOOR",
    "PosteriorVerdict",
    "RouterClosedLoopHelper",
    "RouterDecisionHandle",
    "brier_component",
    "cell_fingerprint",
    "score_band_for",
]
