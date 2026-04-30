"""apps_qna flywheel promoter — Wave 5 phase 5.2.

Reads the ``apps_qna_pack_lifecycle`` ledger, identifies routes / cards
that consistently win across multiple namespaces, and emits a
``flywheel_defaults.json`` snapshot the wizard reads when constructing a
fresh ``likely_questions`` priority order. The flywheel turns
"empirically dominant in past rehearsals" into "default for next pack".

Architecture
------------
- Aggregates outcome rows per arm, weighted by namespace count
- Filters to arms with ``n >= min_n`` and ``mean >= min_success_rate``
- Ranks remaining arms by mean success rate descending
- Emits a JSON snapshot through the spine UWG
- Optionally emits a ``ROUTER_DECISION`` marker per promoted arm so the
  promotion path is auditable per constitutional §29

The wizard's ``seed_likely_questions_from_research`` reads the snapshot
when present and uses it as a tie-breaker for cold-start namespaces
(prepends globally-dominant routes that aren't already in the ranked
result).
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_qna.integrations.spine_adapter import (
    emit_pack_lifecycle_event,
    write_card_text,
)

_log = logging.getLogger(__name__)

_LEDGER_NAME: str = "apps_qna_pack_lifecycle"
_DEFAULT_FLYWHEEL_PATH: Path = Path("artifacts/apps_qna/flywheel_defaults.json")
_DEFAULT_MIN_N: int = 10
_DEFAULT_MIN_SUCCESS_RATE: float = 0.55
_DEFAULT_MIN_NAMESPACE_COUNT: int = 2
_ROUTER_LAYER: str = "L6"
_ROUTER_NAME: str = "apps_qna_flywheel"


@dataclass(frozen=True)
class FlywheelArm:
    """One promoted arm in the flywheel snapshot."""

    arm_kind: str
    """``route`` (W4.1) or ``card`` (W4.2)."""

    arm: str
    n: int
    successes: int
    mean: float
    namespace_count: int


def _ledger_db_path() -> Path | None:
    try:
        from tools.ledgers.schema_registry import get

        return get(_LEDGER_NAME).db_path
    except (ImportError, KeyError):
        return None


def _aggregate_arm_outcomes(
    db_path: Path,
    event_kind: str,
    arm_field: str,
) -> dict[str, dict[str, Any]]:
    """Aggregate per-arm stats across all namespaces.

    Returns ``{arm: {n, successes, namespaces: set[str]}}``.
    """
    if not db_path.is_file():
        return {}
    sql = (
        "SELECT prediction_json, outcome_json FROM events "
        "WHERE event_kind = ? AND outcome_json IS NOT NULL"
    )
    counts: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"n": 0, "successes": 0, "namespaces": set()}
    )
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            for prediction_json, outcome_json in con.execute(sql, (event_kind,)):
                if not prediction_json or not outcome_json:
                    continue
                try:
                    pred = json.loads(prediction_json)
                    out = json.loads(outcome_json)
                except json.JSONDecodeError:
                    continue
                arm = pred.get(arm_field)
                ns = pred.get("namespace") or ""
                if not arm or not ns:
                    continue
                success = bool(out.get("success"))
                if not success:
                    if "asked" in out and "landed" in out:
                        success = bool(out.get("asked")) and bool(out.get("landed"))
                    elif "included" in out and "useful" in out:
                        success = bool(out.get("included")) and bool(out.get("useful"))
                bucket = counts[arm]
                bucket["n"] += 1
                if success:
                    bucket["successes"] += 1
                bucket["namespaces"].add(ns)
        finally:
            con.close()
    except sqlite3.Error as exc:
        _log.debug("flywheel aggregation sqlite error: %r", exc)
        return {}
    return dict(counts)


def _select_promoted_arms(
    aggregated: dict[str, dict[str, Any]],
    *,
    arm_kind: str,
    min_n: int,
    min_success_rate: float,
    min_namespace_count: int,
) -> list[FlywheelArm]:
    """Filter and rank arms by mean success rate."""
    promoted: list[FlywheelArm] = []
    for arm, stats in aggregated.items():
        n = stats["n"]
        successes = stats["successes"]
        namespace_count = len(stats["namespaces"])
        if n < min_n:
            continue
        if namespace_count < min_namespace_count:
            continue
        mean = successes / n if n > 0 else 0.0
        if mean < min_success_rate:
            continue
        promoted.append(
            FlywheelArm(
                arm_kind=arm_kind,
                arm=arm,
                n=n,
                successes=successes,
                mean=mean,
                namespace_count=namespace_count,
            )
        )
    promoted.sort(key=lambda a: (a.mean, a.n), reverse=True)
    return promoted


def compute_flywheel_defaults(
    *,
    db_path: Path | None = None,
    min_n: int = _DEFAULT_MIN_N,
    min_success_rate: float = _DEFAULT_MIN_SUCCESS_RATE,
    min_namespace_count: int = _DEFAULT_MIN_NAMESPACE_COUNT,
) -> dict[str, Any]:
    """Compute the flywheel snapshot dict.

    Returns::

        {
          "schema_version": 1,
          "promoted_routes": [{"arm": "executive_fit", "n": 30, "mean": 0.7, ...}, ...],
          "promoted_cards": [...],
          "thresholds": {"min_n": ..., "min_success_rate": ..., ...}
        }
    """
    path = db_path or _ledger_db_path()
    if path is None or not path.is_file():
        return {
            "schema_version": 1,
            "promoted_routes": [],
            "promoted_cards": [],
            "thresholds": {
                "min_n": min_n,
                "min_success_rate": min_success_rate,
                "min_namespace_count": min_namespace_count,
            },
            "warning": "Ledger DB not available",
        }

    routes_agg = _aggregate_arm_outcomes(path, "route_select", "selected_route")
    cards_agg = _aggregate_arm_outcomes(path, "paste_set_select", "selected_card")

    promoted_routes = _select_promoted_arms(
        routes_agg,
        arm_kind="route",
        min_n=min_n,
        min_success_rate=min_success_rate,
        min_namespace_count=min_namespace_count,
    )
    promoted_cards = _select_promoted_arms(
        cards_agg,
        arm_kind="card",
        min_n=min_n,
        min_success_rate=min_success_rate,
        min_namespace_count=min_namespace_count,
    )

    return {
        "schema_version": 1,
        "promoted_routes": [
            {
                "arm": arm.arm,
                "n": arm.n,
                "successes": arm.successes,
                "mean": round(arm.mean, 4),
                "namespace_count": arm.namespace_count,
            }
            for arm in promoted_routes
        ],
        "promoted_cards": [
            {
                "arm": arm.arm,
                "n": arm.n,
                "successes": arm.successes,
                "mean": round(arm.mean, 4),
                "namespace_count": arm.namespace_count,
            }
            for arm in promoted_cards
        ],
        "thresholds": {
            "min_n": min_n,
            "min_success_rate": min_success_rate,
            "min_namespace_count": min_namespace_count,
        },
    }


def emit_flywheel_snapshot(
    *,
    output_path: Path | None = None,
    db_path: Path | None = None,
    min_n: int = _DEFAULT_MIN_N,
    min_success_rate: float = _DEFAULT_MIN_SUCCESS_RATE,
    min_namespace_count: int = _DEFAULT_MIN_NAMESPACE_COUNT,
) -> Path:
    """Compute the snapshot and write it through the spine UWG.

    Emits a paired ROUTER_DECISION marker + ledger row per constitutional
    §29 (this IS a promotion-class decision).
    """
    snapshot = compute_flywheel_defaults(
        db_path=db_path,
        min_n=min_n,
        min_success_rate=min_success_rate,
        min_namespace_count=min_namespace_count,
    )
    target = output_path or _DEFAULT_FLYWHEEL_PATH
    payload = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"
    write_card_text(target, payload, encoding="utf-8")

    decision_id = uuid.uuid4().hex
    print(
        f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
        f"decision_id={decision_id} selected=snapshot_emit "
        f"promoted_routes={len(snapshot['promoted_routes'])} "
        f"promoted_cards={len(snapshot['promoted_cards'])}"
    )
    emit_pack_lifecycle_event(
        event_kind="promote_decision",
        prediction={
            "kind": "flywheel_snapshot",
            "promoted_route_count": len(snapshot["promoted_routes"]),
            "promoted_card_count": len(snapshot["promoted_cards"]),
            "thresholds": snapshot["thresholds"],
        },
        outcome={"snapshot_path": str(target)},
        score_band="promote" if (
            snapshot["promoted_routes"] or snapshot["promoted_cards"]
        ) else "insufficient_evidence",
        metadata={"decision_id": decision_id},
    )
    _log.info(
        "flywheel snapshot written to %s (promoted_routes=%d, promoted_cards=%d)",
        target,
        len(snapshot["promoted_routes"]),
        len(snapshot["promoted_cards"]),
    )
    return target


def load_flywheel_defaults(
    snapshot_path: Path | None = None,
) -> dict[str, Any]:
    """Load the most recent flywheel snapshot. Empty dict on any failure."""
    target = snapshot_path or _DEFAULT_FLYWHEEL_PATH
    if not target.is_file():
        return {}
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


__all__ = [
    "FlywheelArm",
    "compute_flywheel_defaults",
    "emit_flywheel_snapshot",
    "load_flywheel_defaults",
]
