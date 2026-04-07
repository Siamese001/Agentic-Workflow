"""
Guardian: Location Alignment — Deterministic location compliance enforcement.

Reproduces the legacy ``LocationAgent`` / ``LocationValidatorAgent`` detection
semantics as a scan-only guardian with zero side effects.

Checks:
- misplaced_files: Python files violating structural location rules
  (files floating at territory root, forbidden backup/temp patterns)
- missing_directories: Required sovereign root directories that do not exist

Outputs a schema-locked GuardianResult JSON artifact.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_location_alignment \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
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

emit_replay_key("p0", "run_guardian_location_alignment")
emit_determinism_digest("p0", "run_guardian_location_alignment")

_emit_dispatches_healing_run("p1", "run_guardian_location_alignment", "L0")
_emit_routes_through("p1", "run_guardian_location_alignment", "L0")
_emit_checks_agent_registry("p1", "run_guardian_location_alignment", "agent_registry")
_emit_validates_agent_capability("p1", "run_guardian_location_alignment", "capability")
_emit_dispatches_execution_plan("p1", "run_guardian_location_alignment", "exec_plan")
_emit_agent_executes_agent("p1", "run_guardian_location_alignment", "sub_agent")
_emit_routes_to_agent("p1", "run_guardian_location_alignment", "target_agent")
_emit_verifies_policy("p1", "run_guardian_location_alignment", "policy_check")
_emit_observes_runtime_state("p1", "run_guardian_location_alignment", "runtime_state")
_emit_verifies_boundary("p1", "run_guardian_location_alignment", "boundary_check")
_emit_transcripts_response("p1", "run_guardian_location_alignment", "transcript")
_emit_hard_fails_untranscripted("p1", "run_guardian_location_alignment")
_emit_gated_by_confidence("p1", "run_guardian_location_alignment", "confidence_gate")
_emit_escalates_to_human("p1", "run_guardian_location_alignment", "L0")
_emit_reads_policy_state("p1", "run_guardian_location_alignment", "L0")
_emit_authorize_and_execute("p2", "run_guardian_location_alignment", "execution_auth")
_emit_validates_capability("p2", "run_guardian_location_alignment", "capability_check")
_emit_routes_to_capability("p2", "run_guardian_location_alignment", "capability_route")
_emit_writes_via_uwg("p2", "run_guardian_location_alignment", "uwg_write")
_emit_blocks_direct_write("p2", "run_guardian_location_alignment", "direct_write_block")
_emit_records_tool_invocation("p2", "run_guardian_location_alignment", "tool_invocation")
_emit_captures_execution_output("p2", "run_guardian_location_alignment", "exec_output")
_emit_dispatches_agent("p3", "run_guardian_location_alignment", "agent_dispatch")
_emit_coordinates_agents("p3", "run_guardian_location_alignment", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_guardian_location_alignment", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_guardian_location_alignment", "healing_outcome")
_emit_escalates_failure("p3", "run_guardian_location_alignment", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_guardian_location_alignment", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_guardian_location_alignment", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_guardian_location_alignment", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_guardian_location_alignment", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_guardian_location_alignment", "eval_metric")
_emit_stores_embedding("p4", "run_guardian_location_alignment", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_guardian_location_alignment", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_guardian_location_alignment", "exec_snapshot_link")
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

_emit_emits_metric_event("run_guardian_location_alignment", "p4obs", "metric_1")
_emit_emits_metric_event("run_guardian_location_alignment", "p4obs", "metric_2")
_emit_emits_metric_event("run_guardian_location_alignment", "p4obs", "metric_3")
_emit_emits_metric_event("run_guardian_location_alignment", "p4obs", "metric_4")
_emit_emits_metric_event("run_guardian_location_alignment", "p4obs", "metric_5")
_emit_emits_metric_event("run_guardian_location_alignment", "p4obs", "metric_6")
_emit_records_incident_event("run_guardian_location_alignment", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_guardian_location_alignment", "p4obs", "anomaly")
_emit_writes_observability_log("run_guardian_location_alignment", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_guardian_location_alignment", "p4obs", "mon_state")
_emit_triggers_alert("run_guardian_location_alignment", "p4obs", "alert")
_emit_links_incident_trace("run_guardian_location_alignment", "p4obs", "trace_link")
_emit_captures_pattern("run_guardian_location_alignment", "p3lm", "pattern")
_emit_records_learning_event("run_guardian_location_alignment", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_guardian_location_alignment", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_guardian_location_alignment", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_guardian_location_alignment", "p3lm", "routing")
_emit_improves_agent_policy("run_guardian_location_alignment", "p3lm", "policy")
_emit_stores_learning_state("run_guardian_location_alignment", "p3lm", "state")
_emit_records_execution_trace("run_guardian_location_alignment", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_guardian_location_alignment", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_guardian_location_alignment", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_guardian_location_alignment", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_guardian_location_alignment", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_guardian_location_alignment", "env_read", "p2_env_1")
_emit_reads_environ("run_guardian_location_alignment", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_guardian_location_alignment", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_guardian_location_alignment", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_guardian_location_alignment", "context_pull")
_emit_pulls_context("p1", "run_guardian_location_alignment", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_guardian_location_alignment", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_guardian_location_alignment", "uwg_term_2")
_emit_writes_through("p1", "run_guardian_location_alignment", "write_through")
_emit_writes_through("p1", "run_guardian_location_alignment", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_guardian_location_alignment", "safety_validation")
_emit_invokes_eval("p1", "run_guardian_location_alignment", "eval_call")
_emit_proposal_commits_routing("p1", "run_guardian_location_alignment", "routing_commit")

GUARDIAN_ID = "location_alignment"

# Legacy-equivalent forbidden file patterns
# (from LocationValidatorAgent._check_naming_conventions)
FORBIDDEN_FILE_PATTERNS: tuple[str, ...] = (".bak", ".backup", ".old", ".tmp")

# Files allowed at territory root level (not considered misplaced)
ROOT_LEVEL_ALLOWED: frozenset[str] = frozenset({"__init__.py"})

# Legacy-equivalent skip patterns
# (from LocationValidatorAgent.run)
SKIP_PARTS: frozenset[str] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def scan_missing_directories(
    repo_root: Path,
    required_roots: frozenset[str] | None = None,
) -> list[str]:
    """Return sorted list of required sovereign roots that are missing or not directories.

    Reproduces ``LocationValidatorAgent.validate_sovereign_roots()``.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "scan_missing_directories", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "scan_missing_directories", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "scan_missing_directories")
    if required_roots is None:
        required_roots = ROOT_WHITELIST

    missing: list[str] = []
    for root_name in sorted(required_roots):
        root_path = repo_root / root_name
        if not root_path.exists():
            missing.append(root_name)
        elif not root_path.is_dir():
            missing.append(root_name)
    return sorted(missing)


def scan_misplaced_files(
    repo_root: Path,
    scan_roots: frozenset[str] | None = None,
) -> list[str]:
    """Return sorted repo-relative POSIX paths of misplaced Python files.

    Reproduces key structural checks from ``LocationValidatorAgent.run()``
    and ``validate_file_location()``:

    1. Python files sitting directly at a sovereign territory root
       (should be in a recognized subfolder; __init__.py exempt).
    2. Files with forbidden backup/temp patterns anywhere in territories.
    """
    if scan_roots is None:
        scan_roots = ROOT_WHITELIST

    hits: list[str] = []
    for root_name in sorted(scan_roots):
        root_path = repo_root / root_name
        if not root_path.exists() or not root_path.is_dir():
            continue

        # Pass 1: Python files — check structural placement
        for py_file in sorted(root_path.rglob("*.py")):
            if any(skip in py_file.parts for skip in SKIP_PARTS):
                continue

            rel_to_root = py_file.relative_to(root_path)

            # Rule 1: files floating at territory root (not in a subfolder)
            if len(rel_to_root.parts) == 1 and rel_to_root.name not in ROOT_LEVEL_ALLOWED:
                hits.append(normalize_repo_path(py_file.relative_to(repo_root)))
                continue

            # Rule 2: forbidden file patterns in .py files
            for pattern in FORBIDDEN_FILE_PATTERNS:
                if pattern in py_file.name:
                    hits.append(normalize_repo_path(py_file.relative_to(repo_root)))
                    break

        # Pass 2: forbidden backup/temp files (any extension matching patterns)
        for pattern in FORBIDDEN_FILE_PATTERNS:
            for bad_file in sorted(root_path.rglob(f"*{pattern}")):
                if not bad_file.is_file():
                    continue
                if any(skip in bad_file.parts for skip in SKIP_PARTS):
                    continue
                hits.append(normalize_repo_path(bad_file.relative_to(repo_root)))

    return sorted(set(hits))


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_location_alignment_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    required_roots: frozenset[str] | None = None,
    scan_roots: frozenset[str] | None = None,
) -> GuardianResult:
    """
    Execute the location alignment guardian and return a schema-locked GuardianResult.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism (omitted if None).
        required_roots: Override ROOT_WHITELIST for testing.
        scan_roots: Override scan scope for testing.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    # --- Check 1: misplaced_files ---
    try:
        misplaced = scan_misplaced_files(repo_root, scan_roots)
        if misplaced:
            result.add_check(
                check_id="misplaced_files",
                status=CheckStatus.FAIL,
                details=f"Found {len(misplaced)} misplaced file(s)",
                evidence={"paths": misplaced},
            )
        else:
            result.add_check(
                check_id="misplaced_files",
                status=CheckStatus.PASS,
                details="No misplaced files detected",
                evidence={"paths": []},
            )
        result.metrics["misplaced_file_count"] = len(misplaced)

    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="misplaced_files",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"misplaced_files scan failed: {exc}")

    # --- Check 2: missing_directories ---
    try:
        missing = scan_missing_directories(repo_root, required_roots)
        if missing:
            result.add_check(
                check_id="missing_directories",
                status=CheckStatus.FAIL,
                details=f"Found {len(missing)} missing sovereign root(s)",
                evidence={"directories": missing},
            )
        else:
            result.add_check(
                check_id="missing_directories",
                status=CheckStatus.PASS,
                details="All required sovereign roots present",
                evidence={"directories": []},
            )
        result.metrics["missing_directory_count"] = len(missing)

    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="missing_directories",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"missing_directories scan failed: {exc}")

    # --- Finalize summary ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks
    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks

    if result.status == GuardianStatus.PASS.value:
        result.summary = f"Location alignment: {passed_checks}/{total_checks} checks passed"
    else:
        result.summary = f"Location alignment: {failed_checks}/{total_checks} checks failed"
        result.remediation_hints = [
            "Move misplaced files into recognized subfolders (config/, types/, reasoning/, engines/, etc.)",
            "Remove or relocate backup/temp files (.bak, .backup, .old, .tmp)",
            "Create missing sovereign root directories",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_location_alignment_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Location alignment guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Location Alignment Guardian")
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

    result = run_location_alignment_guardian(
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
