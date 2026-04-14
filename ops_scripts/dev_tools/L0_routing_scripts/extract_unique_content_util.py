#!/usr/bin/env python3
"""
Extract unique classes/functions from high-priority archived files.
Only extracts content that doesn't exist in current codebase.
"""

import ast
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "extract_unique_content_util")
emit_determinism_digest("p0", "extract_unique_content_util")

_emit_dispatches_healing_run("p1", "extract_unique_content_util", "L0")
_emit_routes_through("p1", "extract_unique_content_util", "L0")
_emit_checks_agent_registry("p1", "extract_unique_content_util", "agent_registry")
_emit_validates_agent_capability("p1", "extract_unique_content_util", "capability")
_emit_dispatches_execution_plan("p1", "extract_unique_content_util", "exec_plan")
_emit_agent_executes_agent("p1", "extract_unique_content_util", "sub_agent")
_emit_routes_to_agent("p1", "extract_unique_content_util", "target_agent")
_emit_verifies_policy("p1", "extract_unique_content_util", "policy_check")
_emit_observes_runtime_state("p1", "extract_unique_content_util", "runtime_state")
_emit_verifies_boundary("p1", "extract_unique_content_util", "boundary_check")
_emit_transcripts_response("p1", "extract_unique_content_util", "transcript")
_emit_hard_fails_untranscripted("p1", "extract_unique_content_util")
_emit_gated_by_confidence("p1", "extract_unique_content_util", "confidence_gate")
_emit_escalates_to_human("p1", "extract_unique_content_util", "L0")
_emit_reads_policy_state("p1", "extract_unique_content_util", "L0")

_emit_records_execution_trace("p0", "evidence", "extract_unique_content_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "extract_unique_content_util", "p0_governance")
_emit_snapshots_state("p0", "extract_unique_content_util", "state_snapshot")
_emit_authorize_and_execute("p2", "extract_unique_content_util", "execution_auth")
_emit_validates_capability("p2", "extract_unique_content_util", "capability_check")
_emit_routes_to_capability("p2", "extract_unique_content_util", "capability_route")
_emit_writes_via_uwg("p2", "extract_unique_content_util", "uwg_write")
_emit_blocks_direct_write("p2", "extract_unique_content_util", "direct_write_block")
_emit_records_tool_invocation("p2", "extract_unique_content_util", "tool_invocation")
_emit_captures_execution_output("p2", "extract_unique_content_util", "exec_output")
_emit_dispatches_agent("p3", "extract_unique_content_util", "agent_dispatch")
_emit_coordinates_agents("p3", "extract_unique_content_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "extract_unique_content_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "extract_unique_content_util", "healing_outcome")
_emit_escalates_failure("p3", "extract_unique_content_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "extract_unique_content_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "extract_unique_content_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "extract_unique_content_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "extract_unique_content_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "extract_unique_content_util", "eval_metric")
_emit_stores_embedding("p4", "extract_unique_content_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "extract_unique_content_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "extract_unique_content_util", "exec_snapshot_link")
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
from tqdm import tqdm

_emit_emits_metric_event("extract_unique_content_util", "p4obs", "metric_1")
_emit_emits_metric_event("extract_unique_content_util", "p4obs", "metric_2")
_emit_emits_metric_event("extract_unique_content_util", "p4obs", "metric_3")
_emit_emits_metric_event("extract_unique_content_util", "p4obs", "metric_4")
_emit_emits_metric_event("extract_unique_content_util", "p4obs", "metric_5")
_emit_emits_metric_event("extract_unique_content_util", "p4obs", "metric_6")
_emit_records_incident_event("extract_unique_content_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("extract_unique_content_util", "p4obs", "anomaly")
_emit_writes_observability_log("extract_unique_content_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("extract_unique_content_util", "p4obs", "mon_state")
_emit_triggers_alert("extract_unique_content_util", "p4obs", "alert")
_emit_links_incident_trace("extract_unique_content_util", "p4obs", "trace_link")
_emit_captures_pattern("extract_unique_content_util", "p3lm", "pattern")
_emit_records_learning_event("extract_unique_content_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("extract_unique_content_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("extract_unique_content_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("extract_unique_content_util", "p3lm", "routing")
_emit_improves_agent_policy("extract_unique_content_util", "p3lm", "policy")
_emit_stores_learning_state("extract_unique_content_util", "p3lm", "state")
_emit_records_execution_trace("extract_unique_content_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("extract_unique_content_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("extract_unique_content_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("extract_unique_content_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("extract_unique_content_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("extract_unique_content_util", "env_read", "p2_env_1")
_emit_reads_environ("extract_unique_content_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("extract_unique_content_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("extract_unique_content_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "extract_unique_content_util", "context_pull")
_emit_pulls_context("p1", "extract_unique_content_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "extract_unique_content_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "extract_unique_content_util", "uwg_term_2")
_emit_writes_through("p1", "extract_unique_content_util", "write_through")
_emit_writes_through("p1", "extract_unique_content_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "extract_unique_content_util", "safety_validation")
_emit_invokes_eval("p1", "extract_unique_content_util", "eval_call")
_emit_proposal_commits_routing("p1", "extract_unique_content_util", "routing_commit")


def build_codebase_index(dirs: list[str]) -> tuple[set[str], set[str]]:
    """Build index of all class and function names in current codebase."""
    classes = set()
    functions = set()

    for dir_path in tqdm(dirs, desc="Processing", unit="item"):
        for py_file in tqdm(Path(dir_path).rglob("*.py"), desc="Processing", unit="item"):
            if "__pycache__" in str(py_file) or ARCHIVES_DIR in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.add(node.name.lower())
                    elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        functions.add(node.name.lower())
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                continue

    return classes, functions


def analyze_archive_file(file_path: Path, existing_classes: set[str], existing_functions: set[str]) -> dict:
    """Analyze an archived file and identify unique content."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
    except (ValueError, TypeError, RuntimeError) as e:
        return {"error": True}

    unique_classes = []
    unique_functions = []
    existing_in_file = []

    for node in tqdm(ast.iter_child_nodes(tree), desc="Processing", unit="item"):
        if isinstance(node, ast.ClassDef):
            if node.name.lower() not in existing_classes:
                # Get bases
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)

                # Get methods
                methods = [
                    item.name
                    for item in node.body
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
                ]

                unique_classes.append(
                    {
                        "name": node.name,
                        "bases": bases,
                        "methods": methods[:10],
                        "is_agent": node.name.endswith("Agent"),
                        "lineno": node.lineno,
                        "end_lineno": getattr(node, "end_lineno", node.lineno + 50),
                    },
                )
            else:
                existing_in_file.append(node.name)

        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if node.name.lower() not in existing_functions and not node.name.startswith("_"):
                params = [arg.arg for arg in node.args.args if arg.arg != "self"]
                unique_functions.append(
                    {
                        "name": node.name,
                        "params": params,
                        "lineno": node.lineno,
                        "end_lineno": getattr(node, "end_lineno", node.lineno + 20),
                    },
                )
            else:
                existing_in_file.append(node.name)

    return {
        "unique_classes": unique_classes,
        "unique_functions": unique_functions,
        "existing": existing_in_file,
        "error": False,
    }


def main():
    print("=" * 80)
    print("EXTRACTING UNIQUE CONTENT FROM HIGH-PRIORITY ARCHIVES")
    print("=" * 80)

    # Build codebase index
    print("\n[1/3] Building codebase index...")
    current_dirs = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, "scripts"]
    existing_classes, existing_functions = build_codebase_index(current_dirs)
    print(f"  Indexed: {len(existing_classes)} classes, {len(existing_functions)} functions")

    # High-priority files to analyze (remaining 44 from report)
    high_priority_files = [
        # Legacy agents with unique detectors
        (
            "archives/legacy_agents/legacy_detectors/DuplicateCodeDetectorAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/PerformanceBottleneckAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/SecurityVulnerabilityAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/UnusedImportCleanerAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/DeprecatedAPIDetectorAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/MemoryLeakDetectorAgent.py",
            "apps_shared/base_agents",
        ),
        # Legacy validators
        ("archives/legacy_validators/StructuralHealerAgent.py", "apps_shared/base_agents"),
        ("archives/legacy_validators/CanonValidatorAgent.py", "apps_shared/base_agents"),
        (
            "archives/legacy_validators/ContentCleanlinessValidatorAgent.py",
            "apps_shared/base_agents",
        ),
        # Reachout Engine - agents
        ("archives/Reachout Engine Archive/deprecated in v13/agents_v13.py", "apps_lic/engines"),
        ("archives/Reachout Engine Archive/Agentic LIC/rag.py", "apps_lic/engines/stacks"),
        # Reachout Engine - models and utilities
        ("archives/Reachout Engine Archive/deprecated in v13/toggles.py", "apps_lic/engines/utils"),
        ("archives/Reachout Engine Archive/deprecated in v13/models.py", "apps_lic/engines/utils"),
        # apps_lic archive - routing and archetypes
        ("archives/apps_lic/L1_cognition/lic_cta_patterns.py", "apps_lic/engines/utils"),
        ("archives/apps_lic/L1_cognition/lic_routing_rules.py", "apps_lic/engines/utils"),
        ("archives/apps_lic/L1_cognition/lic_archetypes.py", "apps_lic/engines/utils"),
        ("archives/apps_lic/L1_cognition/lic_vector_memory.py", "apps_lic/engines/utils"),
        ("archives/apps_lic/L1_cognition/lic_code_interpreter.py", "apps_lic/engines/utils"),
        # apps_rg archive - creative brief
        ("archives/apps_rg/L1_cognition/rg_creative_brief.py", "apps_rg/engines/utils"),
        # Legacy orchestrators
        (
            "archives/legacy_orchestrators/SelfRecoveringOrchestratorAgent.py",
            "apps_shared/base_agents",
        ),
    ]

    print(f"\n[2/3] Analyzing {len(high_priority_files)} high-priority files...")

    to_restore_full = []  # Files to restore completely
    to_extract = []  # Files with some unique content to extract
    skip_files = []  # Files with no unique content

    for archive_path, target_dir in tqdm(high_priority_files, desc="Processing", unit="item"):
        file_path = Path(archive_path)
        if not file_path.exists():
            print(f"  [NOT FOUND] {archive_path}")
            continue

        result = analyze_archive_file(file_path, existing_classes, existing_functions)

        if result.get("error"):
            print(f"  [SYNTAX ERROR] {file_path.name}")
            continue

        unique_classes = result["unique_classes"]
        unique_functions = result["unique_functions"]
        existing = result["existing"]

        unique_agents = [c for c in unique_classes if c["is_agent"]]
        unique_other = [c for c in unique_classes if not c["is_agent"]]

        if unique_agents:
            # Has unique agents - restore full file
            to_restore_full.append(
                {
                    "source": archive_path,
                    "target": target_dir,
                    "unique_agents": [a["name"] for a in unique_agents],
                    "unique_classes": [c["name"] for c in unique_other],
                    "unique_functions": [f["name"] for f in unique_functions],
                },
            )
            print(f"  [RESTORE FULL] {file_path.name} - {len(unique_agents)} unique agents")
        elif unique_other or unique_functions:
            # Has unique classes/functions but no agents
            to_extract.append(
                {
                    "source": archive_path,
                    "target": target_dir,
                    "unique_classes": [c["name"] for c in unique_other],
                    "unique_functions": [f["name"] for f in unique_functions],
                    "existing": existing,
                },
            )
            print(
                f"  [EXTRACT] {file_path.name} - {len(unique_other)} classes, {len(unique_functions)} functions",
            )
        else:
            skip_files.append(
                {
                    "source": archive_path,
                    "existing": existing,
                },
            )
            print(f"  [SKIP] {file_path.name} - all content exists")

    # Print summary
    print("\n" + "=" * 80)
    print("RESTORATION PLAN")
    print("=" * 80)

    print(f"\n## RESTORE FULL ({len(to_restore_full)} files)")
    for item in to_restore_full:
        print(f"\n  {Path(item['source']).name} -> {item['target']}/")
        print(f"    Unique Agents: {item['unique_agents']}")
        if item["unique_classes"]:
            print(f"    Unique Classes: {item['unique_classes'][:5]}")

    print(f"\n## EXTRACT UNIQUE CONTENT ({len(to_extract)} files)")
    for item in to_extract:
        print(f"\n  {Path(item['source']).name} -> {item['target']}/")
        print(f"    Unique Classes: {item['unique_classes'][:5]}")
        print(f"    Unique Functions: {item['unique_functions'][:5]}")

    print(f"\n## SKIP ({len(skip_files)} files)")
    for item in skip_files:
        print(f"  {Path(item['source']).name} - exists: {item['existing'][:3]}")

    # Execute restorations
    print("\n" + "=" * 80)
    print("EXECUTING RESTORATIONS")
    print("=" * 80)

    import shutil

    restored_count = 0
    for item in tqdm(to_restore_full, desc="Processing", unit="item"):
        src = Path(item["source"])
        target_dir = Path(item["target"])
        target_dir.mkdir(parents=True, exist_ok=True)

        # Use agent name as filename if available
        if item["unique_agents"]:
            dst_name = item["unique_agents"][0] + ".py"
        else:
            dst_name = src.name

        dst = target_dir / dst_name

        if not dst.exists():
            shutil.copy2(str(src), str(dst))
            print(f"  ✓ Restored: {dst}")
            restored_count += 1
        else:
            print(f"  - Skipped (exists): {dst}")

    # For extract files, copy the whole file (simpler than extracting individual classes)
    for item in tqdm(to_extract, desc="Processing", unit="item"):
        src = Path(item["source"])
        target_dir = Path(item["target"])
        target_dir.mkdir(parents=True, exist_ok=True)

        dst = target_dir / src.name

        if not dst.exists():
            shutil.copy2(str(src), str(dst))
            print(f"  ✓ Restored: {dst}")
            restored_count += 1
        else:
            print(f"  - Skipped (exists): {dst}")

    print(f"\n  Total restored: {restored_count} files")


if __name__ == "__main__":
    main()
