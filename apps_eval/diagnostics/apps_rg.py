"""Shadow-only apps_rg diagnostics derived from completed run artifacts."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

from apps_eval.contracts import (
    AppOutputSnapshot,
    DiagnosticObservationV1,
    DiagnosticSourceArtifactRef,
    DiagnosticSummaryV1,
    ScorecardRow,
)
from apps_eval.artifacts.apps_rg_resolver import ResolvedAppsRgArtifact, resolve_apps_rg_artifact
from apps_eval.coverage.apps_rg import load_apps_rg_contracts

_AUTHORITY = "post_run_l6_shadow_only"
_UNSAFE_E4_REPAIRS = [
    "missing_graph_evidence",
    "missing_briefing",
    "broader_retrieval",
    "route_change",
    "provider_substitution",
    "hitl",
    "l4_learning",
]


def _canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _path_digest(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _json_payload(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _snapshot_source(snapshot: AppOutputSnapshot, snapshot_ref: str, snapshot_digest: str) -> DiagnosticSourceArtifactRef:
    digest = snapshot_digest or snapshot.deterministic_hash or _canonical_digest(snapshot.to_dict())
    ref = snapshot_ref or snapshot.run_root or f"snapshot:{snapshot.scenario_id}"
    return DiagnosticSourceArtifactRef(
        artifact_role="app_output_snapshot",
        artifact_ref=str(ref),
        artifact_digest=digest,
    )


def _row_source(row: ScorecardRow) -> DiagnosticSourceArtifactRef:
    return DiagnosticSourceArtifactRef(
        artifact_role=row.artifact_role or "scorecard_row",
        artifact_ref=row.artifact_ref or f"scorecard_row:{row.row_id}",
        artifact_digest=row.evidence_digest or _canonical_digest(row.to_dict()),
    )


def _artifact_index_source(snapshot: AppOutputSnapshot, role: str, fallback: DiagnosticSourceArtifactRef) -> DiagnosticSourceArtifactRef:
    value = snapshot.artifact_index.get(role)
    if value in (None, "", [], {}):
        return fallback
    return DiagnosticSourceArtifactRef(
        artifact_role=role,
        artifact_ref=str(_as_list(value)[0]),
        artifact_digest=_canonical_digest(value),
    )


def _resolved_source(resolved: ResolvedAppsRgArtifact, fallback: DiagnosticSourceArtifactRef) -> DiagnosticSourceArtifactRef:
    if not resolved.found:
        return fallback
    return DiagnosticSourceArtifactRef(
        artifact_role=resolved.artifact_role,
        artifact_ref=resolved.artifact_ref,
        artifact_digest=resolved.evidence_digest or _canonical_digest(resolved.payload),
    )


def _run_root(snapshot: AppOutputSnapshot) -> Path | None:
    return Path(snapshot.run_root).resolve() if snapshot.run_root else None


def _load_root_json(snapshot: AppOutputSnapshot, rel_paths: list[str]) -> tuple[str, str, Any]:
    root = _run_root(snapshot)
    if root is None:
        return "", "", None
    for rel in rel_paths:
        path = root / rel
        if path.is_file():
            return path.as_posix(), _path_digest(path), _json_payload(path)
    return "", "", None


def _count_nonempty(value: Any) -> int:
    if isinstance(value, dict):
        return len([key for key, item in value.items() if key and item not in (None, "", [], {})])
    if isinstance(value, list):
        return len([item for item in value if item not in (None, "", [], {})])
    return 1 if value not in (None, "", [], {}) else 0


def _graph_metrics(payload: Any) -> dict[str, Any]:
    data = _as_dict(payload)
    receipt = _as_dict(data.get("sqlite_selection_receipt") or data.get("selection_receipt"))
    metrics = _as_dict(data.get("binding_metrics"))
    selected_by_fact = data.get("selected_by_fact")
    rejected_by_fact = data.get("rejected_by_fact")
    selected_candidates = data.get("selected_candidates")
    rejection_receipts = data.get("rejection_receipts") or receipt.get("rejection_receipts")
    selected_count = (
        int(metrics.get("sqlite_selected_skill_count") or 0)
        or _count_nonempty(selected_candidates)
        or _count_nonempty(selected_by_fact)
    )
    candidate_count = int(metrics.get("sqlite_ranked_candidate_count") or data.get("candidate_count") or 0)
    rejected_count = (
        int(metrics.get("rejected_sibling_skill_count") or 0)
        or _count_nonempty(rejected_by_fact)
        or _count_nonempty(rejection_receipts)
    )
    return {
        "candidate_count": candidate_count,
        "selected_count": selected_count,
        "rejected_sibling_count": rejected_count,
        "path_signature_count": _count_nonempty(data.get("path_signature") or data.get("path_signatures")),
        "direct_support_count": int(metrics.get("direct_support_count") or 0),
        "adjacent_only_count": int(metrics.get("adjacent_only_count") or 0),
        "metric_bucket_counts": metrics.get("metric_bucket_counts") or receipt.get("metric_bucket_counts") or {},
        "skill_family_counts": metrics.get("skill_family_counts") or receipt.get("skill_family_counts") or {},
        "rejection_reason_count": _count_nonempty(rejection_receipts),
    }


def _x1d_category(payload: Any) -> str:
    data = _as_dict(payload)
    if not data:
        return "UNKNOWN"
    for key in (
        "diagnostic_category",
        "x1d_diagnostic_category",
        "judge_diagnostic_category",
        "category",
    ):
        value = str(data.get(key) or "").strip().upper()
        if value:
            return value
    if data.get("provider_unavailable") is True:
        return "PROVIDER_UNAVAILABLE"
    if data.get("schema_or_parser_blocked") is True:
        return "JUDGE_SCHEMA_OR_PARSER_BLOCKED"
    if data.get("x1d_judge_execution_mismatch") is True:
        return "JUDGE_EXECUTION_PROVIDER_MISMATCH"
    if data.get("model_backed_fail") is True:
        return "MODEL_BACKED_FAIL"
    if data.get("model_backed_pass") is True:
        return "MODEL_BACKED_PASS"
    verdict = str(data.get("overall") or data.get("verdict") or "").upper()
    if verdict == "PASS":
        return "MODEL_BACKED_PASS"
    if verdict == "FAIL":
        return "MODEL_BACKED_FAIL"
    return "UNKNOWN"


def _obs(
    *,
    diagnostic_id: str,
    family: str,
    suite_id: str,
    scenario_id: str,
    run_id: str,
    stage_id: str,
    depends_on_microstep_id: str,
    source: DiagnosticSourceArtifactRef,
    verdict: str,
    observed: Any,
    threshold: Any,
    reason: str,
    lane_id: str = "",
    evidence_ref: str = "",
    evidence_digest: str = "",
    action: str = "",
) -> DiagnosticObservationV1:
    return DiagnosticObservationV1(
        diagnostic_id=diagnostic_id,
        diagnostic_family=family,
        suite_id=suite_id,
        scenario_id=scenario_id,
        app_id="apps_rg",
        run_id=run_id,
        lane_id=lane_id,
        stage_id=stage_id,
        depends_on_microstep_id=depends_on_microstep_id,
        source_artifact_refs=[source],
        diagnostic_verdict=verdict,
        observed_value=observed,
        threshold=threshold,
        reason=reason,
        recommended_future_action=action,
        evidence_ref=evidence_ref,
        evidence_digest=evidence_digest,
        promotion_state="shadow",
        existing_row_overlap="enriches",
        authority=_AUTHORITY,
    )


def _summary(suite_id: str, run_id: str, rows: list[DiagnosticObservationV1]) -> DiagnosticSummaryV1:
    family_counts = Counter(row.diagnostic_family for row in rows)
    stage_counts = Counter(str(row.stage_id) for row in rows)
    lane_counts = Counter(row.lane_id for row in rows if row.lane_id)
    verdict_counts = Counter(str(row.diagnostic_verdict) for row in rows)
    promotion_counts = Counter(str(row.promotion_state) for row in rows)
    return DiagnosticSummaryV1(
        suite_id=suite_id,
        app_id="apps_rg",
        run_id=run_id,
        observation_count=len(rows),
        family_counts={key: family_counts[key] for key in sorted(family_counts)},
        stage_counts={key: stage_counts[key] for key in sorted(stage_counts)},
        lane_counts={key: lane_counts[key] for key in sorted(lane_counts)},
        verdict_counts={key: verdict_counts[key] for key in sorted(verdict_counts)},
        promotion_state_counts={key: promotion_counts[key] for key in sorted(promotion_counts)},
    )


def _index_rows(scorecard_rows: list[ScorecardRow]) -> dict[str, dict[str, list[ScorecardRow]]]:
    indexed: dict[str, dict[str, list[ScorecardRow]]] = {
        "stage": {},
        "lane": {},
        "role": {},
        "microstep": {},
        "gate": {},
    }
    for row in scorecard_rows:
        for index_name, value in (
            ("stage", str(row.stage_id or "")),
            ("lane", row.lane_id),
            ("role", row.artifact_role),
            ("microstep", row.microstep_id),
            ("gate", row.gate_id),
        ):
            if value:
                indexed[index_name].setdefault(str(value), []).append(row)
    return indexed


def _first_row(rows: list[ScorecardRow]) -> ScorecardRow | None:
    return rows[0] if rows else None


def _lane_ids(indexed: dict[str, dict[str, list[ScorecardRow]]]) -> list[str]:
    return sorted(indexed["lane"])


def _row_payload(row: ScorecardRow | None) -> Any:
    if row is None or not row.artifact_ref:
        return None
    try:
        return _json_payload(Path(row.artifact_ref))
    except (OSError, TypeError, ValueError):
        return None


def _row_source_or_snapshot(row: ScorecardRow | None, fallback: DiagnosticSourceArtifactRef) -> DiagnosticSourceArtifactRef:
    return _row_source(row) if row else fallback


def build_apps_rg_diagnostics(
    *,
    suite_id: str,
    scenario_id: str,
    snapshot: AppOutputSnapshot,
    run_id: str,
    scorecard_rows: list[ScorecardRow],
    snapshot_ref: str = "",
    snapshot_digest: str = "",
) -> dict[str, Any]:
    """Build shadow diagnostics from completed apps_rg artifacts.

    The collector never calls product runtime code. It only inspects the normalized
    snapshot, resolved scorecard rows, and files already present under run_root.
    """
    if snapshot.app_id != "apps_rg":
        raise ValueError(f"apps_rg diagnostics require apps_rg snapshot, got {snapshot.app_id!r}")

    source = _snapshot_source(snapshot, snapshot_ref, snapshot_digest)
    artifact_contract = load_apps_rg_contracts()["artifact_contract"]
    indexed_rows = _index_rows(scorecard_rows)
    observations: list[DiagnosticObservationV1] = []

    graph_artifact = resolve_apps_rg_artifact(
        snapshot=snapshot,
        role="graph_selection_rationale",
        artifact_contract=artifact_contract,
    )
    graph_ref = graph_artifact.artifact_ref
    graph_digest = graph_artifact.evidence_digest
    graph_payload = graph_artifact.payload
    if not graph_artifact.found:
        graph_ref, graph_digest, graph_payload = _load_root_json(
        snapshot,
        [
            "native_c03_final_evidence.json",
            "graph_selection_rationale.json",
            "c03_promotion_candidates.json",
            "selected_graph_evidence_plan.json",
        ],
        )
    graph_source = (
        _resolved_source(graph_artifact, source)
        if graph_artifact.found
        else DiagnosticSourceArtifactRef("graph_receipt", graph_ref, graph_digest)
        if graph_ref and graph_digest
        else _artifact_index_source(snapshot, "graph_selection_rationale", source)
    )
    graph_metrics = _graph_metrics(graph_payload)
    observations.append(
        _obs(
            diagnostic_id=f"{scenario_id}.graph_traversal.sufficiency",
            family="graph_traversal",
            suite_id=suite_id,
            scenario_id=scenario_id,
            run_id=run_id,
            stage_id="C0",
            depends_on_microstep_id="C0.evidence_manifest.present",
            source=graph_source,
            verdict="PASS" if graph_metrics["selected_count"] > 0 else "NOT_OBSERVED",
            observed=graph_metrics,
            threshold={"selected_count": ">0"},
            reason="graph traversal receipt observed" if graph_metrics["selected_count"] > 0 else "graph traversal receipt not observed",
            evidence_ref=graph_ref,
            evidence_digest=graph_digest,
            action="review graph receipt emission if graph diagnostics stay sparse",
        )
    )

    briefing = snapshot.provenance.get("resolved_inputs", {}) if isinstance(snapshot.provenance, dict) else {}
    briefing_ref = str(briefing.get("manual_brief_ref") or briefing.get("briefing_ref") or "")
    observations.append(
        _obs(
            diagnostic_id=f"{scenario_id}.briefing_to_graph.grounding",
            family="briefing_to_graph",
            suite_id=suite_id,
            scenario_id=scenario_id,
            run_id=run_id,
            stage_id="C0",
            depends_on_microstep_id="C0.evidence_manifest.present",
            source=source,
            verdict="PASS" if briefing_ref or graph_metrics["selected_count"] > 0 else "NOT_OBSERVED",
            observed={"manual_brief_ref": briefing_ref, "graph_selected_count": graph_metrics["selected_count"]},
            threshold={"manual_brief_ref": "present or graph targeting receipt present"},
            reason="briefing/graph targeting evidence observed" if briefing_ref or graph_metrics["selected_count"] > 0 else "briefing-to-graph evidence not observed",
            action="ensure apps_research briefing refs and graph targeting receipts are indexed",
        )
    )

    retrieval_observed = {
        "raw_artifact_refs": len(snapshot.raw_artifact_refs),
        "claims": len(snapshot.claims),
        "artifacts": len(snapshot.artifacts),
        "allowed_fact_refs": len(snapshot.provenance.get("evidence_refs", [])) if isinstance(snapshot.provenance, dict) else 0,
    }
    observations.append(
        _obs(
            diagnostic_id=f"{scenario_id}.retrieval_quality.coverage",
            family="retrieval_quality",
            suite_id=suite_id,
            scenario_id=scenario_id,
            run_id=run_id,
            stage_id="C0",
            depends_on_microstep_id="C0.evidence_manifest.present",
            source=source,
            verdict="PASS" if max(retrieval_observed.values()) > 0 else "NOT_OBSERVED",
            observed=retrieval_observed,
            threshold={"any_retrieval_evidence": ">0"},
            reason="retrieval evidence observed" if max(retrieval_observed.values()) > 0 else "retrieval evidence not observed",
            action="index retrieval namespace and lineage receipts for richer diagnostics",
        )
    )

    l2_rows = indexed_rows["stage"].get("L2", [])
    l2_failures = [row.failure_mode for row in l2_rows if row.verdict not in {"PASS", "NOT_APPLICABLE"}]
    observations.append(
        _obs(
            diagnostic_id=f"{scenario_id}.l2_failure_retry.initial_state",
            family="l2_failure_retry",
            suite_id=suite_id,
            scenario_id=scenario_id,
            run_id=run_id,
            stage_id="L2",
            depends_on_microstep_id="L2.*.output_present",
            source=_row_source(l2_rows[0]) if l2_rows else source,
            verdict="WARN" if l2_failures else "PASS" if l2_rows else "NOT_OBSERVED",
            observed={"l2_row_count": len(l2_rows), "non_pass_failure_modes": l2_failures},
            threshold={"non_pass_failure_modes": 0},
            reason="L2 non-pass rows observed" if l2_failures else "L2 rows did not expose initial failure",
            action="preserve provider attempt spans and recovered-on-retry receipts",
        )
    )

    lane_ids = _lane_ids(indexed_rows)
    if lane_ids:
        for lane_id in lane_ids:
            lane_rows = indexed_rows["lane"][lane_id]
            lane_l2_rows = [row for row in lane_rows if str(row.stage_id) == "L2"]
            lane_l2_failures = [row.failure_mode for row in lane_l2_rows if row.verdict not in {"PASS", "NOT_APPLICABLE"}]
            observations.append(
                _obs(
                    diagnostic_id=f"{scenario_id}.{lane_id}.l2_failure_retry.initial_state",
                    family="l2_failure_retry",
                    suite_id=suite_id,
                    scenario_id=scenario_id,
                    run_id=run_id,
                    lane_id=lane_id,
                    stage_id="L2",
                    depends_on_microstep_id=f"{lane_id}.L2.output.present",
                    source=_row_source_or_snapshot(_first_row(lane_l2_rows), source),
                    verdict="WARN" if lane_l2_failures else "PASS" if lane_l2_rows else "NOT_OBSERVED",
                    observed={"l2_row_count": len(lane_l2_rows), "non_pass_failure_modes": lane_l2_failures},
                    threshold={"non_pass_failure_modes": 0},
                    reason="lane L2 non-pass rows observed" if lane_l2_failures else "lane L2 rows did not expose initial failure",
                    action="preserve provider attempt spans and recovered-on-retry receipts per lane",
                )
            )

            lane_x2_rows = [row for row in lane_rows if str(row.stage_id) == "X2"]
            lane_x2_failures = [row.failure_mode for row in lane_x2_rows if row.verdict not in {"PASS", "NOT_APPLICABLE"}]
            observations.append(
                _obs(
                    diagnostic_id=f"{scenario_id}.{lane_id}.x2_gate_quality.verdict",
                    family="x2_gate_quality",
                    suite_id=suite_id,
                    scenario_id=scenario_id,
                    run_id=run_id,
                    lane_id=lane_id,
                    stage_id="X2",
                    depends_on_microstep_id=f"{lane_id}.X2.gates.pass",
                    source=_row_source_or_snapshot(_first_row(lane_x2_rows), source),
                    verdict="WARN" if lane_x2_failures else "PASS" if lane_x2_rows else "NOT_OBSERVED",
                    observed={"x2_row_count": len(lane_x2_rows), "non_pass_failure_modes": lane_x2_failures},
                    threshold={"x2_non_pass_failure_modes": 0},
                    reason="lane X2 gate non-pass rows observed" if lane_x2_failures else "lane X2 gates did not expose failure",
                    action="trend deterministic gate failures per lane",
                )
            )

            lane_x1d_rows = [row for row in lane_rows if str(row.stage_id) == "X1D"]
            x1d_row = _first_row([row for row in lane_x1d_rows if row.gate_id == "x1d_judge_result_pass"] or lane_x1d_rows)
            x1d_category = _x1d_category(_row_payload(x1d_row))
            observations.append(
                _obs(
                    diagnostic_id=f"{scenario_id}.{lane_id}.x1d_judge_calibration.category",
                    family="x1d_judge_calibration",
                    suite_id=suite_id,
                    scenario_id=scenario_id,
                    run_id=run_id,
                    lane_id=lane_id,
                    stage_id="X1D",
                    depends_on_microstep_id=f"{lane_id}.X1D.judge_result.pass",
                    source=_row_source_or_snapshot(x1d_row, source),
                    verdict="PASS" if x1d_category == "MODEL_BACKED_PASS" else "WARN" if x1d_category != "UNKNOWN" else "NOT_OBSERVED",
                    observed={"x1d_category": x1d_category},
                    threshold={"category": "MODEL_BACKED_PASS or classified non-quality issue"},
                    reason=f"lane x1d runtime category {x1d_category}",
                    action="trend quality failures separately from judge execution failures per lane",
                )
            )

            lane_x3_rows = [row for row in lane_rows if str(row.stage_id) == "X3"]
            lane_x3_failures = [row.failure_mode for row in lane_x3_rows if row.verdict not in {"PASS", "NOT_APPLICABLE"}]
            observations.append(
                _obs(
                    diagnostic_id=f"{scenario_id}.{lane_id}.x3_disposition_quality.verdict",
                    family="x3_disposition_quality",
                    suite_id=suite_id,
                    scenario_id=scenario_id,
                    run_id=run_id,
                    lane_id=lane_id,
                    stage_id="X3",
                    depends_on_microstep_id=f"{lane_id}.X3.disposition.earned",
                    source=_row_source_or_snapshot(_first_row(lane_x3_rows), source),
                    verdict="WARN" if lane_x3_failures else "PASS" if lane_x3_rows else "NOT_OBSERVED",
                    observed={"x3_row_count": len(lane_x3_rows), "non_pass_failure_modes": lane_x3_failures},
                    threshold={"earned_disposition_non_pass_failure_modes": 0},
                    reason="lane X3 disposition non-pass rows observed" if lane_x3_failures else "lane X3 disposition did not expose failure",
                    action="trend earned-disposition quality per lane",
                )
            )

            lane_l6_rows = [row for row in lane_rows if str(row.stage_id) == "L6"]
            lane_l6_failures = [row.failure_mode for row in lane_l6_rows if row.verdict not in {"PASS", "NOT_APPLICABLE"}]
            observations.append(
                _obs(
                    diagnostic_id=f"{scenario_id}.{lane_id}.l6_shadow_non_mutation.verdict",
                    family="l6_shadow_non_mutation",
                    suite_id=suite_id,
                    scenario_id=scenario_id,
                    run_id=run_id,
                    lane_id=lane_id,
                    stage_id="L6",
                    depends_on_microstep_id=f"{lane_id}.L6.shadow_package.non_mutating",
                    source=_row_source_or_snapshot(_first_row(lane_l6_rows), source),
                    verdict="FAIL" if lane_l6_failures else "PASS" if lane_l6_rows else "NOT_OBSERVED",
                    observed={"l6_row_count": len(lane_l6_rows), "non_pass_failure_modes": lane_l6_failures},
                    threshold={"non_mutation_failures": 0},
                    reason="lane L6 non-mutation failure observed" if lane_l6_failures else "lane L6 shadow package remained non-mutating",
                    action="keep diagnostic L6 observations future-run-only and non-mutating",
                )
            )
    else:
        observations.append(
            _obs(
                diagnostic_id=f"{scenario_id}.x1d_judge_calibration.category",
                family="x1d_judge_calibration",
                suite_id=suite_id,
                scenario_id=scenario_id,
                run_id=run_id,
                stage_id="X1D",
                depends_on_microstep_id="X1D.*.judge_result_pass",
                source=source,
                verdict="NOT_OBSERVED",
                observed={"x1d_category": "UNKNOWN"},
                threshold={"category": "MODEL_BACKED_PASS or classified non-quality issue"},
                reason="x1d runtime category UNKNOWN",
                action="trend quality failures separately from judge execution failures",
            )
        )

    observations.append(
        _obs(
            diagnostic_id=f"{scenario_id}.e4_heal_opportunity.safety",
            family="e4_heal_opportunity",
            suite_id=suite_id,
            scenario_id=scenario_id,
            run_id=run_id,
            stage_id="L2",
            depends_on_microstep_id="L2.*.output_present",
            source=source,
            verdict="PASS",
            observed={"unsafe_current_run_repairs": _UNSAFE_E4_REPAIRS},
            threshold={"unsafe_repairs": "must remain blocked"},
            reason="unsafe current-run repair classes are diagnostic-only",
            action="only consider same-authority deterministic repairs in future runtime plans",
        )
    )

    l1_row = _first_row(indexed_rows["role"].get("l1_static_plan_profile", []))
    observations.append(
        _obs(
            diagnostic_id=f"{scenario_id}.l1_planning_rigor.inference_debt",
            family="l1_planning_rigor",
            suite_id=suite_id,
            scenario_id=scenario_id,
            run_id=run_id,
            stage_id="L1",
            depends_on_microstep_id="L1.static_plan_profile.present",
            source=_row_source(l1_row) if l1_row else source,
            verdict="PASS" if l1_row and l1_row.verdict == "PASS" else "NOT_OBSERVED",
            observed={"l1_profile_verdict": l1_row.verdict if l1_row else ""},
            threshold={"l1_profile_verdict": "PASS"},
            reason="L1 profile evidence observed" if l1_row else "L1 planning profile evidence not observed",
            action="expand L1 planning prior, judge expectation, graph traversal, and repair-budget receipts",
        )
    )

    l0_row = _first_row(indexed_rows["role"].get("l0_route_profile", []) or indexed_rows["role"].get("l0_managed_route_profile", []))
    cache_observed = "l2_semantic_cache" in json.dumps(snapshot.to_dict(), sort_keys=True, default=str)
    observations.append(
        _obs(
            diagnostic_id=f"{scenario_id}.l0_routing_cache.no_bypass",
            family="l0_routing_cache",
            suite_id=suite_id,
            scenario_id=scenario_id,
            run_id=run_id,
            stage_id="L0",
            depends_on_microstep_id="L0.managed_route.present",
            source=_row_source(l0_row) if l0_row else source,
            verdict="PASS" if l0_row and l0_row.verdict == "PASS" else "NOT_OBSERVED",
            observed={"l0_route_verdict": l0_row.verdict if l0_row else "", "semantic_cache_reference_observed": cache_observed},
            threshold={"route_profile": "PASS", "cache_bypass": "not observed"},
            reason="L0 route evidence observed without cache bypass signal" if l0_row else "L0 route/cache evidence not observed",
            action="continue recording R1B-disabled no-bypass evidence while cache bypass is disabled",
        )
    )

    return {
        "rows": observations,
        "summary": _summary(suite_id, run_id, observations),
    }
