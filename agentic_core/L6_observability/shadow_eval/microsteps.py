"""Microstep-grain L6 shadow observation helpers.

This module is intentionally app-agnostic. Callers pass expanded microstep
contract rows, optional apps_eval scorecard rows, and artifact observations as
plain mappings. L6 records observations and alignment facts only; it does not
grade, mutate, promote, or write durable policy state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from agentic_core.L6_observability.shadow_eval._digest import stamp_digest

L6_MICROSTEP_OBSERVATION_SCHEMA_VERSION = "agentic_core.l6_microstep_observation.v1"
L6_MICROSTEP_COVERAGE_SCHEMA_VERSION = "agentic_core.l6_microstep_coverage.v1"
L6_APPS_EVAL_ALIGNMENT_SCHEMA_VERSION = "agentic_core.l6_apps_eval_alignment.v1"
EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY = "CONTRACT_ONLY_ADVISORY"
EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF = "APPS_EVAL_BOUND_PROOF"
EVIDENCE_CLASS_FAILURE_TERMINAL_ADVISORY = "FAILURE_TERMINAL_ADVISORY"
EVIDENCE_CLASSES = frozenset(
    {
        EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY,
        EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF,
        EVIDENCE_CLASS_FAILURE_TERMINAL_ADVISORY,
    }
)

OBSERVED_STATUSES = frozenset({"OBSERVED", "MISSING", "UNKNOWN", "DRIFT", "VIOLATION"})
SHADOW_CLASSIFICATIONS = frozenset(
    {
        "NORMAL",
        "QUALITY_GAP",
        "COVERAGE_GAP",
        "AUTHORITY_GAP",
        "PROVIDER_GAP",
        "LINEAGE_GAP",
        "ORPHAN_OBSERVATION",
    }
)


@dataclass(slots=True)
class L6MicrostepObservation:
    record_type: str
    microstep_id: str
    stage_id: str
    lane_id: str
    apps_eval_row_id: str
    runtime_exhaust_bundle_id: str
    source_ref: str
    artifact_digest: str
    observed_status: str
    eval_verdict_seen: str
    shadow_classification: str
    root_cause_candidate: str
    future_run_recommendation: str
    current_run_mutation_assertion: bool = False
    l4_write_assertion: bool = False
    future_run_only: bool = True
    component_id: str = ""
    subcomponent_id: str = ""
    gate_id: str = ""
    artifact_role: str = ""
    required: bool = True
    severity: str = "INFO"
    orphan_observation: bool = False
    decisive_reason_seen: str = ""
    schema_version: str = L6_MICROSTEP_OBSERVATION_SCHEMA_VERSION
    deterministic_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def evidence_class_for_alignment_source(alignment_source: str) -> str:
    source = str(alignment_source or "").strip()
    if source == "apps_eval_scorecard_rows":
        return EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF
    if source == "failure_terminal_no_apps_eval_rows":
        return EVIDENCE_CLASS_FAILURE_TERMINAL_ADVISORY
    return EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY


def expand_microstep_contract(microstep_contract: Mapping[str, Any], lane_contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Expand global, lane-template, and cross-run microsteps into rows."""
    stage_order = {
        stage: idx
        for idx, stage in enumerate(
            microstep_contract.get(
                "stage_enum",
                ["U0", "L1", "L0", "C0", "PA", "L2", "X2", "X1D", "X3", "EXIT", "L6", "PACKAGE", "REGRESSION"],
            )
        )
    }
    rows: list[dict[str, Any]] = []
    rows.extend(dict(item) for item in microstep_contract.get("global_microsteps", []))
    lanes = [str(lane) for lane in lane_contract.get("generated_lanes", [])]
    for lane in lanes:
        for template in microstep_contract.get("lane_microstep_templates", []):
            item = dict(template)
            item["lane_id"] = lane
            item["microstep_id"] = str(item.pop("microstep_id_template")).format(lane=lane)
            item["gate_id"] = str(item.get("gate_id") or "").format(lane=lane)
            rows.append(item)
    rows.extend(dict(item) for item in microstep_contract.get("cross_run_microsteps", []))
    return sorted(
        rows,
        key=lambda row: (
            stage_order.get(str(row.get("stage_id")), 99),
            str(row.get("lane_id", "")),
            str(row.get("microstep_id", "")),
        ),
    )


def observation_to_dict(observation: L6MicrostepObservation) -> dict[str, Any]:
    return observation.to_dict()


def _status_from_eval_row(row: Mapping[str, Any]) -> str:
    verdict = str(row.get("verdict") or "UNKNOWN").upper()
    failure_mode = str(row.get("failure_mode") or "")
    if failure_mode == "coverage.missing_required_artifact":
        return "MISSING"
    if verdict in {"UNKNOWN", "NOT_RUN"}:
        return "UNKNOWN"
    if verdict == "FAIL":
        return "DRIFT"
    if verdict in {"PASS", "WARN", "NOT_APPLICABLE"}:
        return "OBSERVED"
    return "UNKNOWN"


def _classification_from_row(row: Mapping[str, Any], observed_status: str) -> str:
    failure_mode = str(row.get("failure_mode") or "")
    failure_family = str(row.get("failure_family") or "")
    stage_id = str(row.get("stage_id") or "")
    if observed_status == "MISSING" or failure_mode.startswith("coverage."):
        return "COVERAGE_GAP"
    if "lineage" in failure_mode.lower() or "evidence" in failure_mode.lower():
        return "LINEAGE_GAP"
    if stage_id == "X1D" or "provider" in failure_mode.lower():
        return "PROVIDER_GAP"
    if failure_family in {"microstep", "dependency"} or observed_status in {"DRIFT", "UNKNOWN"}:
        return "QUALITY_GAP"
    return "NORMAL"


def _recommendation(classification: str, status: str, microstep_id: str) -> str:
    if classification == "NORMAL":
        return "No current-run change; retain as observed evidence for future trend baselines."
    if classification == "ORPHAN_OBSERVATION":
        return f"Future-run only: register or remove orphan L6 observation for {microstep_id}."
    if status == "MISSING":
        return f"Future-run only: harden artifact emission or registry mapping for {microstep_id}."
    return f"Future-run only: inspect recurring {classification.lower()} at {microstep_id}."


def build_observation_from_eval_row(
    row: Mapping[str, Any],
    *,
    runtime_exhaust_bundle_id: str,
) -> L6MicrostepObservation:
    """Create an L6 observation from an apps_eval scorecard row."""
    observed_status = _status_from_eval_row(row)
    classification = _classification_from_row(row, observed_status)
    observation = L6MicrostepObservation(
        record_type="L6MicrostepObservation",
        microstep_id=str(row.get("microstep_id") or ""),
        stage_id=str(row.get("stage_id") or ""),
        lane_id=str(row.get("lane_id") or ""),
        apps_eval_row_id=str(row.get("row_id") or ""),
        runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
        source_ref=str(row.get("artifact_ref") or row.get("evidence_ref") or ""),
        artifact_digest=str(row.get("evidence_digest") or ""),
        observed_status=observed_status,
        eval_verdict_seen=str(row.get("verdict") or "UNKNOWN"),
        shadow_classification=classification,
        root_cause_candidate="UNKNOWN_ROOT_CAUSE" if classification == "NORMAL" else classification,
        future_run_recommendation=_recommendation(classification, observed_status, str(row.get("microstep_id") or "")),
        component_id=str(row.get("component_id") or ""),
        subcomponent_id=str(row.get("subcomponent_id") or ""),
        gate_id=str(row.get("gate_id") or ""),
        artifact_role=str(row.get("artifact_role") or ""),
        required=bool(row.get("required", True)),
        severity=str(row.get("severity") or "INFO"),
        decisive_reason_seen=str(row.get("decisive_reason") or ""),
    )
    return stamp_digest(observation)


def build_observation_from_contract_row(
    item: Mapping[str, Any],
    *,
    runtime_exhaust_bundle_id: str,
    source_ref: str = "",
    artifact_digest: str = "",
    eval_verdict_seen: str = "UNKNOWN",
    apps_eval_row_id: str = "",
    observed_status: str | None = None,
    decisive_reason_seen: str = "",
) -> L6MicrostepObservation:
    """Create an L6 observation from a contract row and observed artifact ref."""
    status = observed_status or ("OBSERVED" if source_ref else "MISSING")
    classification = "NORMAL" if status == "OBSERVED" else "COVERAGE_GAP"
    observation = L6MicrostepObservation(
        record_type="L6MicrostepObservation",
        microstep_id=str(item.get("microstep_id") or ""),
        stage_id=str(item.get("stage_id") or ""),
        lane_id=str(item.get("lane_id") or ""),
        apps_eval_row_id=apps_eval_row_id,
        runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
        source_ref=source_ref,
        artifact_digest=artifact_digest,
        observed_status=status,
        eval_verdict_seen=eval_verdict_seen,
        shadow_classification=classification,
        root_cause_candidate="UNKNOWN_ROOT_CAUSE" if classification == "NORMAL" else classification,
        future_run_recommendation=_recommendation(classification, status, str(item.get("microstep_id") or "")),
        component_id=str(item.get("component_id") or ""),
        subcomponent_id=str(item.get("subcomponent_id") or ""),
        gate_id=str(item.get("gate_id") or ""),
        artifact_role=str(item.get("artifact_role") or ""),
        required=bool(item.get("required", True)),
        severity=str(item.get("severity") or "INFO"),
        decisive_reason_seen=decisive_reason_seen,
    )
    return stamp_digest(observation)


def build_orphan_observation(
    *,
    microstep_id: str,
    runtime_exhaust_bundle_id: str,
    source_ref: str,
    artifact_digest: str = "",
    stage_id: str = "",
    lane_id: str = "",
) -> L6MicrostepObservation:
    observation = L6MicrostepObservation(
        record_type="L6MicrostepObservation",
        microstep_id=microstep_id,
        stage_id=stage_id,
        lane_id=lane_id,
        apps_eval_row_id="",
        runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
        source_ref=source_ref,
        artifact_digest=artifact_digest,
        observed_status="UNKNOWN",
        eval_verdict_seen="NOT_RUN",
        shadow_classification="ORPHAN_OBSERVATION",
        root_cause_candidate="COVERAGE_GAP",
        future_run_recommendation=_recommendation("ORPHAN_OBSERVATION", "UNKNOWN", microstep_id),
        required=False,
        orphan_observation=True,
    )
    return stamp_digest(observation)


def build_observations_from_eval_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    runtime_exhaust_bundle_id: str,
) -> list[L6MicrostepObservation]:
    return [
        build_observation_from_eval_row(row, runtime_exhaust_bundle_id=runtime_exhaust_bundle_id)
        for row in rows
    ]


def build_microstep_coverage(observations: Iterable[L6MicrostepObservation | Mapping[str, Any]]) -> dict[str, Any]:
    rows = [obs.to_dict() if isinstance(obs, L6MicrostepObservation) else dict(obs) for obs in observations]
    required = [row for row in rows if row.get("required", True) and not row.get("orphan_observation")]
    status_counts: dict[str, int] = {}
    classification_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("observed_status") or "UNKNOWN")
        classification = str(row.get("shadow_classification") or "QUALITY_GAP")
        status_counts[status] = status_counts.get(status, 0) + 1
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
    missing = [row["microstep_id"] for row in required if row.get("observed_status") == "MISSING"]
    unknown = [row["microstep_id"] for row in required if row.get("observed_status") == "UNKNOWN"]
    violations = [row["microstep_id"] for row in required if row.get("observed_status") == "VIOLATION"]
    return {
        "schema_version": L6_MICROSTEP_COVERAGE_SCHEMA_VERSION,
        "rows_seen": len(rows),
        "required_rows_seen": len(required),
        "observed_required": sum(1 for row in required if row.get("observed_status") == "OBSERVED"),
        "missing_required": len(missing),
        "unknown_required": len(unknown),
        "violation_required": len(violations),
        "orphan_observations": sum(1 for row in rows if row.get("orphan_observation")),
        "coverage_complete": not missing and not unknown and not violations,
        "status_counts": dict(sorted(status_counts.items())),
        "shadow_classification_counts": dict(sorted(classification_counts.items())),
        "missing_microstep_ids": missing,
        "unknown_microstep_ids": unknown,
        "violation_microstep_ids": violations,
    }


def build_microstep_rca(observations: Iterable[L6MicrostepObservation | Mapping[str, Any]]) -> dict[str, Any]:
    rows = [obs.to_dict() if isinstance(obs, L6MicrostepObservation) else dict(obs) for obs in observations]
    gaps = [
        row
        for row in rows
        if row.get("shadow_classification") != "NORMAL" or row.get("observed_status") != "OBSERVED"
    ]
    repeated: dict[str, dict[str, Any]] = {}
    for row in gaps:
        key = "|".join(
            [
                str(row.get("stage_id") or ""),
                str(row.get("lane_id") or ""),
                str(row.get("artifact_role") or ""),
                str(row.get("shadow_classification") or ""),
                str(row.get("observed_status") or ""),
            ]
        )
        bucket = repeated.setdefault(
            key,
            {
                "recurrence_key": key,
                "stage_id": str(row.get("stage_id") or ""),
                "lane_id": str(row.get("lane_id") or ""),
                "artifact_role": str(row.get("artifact_role") or ""),
                "shadow_classification": str(row.get("shadow_classification") or ""),
                "observed_status": str(row.get("observed_status") or ""),
                "recurrence_count": 0,
                "microstep_ids": [],
            },
        )
        bucket["recurrence_count"] += 1
        bucket["microstep_ids"].append(str(row.get("microstep_id") or ""))
    trace_rows = [row for row in rows if row.get("artifact_role") == "trace_reconciliation"]
    trace_gaps = [row for row in trace_rows if row in gaps]
    return {
        "schema_version": "agentic_core.l6_microstep_rca.v1",
        "gap_count": len(gaps),
        "root_cause_candidates": sorted({str(row.get("root_cause_candidate") or "UNKNOWN_ROOT_CAUSE") for row in gaps}),
        "first_gap_microstep_id": str(gaps[0].get("microstep_id") or "") if gaps else "",
        "first_blocking_gap": dict(gaps[0]) if gaps else {},
        "gap_groups_by_stage": _count_by(gaps, "stage_id"),
        "gap_groups_by_lane": _count_by(gaps, "lane_id"),
        "gap_groups_by_artifact_role": _count_by(gaps, "artifact_role"),
        "gap_groups_by_shadow_classification": _count_by(gaps, "shadow_classification"),
        "trace_reconciliation_verdict": "GAP" if trace_gaps else "OBSERVED" if trace_rows else "NOT_OBSERVED",
        "top_repeated_gap_candidates": sorted(
            repeated.values(),
            key=lambda item: (-int(item["recurrence_count"]), str(item["recurrence_key"])),
        )[:10],
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
    }


def _count_by(rows: Iterable[Mapping[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get(field) or "UNKNOWN")
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def build_microstep_patterns(observations: Iterable[L6MicrostepObservation | Mapping[str, Any]]) -> dict[str, Any]:
    rows = [obs.to_dict() if isinstance(obs, L6MicrostepObservation) else dict(obs) for obs in observations]
    coverage = build_microstep_coverage(rows)
    recurrence: dict[str, int] = {}
    severity_rollup: dict[str, int] = {}
    for row in rows:
        key = "|".join(
            [
                str(row.get("stage_id") or ""),
                str(row.get("lane_id") or ""),
                str(row.get("artifact_role") or ""),
                str(row.get("observed_status") or ""),
            ]
        )
        recurrence[key] = recurrence.get(key, 0) + 1
        severity = str(row.get("severity") or "INFO")
        severity_rollup[severity] = severity_rollup.get(severity, 0) + 1
    repeated = sorted(recurrence.items(), key=lambda item: (-item[1], item[0]))
    gap_present = any(
        row.get("shadow_classification") != "NORMAL" or row.get("observed_status") != "OBSERVED"
        for row in rows
    )
    pattern_status = "BASELINE"
    if gap_present:
        pattern_status = "REGRESSION_CANDIDATE" if any(count > 1 for _, count in repeated) else "WATCH"
    return {
        "schema_version": "agentic_core.l6_microstep_patterns.v1",
        "status_counts": coverage["status_counts"],
        "shadow_classification_counts": coverage["shadow_classification_counts"],
        "pattern_status": pattern_status,
        "recurrence_key": repeated[0][0] if repeated else "",
        "recurrence_count": repeated[0][1] if repeated else 0,
        "severity_rollup": dict(sorted(severity_rollup.items())),
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
    }


def build_future_run_proposals(observations: Iterable[L6MicrostepObservation | Mapping[str, Any]]) -> dict[str, Any]:
    rows = [obs.to_dict() if isinstance(obs, L6MicrostepObservation) else dict(obs) for obs in observations]
    proposals = [
        {
            "proposal_id": canonical_digest(
                {
                    "microstep_id": row.get("microstep_id"),
                    "artifact_role": row.get("artifact_role"),
                    "observed_status": row.get("observed_status"),
                }
            ),
            "microstep_id": row.get("microstep_id"),
            "proposal_type": "FUTURE_RUN_HARDENING",
            "target_surface": row.get("artifact_role") or row.get("stage_id") or "unknown_surface",
            "recommended_owner": "future_run_observability_owner",
            "evidence_refs": [row.get("source_ref")] if row.get("source_ref") else [],
            "recommendation": row.get("future_run_recommendation"),
            "blocked_current_run_mutation": True,
            "requires_gauntlet": True,
            "uwg_required_for_activation": True,
            "current_run_mutation_assertion": False,
            "l4_write_assertion": False,
            "future_run_only": True,
        }
        for row in rows
        if row.get("shadow_classification") != "NORMAL" or row.get("observed_status") != "OBSERVED"
    ]
    return {
        "schema_version": "agentic_core.l6_microstep_future_run_proposals.v1",
        "proposal_count": len(proposals),
        "proposals": proposals,
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
    }


def build_apps_eval_alignment(
    *,
    run_id: str,
    runtime_exhaust_bundle_id: str,
    microstep_contract_digest: str,
    apps_eval_scorecard_ref: str,
    l6_observation_ref: str,
    apps_eval_rows: Iterable[Mapping[str, Any]],
    l6_observations: Iterable[L6MicrostepObservation | Mapping[str, Any]],
    alignment_source: str = "apps_eval_scorecard_rows",
    apps_eval_rows_bound: bool | None = None,
) -> dict[str, Any]:
    eval_rows = [dict(row) for row in apps_eval_rows if row.get("required", True)]
    obs_rows = [obs.to_dict() if isinstance(obs, L6MicrostepObservation) else dict(obs) for obs in l6_observations]
    eval_by_id = {str(row.get("microstep_id") or ""): row for row in eval_rows}
    obs_by_id = {
        str(row.get("microstep_id") or ""): row
        for row in obs_rows
        if not row.get("orphan_observation") and row.get("microstep_id")
    }
    orphan_observations = sorted(
        str(row.get("microstep_id") or "")
        for row in obs_rows
        if row.get("orphan_observation") and row.get("microstep_id")
    )
    missing_in_l6 = sorted(set(eval_by_id) - set(obs_by_id))
    missing_in_apps_eval = sorted(set(obs_by_id) - set(eval_by_id))
    verdict_mismatches = []
    for microstep_id in sorted(set(eval_by_id) & set(obs_by_id)):
        eval_verdict = str(eval_by_id[microstep_id].get("verdict") or "UNKNOWN")
        seen_verdict = str(obs_by_id[microstep_id].get("eval_verdict_seen") or "UNKNOWN")
        if seen_verdict != eval_verdict:
            verdict_mismatches.append(
                {
                    "microstep_id": microstep_id,
                    "apps_eval_verdict": eval_verdict,
                    "l6_eval_verdict_seen": seen_verdict,
                }
            )
    authority_mismatch = any(
        row.get("current_run_mutation_assertion") is not False
        or row.get("l4_write_assertion") is not False
        or row.get("future_run_only") is not True
        for row in obs_rows
    )
    resolved_rows_bound = (
        alignment_source == "apps_eval_scorecard_rows"
        if apps_eval_rows_bound is None
        else bool(apps_eval_rows_bound)
    )
    return {
        "schema_version": L6_APPS_EVAL_ALIGNMENT_SCHEMA_VERSION,
        "run_id": run_id,
        "runtime_exhaust_bundle_id": runtime_exhaust_bundle_id,
        "microstep_contract_digest": microstep_contract_digest,
        "apps_eval_scorecard_ref": apps_eval_scorecard_ref,
        "l6_observation_ref": l6_observation_ref,
        "alignment_source": alignment_source,
        "apps_eval_rows_bound": resolved_rows_bound,
        "evidence_class": evidence_class_for_alignment_source(alignment_source),
        "contract_only_alignment_is_not_eval_proof": not resolved_rows_bound,
        "coverage_join_key": "microstep_id",
        "rows_expected": len(eval_rows),
        "apps_eval_rows_seen": len(eval_rows),
        "l6_observation_rows_seen": len(obs_rows),
        "missing_in_apps_eval": missing_in_apps_eval,
        "missing_in_l6": missing_in_l6,
        "orphan_observations": orphan_observations,
        "verdict_mismatches": verdict_mismatches,
        "authority_mismatch": authority_mismatch,
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
    }


__all__ = [
    "L6_APPS_EVAL_ALIGNMENT_SCHEMA_VERSION",
    "L6_MICROSTEP_COVERAGE_SCHEMA_VERSION",
    "L6_MICROSTEP_OBSERVATION_SCHEMA_VERSION",
    "L6MicrostepObservation",
    "build_apps_eval_alignment",
    "build_future_run_proposals",
    "build_microstep_coverage",
    "build_microstep_patterns",
    "build_microstep_rca",
    "build_observation_from_contract_row",
    "build_observation_from_eval_row",
    "build_observations_from_eval_rows",
    "build_orphan_observation",
    "canonical_digest",
    "evidence_class_for_alignment_source",
    "EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF",
    "EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY",
    "EVIDENCE_CLASS_FAILURE_TERMINAL_ADVISORY",
    "EVIDENCE_CLASSES",
    "expand_microstep_contract",
    "observation_to_dict",
]
