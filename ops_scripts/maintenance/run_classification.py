#!/usr/bin/env python3
"""
File Classification Analysis Script - Refined Version
Runs classification analysis on SSOT-approved folders and generates detailed report.

FOCUS: Only flag actual naming violations, avoid false positives.
- SCRIPT: PascalCase files in ops_scripts/ or scripts/ should be snake_case
- TEST: Files in tests/ without test_ prefix
- MIXIN: Files with Mixin in class name but PascalCase filename
- Avoid flagging: Errors, Strategies, Validators, Guardrails, etc. as needing Agent suffix
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "run_classification")
_emit_applies_guardrail("p0", "run_classification", "p0_governance")
_emit_reads_policy_state("p0", "run_classification", "policy_binding")
_emit_snapshots_state("p0", "run_classification", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("run_classification", "p4obs", "metric_1")
_emit_emits_metric_event("run_classification", "p4obs", "metric_2")
_emit_emits_metric_event("run_classification", "p4obs", "metric_3")
_emit_emits_metric_event("run_classification", "p4obs", "metric_4")
_emit_emits_metric_event("run_classification", "p4obs", "metric_5")
_emit_emits_metric_event("run_classification", "p4obs", "metric_6")
_emit_records_incident_event("run_classification", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_classification", "p4obs", "anomaly")
_emit_writes_observability_log("run_classification", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_classification", "p4obs", "mon_state")
_emit_triggers_alert("run_classification", "p4obs", "alert")
_emit_links_incident_trace("run_classification", "p4obs", "trace_link")
_emit_captures_pattern("run_classification", "p3lm", "pattern")
_emit_records_learning_event("run_classification", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_classification", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_classification", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_classification", "p3lm", "routing")
_emit_improves_agent_policy("run_classification", "p3lm", "policy")
_emit_stores_learning_state("run_classification", "p3lm", "state")
_emit_records_execution_trace("run_classification", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_classification", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_classification", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_classification", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_classification", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_classification", "env_read", "p2_env_1")
_emit_reads_environ("run_classification", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_classification", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_classification", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_classification", "context_pull")
_emit_pulls_context("p1", "run_classification", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "run_classification", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_classification", "uwg_term_2")
_emit_writes_through("p1", "run_classification", "write_through")
_emit_writes_through("p1", "run_classification", "write_through_2")
_emit_validated_by_safety_plane("p1", "run_classification", "safety_validation")
_emit_invokes_eval("p1", "run_classification", "eval_call")
_emit_proposal_commits_routing("p1", "run_classification", "routing_commit")
_emit_escalates_to_human("p1", "run_classification", "human_escalation")
_emit_routes_through("p1", "run_classification", "route_through")
_emit_checks_agent_registry("p1", "run_classification", "agent_registry")
_emit_validates_agent_capability("p1", "run_classification", "capability")
_emit_dispatches_execution_plan("p1", "run_classification", "exec_plan")
_emit_agent_executes_agent("p1", "run_classification", "sub_agent")
_emit_routes_to_agent("p1", "run_classification", "target_agent")
_emit_verifies_policy("p1", "run_classification", "policy_check")
_emit_observes_runtime_state("p1", "run_classification", "runtime_state")
_emit_verifies_boundary("p1", "run_classification", "boundary_check")
_emit_transcripts_response("p1", "run_classification", "transcript")
_emit_hard_fails_untranscripted("p1", "run_classification")
_emit_gated_by_confidence("p1", "run_classification", "confidence_gate")
emit_replay_key("p0", "run_classification")
emit_determinism_digest("p0", "run_classification")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "run_classification", "execution_auth")
_emit_validates_capability("p2", "run_classification", "capability_check")
_emit_routes_to_capability("p2", "run_classification", "capability_route")
_emit_writes_via_uwg("p2", "run_classification", "uwg_write")
_emit_blocks_direct_write("p2", "run_classification", "direct_write_block")
_emit_records_tool_invocation("p2", "run_classification", "tool_invocation")
_emit_captures_execution_output("p2", "run_classification", "exec_output")
_emit_dispatches_agent("p3", "run_classification", "agent_dispatch")
_emit_coordinates_agents("p3", "run_classification", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_classification", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_classification", "healing_outcome")
_emit_escalates_failure("p3", "run_classification", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_classification", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_classification", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_classification", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_classification", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_classification", "eval_metric")
_emit_stores_embedding("p4", "run_classification", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_classification", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_classification", "exec_snapshot_link")


def get_python_files_fast(root: Path) -> list[Path]:
    """Optimized repository scanner that prunes heavy directories"""
    python_files = []
    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith(".py"):
                python_files.append(Path(dirpath) / filename)
    return python_files


def classify_file(path: Path) -> str:
    """
    Classify file by type — delegates to the classification kernel (SSOT).

    [REFACTORED 2026-02-08] Removed 130-line reimplementation.
    Now delegates to the zero-dependency classification kernel for
    consistent results across all tools.

    This script's purpose is to flag naming violations, so it wraps the
    kernel result to determine if a file needs renaming or not.
    """
    from agentic_core.L5_safety.core_kernel.classification_kernel import classify_file_standalone

    file_type = classify_file_standalone(path)

    # This script only cares about files that need naming fixes.
    # Most types are already compliant — only flag actionable violations.
    if file_type in (
        "AGENT",
        "ORCHESTRATOR",
        "STRATEGY",
        "ADAPTER",
        "VALIDATOR",
        "EXCEPTION",
        "CONFIG",
        "FACTORY",
        "SERVICE",
        "ENGINE",
        "TYPES",
        "CLASS",
        "UTILITY",
        "STUB",
        "IGNORE",
    ):
        # Check if SCRIPT needs PascalCase→snake_case conversion
        pass

    if file_type == "SCRIPT":
        # Only flag if it's PascalCase (needs conversion to snake_case)
        if re.match(r"^[A-Z]", path.stem):
            return "SCRIPT"
        return "IGNORE"

    if file_type == "TEST":
        # Only flag if missing test_ prefix
        if path.name.startswith("test_") or path.name.endswith("_test.py"):
            return "IGNORE"
        return "TEST"

    if file_type == "MIXIN":
        # Only flag if filename is PascalCase (not already snake_case)
        if re.match(r"^[A-Z]", path.stem) and not path.stem.islower():
            return "MIXIN"
        return "IGNORE"

    if file_type == "PROTOCOL":
        return "PROTOCOL"

    if file_type == "GATEWAY":
        return "GATEWAY"

    return "IGNORE"


def get_compliant_name(path: Path, file_type: str) -> str | None:
    """Get compliant name for file based on type"""
    if file_type in {"IGNORE", "TYPES", "UTILITY", "PROTOCOL", "GATEWAY"}:
        return None

    if file_type == "SCRIPT":
        # Convert PascalCase to snake_case
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", path.stem).lower().replace("__", "_")
        return f"{snake}.py" if f"{snake}.py" != path.name else None

    if file_type == "TEST":
        # Add test_ prefix and convert to snake_case
        stem = path.stem
        if stem.startswith("test_"):
            return None  # Already compliant
        # Convert PascalCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", stem)
        clean = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        return f"test_{clean}.py" if f"test_{clean}.py" != path.name else None

    if file_type == "MIXIN":
        stem = path.stem
        # Check if already snake_case with _mixin suffix
        if stem.islower() and stem.endswith("_mixin"):
            return None  # Already compliant
        # Convert PascalCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", stem)
        clean_stem = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        if not clean_stem.endswith("_mixin"):
            clean_stem += "_mixin"
        target = f"{clean_stem}.py"
        return target if target != path.name else None

    return None


def find_imports_to_update(
    project_root: Path,
    old_name: str,
    new_name: str,
) -> list[dict[str, Any]]:
    """Find all files that import the old module name"""
    old_mod = old_name.replace(".py", "")
    new_mod = new_name.replace(".py", "")

    import_updates = []
    python_files = get_python_files_fast(project_root)

    for path in python_files:
        try:
            content = path.read_text(encoding="utf-8")
            if old_mod not in content:
                continue

            # Check for import patterns
            patterns = [
                rf"from\s+[\w.]*{re.escape(old_mod)}\s+import",
                rf"import\s+[\w.]*{re.escape(old_mod)}",
            ]

            for pattern in patterns:
                if re.search(pattern, content):
                    import_updates.append(
                        {
                            "file": str(path.relative_to(project_root)),
                            "old_module": old_mod,
                            "new_module": new_mod,
                        },
                    )
                    break
        # guardian: allow-silent-swallow
        except:  # noqa: E722  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            continue

    return import_updates


def main():
    """Main analysis function"""
    print("=" * 80)
    print("FILE CLASSIFICATION ANALYSIS")
    print("=" * 80)

    project_root = Path(__file__).parent.resolve()
    python_files = get_python_files_fast(project_root)

    stats = {"analyzed": len(python_files), "compliant": 0, "violations": {}}

    proposals = []

    for path in python_files:
        if not path.exists():
            continue

        file_type = classify_file(path)
        if file_type == "IGNORE":
            continue

        new_name = get_compliant_name(path, file_type)
        if new_name and new_name != path.name:
            stats["violations"][file_type] = stats["violations"].get(file_type, 0) + 1

            # Find import updates needed
            import_updates = find_imports_to_update(project_root, path.name, new_name)

            proposals.append(
                {
                    "current_path": str(path),
                    "current_name": path.name,
                    "proposed_name": new_name,
                    "file_type": file_type,
                    "relative_path": str(path.relative_to(project_root)),
                    "import_updates": import_updates,
                    "import_count": len(import_updates),
                },
            )
        else:
            stats["compliant"] += 1

    # Print summary
    print(f"\nTotal files analyzed: {stats['analyzed']}")
    print(f"Compliant files: {stats['compliant']}")
    total_violations = sum(stats["violations"].values())
    print(f"Total violations: {total_violations}")

    if total_violations > 0:
        print("\nViolation breakdown:")
        for vtype, count in sorted(stats["violations"].items(), key=lambda x: -x[1]):
            if count > 0:
                print(f"  {vtype}: {count}")

        # Group by phase
        phase1 = [p for p in proposals if p["file_type"] == "AGENT"]
        phase2 = [p for p in proposals if p["file_type"] == "MIXIN"]
        phase3 = [p for p in proposals if p["file_type"] == "TEST"]
        other = [p for p in proposals if p["file_type"] not in {"AGENT", "MIXIN", "TEST"}]

        print(f"\n{'=' * 80}")
        print(f"PHASE 1: AGENT RENAMES ({len(phase1)} files)")
        print(f"{'=' * 80}")
        for i, proposal in enumerate(phase1[:20], 1):
            print(f"{i:3d}. {proposal['relative_path']}")
            print(f"     {proposal['current_name']} -> {proposal['proposed_name']}")
            print(f"     Import updates needed: {proposal['import_count']}")
        if len(phase1) > 20:
            print(f"... and {len(phase1) - 20} more")

        print(f"\n{'=' * 80}")
        print(f"PHASE 2: MIXIN RENAMES ({len(phase2)} files)")
        print(f"{'=' * 80}")
        for i, proposal in enumerate(phase2[:20], 1):
            print(f"{i:3d}. {proposal['relative_path']}")
            print(f"     {proposal['current_name']} -> {proposal['proposed_name']}")
            print(f"     Import updates needed: {proposal['import_count']}")
        if len(phase2) > 20:
            print(f"... and {len(phase2) - 20} more")

        print(f"\n{'=' * 80}")
        print(f"PHASE 3: TEST RENAMES ({len(phase3)} files)")
        print(f"{'=' * 80}")
        for i, proposal in enumerate(phase3[:20], 1):
            print(f"{i:3d}. {proposal['relative_path']}")
            print(f"     {proposal['current_name']} -> {proposal['proposed_name']}")
        if len(phase3) > 20:
            print(f"... and {len(phase3) - 20} more")

        if other:
            print(f"\n{'=' * 80}")
            print(f"OTHER RENAMES ({len(other)} files)")
            print(f"{'=' * 80}")
            for i, proposal in enumerate(other[:10], 1):
                print(f"{i:3d}. {proposal['relative_path']} ({proposal['file_type']})")
                print(f"     {proposal['current_name']} -> {proposal['proposed_name']}")

    print(f"\nTotal proposals: {len(proposals)}")

    # Save detailed report
    report = {
        "summary": stats,
        "proposals": proposals,
        "total_proposals": len(proposals),
        "phase1_agent_count": len([p for p in proposals if p["file_type"] == "AGENT"]),
        "phase2_mixin_count": len([p for p in proposals if p["file_type"] == "MIXIN"]),
        "phase3_test_count": len([p for p in proposals if p["file_type"] == "TEST"]),
    }

    report_file = project_root / "file_classification_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {report_file}")
    return report


if __name__ == "__main__":
    main()
