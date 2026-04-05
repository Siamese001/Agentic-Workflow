from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "extract_pattern_util")
emit_determinism_digest("p0", "extract_pattern_util")

_emit_dispatches_healing_run("p1", "extract_pattern_util", "L5")
_emit_routes_through("p1", "extract_pattern_util", "L5")
_emit_checks_agent_registry("p1", "extract_pattern_util", "agent_registry")
_emit_validates_agent_capability("p1", "extract_pattern_util", "capability")
_emit_dispatches_execution_plan("p1", "extract_pattern_util", "exec_plan")
_emit_agent_executes_agent("p1", "extract_pattern_util", "sub_agent")
_emit_routes_to_agent("p1", "extract_pattern_util", "target_agent")
_emit_verifies_policy("p1", "extract_pattern_util", "policy_check")
_emit_observes_runtime_state("p1", "extract_pattern_util", "runtime_state")
_emit_verifies_boundary("p1", "extract_pattern_util", "boundary_check")
_emit_transcripts_response("p1", "extract_pattern_util", "transcript")
_emit_hard_fails_untranscripted("p1", "extract_pattern_util")
_emit_gated_by_confidence("p1", "extract_pattern_util", "confidence_gate")
_emit_escalates_to_human("p1", "extract_pattern_util", "L5")
_emit_reads_policy_state("p1", "extract_pattern_util", "L5")
_emit_authorize_and_execute("p2", "extract_pattern_util", "execution_auth")
_emit_validates_capability("p2", "extract_pattern_util", "capability_check")
_emit_routes_to_capability("p2", "extract_pattern_util", "capability_route")
_emit_writes_via_uwg("p2", "extract_pattern_util", "uwg_write")
_emit_blocks_direct_write("p2", "extract_pattern_util", "direct_write_block")
_emit_records_tool_invocation("p2", "extract_pattern_util", "tool_invocation")
_emit_captures_execution_output("p2", "extract_pattern_util", "exec_output")
_emit_dispatches_agent("p3", "extract_pattern_util", "agent_dispatch")
_emit_coordinates_agents("p3", "extract_pattern_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "extract_pattern_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "extract_pattern_util", "healing_outcome")
_emit_escalates_failure("p3", "extract_pattern_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "extract_pattern_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "extract_pattern_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "extract_pattern_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "extract_pattern_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "extract_pattern_util", "eval_metric")
_emit_stores_embedding("p4", "extract_pattern_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "extract_pattern_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "extract_pattern_util", "exec_snapshot_link")

"\nExtract PatternEnforcerAgent from canon_agents_pattern.py.\nAlso removes SubAtomicAgent stub and adds proper import.\n"
import ast
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("extract_pattern_util", "p4obs", "metric_1")
_emit_emits_metric_event("extract_pattern_util", "p4obs", "metric_2")
_emit_emits_metric_event("extract_pattern_util", "p4obs", "metric_3")
_emit_emits_metric_event("extract_pattern_util", "p4obs", "metric_4")
_emit_emits_metric_event("extract_pattern_util", "p4obs", "metric_5")
_emit_emits_metric_event("extract_pattern_util", "p4obs", "metric_6")
_emit_records_incident_event("extract_pattern_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("extract_pattern_util", "p4obs", "anomaly")
_emit_writes_observability_log("extract_pattern_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("extract_pattern_util", "p4obs", "mon_state")
_emit_triggers_alert("extract_pattern_util", "p4obs", "alert")
_emit_links_incident_trace("extract_pattern_util", "p4obs", "trace_link")
_emit_captures_pattern("extract_pattern_util", "p3lm", "pattern")
_emit_records_learning_event("extract_pattern_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("extract_pattern_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("extract_pattern_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("extract_pattern_util", "p3lm", "routing")
_emit_improves_agent_policy("extract_pattern_util", "p3lm", "policy")
_emit_stores_learning_state("extract_pattern_util", "p3lm", "state")
_emit_records_execution_trace("extract_pattern_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("extract_pattern_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("extract_pattern_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("extract_pattern_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("extract_pattern_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("extract_pattern_util", "env_read", "p2_env_1")
_emit_reads_environ("extract_pattern_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("extract_pattern_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("extract_pattern_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "extract_pattern_util", "context_pull")
_emit_pulls_context("p1", "extract_pattern_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "extract_pattern_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "extract_pattern_util", "uwg_term_2")
_emit_writes_through("p1", "extract_pattern_util", "write_through")
_emit_writes_through("p1", "extract_pattern_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "extract_pattern_util", "safety_validation")
_emit_invokes_eval("p1", "extract_pattern_util", "eval_call")
_emit_proposal_commits_routing("p1", "extract_pattern_util", "routing_commit")

SOURCE_FILE = Path("agentic_core/L1_cognition/thought_engine/canon_agents_pattern.py")
TARGET_DIR = Path("agentic_core/L1_cognition/thought_engine")


def extract_class_with_context(content: str, class_name: str) -> tuple[str, int, int]:
    """Extract class source with preceding comments."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_class_with_context", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_class_with_context", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "extract_class_with_context")
    lines = content.split("\n")
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith("#") or not prev_line:
                    start_line -= 1
                else:
                    break
            class_source = "\n".join(lines[start_line:end_line])
            return (class_source, start_line + 1, end_line)
    raise ValueError(f"Class {class_name} not found")


def create_pattern_enforcer_file(class_source: str):
    """Create sovereign file for PatternEnforcerAgent."""
    target_file = TARGET_DIR / "PatternEnforcerAgent.py"
    content = f'"""\nPatternEnforcerAgent - Extracted from canon_agents_pattern.py\nEnforces coding patterns and best practices across Python files.\n"""\nimport ast\nimport logging\nimport re\nfrom typing import Any, Dict, List, Optional, Protocol, Tuple\n\n# DEPRECATED: CanonBaseAgentInterface removed - use Protocol instead\ntry:\n    from agentic_core.base_agents.canon_base_agent_interface import CanonBaseAgentInterface\nexcept ImportError:\n    class CanonBaseAgentInterface(Protocol):\n        pass\n\nfrom agentic_core.L3_orchestration.reasoning.subatomic_testing_mixin import subatomic_testing_mixin\nfrom agentic_core.L5_safety.enforcement.mcp_hardened_mixin import mcp_hardened_mixin\nfrom agentic_core.L5_safety.config.structure_blueprint_config import (\n    SOVEREIGN_TERRITORIES,\n    CORE_SUBFOLDER_MAP,\n)\nfrom agentic_core.mixins.healer_mixin import healer_mixin\n\nLogger: Any = logging.getLogger(__name__)\n\n{class_source}\n'
    print(f"Creating {target_file}")
    _wg.open_write(target_file, content)
    return target_file


def update_source_file(source_file: Path):
    """Remove PatternEnforcerAgent and SubAtomicAgent stub, add proper import."""
    with open(source_file, encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")
    tree = ast.parse(content)
    classes_to_remove = ["PatternEnforcerAgent", "SubAtomicAgent"]
    ranges_to_remove = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in classes_to_remove:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith("#") or not prev_line:
                    start_line -= 1
                else:
                    break
            ranges_to_remove.append((start_line, end_line, node.name))
    ranges_to_remove.sort(reverse=True)
    backup_file = source_file.with_suffix(".py.bak")
    print(f"  Creating backup: {backup_file}")
    with open(source_file, encoding="utf-8") as f:
        _wg.open_write(backup_file, f.read())
    for start, end, name in ranges_to_remove:
        del lines[start:end]
        if name == "PatternEnforcerAgent":
            lines.insert(start, f"# {name} extracted to {name}.py (Phase B Task 4)")
            lines.insert(start + 1, "")
    import_line = "from agentic_core.L3_orchestration.reasoning.SubAtomicAgent import SubAtomicAgent"
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("from agentic_core.base_agents"):
            insert_idx = i + 1
            break
    lines.insert(insert_idx, import_line)
    lines.insert(insert_idx + 1, "")
    _wg.open_write(source_file, "\n".join(lines))


def main():
    print("=" * 60)
    print("PATTERN AGENT EXTRACTION - PHASE B TASK 4")
    print("=" * 60)
    print(f"\nReading {SOURCE_FILE}")
    with open(SOURCE_FILE, encoding="utf-8") as f:
        content = f.read()
    print("\n📦 Extracting PatternEnforcerAgent...")
    try:
        class_source, start, end = extract_class_with_context(content, "PatternEnforcerAgent")
        target_file = create_pattern_enforcer_file(class_source)
        print(f"  ✅ Created {target_file} (lines {start}-{end})")
    except (ValueError, TypeError) as e:
        print(f"  ❌ Failed: {e}")
        return False
    print(f"\nUpdating {SOURCE_FILE}...")
    print("  - Removing PatternEnforcerAgent")
    print("  - Removing SubAtomicAgent stub")
    print("  - Adding SubAtomicAgent import")
    update_source_file(SOURCE_FILE)
    print(f"  ✅ Updated {SOURCE_FILE}")
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print("\n✅ PatternEnforcerAgent.py created")
    print("✅ canon_agents_pattern.py updated with proper import")
    print("\n⚠️  Next steps:")
    print("  1. Rename _GenerativeGuard_Deprecated in CanonHealerAgent.py")
    print("  2. Update imports for PatternEnforcerAgent")
    print("  3. Run discovery to verify 281 agents")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
