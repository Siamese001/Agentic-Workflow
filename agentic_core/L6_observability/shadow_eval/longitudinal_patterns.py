"""Longitudinal L6 pattern synthesis over distinct completed runs."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any, Iterable, Mapping

LONGITUDINAL_PATTERN_SCHEMA_VERSION = "agentic_core.l6_longitudinal_patterns.v1"


def _digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _recurrence_key(row: Mapping[str, Any]) -> tuple[str, ...]:
    return (
        str(row.get("app_id") or "apps_rg"),
        str(row.get("lane_id") or ""),
        str(row.get("microstep_id") or ""),
        str(row.get("failure_mode") or row.get("shadow_classification") or ""),
        str(row.get("artifact_role") or ""),
        str(row.get("policy_version") or row.get("rubric_version") or ""),
    )


def synthesize_longitudinal_patterns(
    observations: Iterable[Mapping[str, Any]],
    *,
    minimum_distinct_runs: int = 2,
    window_size: int = 1000,
) -> dict[str, Any]:
    if minimum_distinct_runs < 2:
        raise ValueError("minimum_distinct_runs must be >= 2")
    rows = [dict(row) for row in observations][-window_size:]
    gaps = [
        row
        for row in rows
        if row.get("shadow_classification") != "NORMAL"
        or row.get("observed_status") != "OBSERVED"
    ]
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in gaps:
        grouped[_recurrence_key(row)].append(row)

    patterns: list[dict[str, Any]] = []
    proposals: list[dict[str, Any]] = []
    for key, group in grouped.items():
        run_ids = sorted({str(row.get("run_id") or "") for row in group if row.get("run_id")})
        distinct_runs = len(run_ids)
        if distinct_runs < minimum_distinct_runs:
            continue
        first_seen = min(str(row.get("observed_at") or "") for row in group)
        last_seen = max(str(row.get("observed_at") or "") for row in group)
        pattern_id = _digest({"recurrence_key": key, "run_ids": run_ids})
        pattern = {
            "pattern_id": pattern_id,
            "recurrence_key": "|".join(key),
            "app_id": key[0],
            "lane_id": key[1],
            "microstep_id": key[2],
            "failure_mode": key[3],
            "artifact_role": key[4],
            "policy_or_rubric_version": key[5],
            "distinct_run_count": distinct_runs,
            "run_ids": run_ids,
            "observation_count": len(group),
            "first_seen": first_seen,
            "last_seen": last_seen,
            "pattern_status": "REGRESSION_CANDIDATE",
        }
        patterns.append(pattern)
        proposals.append(
            {
                "proposal_id": _digest({"pattern_id": pattern_id, "type": "FUTURE_RUN_HARDENING"}),
                "pattern_id": pattern_id,
                "proposal_type": "FUTURE_RUN_HARDENING",
                "target_surface": key[4] or key[2],
                "recommended_owner": "apps_rg_observability_owner",
                "completed_eval_seal_required": True,
                "rca_packet_required": True,
                "blast_radius_required": True,
                "test_plan_required": True,
                "rollback_plan_required": True,
                "requires_gauntlet": True,
                "uwg_required_for_activation": True,
                "current_run_effect": "none",
                "future_run_only": True,
            }
        )

    patterns.sort(key=lambda item: (-item["distinct_run_count"], item["recurrence_key"]))
    proposals.sort(key=lambda item: item["proposal_id"])
    return {
        "schema_version": LONGITUDINAL_PATTERN_SCHEMA_VERSION,
        "minimum_distinct_runs": minimum_distinct_runs,
        "rows_seen": len(rows),
        "gap_rows_seen": len(gaps),
        "pattern_count": len(patterns),
        "patterns": patterns,
        "proposal_count": len(proposals),
        "proposals": proposals,
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
    }


__all__ = ["LONGITUDINAL_PATTERN_SCHEMA_VERSION", "synthesize_longitudinal_patterns"]
