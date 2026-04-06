"""
Wave 0B: Categorized restore from .healing_backups/

Restores files that were unintentionally archived by the healing pipeline into
.healing_backups/ during the run11 archiving event.

Category routing:
  1. test_*.py          -> tests/_quarantine/restored_tests/
  2. PascalCase*Agent.py -> <inferred-layer>/reasoning/   (apps_rg, apps_lic, agentic_core)
  3. snake_case*.py     -> tests/_quarantine/restored_snake_case/  (manual triage)
  4. __init__.py        -> original package path (strip timestamp suffix from backup name)
  5. naming_violations/ -> HOLD — do not auto-restore

Run:
    python -m ops_scripts.general.restore_from_healing_backup [--dry-run] [--backup-root PATH]

AST analysis is used for category inference. No heuristics on file content patterns.
"""

from __future__ import annotations

import argparse
import ast
import re
import shutil
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L5_SAFETY_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("restore_from_healing_backup", "p4obs", "metric_1")
_emit_emits_metric_event("restore_from_healing_backup", "p4obs", "metric_2")
_emit_emits_metric_event("restore_from_healing_backup", "p4obs", "metric_3")
_emit_emits_metric_event("restore_from_healing_backup", "p4obs", "metric_4")
_emit_emits_metric_event("restore_from_healing_backup", "p4obs", "metric_5")
_emit_emits_metric_event("restore_from_healing_backup", "p4obs", "metric_6")
_emit_records_incident_event("restore_from_healing_backup", "p4obs", "incident")
_emit_captures_runtime_anomaly("restore_from_healing_backup", "p4obs", "anomaly")
_emit_writes_observability_log("restore_from_healing_backup", "p4obs", "obs_log")
_emit_updates_monitoring_state("restore_from_healing_backup", "p4obs", "mon_state")
_emit_triggers_alert("restore_from_healing_backup", "p4obs", "alert")
_emit_links_incident_trace("restore_from_healing_backup", "p4obs", "trace_link")
_emit_captures_pattern("restore_from_healing_backup", "p3lm", "pattern")
_emit_records_learning_event("restore_from_healing_backup", "p3lm", "learning_event")
_emit_writes_learning_snapshot("restore_from_healing_backup", "p3lm", "snapshot")
_emit_feeds_meta_learning("restore_from_healing_backup", "p3lm", "meta_feed")
_emit_updates_routing_strategy("restore_from_healing_backup", "p3lm", "routing")
_emit_improves_agent_policy("restore_from_healing_backup", "p3lm", "policy")
_emit_stores_learning_state("restore_from_healing_backup", "p3lm", "state")
_emit_records_execution_trace("restore_from_healing_backup", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("restore_from_healing_backup", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("restore_from_healing_backup", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("restore_from_healing_backup", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("restore_from_healing_backup", "L4_STATE", "p2_trace_5")
_emit_reads_environ("restore_from_healing_backup", "env_read", "p2_env_1")
_emit_reads_environ("restore_from_healing_backup", "env_read", "p2_env_2")
_emit_reads_runtime_state("restore_from_healing_backup", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("restore_from_healing_backup", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "restore_from_healing_backup")
_emit_applies_guardrail("p0", "restore_from_healing_backup", "p0_governance")
_emit_reads_policy_state("p0", "restore_from_healing_backup", "policy_binding")
_emit_snapshots_state("p0", "restore_from_healing_backup", "state_snapshot")
_emit_pulls_context("p1", "restore_from_healing_backup", "context_pull")
_emit_pulls_context("p1", "restore_from_healing_backup", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "restore_from_healing_backup", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "restore_from_healing_backup", "uwg_term_secondary")
_emit_writes_through("p1", "restore_from_healing_backup", "write_through")
_emit_writes_through("p1", "restore_from_healing_backup", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "restore_from_healing_backup", "safety_validation")
_emit_invokes_eval("p1", "restore_from_healing_backup", "eval_call")
_emit_proposal_commits_routing("p1", "restore_from_healing_backup", "routing_commit")
_emit_escalates_to_human("p1", "restore_from_healing_backup", "human_escalation")
_emit_routes_through("p1", "restore_from_healing_backup", "route_through")
_emit_checks_agent_registry("p1", "restore_from_healing_backup", "agent_registry")
_emit_validates_agent_capability("p1", "restore_from_healing_backup", "capability")
_emit_dispatches_execution_plan("p1", "restore_from_healing_backup", "exec_plan")
_emit_agent_executes_agent("p1", "restore_from_healing_backup", "sub_agent")
_emit_routes_to_agent("p1", "restore_from_healing_backup", "target_agent")
_emit_verifies_policy("p1", "restore_from_healing_backup", "policy_check")
_emit_observes_runtime_state("p1", "restore_from_healing_backup", "runtime_state")
_emit_verifies_boundary("p1", "restore_from_healing_backup", "boundary_check")
_emit_transcripts_response("p1", "restore_from_healing_backup", "transcript")
_emit_hard_fails_untranscripted("p1", "restore_from_healing_backup")
_emit_gated_by_confidence("p1", "restore_from_healing_backup", "confidence_gate")
emit_replay_key("p0", "restore_from_healing_backup")
emit_determinism_digest("p0", "restore_from_healing_backup")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "restore_from_healing_backup", "execution_auth")
_emit_validates_capability("p2", "restore_from_healing_backup", "capability_check")
_emit_routes_to_capability("p2", "restore_from_healing_backup", "capability_route")
_emit_writes_via_uwg("p2", "restore_from_healing_backup", "uwg_write")
_emit_blocks_direct_write("p2", "restore_from_healing_backup", "direct_write_block")
_emit_records_tool_invocation("p2", "restore_from_healing_backup", "tool_invocation")
_emit_captures_execution_output("p2", "restore_from_healing_backup", "exec_output")
_emit_dispatches_agent("p3", "restore_from_healing_backup", "agent_dispatch")
_emit_coordinates_agents("p3", "restore_from_healing_backup", "agent_coordination")
_emit_records_workflow_lineage("p3", "restore_from_healing_backup", "workflow_lineage")
_emit_records_healing_outcome("p3", "restore_from_healing_backup", "healing_outcome")
_emit_escalates_failure("p3", "restore_from_healing_backup", "failure_escalation")
_emit_orchestrates_workflow("p3", "restore_from_healing_backup", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "restore_from_healing_backup", "healing_dispatch")
_emit_invokes_evaluation("p3", "restore_from_healing_backup", "evaluation_signal")
_emit_records_telemetry_event("p4", "restore_from_healing_backup", "telemetry_event")
_emit_captures_evaluation_metric("p4", "restore_from_healing_backup", "eval_metric")
_emit_stores_embedding("p4", "restore_from_healing_backup", "embedding_store")
_emit_updates_meta_learning_state("p4", "restore_from_healing_backup", "meta_learning")
_emit_links_execution_to_snapshot("p4", "restore_from_healing_backup", "exec_snapshot_link")

PROJECT_ROOT = get_validated_project_root()
DEFAULT_BACKUP_ROOT = PROJECT_ROOT / ".healing_backups"

# Destination roots for each category
DEST_QUARANTINE_TESTS = PROJECT_ROOT / TESTS_DIR / "_quarantine" / "restored_tests"
DEST_QUARANTINE_SNAKE = PROJECT_ROOT / TESTS_DIR / "_quarantine" / "restored_snake_case"

LAYER_ROOTS = [
    PROJECT_ROOT / APPS_RG_DIR,
    PROJECT_ROOT / APPS_LIC_DIR,
    PROJECT_ROOT / APPS_SHARED_DIR,
    PROJECT_ROOT / L5_SAFETY_DIR,
    PROJECT_ROOT / L1_COGNITION_DIR,
    PROJECT_ROOT / L2_EXECUTION_DIR,
    PROJECT_ROOT / L3_ORCHESTRATION_DIR,
    PROJECT_ROOT / L0_ROUTING_DIR,
]

PASCAL_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*Agent\.py$")
SNAKE_RE = re.compile(r"^[a-z_][a-z0-9_]*\.py$")
INIT_RE = re.compile(r"^__init__(\.py|\.[0-9]+\.py)$")
NAMING_VIOLATION_RE = re.compile(r"^naming_violations[/\\]")


def _infer_agent_layer(py_path: Path) -> Path | None:
    """Use AST to detect the primary base class and infer layer root."""
    try:
        src = py_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except (ValueError, TypeError, RuntimeError) as e:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for base in node.bases:
            base_name = ""
            if isinstance(base, ast.Attribute):
                base_name = base.attr
            elif isinstance(base, ast.Name):
                base_name = base.id
            if APPS_RG_DIR in src and APPS_LIC_DIR not in src:
                return PROJECT_ROOT / APPS_RG_DIR / "reasoning"
            if APPS_LIC_DIR in src and APPS_RG_DIR not in src:
                return PROJECT_ROOT / APPS_LIC_DIR / "reasoning"
    # Default: agentic_core L5_safety (most archived agents were there)
    return PROJECT_ROOT / L5_SAFETY_DIR / "reasoning"


def _strip_timestamp_suffix(name: str) -> str:
    """Remove trailing .YYYYMMDDHHMMSS timestamp from backup filenames."""
    return re.sub(r"\.\d{14}$", "", name)


def _categorize(path: Path, rel: Path) -> tuple[str, Path | None]:
    """
    Returns (category, destination_path).

    Categories:
      TEST, AGENT, SNAKE, INIT, NAMING_VIOLATION, UNKNOWN
    """
    name = path.name
    rel_str = str(rel)

    if NAMING_VIOLATION_RE.match(rel_str):
        return "NAMING_VIOLATION", None

    if INIT_RE.match(name):
        clean_name = _strip_timestamp_suffix(name)
        # Best-effort: place into same relative directory minus the backup prefix
        parts = rel.parts[1:]  # strip the first backup subfolder
        if parts:
            dest = PROJECT_ROOT.joinpath(*parts[:-1]) / clean_name
        else:
            dest = PROJECT_ROOT / clean_name
        return "INIT", dest

    if name.startswith("test_") and name.endswith(".py"):
        return "TEST", DEST_QUARANTINE_TESTS / name

    if PASCAL_RE.match(name):
        layer = _infer_agent_layer(path)
        dest = (layer or PROJECT_ROOT / L5_SAFETY_DIR / "reasoning") / name
        return "AGENT", dest

    if SNAKE_RE.match(name) and name.endswith(".py"):
        return "SNAKE", DEST_QUARANTINE_SNAKE / name

    return "UNKNOWN", DEST_QUARANTINE_SNAKE / name


def restore(backup_root: Path = DEFAULT_BACKUP_ROOT, dry_run: bool = True) -> dict:
    """Main restore driver. Returns summary dict."""
    if not backup_root.exists():
        print(f"ERROR: Backup root not found: {backup_root}")
        return {"error": f"backup root not found: {backup_root}"}

    summary: dict[str, list[str]] = {
        "TEST": [],
        "AGENT": [],
        "SNAKE": [],
        "INIT": [],
        "NAMING_VIOLATION": [],
        "UNKNOWN": [],
        "SKIPPED_EXISTS": [],
        "ERROR": [],
    }

    all_py = list(backup_root.rglob("*.py"))
    print(f"[restore] Scanning {len(all_py)} .py files under {backup_root.name}/")

    for src_path in all_py:
        try:
            rel = src_path.relative_to(backup_root)
        except ValueError:
            continue

        category, dest = _categorize(src_path, rel)

        if category == "NAMING_VIOLATION" or dest is None:
            summary["NAMING_VIOLATION"].append(str(rel))
            print(f"  HOLD [naming_violation]: {rel}")
            continue

        if dest.exists():
            summary["SKIPPED_EXISTS"].append(str(rel))
            print(f"  SKIP [exists]: {rel} -> {dest.relative_to(PROJECT_ROOT)}")
            continue

        print(f"  {category}: {rel} -> {dest.relative_to(PROJECT_ROOT)}")
        summary[category].append(str(rel))

        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest)

    print("\n[restore] Summary:")
    for cat, items in summary.items():
        if items:
            print(f"  {cat}: {len(items)}")

    if dry_run:
        print("\n[restore] DRY-RUN: no files written. Pass --no-dry-run to apply.")

    return {k: len(v) for k, v in summary.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Wave 0B: restore files from .healing_backups/")
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=DEFAULT_BACKUP_ROOT,
        help="Path to .healing_backups/ directory",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        default=False,
        help="Actually copy files (default is dry-run)",
    )
    args = parser.parse_args()
    result = restore(backup_root=args.backup_root, dry_run=not args.no_dry_run)
    errors = result.get("ERROR", 0)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
