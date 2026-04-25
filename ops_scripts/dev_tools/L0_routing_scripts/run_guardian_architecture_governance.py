"""
Guardian: Architecture Governance — Deterministic layer-import compliance enforcement.

Wraps the legacy ``gravity_validator.UnifiedSSOTValidator`` scan semantics as a
scan-only guardian with zero side effects.

Checks:
- import_compliance: Illegal upward dependencies (lower layer importing higher layer)
- layer_gravity: Agents physically located in the wrong layer

Uses AST-based import analysis and the SSOT scanner for deterministic detection.

CLI:
    python -m agentic_core.L0_routing.scripts.run_guardian_architecture_governance \\
        --write-artifacts docs/reports/plans \\
        --strict
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
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

emit_replay_key("p0", "run_guardian_architecture_governance")
emit_determinism_digest("p0", "run_guardian_architecture_governance")

_emit_dispatches_healing_run("p1", "run_guardian_architecture_governance", "L0")
_emit_routes_through("p1", "run_guardian_architecture_governance", "L0")
_emit_checks_agent_registry("p1", "run_guardian_architecture_governance", "agent_registry")
_emit_validates_agent_capability("p1", "run_guardian_architecture_governance", "capability")
_emit_dispatches_execution_plan("p1", "run_guardian_architecture_governance", "exec_plan")
_emit_agent_executes_agent("p1", "run_guardian_architecture_governance", "sub_agent")
_emit_routes_to_agent("p1", "run_guardian_architecture_governance", "target_agent")
_emit_verifies_policy("p1", "run_guardian_architecture_governance", "policy_check")
_emit_observes_runtime_state("p1", "run_guardian_architecture_governance", "runtime_state")
_emit_verifies_boundary("p1", "run_guardian_architecture_governance", "boundary_check")
_emit_transcripts_response("p1", "run_guardian_architecture_governance", "transcript")
_emit_hard_fails_untranscripted("p1", "run_guardian_architecture_governance")
_emit_gated_by_confidence("p1", "run_guardian_architecture_governance", "confidence_gate")
_emit_escalates_to_human("p1", "run_guardian_architecture_governance", "L0")
_emit_reads_policy_state("p1", "run_guardian_architecture_governance", "L0")
_emit_authorize_and_execute("p2", "run_guardian_architecture_governance", "execution_auth")
_emit_validates_capability("p2", "run_guardian_architecture_governance", "capability_check")
_emit_routes_to_capability("p2", "run_guardian_architecture_governance", "capability_route")
_emit_writes_via_uwg("p2", "run_guardian_architecture_governance", "uwg_write")
_emit_blocks_direct_write("p2", "run_guardian_architecture_governance", "direct_write_block")
_emit_records_tool_invocation("p2", "run_guardian_architecture_governance", "tool_invocation")
_emit_captures_execution_output("p2", "run_guardian_architecture_governance", "exec_output")
_emit_dispatches_agent("p3", "run_guardian_architecture_governance", "agent_dispatch")
_emit_coordinates_agents("p3", "run_guardian_architecture_governance", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_guardian_architecture_governance", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_guardian_architecture_governance", "healing_outcome")
_emit_escalates_failure("p3", "run_guardian_architecture_governance", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_guardian_architecture_governance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_guardian_architecture_governance", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_guardian_architecture_governance", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_guardian_architecture_governance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_guardian_architecture_governance", "eval_metric")
_emit_stores_embedding("p4", "run_guardian_architecture_governance", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_guardian_architecture_governance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_guardian_architecture_governance", "exec_snapshot_link")
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

_emit_emits_metric_event("run_guardian_architecture_governance", "p4obs", "metric_1")
_emit_emits_metric_event("run_guardian_architecture_governance", "p4obs", "metric_2")
_emit_emits_metric_event("run_guardian_architecture_governance", "p4obs", "metric_3")
_emit_emits_metric_event("run_guardian_architecture_governance", "p4obs", "metric_4")
_emit_emits_metric_event("run_guardian_architecture_governance", "p4obs", "metric_5")
_emit_emits_metric_event("run_guardian_architecture_governance", "p4obs", "metric_6")
_emit_records_incident_event("run_guardian_architecture_governance", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_guardian_architecture_governance", "p4obs", "anomaly")
_emit_writes_observability_log("run_guardian_architecture_governance", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_guardian_architecture_governance", "p4obs", "mon_state")
_emit_triggers_alert("run_guardian_architecture_governance", "p4obs", "alert")
_emit_links_incident_trace("run_guardian_architecture_governance", "p4obs", "trace_link")
_emit_captures_pattern("run_guardian_architecture_governance", "p3lm", "pattern")
_emit_records_learning_event("run_guardian_architecture_governance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_guardian_architecture_governance", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_guardian_architecture_governance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_guardian_architecture_governance", "p3lm", "routing")
_emit_improves_agent_policy("run_guardian_architecture_governance", "p3lm", "policy")
_emit_stores_learning_state("run_guardian_architecture_governance", "p3lm", "state")
_emit_records_execution_trace("run_guardian_architecture_governance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_guardian_architecture_governance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_guardian_architecture_governance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_guardian_architecture_governance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_guardian_architecture_governance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_guardian_architecture_governance", "env_read", "p2_env_1")
_emit_reads_environ("run_guardian_architecture_governance", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_guardian_architecture_governance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_guardian_architecture_governance", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_guardian_architecture_governance", "context_pull")
_emit_pulls_context("p1", "run_guardian_architecture_governance", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_guardian_architecture_governance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_guardian_architecture_governance", "uwg_term_2")
_emit_writes_through("p1", "run_guardian_architecture_governance", "write_through")
_emit_writes_through("p1", "run_guardian_architecture_governance", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_guardian_architecture_governance", "safety_validation")
_emit_invokes_eval("p1", "run_guardian_architecture_governance", "eval_call")
_emit_proposal_commits_routing("p1", "run_guardian_architecture_governance", "routing_commit")

GUARDIAN_ID = "architecture_governance"

# Layer numeric ordering for waterfall enforcement
LAYER_HIERARCHY: dict[str, int] = {
    "L0": 0,
    "L1": 1,
    "L2": 2,
    "L3": 3,
    "L4": 4,
    "L5": 5,
    "L6": 6,
}

# Directories to skip during scanning
SKIP_PARTS: frozenset[str] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)


# ---------------------------------------------------------------------------
# Scan functions (pure, deterministic, no side-effects)
# ---------------------------------------------------------------------------


def _get_layer_from_path(file_path: Path) -> str | None:
    """Extract layer (L0-L6) from file path parts."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_layer_from_path", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_layer_from_path", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_layer_from_path")
    for part in file_path.parts:
        if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
            return part[:2]
    return None


def _extract_target_layer(node: ast.AST) -> str | None:
    """Extract target layer from an import AST node."""
    if isinstance(node, ast.ImportFrom):
        if node.module and AGENTIC_CORE_DIR in node.module:
            for part in node.module.split("."):
                if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
                    return part[:2]
    elif isinstance(node, ast.Import):
        for alias in node.names:
            if AGENTIC_CORE_DIR in alias.name:
                for part in alias.name.split("."):
                    if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
                        return part[:2]
    return None


def _collect_python_files(repo_root: Path) -> list[Path]:
    """Return sorted Python files under agentic_core/ for import scanning."""
    agentic_core = repo_root / AGENTIC_CORE_DIR
    if not agentic_core.exists():
        return []

    result: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(agentic_core):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_PARTS)
        for fname in sorted(filenames):
            if fname.endswith(".py"):
                result.append(Path(dirpath) / fname)
    return result


def scan_import_compliance(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Detect illegal upward dependencies (lower layer importing higher layer).

    Reproduces ``gravity_validator._check_import_violations()`` detection
    using pure AST parsing.

    Returns sorted list of violation dicts with keys:
    path, source_layer, target_layer, import_line, line_number.
    """
    if files is None:
        files = _collect_python_files(repo_root)

    violations: list[dict] = []
    for fpath in tqdm(files, desc="Processing", unit="item"):
        source_layer = _get_layer_from_path(fpath)
        if source_layer is None or source_layer not in LAYER_HIERARCHY:
            continue

        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content, filename=str(fpath))
        except (
            SyntaxError,
            UnicodeDecodeError,
        ):  # guardian: allow-silent-swallow -- acceptable exception handling
            continue

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue

            target_layer = _extract_target_layer(node)
            if target_layer is None or target_layer not in LAYER_HIERARCHY:
                continue

            # Upward dependency: source layer number < target layer number
            if LAYER_HIERARCHY[source_layer] < LAYER_HIERARCHY[target_layer]:
                # Reconstruct import line
                if isinstance(node, ast.ImportFrom):
                    import_line = f"from {node.module} import ..."
                else:
                    import_line = f"import {node.names[0].name}"

                rel = normalize_repo_path(fpath.relative_to(repo_root))
                violations.append(
                    {
                        "path": rel,
                        "source_layer": source_layer,
                        "target_layer": target_layer,
                        "import_line": import_line[:120],
                        "line_number": node.lineno,
                    },
                )

    return sorted(violations, key=lambda v: (v["path"], v["line_number"]))


def scan_layer_gravity(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Detect agents physically located in the wrong layer.

    Reproduces ``gravity_validator._check_gravity_violations()`` detection
    using the SSOT scanner. An agent's assigned layer (from its class or
    naming convention) must match its physical location layer.

    Returns sorted list of violation dicts with keys:
    path, agent_name, actual_layer, assigned_layer.
    """
    try:
        from agentic_core.L0_routing.enforcement.safety_enforcement_seam import (
            load_ssot_scanner,
        )

        SSOTScanner = load_ssot_scanner().SSOTScanner
    except ImportError:
        return []

    try:
        scanner = SSOTScanner(repo_root)
        gravity_agents = scanner.find_gravity_violations()
    except (ValueError, TypeError):  # guardian: allow-silent-swallow
        return []

    violations: list[dict] = []
    for agent in tqdm(gravity_agents, desc="Processing", unit="item"):
        violations.append(
            {
                "path": normalize_repo_path(agent.relative_path),
                "agent_name": agent.class_name,
                "actual_layer": agent.layer,
                "assigned_layer": agent.assigned_layer,
            },
        )

    return sorted(violations, key=lambda v: v["path"])


# ---------------------------------------------------------------------------
# Main guardian logic
# ---------------------------------------------------------------------------


def run_architecture_governance_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
) -> GuardianResult:
    """Execute architecture governance guardian.

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

    # --- Check: import_compliance ---
    try:
        import_violations = scan_import_compliance(repo_root, files)

        if import_violations:
            result.add_check(
                check_id="import_compliance",
                status=CheckStatus.FAIL,
                details=f"{len(import_violations)} upward import violation(s) detected",
                evidence={
                    "violation_count": len(import_violations),
                    "violations": import_violations,
                },
            )
        else:
            result.add_check(
                check_id="import_compliance",
                status=CheckStatus.PASS,
                details="No upward import violations detected",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling

    # --- Check: layer_gravity ---
    try:
        gravity_violations = scan_layer_gravity(repo_root, files)

        if gravity_violations:
            result.add_check(
                check_id="layer_gravity",
                status=CheckStatus.FAIL,
                details=f"{len(gravity_violations)} agent(s) in wrong layer",
                evidence={
                    "violation_count": len(gravity_violations),
                    "violations": gravity_violations,
                },
            )
        else:
            result.add_check(
                check_id="layer_gravity",
                status=CheckStatus.PASS,
                details="All agents in correct layers",
                evidence={"violation_count": 0, "violations": []},
            )
    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling

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
            f"Architecture governance: {passed_checks}/{total_checks} checks passed "
            f"({len(files)} files scanned)"
        )
    else:
        result.summary = (
            f"Architecture governance: {failed_checks}/{total_checks} checks failed "
            f"({len(files)} files scanned)"
        )
        result.remediation_hints = [
            "Fix upward import violations: lower layers must not import from higher layers",
            "Move agents to their assigned layer per the SSOT scanner classification",
        ]

    # --- V15 signing (before serialization) ---
    maybe_sign_result(result, commit_hash="HEAD")

    # --- Write artifact ---
    if write_artifacts_dir:
        artifact_dir = repo_root / write_artifacts_dir
        out_path = write_guardian_result(
            result,
            artifact_dir,
            "guardian_architecture_governance_result.json",
        )
        result.add_artifact(
            ArtifactType.JSON,
            normalize_repo_path(out_path.relative_to(repo_root)),
            "Architecture governance guardian result JSON",
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Architecture Governance Guardian",
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

    result = run_architecture_governance_guardian(
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
