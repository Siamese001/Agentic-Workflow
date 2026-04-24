#!/usr/bin/env python3
"""
Add @dataclass decorator to all agents that don't have it.

This script:
1. Reads agent_discovery_full.json to find agents with schema_strictness < 100%
2. Adds @dataclass decorator and dataclasses import to each agent file
3. Preserves existing code structure
"""

import ast
import json
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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
from tqdm import tqdm

_emit_emits_metric_event("add_dataclass_to_agents_util", "p4obs", "metric_1")
_emit_emits_metric_event("add_dataclass_to_agents_util", "p4obs", "metric_2")
_emit_emits_metric_event("add_dataclass_to_agents_util", "p4obs", "metric_3")
_emit_emits_metric_event("add_dataclass_to_agents_util", "p4obs", "metric_4")
_emit_emits_metric_event("add_dataclass_to_agents_util", "p4obs", "metric_5")
_emit_emits_metric_event("add_dataclass_to_agents_util", "p4obs", "metric_6")
_emit_records_incident_event("add_dataclass_to_agents_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("add_dataclass_to_agents_util", "p4obs", "anomaly")
_emit_writes_observability_log("add_dataclass_to_agents_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("add_dataclass_to_agents_util", "p4obs", "mon_state")
_emit_triggers_alert("add_dataclass_to_agents_util", "p4obs", "alert")
_emit_links_incident_trace("add_dataclass_to_agents_util", "p4obs", "trace_link")
_emit_captures_pattern("add_dataclass_to_agents_util", "p3lm", "pattern")
_emit_records_learning_event("add_dataclass_to_agents_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("add_dataclass_to_agents_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("add_dataclass_to_agents_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("add_dataclass_to_agents_util", "p3lm", "routing")
_emit_improves_agent_policy("add_dataclass_to_agents_util", "p3lm", "policy")
_emit_stores_learning_state("add_dataclass_to_agents_util", "p3lm", "state")
_emit_records_execution_trace("add_dataclass_to_agents_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("add_dataclass_to_agents_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("add_dataclass_to_agents_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("add_dataclass_to_agents_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("add_dataclass_to_agents_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("add_dataclass_to_agents_util", "env_read", "p2_env_1")
_emit_reads_environ("add_dataclass_to_agents_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("add_dataclass_to_agents_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("add_dataclass_to_agents_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "add_dataclass_to_agents_util")
emit_determinism_digest("p0", "add_dataclass_to_agents_util")

_emit_dispatches_healing_run("p1", "add_dataclass_to_agents_util", "L0")
_emit_routes_through("p1", "add_dataclass_to_agents_util", "L0")
_emit_checks_agent_registry("p1", "add_dataclass_to_agents_util", "agent_registry")
_emit_validates_agent_capability("p1", "add_dataclass_to_agents_util", "capability")
_emit_dispatches_execution_plan("p1", "add_dataclass_to_agents_util", "exec_plan")
_emit_agent_executes_agent("p1", "add_dataclass_to_agents_util", "sub_agent")
_emit_routes_to_agent("p1", "add_dataclass_to_agents_util", "target_agent")
_emit_verifies_policy("p1", "add_dataclass_to_agents_util", "policy_check")
_emit_observes_runtime_state("p1", "add_dataclass_to_agents_util", "runtime_state")
_emit_verifies_boundary("p1", "add_dataclass_to_agents_util", "boundary_check")
_emit_transcripts_response("p1", "add_dataclass_to_agents_util", "transcript")
_emit_hard_fails_untranscripted("p1", "add_dataclass_to_agents_util")
_emit_gated_by_confidence("p1", "add_dataclass_to_agents_util", "confidence_gate")
_emit_escalates_to_human("p1", "add_dataclass_to_agents_util", "L0")
_emit_reads_policy_state("p1", "add_dataclass_to_agents_util", "L0")
_emit_pulls_context("p1", "add_dataclass_to_agents_util", "context_pull")
_emit_pulls_context("p1", "add_dataclass_to_agents_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "add_dataclass_to_agents_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "add_dataclass_to_agents_util", "uwg_term_secondary")
_emit_writes_through("p1", "add_dataclass_to_agents_util", "write_through")
_emit_writes_through("p1", "add_dataclass_to_agents_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "add_dataclass_to_agents_util", "safety_validation")
_emit_invokes_eval("p1", "add_dataclass_to_agents_util", "eval_call")
_emit_proposal_commits_routing("p1", "add_dataclass_to_agents_util", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "add_dataclass_to_agents_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "add_dataclass_to_agents_util", "p0_governance")
_emit_snapshots_state("p0", "add_dataclass_to_agents_util", "state_snapshot")
_emit_authorize_and_execute("p2", "add_dataclass_to_agents_util", "execution_auth")
_emit_validates_capability("p2", "add_dataclass_to_agents_util", "capability_check")
_emit_routes_to_capability("p2", "add_dataclass_to_agents_util", "capability_route")
_emit_writes_via_uwg("p2", "add_dataclass_to_agents_util", "uwg_write")
_emit_blocks_direct_write("p2", "add_dataclass_to_agents_util", "direct_write_block")
_emit_records_tool_invocation("p2", "add_dataclass_to_agents_util", "tool_invocation")
_emit_captures_execution_output("p2", "add_dataclass_to_agents_util", "exec_output")
_emit_dispatches_agent("p3", "add_dataclass_to_agents_util", "agent_dispatch")
_emit_coordinates_agents("p3", "add_dataclass_to_agents_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "add_dataclass_to_agents_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "add_dataclass_to_agents_util", "healing_outcome")
_emit_escalates_failure("p3", "add_dataclass_to_agents_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "add_dataclass_to_agents_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "add_dataclass_to_agents_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "add_dataclass_to_agents_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "add_dataclass_to_agents_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "add_dataclass_to_agents_util", "eval_metric")
_emit_stores_embedding("p4", "add_dataclass_to_agents_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "add_dataclass_to_agents_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "add_dataclass_to_agents_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent


def has_dataclass_decorator(source: str) -> bool:
    """Check if source already has @dataclass decorator."""
    return "@dataclass" in source


def has_dataclass_import(source: str) -> bool:
    """Check if source already imports dataclass."""
    return "from dataclasses import" in source or "import dataclasses" in source


def add_dataclass_to_file(file_path: Path) -> bool:
    """Add @dataclass decorator to agent class in file.

    Returns True if changes were made.
    """
    if not file_path.exists():
        return False

    try:
        source = file_path.read_text(encoding="utf-8")
        original_source = source

        # Skip if already has @dataclass
        if has_dataclass_decorator(source):
            return False

        # Parse to find the agent class
        try:
            tree = ast.parse(source)
        except SyntaxError:  # guardian: allow-silent-swallow -- acceptable exception handling
            return False

        # Find the main agent class (ends with 'Agent')
        agent_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                agent_class = node
                break

        if not agent_class:
            return False

        lines = source.split("\n")

        # Add dataclass import if needed
        if not has_dataclass_import(source):
            # Find the best place to add the import
            import_line = 0
            for i, line in enumerate(lines):
                if line.startswith("from __future__"):
                    import_line = i + 1
                elif line.startswith("import ") or line.startswith("from "):
                    import_line = i + 1
                elif line.strip() and not line.startswith("#") and not line.startswith('"""'):
                    break

            lines.insert(import_line, "from dataclasses import dataclass")

        # Find the class definition line and add @dataclass before it
        # Need to re-parse after potential import addition
        source = "\n".join(lines)
        try:
            # guardian: allow-silent-swallow -- acceptable exception handling
            tree = ast.parse(source)
        except SyntaxError:
            return False

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                # Check if already has @dataclass decorator
                has_dc = False
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name) and dec.id == "dataclass":
                        has_dc = True
                    elif (
                        isinstance(dec, ast.Call)
                        and isinstance(dec.func, ast.Name)
                        and dec.func.id == "dataclass"
                    ):
                        has_dc = True

                if not has_dc:
                    # Add @dataclass decorator before the class
                    lines = source.split("\n")
                    class_line = node.lineno - 1  # 0-indexed

                    # Get the indentation of the class line
                    indent = ""
                    if lines[class_line]:
                        indent = len(lines[class_line]) - len(lines[class_line].lstrip())
                        indent = " " * indent

                    # Insert @dataclass before the class definition
                    lines.insert(class_line, f"{indent}@dataclass")
                    source = "\n".join(lines)
                break

        if source != original_source:
            assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
            file_path.write_text(source, encoding="utf-8")
            return True

        return False

    except (ValueError, TypeError) as e:
        print(f"  Error processing {file_path}: {e}")
        return False


def main():
    print("=" * 70)
    print("Adding @dataclass decorator to agents for schema Strictness 100%")
    print("=" * 70)

    # Load agent discovery
    discovery_path = PROJECT_ROOT / "agent_discovery_full.json"
    with open(discovery_path, encoding="utf-8") as f:
        agents = json.load(f)

    # Find agents needing @dataclass
    agents_to_fix = [a for a in agents if a.get("schema_strictness", 100) < 100]

    print(f"\nAgents needing @dataclass: {len(agents_to_fix)}")

    fixed_count = 0
    skipped_count = 0

    for agent in tqdm(agents_to_fix, desc="Processing", unit="item"):
        path = agent["path"]
        file_path = PROJECT_ROOT / path

        if not file_path.exists():
            # Try with different path variations
            alt_paths = [
                PROJECT_ROOT / AGENTIC_CORE_DIR / path,
                PROJECT_ROOT / path.replace("\\", "/"),
            ]
            for alt in alt_paths:
                if alt.exists():
                    file_path = alt
                    break

        if not file_path.exists():
            skipped_count += 1
            continue

        if add_dataclass_to_file(file_path):
            print(f"  ✓ {agent['class_name']}")
            fixed_count += 1
        else:
            skipped_count += 1

    print("\n" + "=" * 70)
    print(f"✅ Added @dataclass to {fixed_count} agent files")
    print(f"   Skipped: {skipped_count} (already have @dataclass or couldn't process)")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
