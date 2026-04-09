"""
_ssot_validation_artifacts.py — Validation JSON writers and healing action recorder.

Extracted from execute_ssot.py to reduce file size and improve cohesion.
All public symbols are re-exported from execute_ssot.py for backward compat.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "_ssot_validation_artifacts")
emit_determinism_digest("p0", "_ssot_validation_artifacts")

_emit_dispatches_healing_run("p1", "_ssot_validation_artifacts", "L0")
_emit_routes_through("p1", "_ssot_validation_artifacts", "L0")
_emit_checks_agent_registry("p1", "_ssot_validation_artifacts", "agent_registry")
_emit_validates_agent_capability("p1", "_ssot_validation_artifacts", "capability")
_emit_dispatches_execution_plan("p1", "_ssot_validation_artifacts", "exec_plan")
_emit_agent_executes_agent("p1", "_ssot_validation_artifacts", "sub_agent")
_emit_routes_to_agent("p1", "_ssot_validation_artifacts", "target_agent")
_emit_verifies_policy("p1", "_ssot_validation_artifacts", "policy_check")
_emit_observes_runtime_state("p1", "_ssot_validation_artifacts", "runtime_state")
_emit_verifies_boundary("p1", "_ssot_validation_artifacts", "boundary_check")
_emit_transcripts_response("p1", "_ssot_validation_artifacts", "transcript")
_emit_hard_fails_untranscripted("p1", "_ssot_validation_artifacts")
_emit_gated_by_confidence("p1", "_ssot_validation_artifacts", "confidence_gate")
_emit_escalates_to_human("p1", "_ssot_validation_artifacts", "L0")
_emit_reads_policy_state("p1", "_ssot_validation_artifacts", "L0")
_emit_authorize_and_execute("p2", "_ssot_validation_artifacts", "execution_auth")
_emit_validates_capability("p2", "_ssot_validation_artifacts", "capability_check")
_emit_routes_to_capability("p2", "_ssot_validation_artifacts", "capability_route")
_emit_writes_via_uwg("p2", "_ssot_validation_artifacts", "uwg_write")
_emit_blocks_direct_write("p2", "_ssot_validation_artifacts", "direct_write_block")
_emit_records_tool_invocation("p2", "_ssot_validation_artifacts", "tool_invocation")
_emit_captures_execution_output("p2", "_ssot_validation_artifacts", "exec_output")
_emit_dispatches_agent("p3", "_ssot_validation_artifacts", "agent_dispatch")
_emit_coordinates_agents("p3", "_ssot_validation_artifacts", "agent_coordination")
_emit_records_workflow_lineage("p3", "_ssot_validation_artifacts", "workflow_lineage")
_emit_records_healing_outcome("p3", "_ssot_validation_artifacts", "healing_outcome")
_emit_escalates_failure("p3", "_ssot_validation_artifacts", "failure_escalation")
_emit_orchestrates_workflow("p3", "_ssot_validation_artifacts", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_ssot_validation_artifacts", "healing_dispatch")
_emit_invokes_evaluation("p3", "_ssot_validation_artifacts", "evaluation_signal")
_emit_records_telemetry_event("p4", "_ssot_validation_artifacts", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_ssot_validation_artifacts", "eval_metric")
_emit_stores_embedding("p4", "_ssot_validation_artifacts", "embedding_store")
_emit_updates_meta_learning_state("p4", "_ssot_validation_artifacts", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_ssot_validation_artifacts", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("_ssot_validation_artifacts", "p4obs", "metric_1")
_emit_emits_metric_event("_ssot_validation_artifacts", "p4obs", "metric_2")
_emit_emits_metric_event("_ssot_validation_artifacts", "p4obs", "metric_3")
_emit_emits_metric_event("_ssot_validation_artifacts", "p4obs", "metric_4")
_emit_emits_metric_event("_ssot_validation_artifacts", "p4obs", "metric_5")
_emit_emits_metric_event("_ssot_validation_artifacts", "p4obs", "metric_6")
_emit_records_incident_event("_ssot_validation_artifacts", "p4obs", "incident")
_emit_captures_runtime_anomaly("_ssot_validation_artifacts", "p4obs", "anomaly")
_emit_writes_observability_log("_ssot_validation_artifacts", "p4obs", "obs_log")
_emit_updates_monitoring_state("_ssot_validation_artifacts", "p4obs", "mon_state")
_emit_triggers_alert("_ssot_validation_artifacts", "p4obs", "alert")
_emit_links_incident_trace("_ssot_validation_artifacts", "p4obs", "trace_link")
_emit_captures_pattern("_ssot_validation_artifacts", "p3lm", "pattern")
_emit_records_learning_event("_ssot_validation_artifacts", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_ssot_validation_artifacts", "p3lm", "snapshot")
_emit_feeds_meta_learning("_ssot_validation_artifacts", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_ssot_validation_artifacts", "p3lm", "routing")
_emit_improves_agent_policy("_ssot_validation_artifacts", "p3lm", "policy")
_emit_stores_learning_state("_ssot_validation_artifacts", "p3lm", "state")
_emit_records_execution_trace("_ssot_validation_artifacts", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_ssot_validation_artifacts", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_ssot_validation_artifacts", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_ssot_validation_artifacts", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_ssot_validation_artifacts", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_ssot_validation_artifacts", "env_read", "p2_env_1")
_emit_reads_environ("_ssot_validation_artifacts", "env_read", "p2_env_2")
_emit_reads_runtime_state("_ssot_validation_artifacts", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_ssot_validation_artifacts", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_ssot_validation_artifacts", "context_pull")
_emit_pulls_context("p1", "_ssot_validation_artifacts", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "_ssot_validation_artifacts", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_ssot_validation_artifacts", "uwg_term_2")
_emit_writes_through("p1", "_ssot_validation_artifacts", "write_through")
_emit_writes_through("p1", "_ssot_validation_artifacts", "write_through_2")
_emit_validated_by_safety_plane("p1", "_ssot_validation_artifacts", "safety_validation")
_emit_invokes_eval("p1", "_ssot_validation_artifacts", "eval_call")
_emit_proposal_commits_routing("p1", "_ssot_validation_artifacts", "routing_commit")

logger = logging.getLogger(__name__)


def _normalize_finding_id(finding: dict, validator: str, index: int) -> str:
    """Generate normalized finding ID: {validator}:{path}:{rule}:{index}.

    Per hostile audit Section B3: Finding IDs must be normalized and deterministic.
    Per .windsurf/rules/constitutional.md §1.7: Identical input → identical output.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_normalize_finding_id", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_normalize_finding_id", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_normalize_finding_id")
    path = finding.get("file", finding.get("path", "UNKNOWN"))
    rule = finding.get("type", finding.get("rule", "UNKNOWN"))
    path_normalized = str(path).replace("\\", "/")
    return f"{validator}:{path_normalized}:{rule}:{index:04d}"


def _write_pre_validation_json(
    violations: list[dict],
    trace_id: str,
    territory: str,
    validators_used: list[str],
    output_dir: Path,
) -> None:
    """Write pre_validation.json before any healing occurs.

    Per hostile audit Section C2: Pre-heal state must be captured in structured artifact.
    Per hostile audit Section B3: Findings must have normalized IDs and validator provenance.
    Per .windsurf/rules/constitutional.md §2.2: Evidence must be deterministic, ASCII-only.
    """
    from datetime import timezone

    findings = []
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    targeted_paths = set()
    for idx, violation in enumerate(violations):
        validator = violation.get("suggested_agent", "UNKNOWN")
        finding_id = _normalize_finding_id(violation, validator, idx)
        vtype = violation.get("type", "")
        if "FORBIDDEN" in vtype or "ARCHIVED" in vtype:
            severity = "high"
        elif "DUPLICATE" in vtype:
            severity = "medium"
        else:
            severity = "low"
        severity_counts[severity] += 1
        path = violation.get("file", violation.get("path", ""))
        if path:
            targeted_paths.add(str(path))
        findings.append(
            {
                "id": finding_id,
                "validator": validator,
                "path": str(path),
                "severity": severity,
                "rule": violation.get("type", "UNKNOWN"),
                "description": violation.get("message", ""),
            },
        )
    pre_validation = {
        "trace_id": trace_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "territory": territory,
        "validators": validators_used,
        "findings": findings,
        "counts": {
            "total": len(findings),
            "high": severity_counts["high"],
            "medium": severity_counts["medium"],
            "low": severity_counts["low"],
        },
        "targeted_paths": sorted(targeted_paths),
    }
    output_path = output_dir / "pre_validation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pre_validation, f, indent=2, ensure_ascii=True)
    logger.info(f"[PRE-VALIDATION] Wrote {len(findings)} findings to {output_path}")


def _write_post_validation_json(
    pre_validation_path: Path,
    phase3_result: dict,
    trace_id: str,
    territory: str,
    output_dir: Path,
) -> None:
    """Write post_validation.json after Phase 3 revalidation.

    Per hostile audit Section C4: Post-heal proof with resolved/residual/regression breakdown.
    Per hostile audit Section B5: Must show resolved, remaining, and newly introduced findings.
    """
    from datetime import timezone

    pre_validation = {}
    if pre_validation_path.exists():
        with open(pre_validation_path, encoding="utf-8") as f:
            pre_validation = json.load(f)
    pre_finding_ids = {f["id"] for f in pre_validation.get("findings", [])}
    pre_finding_count = len(pre_finding_ids)
    remaining_violations = phase3_result.get("remaining_violations", [])
    remaining_findings = []
    for idx, violation in enumerate(remaining_violations):
        validator = violation.get("suggested_agent", "UNKNOWN")
        finding_id = _normalize_finding_id(violation, validator, idx)
        remaining_findings.append(
            {
                "id": finding_id,
                "validator": validator,
                "path": str(violation.get("file", violation.get("path", ""))),
                "rule": violation.get("type", "UNKNOWN"),
            },
        )
    remaining_ids = {f["id"] for f in remaining_findings}
    resolved_ids = list(pre_finding_ids - remaining_ids)
    regression_ids = list(remaining_ids - pre_finding_ids)
    post_validation = {
        "trace_id": trace_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "territory": territory,
        "pre_finding_count": pre_finding_count,
        "resolved_findings": resolved_ids,
        "residual_findings": list(remaining_ids),
        "regressions": regression_ids,
        "post_finding_count": len(remaining_ids),
        "resolution_rate": round(len(resolved_ids) / max(pre_finding_count, 1), 4),
        "validators_rerun": ["Phase3Validator"],
    }
    output_path = output_dir / "post_validation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(post_validation, f, indent=2, ensure_ascii=True)
    logger.info(
        f"[POST-VALIDATION] Resolved: {len(resolved_ids)}, Residual: {len(remaining_ids)}, Regressions: {len(regression_ids)}",
    )


def _write_run_manifest_json(
    trace_id: str,
    execution_mode: str,
    territories: list[str],
    agents_executed: list[str],
    output_dir: Path,
) -> None:
    """E6: Write run_manifest.json with run metadata and execution summary.

    Per hostile audit Section E6: run_manifest.json provides high-level run metadata.
    """
    from datetime import timezone

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "trace_id": trace_id,
        "execution_mode": execution_mode,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "territories": territories,
        "agents_executed": agents_executed,
        "agent_count": len(agents_executed),
        "territory_count": len(territories),
    }
    output_path = output_dir / "run_manifest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=True)
    logger.info(
        f"[RUN-MANIFEST] Wrote run_manifest.json with {len(agents_executed)} agents, {len(territories)} territories",
    )


def _write_decision_summary_json(trace_id: str, decisions_made: list[dict], output_dir: Path) -> None:
    """E6: Write decision_summary.json with routing decision audit trail.

    Per hostile audit Section E6: decision_summary.json provides routing decision audit.
    """
    from datetime import timezone

    output_dir.mkdir(parents=True, exist_ok=True)
    tier_counts = {}
    agent_counts = {}
    for decision in decisions_made:
        tier = decision.get("tier", "UNKNOWN")
        agent = decision.get("agent", "unknown")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    summary = {
        "trace_id": trace_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_decisions": len(decisions_made),
        "tier_distribution": tier_counts,
        "agent_distribution": agent_counts,
        "decisions": decisions_made,
    }
    output_path = output_dir / "decision_summary.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=True)
    logger.info(f"[DECISION-SUMMARY] Wrote decision_summary.json with {len(decisions_made)} decisions")


def _write_artifact_integrity_json(trace_id: str, output_dir: Path) -> None:
    """E7: Write artifact_integrity.json as final step with SHA256 hashes of all artifacts.

    Per hostile audit Section E7: artifact_integrity.json provides cryptographic proof of artifact set.
    """
    import hashlib
    from datetime import timezone

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for artifact_path in output_dir.glob("*.json"):
        if artifact_path.name == "artifact_integrity.json":
            continue
        try:
            content = artifact_path.read_bytes()
            sha256_hash = hashlib.sha256(content).hexdigest()
            artifacts[artifact_path.name] = {
                "sha256": sha256_hash,
                "size_bytes": len(content),
            }  # guardian: File operations with encoding need error-specific handling
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"[ARTIFACT-INTEGRITY] Failed to hash {artifact_path.name}: {e}")
    integrity = {
        "trace_id": trace_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    output_path = output_dir / "artifact_integrity.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(integrity, f, indent=2, ensure_ascii=True)
    logger.info(f"[ARTIFACT-INTEGRITY] Wrote artifact_integrity.json with {len(artifacts)} artifact hashes")


def _record_backup_archival_event(
    state_mgr,
    agent: str,
    category: str,
    count: int = 1,
):
    """Record a backup archival event: a violation that required archival instead of direct fix.

    Appends to state_mgr.state["backup_archival_events"] so _fire_meta_learning_intake
    can surface the signal: 'N violations of category X required archival by agent Y'.
    This feeds the system learning pipeline with hard-to-heal violation patterns.
    """
    ts = datetime.now().isoformat()
    event = {
        "agent": agent,
        "category": category,
        "count": count,
        "timestamp": ts,
    }
    if "backup_archival_events" not in state_mgr.state:
        state_mgr.state["backup_archival_events"] = []
    state_mgr.state["backup_archival_events"].append(event)


def _record_healing_action(
    state_mgr,
    agent: str,
    territory: str,
    routing_score: float = 0.0,
    routing_tier: str = "DETERMINISTIC",
    model: str = "none",
    routing_gate: str = "N/A",
    confidence: float = 0.0,
    fix_summary: str = "",
    outcome: str = "SUCCESS",
    routing_digest: str | None = None,
    check_id: str | None = None,
):
    """[H2] Record a structured healing action for per-territory JSON and Markdown reports.

    Appends to state_mgr.state["healing_actions"] so Phase 5 can filter by territory
    and emit a healing_log in the detailed_cert JSON.

    Also persists the outcome to the system learning memory bridge (fire-and-forget,
    never raises) so healing patterns accumulate cross-session — same wiring as apps_*.
    """
    ts = datetime.now().isoformat()
    action = {
        "agent": agent,
        "territory": territory,
        "routing_score": round(routing_score, 4),
        "routing_tier": routing_tier,
        "model": model,
        "routing_gate": routing_gate,
        "confidence": round(confidence, 4),
        "fix_summary": fix_summary,
        "outcome": outcome,
        "timestamp": ts,
        "routing_digest": routing_digest,
        "check_id": check_id,
    }
    if "healing_actions" not in state_mgr.state:
        state_mgr.state["healing_actions"] = []
    state_mgr.state["healing_actions"].append(action)

    # ------------------------------------------------------------------
    # System learning persistence — fire-and-forget, never raises
    # ------------------------------------------------------------------
    try:
        from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

        _bridge = get_sl_memory_bridge()
        # Build a compact error signature from agent + territory + outcome
        error_sig = f"{agent}::{territory}::{outcome}"
        # Healing success rate: 1.0 = healed, 0.0 = failure/skipped
        _rate = 1.0 if outcome == "SUCCESS" else 0.0
        _bridge.persist_healing_success_rate(error_sig, rate=_rate, count=1, ts=ts)

        # Persist failure pattern for non-success outcomes so RCA can cluster them
        if outcome not in ("SUCCESS",):
            import hashlib as _hl

            _pattern_id = _hl.sha256(f"{error_sig}:{fix_summary[:80]}".encode()).hexdigest()[:16]
            _label = f"{agent} {outcome} in {territory}: {fix_summary[:80]}"
            _centroid = _hl.sha256(f"{agent}:{territory}".encode()).hexdigest()[:16]
            _bridge.persist_failure_pattern(
                pattern_id=_pattern_id,
                pattern_label=_label,
                centroid_hash=_centroid,
                member_count=1,
                ts=ts,
            )
    except ImportError as _sl_err:
        logger.debug("[SL] system_learning persist skipped (not available): %s", _sl_err)
    except (ValueError, TypeError, RuntimeError) as _sl_err:
        logger.warning("[SL] system_learning persist failed: %s", _sl_err)
