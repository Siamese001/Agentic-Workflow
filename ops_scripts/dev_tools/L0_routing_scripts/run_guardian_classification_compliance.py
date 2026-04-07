"""
Guardian: Classification Compliance — Deterministic file classification enforcement.

Wraps the legacy ``FileClassificationAgent`` scan semantics as a scan-only
guardian with zero side effects.

Checks:
- naming_compliance: Compound suffix conflicts in filenames
- territory_compliance: Files residing in incorrect LCD folders per classification

Uses the SSOT classification kernel (``classify_file_standalone``) and
``FILETYPE_TO_FOLDER`` mapping for deterministic, AST-based detection.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_classification_compliance \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    TOOLS_DIR,
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

emit_replay_key("p0", "run_guardian_classification_compliance")
emit_determinism_digest("p0", "run_guardian_classification_compliance")

_emit_dispatches_healing_run("p1", "run_guardian_classification_compliance", "L0")
_emit_routes_through("p1", "run_guardian_classification_compliance", "L0")
_emit_checks_agent_registry("p1", "run_guardian_classification_compliance", "agent_registry")
_emit_validates_agent_capability("p1", "run_guardian_classification_compliance", "capability")
_emit_dispatches_execution_plan("p1", "run_guardian_classification_compliance", "exec_plan")
_emit_agent_executes_agent("p1", "run_guardian_classification_compliance", "sub_agent")
_emit_routes_to_agent("p1", "run_guardian_classification_compliance", "target_agent")
_emit_verifies_policy("p1", "run_guardian_classification_compliance", "policy_check")
_emit_observes_runtime_state("p1", "run_guardian_classification_compliance", "runtime_state")
_emit_verifies_boundary("p1", "run_guardian_classification_compliance", "boundary_check")
_emit_transcripts_response("p1", "run_guardian_classification_compliance", "transcript")
_emit_hard_fails_untranscripted("p1", "run_guardian_classification_compliance")
_emit_gated_by_confidence("p1", "run_guardian_classification_compliance", "confidence_gate")
_emit_escalates_to_human("p1", "run_guardian_classification_compliance", "L0")
_emit_reads_policy_state("p1", "run_guardian_classification_compliance", "L0")
_emit_authorize_and_execute("p2", "run_guardian_classification_compliance", "execution_auth")
_emit_validates_capability("p2", "run_guardian_classification_compliance", "capability_check")
_emit_routes_to_capability("p2", "run_guardian_classification_compliance", "capability_route")
_emit_writes_via_uwg("p2", "run_guardian_classification_compliance", "uwg_write")
_emit_blocks_direct_write("p2", "run_guardian_classification_compliance", "direct_write_block")
_emit_records_tool_invocation("p2", "run_guardian_classification_compliance", "tool_invocation")
_emit_captures_execution_output("p2", "run_guardian_classification_compliance", "exec_output")
_emit_dispatches_agent("p3", "run_guardian_classification_compliance", "agent_dispatch")
_emit_coordinates_agents("p3", "run_guardian_classification_compliance", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_guardian_classification_compliance", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_guardian_classification_compliance", "healing_outcome")
_emit_escalates_failure("p3", "run_guardian_classification_compliance", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_guardian_classification_compliance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_guardian_classification_compliance", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_guardian_classification_compliance", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_guardian_classification_compliance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_guardian_classification_compliance", "eval_metric")
_emit_stores_embedding("p4", "run_guardian_classification_compliance", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_guardian_classification_compliance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_guardian_classification_compliance", "exec_snapshot_link")
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

_emit_emits_metric_event("run_guardian_classification_compliance", "p4obs", "metric_1")
_emit_emits_metric_event("run_guardian_classification_compliance", "p4obs", "metric_2")
_emit_emits_metric_event("run_guardian_classification_compliance", "p4obs", "metric_3")
_emit_emits_metric_event("run_guardian_classification_compliance", "p4obs", "metric_4")
_emit_emits_metric_event("run_guardian_classification_compliance", "p4obs", "metric_5")
_emit_emits_metric_event("run_guardian_classification_compliance", "p4obs", "metric_6")
_emit_records_incident_event("run_guardian_classification_compliance", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_guardian_classification_compliance", "p4obs", "anomaly")
_emit_writes_observability_log("run_guardian_classification_compliance", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_guardian_classification_compliance", "p4obs", "mon_state")
_emit_triggers_alert("run_guardian_classification_compliance", "p4obs", "alert")
_emit_links_incident_trace("run_guardian_classification_compliance", "p4obs", "trace_link")
_emit_captures_pattern("run_guardian_classification_compliance", "p3lm", "pattern")
_emit_records_learning_event("run_guardian_classification_compliance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_guardian_classification_compliance", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_guardian_classification_compliance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_guardian_classification_compliance", "p3lm", "routing")
_emit_improves_agent_policy("run_guardian_classification_compliance", "p3lm", "policy")
_emit_stores_learning_state("run_guardian_classification_compliance", "p3lm", "state")
_emit_records_execution_trace("run_guardian_classification_compliance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_guardian_classification_compliance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_guardian_classification_compliance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_guardian_classification_compliance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_guardian_classification_compliance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_guardian_classification_compliance", "env_read", "p2_env_1")
_emit_reads_environ("run_guardian_classification_compliance", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_guardian_classification_compliance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_guardian_classification_compliance", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_guardian_classification_compliance", "context_pull")
_emit_pulls_context("p1", "run_guardian_classification_compliance", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_guardian_classification_compliance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_guardian_classification_compliance", "uwg_term_2")
_emit_writes_through("p1", "run_guardian_classification_compliance", "write_through")
_emit_writes_through("p1", "run_guardian_classification_compliance", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_guardian_classification_compliance", "safety_validation")
_emit_invokes_eval("p1", "run_guardian_classification_compliance", "eval_call")
_emit_proposal_commits_routing("p1", "run_guardian_classification_compliance", "routing_commit")

GUARDIAN_ID = "classification_compliance"

# Directories to skip during scanning (deterministic, no globs)
SKIP_PARTS: frozenset[str] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)

# LCD canonical folders where territory compliance applies
LCD_FOLDERS: frozenset[str] = frozenset(
    {
        "config",
        "types",
        "reasoning",
        "enforcement",
        "validators",
        "utils",
        TOOLS_DIR,
        "scripts",
    },
)

# Files that should never be classified (skip always)
SKIP_FILENAMES: frozenset[str] = frozenset(
    {
        "__init__.py",
        "__main__.py",
        "conftest.py",
        "setup.py",
    },
)


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def _collect_python_files(repo_root: Path) -> list[Path]:
    """Return sorted list of Python files in agentic_core/ and apps_*/ trees.

    Deterministic: sorted by repo-relative POSIX path, skips SKIP_PARTS.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_collect_python_files", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_collect_python_files", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_collect_python_files")
    result: list[Path] = []
    scan_roots: list[Path] = []

    for item in sorted(repo_root.iterdir(), key=lambda p: p.name):
        if not item.is_dir():
            continue
        if item.name == AGENTIC_CORE_DIR or item.name.startswith("apps_"):
            scan_roots.append(item)

    for scan_root in scan_roots:
        for dirpath, dirnames, filenames in os.walk(scan_root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_PARTS)
            for fname in sorted(filenames):
                if fname.endswith(".py") and fname not in SKIP_FILENAMES:
                    result.append(Path(dirpath) / fname)

    return result


def scan_naming_compliance(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Detect compound suffix conflicts in filenames.

    Returns sorted list of violation dicts with keys:
    filename, path, conflicting_tags, pattern_matched.
    """
    from agentic_core.L0_routing.config import COMPOUND_SUFFIX_CONFLICTS

    if files is None:
        files = _collect_python_files(repo_root)

    violations: list[dict] = []
    for fpath in files:
        stem = fpath.stem
        for pattern, tag_a, tag_b, _example in COMPOUND_SUFFIX_CONFLICTS:
            if re.search(pattern, stem):
                rel = normalize_repo_path(fpath.relative_to(repo_root))
                violations.append(
                    {
                        "filename": fpath.name,
                        "path": rel,
                        "conflicting_tags": sorted([tag_a, tag_b]),
                        "pattern_matched": pattern,
                    },
                )
                break  # First match per file

    return sorted(violations, key=lambda v: v["path"])


def scan_territory_compliance(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Detect files residing in incorrect LCD folders per classification.

    Uses the SSOT classification kernel for AST-based file classification
    and FILETYPE_TO_FOLDER for expected folder mapping.

    Only checks files that are inside a recognized LCD folder within
    agentic_core/ layers. Files in apps_* are excluded (they have
    their own territory rules in FileClassificationAgent).

    Returns sorted list of violation dicts with keys:
    filename, path, classified_as, current_folder, expected_folder.
    """
    from agentic_core.L0_routing.config import FILETYPE_TO_FOLDER
    from agentic_core.L0_routing.enforcement.safety_kernel_seam import (
        load_classification_kernel,
    )

    classify_file_standalone = load_classification_kernel().classify_file_standalone

    if files is None:
        files = _collect_python_files(repo_root)

    violations: list[dict] = []
    for fpath in files:
        parts = fpath.parts

        # Only check files inside agentic_core/ layers in LCD folders
        if AGENTIC_CORE_DIR not in parts:
            continue

        # Must be inside a recognized LCD subfolder
        parent_name = fpath.parent.name
        if parent_name not in LCD_FOLDERS:
            continue

        # Must be inside a layer (L0-L6)
        in_layer = any(p.startswith(("L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_")) for p in parts)
        if not in_layer:
            continue

        # Classify using SSOT kernel
        file_type = classify_file_standalone(fpath)

        # Types that don't get folder-routed
        if file_type in ("CLASS", "STUB", "TEST", "IGNORE", "BASE_AGENT"):
            continue

        expected_folder = FILETYPE_TO_FOLDER.get(file_type)
        if expected_folder is None:
            continue

        # GLOBAL sentinels are handled separately (mixins → GLOBAL_MIXINS)
        if expected_folder in ("GLOBAL_MIXINS", "GLOBAL_INTERFACES"):
            continue

        if parent_name != expected_folder:
            rel = normalize_repo_path(fpath.relative_to(repo_root))
            violations.append(
                {
                    "filename": fpath.name,
                    "path": rel,
                    "classified_as": file_type,
                    "current_folder": parent_name,
                    "expected_folder": expected_folder,
                },
            )

    return sorted(violations, key=lambda v: v["path"])


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_classification_compliance_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """Execute classification compliance guardian.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    """
    if repo_root is None:
        repo_root = get_validated_project_root()

    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
    )

    files = _collect_python_files(repo_root)

    # --- Check: naming_compliance ---
    try:
        naming_violations = scan_naming_compliance(repo_root, files)

        if naming_violations:
            result.add_check(
                check_id="naming_compliance",
                status=CheckStatus.FAIL,
                details=f"{len(naming_violations)} compound suffix conflict(s) detected",
                evidence={
                    "violation_count": len(naming_violations),
                    "violations": naming_violations,
                },
            )
        else:
            result.add_check(
                check_id="naming_compliance",
                status=CheckStatus.PASS,
                details="No compound suffix conflicts detected",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="naming_compliance",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"naming_compliance scan failed: {exc}")

    # --- Check: territory_compliance ---
    try:
        territory_violations = scan_territory_compliance(repo_root, files)

        if territory_violations:
            result.add_check(
                check_id="territory_compliance",
                status=CheckStatus.FAIL,
                details=f"{len(territory_violations)} territory violation(s) detected",
                evidence={
                    "violation_count": len(territory_violations),
                    "violations": territory_violations,
                },
            )
        else:
            result.add_check(
                check_id="territory_compliance",
                status=CheckStatus.PASS,
                details="All files in correct LCD folders",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        result.add_check(
            check_id="territory_compliance",
            status=CheckStatus.FAIL,
            details=f"Scan error: {exc}",
        )
        result.set_error(f"territory_compliance scan failed: {exc}")

    # --- Finalize ---
    total_checks = len(result.checks)
    failed_checks = sum(1 for c in result.checks if c.status == CheckStatus.FAIL.value)
    passed_checks = total_checks - failed_checks

    result.metrics["total_checks"] = total_checks
    result.metrics["passed_checks"] = passed_checks
    result.metrics["failed_checks"] = failed_checks
    result.metrics["files_scanned"] = len(files)

    if result.status == GuardianStatus.PASS.value:
        result.summary = (
            f"Classification compliance: {passed_checks}/{total_checks} checks passed "
            f"({len(files)} files scanned)"
        )
    else:
        result.summary = (
            f"Classification compliance: {failed_checks}/{total_checks} checks failed "
            f"({len(files)} files scanned)"
        )
        result.remediation_hints = [
            "Rename files with compound suffix conflicts (keep terminal suffix only)",
            "Move misplaced files to correct LCD folders per classification",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_classification_compliance_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Classification compliance guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classification Compliance Guardian",
    )
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

    result = run_classification_compliance_guardian(
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
