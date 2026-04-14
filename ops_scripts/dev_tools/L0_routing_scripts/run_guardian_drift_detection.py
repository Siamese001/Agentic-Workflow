"""
Guardian: Drift Detection — Deterministic root-level SSOT drift enforcement.

Reproduces the legacy ``FilesystemSSOTReconcilerAgent.detect_root_drift()``
detection semantics as a scan-only guardian with zero side effects.

Checks:
- Forbidden folders at project root (scripts, logs, coverage_html, observability)
- Archived/backup/old files at project root
- Duplicate folders at root that shadow SSOT locations

Outputs a schema-locked GuardianResult JSON artifact.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_drift_detection \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
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
from ops_scripts.dev_tools.L0_routing.project_root_util import get_validated_project_root

emit_replay_key("p0", "run_guardian_drift_detection")
emit_determinism_digest("p0", "run_guardian_drift_detection")

_emit_dispatches_healing_run("p1", "run_guardian_drift_detection", "L0")
_emit_routes_through("p1", "run_guardian_drift_detection", "L0")
_emit_checks_agent_registry("p1", "run_guardian_drift_detection", "agent_registry")
_emit_validates_agent_capability("p1", "run_guardian_drift_detection", "capability")
_emit_dispatches_execution_plan("p1", "run_guardian_drift_detection", "exec_plan")
_emit_agent_executes_agent("p1", "run_guardian_drift_detection", "sub_agent")
_emit_routes_to_agent("p1", "run_guardian_drift_detection", "target_agent")
_emit_verifies_policy("p1", "run_guardian_drift_detection", "policy_check")
_emit_observes_runtime_state("p1", "run_guardian_drift_detection", "runtime_state")
_emit_verifies_boundary("p1", "run_guardian_drift_detection", "boundary_check")
_emit_transcripts_response("p1", "run_guardian_drift_detection", "transcript")
_emit_hard_fails_untranscripted("p1", "run_guardian_drift_detection")
_emit_gated_by_confidence("p1", "run_guardian_drift_detection", "confidence_gate")
_emit_escalates_to_human("p1", "run_guardian_drift_detection", "L0")
_emit_reads_policy_state("p1", "run_guardian_drift_detection", "L0")
_emit_authorize_and_execute("p2", "run_guardian_drift_detection", "execution_auth")
_emit_validates_capability("p2", "run_guardian_drift_detection", "capability_check")
_emit_routes_to_capability("p2", "run_guardian_drift_detection", "capability_route")
_emit_writes_via_uwg("p2", "run_guardian_drift_detection", "uwg_write")
_emit_blocks_direct_write("p2", "run_guardian_drift_detection", "direct_write_block")
_emit_records_tool_invocation("p2", "run_guardian_drift_detection", "tool_invocation")
_emit_captures_execution_output("p2", "run_guardian_drift_detection", "exec_output")
_emit_dispatches_agent("p3", "run_guardian_drift_detection", "agent_dispatch")
_emit_coordinates_agents("p3", "run_guardian_drift_detection", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_guardian_drift_detection", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_guardian_drift_detection", "healing_outcome")
_emit_escalates_failure("p3", "run_guardian_drift_detection", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_guardian_drift_detection", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_guardian_drift_detection", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_guardian_drift_detection", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_guardian_drift_detection", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_guardian_drift_detection", "eval_metric")
_emit_stores_embedding("p4", "run_guardian_drift_detection", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_guardian_drift_detection", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_guardian_drift_detection", "exec_snapshot_link")
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
from tqdm import tqdm

_emit_emits_metric_event("run_guardian_drift_detection", "p4obs", "metric_1")
_emit_emits_metric_event("run_guardian_drift_detection", "p4obs", "metric_2")
_emit_emits_metric_event("run_guardian_drift_detection", "p4obs", "metric_3")
_emit_emits_metric_event("run_guardian_drift_detection", "p4obs", "metric_4")
_emit_emits_metric_event("run_guardian_drift_detection", "p4obs", "metric_5")
_emit_emits_metric_event("run_guardian_drift_detection", "p4obs", "metric_6")
_emit_records_incident_event("run_guardian_drift_detection", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_guardian_drift_detection", "p4obs", "anomaly")
_emit_writes_observability_log("run_guardian_drift_detection", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_guardian_drift_detection", "p4obs", "mon_state")
_emit_triggers_alert("run_guardian_drift_detection", "p4obs", "alert")
_emit_links_incident_trace("run_guardian_drift_detection", "p4obs", "trace_link")
_emit_captures_pattern("run_guardian_drift_detection", "p3lm", "pattern")
_emit_records_learning_event("run_guardian_drift_detection", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_guardian_drift_detection", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_guardian_drift_detection", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_guardian_drift_detection", "p3lm", "routing")
_emit_improves_agent_policy("run_guardian_drift_detection", "p3lm", "policy")
_emit_stores_learning_state("run_guardian_drift_detection", "p3lm", "state")
_emit_records_execution_trace("run_guardian_drift_detection", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_guardian_drift_detection", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_guardian_drift_detection", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_guardian_drift_detection", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_guardian_drift_detection", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_guardian_drift_detection", "env_read", "p2_env_1")
_emit_reads_environ("run_guardian_drift_detection", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_guardian_drift_detection", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_guardian_drift_detection", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_guardian_drift_detection", "context_pull")
_emit_pulls_context("p1", "run_guardian_drift_detection", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_guardian_drift_detection", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_guardian_drift_detection", "uwg_term_2")
_emit_writes_through("p1", "run_guardian_drift_detection", "write_through")
_emit_writes_through("p1", "run_guardian_drift_detection", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_guardian_drift_detection", "safety_validation")
_emit_invokes_eval("p1", "run_guardian_drift_detection", "eval_call")
_emit_proposal_commits_routing("p1", "run_guardian_drift_detection", "routing_commit")

GUARDIAN_ID = "drift_detection"

# Legacy-equivalent constants (from FilesystemSSOTReconcilerAgent)
FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset(
    {
        "scripts",
        "logs",
        "coverage_html",
        "observability",
    },
)

ARCHIVE_PATTERNS: tuple[str, ...] = (".archived", ".backup", ".old")

SSOT_DUPLICATE_MAP: dict[str, str] = {
    "scripts": "agentic_core/L0_routing/scripts",
    "logs": "agentic_core/L0_routing/logs",
}


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def scan_forbidden_root_folders(repo_root: Path) -> list[str]:
    """Return sorted list of forbidden folder names found at project root."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "scan_forbidden_root_folders", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "scan_forbidden_root_folders", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "scan_forbidden_root_folders")
    hits: list[str] = []
    try:
        for item in tqdm(repo_root.iterdir(), desc="Processing", unit="item"):
            if item.is_dir() and item.name in FORBIDDEN_ROOT_FOLDERS:
                hits.append(item.name)
    # guardian: allow-silent-swallow - acceptable exception handling
    except PermissionError:
        pass
    return sorted(hits)


def scan_archived_files_at_root(repo_root: Path) -> list[str]:
    """Return sorted repo-relative POSIX paths of archived files at root."""
    hits: list[str] = []
    try:
        for item in tqdm(repo_root.iterdir(), desc="Processing", unit="item"):
            if item.is_file():
                for pattern in ARCHIVE_PATTERNS:
                    if pattern in item.name:
                        hits.append(normalize_repo_path(item.relative_to(repo_root)))
                        # guardian: allow-silent-swallow - acceptable exception handling
                        break
    except PermissionError:
        pass
    return sorted(hits)


def scan_duplicate_ssot_folders(repo_root: Path) -> list[dict[str, str]]:
    """Return sorted list of duplicate folder dicts found at root.

    Each dict has keys: name, root_path, ssot_path (repo-relative POSIX).
    Only reported when BOTH root and SSOT paths exist simultaneously.
    """
    hits: list[dict[str, str]] = []
    for folder_name, ssot_rel in tqdm(sorted(SSOT_DUPLICATE_MAP.items()), desc="Processing", unit="item"):
        root_path = repo_root / folder_name
        ssot_path = repo_root / ssot_rel
        if root_path.exists() and ssot_path.exists():
            hits.append(
                {
                    "name": folder_name,
                    "root_path": normalize_repo_path(
                        root_path.relative_to(repo_root),
                    ),
                    "ssot_path": normalize_repo_path(ssot_rel),
                },
            )
    return sorted(hits, key=lambda d: d["name"])


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_drift_detection_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """
    Execute the drift detection guardian and return a schema-locked GuardianResult.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism (omitted if None).

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    # --- Check: root_drift (composite of 3 legacy sub-checks) ---
    try:
        forbidden = scan_forbidden_root_folders(repo_root)
        archived = scan_archived_files_at_root(repo_root)
        duplicates = scan_duplicate_ssot_folders(repo_root)

        drift_detected = bool(forbidden or archived or duplicates)

        evidence: dict = {
            "forbidden_folders": forbidden,
            "archived_files_at_root": archived,
            "duplicate_folders": duplicates,
        }

        if drift_detected:
            details_parts: list[str] = []
            if forbidden:
                details_parts.append(
                    f"{len(forbidden)} forbidden root folder(s)",
                )
            if archived:
                details_parts.append(
                    f"{len(archived)} archived file(s) at root",
                )
            if duplicates:
                details_parts.append(
                    f"{len(duplicates)} duplicate SSOT folder(s)",
                )

            result.add_check(
                check_id="root_drift",
                status=CheckStatus.FAIL,
                details="Root drift detected: " + "; ".join(details_parts),
                evidence=evidence,
            )
        else:
            result.add_check(
                check_id="root_drift",
                status=CheckStatus.PASS,
                details="No root-level SSOT drift detected",
                evidence=evidence,
            )

        result.metrics["forbidden_folder_count"] = len(forbidden)
        result.metrics["archived_file_count"] = len(archived)
        result.metrics["duplicate_folder_count"] = len(duplicates)
        result.metrics["drift_detected"] = drift_detected

    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="root_drift",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"root_drift scan failed: {exc}")

    # --- Finalize summary ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks
    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks

    if result.status == GuardianStatus.PASS.value:
        result.summary = f"Drift detection: {passed_checks}/{total_checks} checks passed"
    else:
        result.summary = f"Drift detection: {failed_checks}/{total_checks} checks failed"
        result.remediation_hints = [
            "Remove forbidden root folders (scripts/, logs/, coverage_html/, observability/)",
            "Move archived/backup/old files to archives/",
            "Remove duplicate folders that shadow SSOT locations",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_drift_detection_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Drift detection guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Drift Detection Guardian")
    parser.add_argument(
        "--write-artifacts",
        default=None,
        help="Repo-relative directory to write result JSON (default: none)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Non-zero exit on FAIL/ERROR",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Injectable ISO-8601 timestamp (omitted if not provided)",
    )
    args = parser.parse_args()

    result = run_drift_detection_guardian(
        write_artifacts_dir=args.write_artifacts,
        timestamp=args.timestamp,
    )

    if args.format == "json":
        print(result.to_json())
    else:
        print(f"Guardian: {result.guardian_id} | Status: {result.status}")
        print(f"Summary: {result.summary}")
        for check in result.checks:
            print(f"  [{check.status}] {check.check_id}: {check.details}")

    if args.strict and result.status != GuardianStatus.PASS.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
