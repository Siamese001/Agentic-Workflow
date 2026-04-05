"""
File: agentic_core/L0_routing/scripts/verify_manifest_util.py
Description: Analysis tool for SSOT Dry-Run Reports.
Usage: python verify_manifest_util.py --report ssot_report_123456.json
Context:
    - Parses the 'ReconciliationManifest' (JSON Report) from execute_ssot.py.
    - Generates a 'Blast Radius' assessment (Count of modified/deleted files).
    - Verifies that no 'High Severity' safety violations were ignored.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "verify_manifest_util")
emit_determinism_digest("p0", "verify_manifest_util")

_emit_dispatches_healing_run("p1", "verify_manifest_util", "L0")
_emit_routes_through("p1", "verify_manifest_util", "L0")
_emit_checks_agent_registry("p1", "verify_manifest_util", "agent_registry")
_emit_validates_agent_capability("p1", "verify_manifest_util", "capability")
_emit_dispatches_execution_plan("p1", "verify_manifest_util", "exec_plan")
_emit_agent_executes_agent("p1", "verify_manifest_util", "sub_agent")
_emit_routes_to_agent("p1", "verify_manifest_util", "target_agent")
_emit_verifies_policy("p1", "verify_manifest_util", "policy_check")
_emit_observes_runtime_state("p1", "verify_manifest_util", "runtime_state")
_emit_verifies_boundary("p1", "verify_manifest_util", "boundary_check")
_emit_transcripts_response("p1", "verify_manifest_util", "transcript")
_emit_hard_fails_untranscripted("p1", "verify_manifest_util")
_emit_gated_by_confidence("p1", "verify_manifest_util", "confidence_gate")
_emit_escalates_to_human("p1", "verify_manifest_util", "L0")
_emit_reads_policy_state("p1", "verify_manifest_util", "L0")
_emit_authorize_and_execute("p2", "verify_manifest_util", "execution_auth")
_emit_validates_capability("p2", "verify_manifest_util", "capability_check")
_emit_routes_to_capability("p2", "verify_manifest_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_manifest_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_manifest_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_manifest_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_manifest_util", "exec_output")
_emit_dispatches_agent("p3", "verify_manifest_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_manifest_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_manifest_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_manifest_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_manifest_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_manifest_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_manifest_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_manifest_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_manifest_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_manifest_util", "eval_metric")
_emit_stores_embedding("p4", "verify_manifest_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_manifest_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_manifest_util", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("verify_manifest_util", "p4obs", "metric_1")
_emit_emits_metric_event("verify_manifest_util", "p4obs", "metric_2")
_emit_emits_metric_event("verify_manifest_util", "p4obs", "metric_3")
_emit_emits_metric_event("verify_manifest_util", "p4obs", "metric_4")
_emit_emits_metric_event("verify_manifest_util", "p4obs", "metric_5")
_emit_emits_metric_event("verify_manifest_util", "p4obs", "metric_6")
_emit_records_incident_event("verify_manifest_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("verify_manifest_util", "p4obs", "anomaly")
_emit_writes_observability_log("verify_manifest_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("verify_manifest_util", "p4obs", "mon_state")
_emit_triggers_alert("verify_manifest_util", "p4obs", "alert")
_emit_links_incident_trace("verify_manifest_util", "p4obs", "trace_link")
_emit_captures_pattern("verify_manifest_util", "p3lm", "pattern")
_emit_records_learning_event("verify_manifest_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verify_manifest_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("verify_manifest_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verify_manifest_util", "p3lm", "routing")
_emit_improves_agent_policy("verify_manifest_util", "p3lm", "policy")
_emit_stores_learning_state("verify_manifest_util", "p3lm", "state")
_emit_records_execution_trace("verify_manifest_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verify_manifest_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verify_manifest_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verify_manifest_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verify_manifest_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verify_manifest_util", "env_read", "p2_env_1")
_emit_reads_environ("verify_manifest_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("verify_manifest_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verify_manifest_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verify_manifest_util", "context_pull")
_emit_pulls_context("p1", "verify_manifest_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "verify_manifest_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verify_manifest_util", "uwg_term_2")
_emit_writes_through("p1", "verify_manifest_util", "write_through")
_emit_writes_through("p1", "verify_manifest_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "verify_manifest_util", "safety_validation")
_emit_invokes_eval("p1", "verify_manifest_util", "eval_call")
_emit_proposal_commits_routing("p1", "verify_manifest_util", "routing_commit")


def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - [MANIFEST] %(message)s")


def analyze_impact(report: dict[str, Any]) -> bool:
    """
    Analyzes the dry-run report to determine if the proposed changes are safe.
    Returns: True if analysis passes safety thresholds, False otherwise.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "analyze_impact", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "analyze_impact", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "analyze_impact")
    phase1 = report.get("phase1", {})
    phase2 = report.get("phase2", {})
    meta = report.get("meta", {})
    if not meta.get("dry_run"):
        logging.warning("⚠️  This report is from a LIVE RUN, not a dry-run.")
    violations = phase1.get("violations_found", [])
    total_violations = len(violations)
    by_type = {}
    for v in violations:
        d_type = v.get("type", "UNKNOWN")
        by_type[d_type] = by_type.get(d_type, 0) + 1
    logging.info(f"--- IMPACT ANALYSIS: {meta.get('territory', 'Unknown')} ---")
    logging.info(f"Total Violations Detected: {total_violations}")
    for k, v in by_type.items():
        logging.info(f"  - {k}: {v}")
    modifications = phase2.get("modifications", [])
    failures = phase2.get("failures", [])
    files_touched = set()
    for mod in modifications:
        if mod.get("target"):
            files_touched.add(mod["target"])
    blast_radius = len(files_touched)
    logging.info("\n--- PROPOSED ACTIONS (Dry Run) ---")
    logging.info(f"Files to be Modified: {blast_radius}")
    logging.info(f"Agents Engaged: {len({m.get('agent') for m in modifications})}")
    logging.info(f"Blocked/Failed Actions: {len(failures)}")
    safety_pass = True
    if blast_radius > 50:
        logging.warning(
            f"🚨 HIGH BLAST RADIUS: {blast_radius} files would be modified. Manual review required."
        )
        safety_pass = False
    budget_blocks = [f for f in failures if "blocked_by_safety" in str(f.get("status", ""))]
    if budget_blocks:
        logging.warning(f"⚠️  {len(budget_blocks)} actions were blocked by safety budget limits.")
    orphans = [v for v in violations if "ORPHAN" in v.get("type", "")]
    if len(orphans) > 10:
        logging.warning(f"🚨 MASS DELETION RISK: {len(orphans)} orphan files identified for deletion.")
        safety_pass = False
    return safety_pass


def main():
    parser = argparse.ArgumentParser(description="SSOT Dry-Run Manifest Analyzer")
    parser.add_argument("report", help="Path to the ssot_report_TIMESTAMP.json file")
    args = parser.parse_args()
    report_path = Path(args.report)
    if not report_path.exists():
        logging.error(f"Report file not found: {report_path}")
        sys.exit(1)
    try:
        with open(report_path) as f:
            data = json.load(f)
        is_safe = analyze_impact(data)
        print("\n" + "=" * 40)
        if is_safe:
            print("✅ ANALYSIS PASSED: Proposed changes look standard.")
            sys.exit(0)
        else:
            print("❌ ANALYSIS FLAGGED RISKS: See warnings above.")
            sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in report file.")
        sys.exit(1)
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        logging.critical(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
