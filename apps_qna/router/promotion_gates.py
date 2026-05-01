"""Wilson CI promotion gates for apps_qna route + paste-set bandits — Wave 4 phase 4.3.

Wraps the spine ``agentic_core.L6_observability.promotion_gates`` for
apps_qna's domain. Reads accumulated outcomes from the
``apps_qna_pack_lifecycle`` ledger, computes Wilson-CI promotion
verdicts per (namespace, candidate_route_or_card, baseline) cell, and
emits paired ROUTER_DECISION + ledger events per constitutional §29.

Promotion criteria (constitutional §29):
  - ``wilson_lower >= 0.60``
  - ``z_score >= 1.96`` (≈95% CI)
  - ``uplift > 0`` (candidate point > baseline point)
  - ``n_each_arm >= 30``

When ALL four hold, the verdict is ``promote``. When any fails, the
verdict is ``rollback`` (or ``insufficient_evidence`` when n is too low).
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Spine import — closes the W4 spine-coverage edge.
from agentic_core.L6_observability.promotion_gates import (
    PromotionVerdict as SpinePromotionVerdict,
    promotion_decision as spine_promotion_decision,
    wilson_interval,
)
from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

_log = logging.getLogger(__name__)

_LEDGER_NAME: str = "apps_qna_pack_lifecycle"
_MIN_N_EACH_ARM: int = 30
_DEFAULT_Z: float = 1.96
_DEFAULT_WILSON_LOWER_FLOOR: float = 0.60
_ROUTER_LAYER: str = "L6"
_ROUTER_NAME: str = "apps_qna_promotion_gate"


@dataclass(frozen=True)
class CellOutcomes:
    """Aggregated success/failure counts for one (namespace, arm) cell."""

    namespace: str
    arm: str
    successes: int
    failures: int

    @property
    def n(self) -> int:
        return self.successes + self.failures


@dataclass(frozen=True)
class AppsQnaPromotionVerdict:
    """Per-cell promotion verdict tagged with the apps_qna domain."""

    namespace: str
    candidate: str
    baseline: str
    promote: bool
    reason: str
    candidate_n: int
    candidate_successes: int
    baseline_n: int
    baseline_successes: int
    wilson_lower_candidate: float
    wilson_upper_baseline: float
    uplift: float
    z_score: float
    decision_id: str = ""

    @property
    def status_band(self) -> str:
        """Constitutional §29 score_band."""
        if self.promote:
            return "promote"
        if "insufficient" in self.reason.lower():
            return "insufficient_evidence"
        return "rollback"


def _ledger_db_path() -> Path | None:
    """Resolve the ledger DB path; None when unavailable."""
    try:
        from tools.ledgers.schema_registry import get

        return get(_LEDGER_NAME).db_path
    except (ImportError, KeyError):  # guardian: allow-return-none-swallow -- ledger schema registry is optional; returns None so caller skips gate when registry missing
        return None


def _aggregate_cell_outcomes(
    *,
    db_path: Path,
    event_kind: str,
    arm_field: str,
    namespace: str | None = None,
) -> dict[tuple[str, str], CellOutcomes]:
    """Walk the ledger and aggregate (namespace, arm) outcome counts.

    Args:
        db_path: ledger DB path.
        event_kind: ``route_select`` or ``paste_set_select``.
        arm_field: ``selected_route`` (W4.1) or ``selected_card`` (W4.2)
            depending on which bandit's outcomes we're aggregating.
        namespace: optional filter; None aggregates across all namespaces.

    Returns:
        ``{(namespace, arm): CellOutcomes, ...}``. Counts only rows whose
        outcome_json is bound — predictions without outcomes don't yet
        contribute evidence.
    """
    if not db_path.is_file():
        return {}
    sql = (
        "SELECT prediction_json, outcome_json FROM events "
        "WHERE event_kind = ? AND outcome_json IS NOT NULL"
    )
    params: tuple[Any, ...] = (event_kind,)
    if namespace is not None:
        sql += " AND prediction_json LIKE ?"
        params = (event_kind, f'%"namespace":"{namespace}"%')

    counts: dict[tuple[str, str], list[int]] = {}
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            for prediction_json, outcome_json in con.execute(sql, params):
                if not prediction_json or not outcome_json:
                    continue
                try:
                    pred = json.loads(prediction_json)
                    out = json.loads(outcome_json)
                except json.JSONDecodeError:
                    continue
                ns = pred.get("namespace") or ""
                arm = pred.get(arm_field) or ""
                if not ns or not arm:
                    continue
                # Success = outcome.success when present, else asked AND landed
                # for routing, included AND useful for paste-set.
                success = bool(out.get("success"))
                if not success:
                    if "asked" in out and "landed" in out:
                        success = bool(out.get("asked")) and bool(out.get("landed"))
                    elif "included" in out and "useful" in out:
                        success = bool(out.get("included")) and bool(out.get("useful"))
                key = (ns, arm)
                bucket = counts.setdefault(key, [0, 0])
                if success:
                    bucket[0] += 1
                else:
                    bucket[1] += 1
        finally:
            con.close()
    except sqlite3.Error as exc:
        _log.debug("aggregation sqlite error: %r", exc)
        return {}

    return {
        key: CellOutcomes(
            namespace=key[0],
            arm=key[1],
            successes=val[0],
            failures=val[1],
        )
        for key, val in counts.items()
    }


def evaluate_promotion(
    *,
    candidate: CellOutcomes,
    baseline: CellOutcomes,
    z: float = _DEFAULT_Z,
    min_n_each_arm: int = _MIN_N_EACH_ARM,
    wilson_lower_floor: float = _DEFAULT_WILSON_LOWER_FLOOR,
) -> AppsQnaPromotionVerdict:
    """Evaluate one (candidate, baseline) cell against the §29 floors.

    Layers the apps_qna-specific ``wilson_lower_floor`` constraint on
    top of the spine's lower-bound > upper-bound contract. Both must
    hold to promote.
    """
    if candidate.namespace != baseline.namespace:
        raise ValueError(
            f"namespace mismatch: candidate={candidate.namespace!r} "
            f"baseline={baseline.namespace!r}"
        )

    spine_verdict: SpinePromotionVerdict = spine_promotion_decision(
        candidate_successes=candidate.successes,
        candidate_n=candidate.n,
        baseline_successes=baseline.successes,
        baseline_n=baseline.n,
        z=z,
        min_n_each_arm=min_n_each_arm,
    )

    # Layer the apps_qna wilson_lower_floor on top.
    promote = spine_verdict.promote
    reason = spine_verdict.reason
    if promote and spine_verdict.candidate.lower < wilson_lower_floor:
        promote = False
        reason = (
            f"candidate Wilson lower {spine_verdict.candidate.lower:.3f} "
            f"below apps_qna §29 floor {wilson_lower_floor:.2f}"
        )

    uplift = spine_verdict.candidate.point - spine_verdict.baseline.point
    decision_id = uuid.uuid4().hex

    return AppsQnaPromotionVerdict(
        namespace=candidate.namespace,
        candidate=candidate.arm,
        baseline=baseline.arm,
        promote=promote,
        reason=reason,
        candidate_n=candidate.n,
        candidate_successes=candidate.successes,
        baseline_n=baseline.n,
        baseline_successes=baseline.successes,
        wilson_lower_candidate=spine_verdict.candidate.lower,
        wilson_upper_baseline=spine_verdict.baseline.upper,
        uplift=uplift,
        z_score=z,
        decision_id=decision_id,
    )


def _emit_promotion_decision_marker(verdict: AppsQnaPromotionVerdict) -> None:
    """Constitutional §29 paired marker for promotion verdicts."""
    print(
        f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
        f"decision_id={verdict.decision_id} "
        f"selected={'promote' if verdict.promote else 'rollback'} "
        f"ns={verdict.namespace} candidate={verdict.candidate} "
        f"baseline={verdict.baseline} "
        f"wilson_lower={verdict.wilson_lower_candidate:.3f} "
        f"uplift={verdict.uplift:+.3f} n_each_arm={verdict.candidate_n}/{verdict.baseline_n}"
    )


def emit_promotion_verdict_to_ledger(
    verdict: AppsQnaPromotionVerdict,
) -> str:
    """Emit a paired ROUTER_DECISION marker + ledger row for the verdict."""
    _emit_promotion_decision_marker(verdict)
    return emit_pack_lifecycle_event(
        event_kind="promote_decision",
        prediction={
            "candidate": verdict.candidate,
            "baseline": verdict.baseline,
            "namespace": verdict.namespace,
            "wilson_lower": verdict.wilson_lower_candidate,
            "wilson_upper_baseline": verdict.wilson_upper_baseline,
            "z_score": verdict.z_score,
            "uplift": verdict.uplift,
            "n_each_arm": min(verdict.candidate_n, verdict.baseline_n),
            "verdict": "promote" if verdict.promote else (
                "insufficient_evidence" if "insufficient" in verdict.reason.lower()
                else "rollback"
            ),
        },
        outcome={
            "promoted": verdict.promote,
            "reason": verdict.reason,
        },
        score_band=verdict.status_band,
        metadata={"decision_id": verdict.decision_id},
    )


def evaluate_route_promotions(
    *,
    namespace: str,
    candidate_route: str,
    baseline_route: str,
    db_path: Path | None = None,
) -> AppsQnaPromotionVerdict:
    """Evaluate W4.1 route promotion candidate vs baseline."""
    path = db_path or _ledger_db_path()
    if path is None:
        raise RuntimeError("apps_qna_pack_lifecycle ledger not registered")
    counts = _aggregate_cell_outcomes(
        db_path=path,
        event_kind="route_select",
        arm_field="selected_route",
        namespace=namespace,
    )
    candidate = counts.get(
        (namespace, candidate_route),
        CellOutcomes(namespace, candidate_route, 0, 0),
    )
    baseline = counts.get(
        (namespace, baseline_route),
        CellOutcomes(namespace, baseline_route, 0, 0),
    )
    verdict = evaluate_promotion(candidate=candidate, baseline=baseline)
    emit_promotion_verdict_to_ledger(verdict)
    return verdict


def evaluate_paste_promotions(
    *,
    namespace: str,
    candidate_card: str,
    baseline_card: str,
    db_path: Path | None = None,
) -> AppsQnaPromotionVerdict:
    """Evaluate W4.2 paste-set promotion candidate vs baseline."""
    path = db_path or _ledger_db_path()
    if path is None:
        raise RuntimeError("apps_qna_pack_lifecycle ledger not registered")
    counts = _aggregate_cell_outcomes(
        db_path=path,
        event_kind="paste_set_select",
        arm_field="selected_card",
        namespace=namespace,
    )
    candidate = counts.get(
        (namespace, candidate_card),
        CellOutcomes(namespace, candidate_card, 0, 0),
    )
    baseline = counts.get(
        (namespace, baseline_card),
        CellOutcomes(namespace, baseline_card, 0, 0),
    )
    verdict = evaluate_promotion(candidate=candidate, baseline=baseline)
    emit_promotion_verdict_to_ledger(verdict)
    return verdict


__all__ = [
    "AppsQnaPromotionVerdict",
    "CellOutcomes",
    "emit_promotion_verdict_to_ledger",
    "evaluate_paste_promotions",
    "evaluate_promotion",
    "evaluate_route_promotions",
    "wilson_interval",
]
