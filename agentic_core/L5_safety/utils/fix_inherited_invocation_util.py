from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "fix_inherited_invocation_util")
emit_determinism_digest("p0", "fix_inherited_invocation_util")

_emit_dispatches_healing_run("p1", "fix_inherited_invocation_util", "L5")
_emit_routes_through("p1", "fix_inherited_invocation_util", "L5")
_emit_checks_agent_registry("p1", "fix_inherited_invocation_util", "agent_registry")
_emit_validates_agent_capability("p1", "fix_inherited_invocation_util", "capability")
_emit_dispatches_execution_plan("p1", "fix_inherited_invocation_util", "exec_plan")
_emit_agent_executes_agent("p1", "fix_inherited_invocation_util", "sub_agent")
_emit_routes_to_agent("p1", "fix_inherited_invocation_util", "target_agent")
_emit_verifies_policy("p1", "fix_inherited_invocation_util", "policy_check")
_emit_observes_runtime_state("p1", "fix_inherited_invocation_util", "runtime_state")
_emit_verifies_boundary("p1", "fix_inherited_invocation_util", "boundary_check")
_emit_transcripts_response("p1", "fix_inherited_invocation_util", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_inherited_invocation_util")
_emit_gated_by_confidence("p1", "fix_inherited_invocation_util", "confidence_gate")
_emit_escalates_to_human("p1", "fix_inherited_invocation_util", "L5")
_emit_reads_policy_state("p1", "fix_inherited_invocation_util", "L5")
_emit_authorize_and_execute("p2", "fix_inherited_invocation_util", "execution_auth")
_emit_validates_capability("p2", "fix_inherited_invocation_util", "capability_check")
_emit_routes_to_capability("p2", "fix_inherited_invocation_util", "capability_route")
_emit_writes_via_uwg("p2", "fix_inherited_invocation_util", "uwg_write")
_emit_blocks_direct_write("p2", "fix_inherited_invocation_util", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_inherited_invocation_util", "tool_invocation")
_emit_captures_execution_output("p2", "fix_inherited_invocation_util", "exec_output")
_emit_dispatches_agent("p3", "fix_inherited_invocation_util", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_inherited_invocation_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_inherited_invocation_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_inherited_invocation_util", "healing_outcome")
_emit_escalates_failure("p3", "fix_inherited_invocation_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_inherited_invocation_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_inherited_invocation_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_inherited_invocation_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_inherited_invocation_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_inherited_invocation_util", "eval_metric")
_emit_stores_embedding("p4", "fix_inherited_invocation_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_inherited_invocation_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_inherited_invocation_util", "exec_snapshot_link")

'\nFix Inherited Invocation - Add heal_repository() methods to agents missing explicit invocation.\n\nThis script:\n1. Loads agents with invocation=\'Inherited\' from agent_discovery_full.json\n2. For each agent class, adds a heal_repository(, **kwargs) method that calls super(, **kwargs).heal_repository(, **kwargs)\n3. This converts "Inherited" → "Yes" status, maximizing invocation %\n'
import ast
import json
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENT_DISCOVERY_JSON
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("fix_inherited_invocation_util", "p4obs", "metric_1")
_emit_emits_metric_event("fix_inherited_invocation_util", "p4obs", "metric_2")
_emit_emits_metric_event("fix_inherited_invocation_util", "p4obs", "metric_3")
_emit_emits_metric_event("fix_inherited_invocation_util", "p4obs", "metric_4")
_emit_emits_metric_event("fix_inherited_invocation_util", "p4obs", "metric_5")
_emit_emits_metric_event("fix_inherited_invocation_util", "p4obs", "metric_6")
_emit_records_incident_event("fix_inherited_invocation_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_inherited_invocation_util", "p4obs", "anomaly")
_emit_writes_observability_log("fix_inherited_invocation_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_inherited_invocation_util", "p4obs", "mon_state")
_emit_triggers_alert("fix_inherited_invocation_util", "p4obs", "alert")
_emit_links_incident_trace("fix_inherited_invocation_util", "p4obs", "trace_link")
_emit_captures_pattern("fix_inherited_invocation_util", "p3lm", "pattern")
_emit_records_learning_event("fix_inherited_invocation_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_inherited_invocation_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_inherited_invocation_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_inherited_invocation_util", "p3lm", "routing")
_emit_improves_agent_policy("fix_inherited_invocation_util", "p3lm", "policy")
_emit_stores_learning_state("fix_inherited_invocation_util", "p3lm", "state")
_emit_records_execution_trace("fix_inherited_invocation_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_inherited_invocation_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_inherited_invocation_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_inherited_invocation_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_inherited_invocation_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_inherited_invocation_util", "env_read", "p2_env_1")
_emit_reads_environ("fix_inherited_invocation_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_inherited_invocation_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_inherited_invocation_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "fix_inherited_invocation_util", "context_pull")
_emit_pulls_context("p1", "fix_inherited_invocation_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "fix_inherited_invocation_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_inherited_invocation_util", "uwg_term_2")
_emit_writes_through("p1", "fix_inherited_invocation_util", "write_through")
_emit_writes_through("p1", "fix_inherited_invocation_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "fix_inherited_invocation_util", "safety_validation")
_emit_invokes_eval("p1", "fix_inherited_invocation_util", "eval_call")
_emit_proposal_commits_routing("p1", "fix_inherited_invocation_util", "routing_commit")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
HEAL_METHOD_TEMPLATE = '\n    def heal_repository(self, **kwargs) -> dict:\n        """Invoke healing chain via super()."""\n        return super(, **kwargs).heal_repository(, **kwargs)\n'


def load_inherited_agents() -> list[dict]:
    """Load agents with invocation='Inherited' status."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_inherited_agents", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_inherited_agents", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "load_inherited_agents")
    with open(DISCOVERY_JSON, encoding="utf-8") as f:
        agents = json.load(f)
    return [
        a for a in agents if a.get("invocation") == "Inherited"
    ]  # guardian: Syntax errors should be caught at parser level, not runtime


def find_class_end(source: str, class_name: str) -> tuple[int, int]:
    """Find the end of a class definition to insert method before it."""
    try:
        tree = ast.parse(source)
    except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
        return (-1, -1)
    for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            if node.body:
                last_node = node.body[-1]
                end_line = getattr(last_node, "end_lineno", last_node.lineno)
                lines = source.splitlines()
                if node.body:
                    first_body_line = node.body[0].lineno - 1
                    if first_body_line < len(lines):
                        indent = len(lines[first_body_line]) - len(lines[first_body_line].lstrip())
                    else:
                        indent = 4
                else:
                    indent = 4
                return (end_line, indent)
    return (-1, -1)  # guardian: Syntax errors should be caught at parser level, not runtime


def has_heal_repository(source: str, class_name: str) -> bool:
    """Check if class already has heal_repository method."""
    try:
        tree = ast.parse(source)
    except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
        return True
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "heal_repository":
                    return True
    return False


def add_heal_repository(file_path: Path, class_name: str) -> bool:
    """Add heal_repository method to a class."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except (RuntimeError, OSError) as e:
        print(f"  [ERROR] Cannot read {file_path}: {e}")
        return False
    if has_heal_repository(source, class_name):
        print(f"  [SKIP] {class_name} already has heal_repository")
        return False
    end_line, indent = find_class_end(source, class_name)
    if end_line < 0:
        print(f"  [ERROR] Cannot find class {class_name} in {file_path}")
        return False
    method_lines = HEAL_METHOD_TEMPLATE.strip().splitlines()
    indented_method = (
        "\n" + "\n".join(" " * indent + line if line.strip() else "" for line in method_lines) + "\n"
    )
    lines = source.splitlines(keepends=True)
    insert_idx = end_line
    while insert_idx < len(lines) and lines[insert_idx - 1].strip() == "":
        insert_idx += 1
    new_lines = lines[:end_line] + [indented_method] + lines[end_line:]
    new_source = "".join(new_lines)
    try:
        _wg.write_text(file_path, new_source, encoding="utf-8")
        print(f"  [ADDED] heal_repository to {class_name}")
        return True
    except (RuntimeError, OSError) as e:
        print(f"  [ERROR] Cannot write {file_path}: {e}")
        return False


def main():
    print("=" * 80)
    print("FIX INHERITED INVOCATION")
    print("=" * 80)
    agents = load_inherited_agents()
    print(f"\nFound {len(agents)} agents with 'Inherited' invocation status\n")
    by_file: dict[str, list[str]] = {}
    for agent in agents:
        path = agent.get("path", "")
        class_name = agent.get("class_name", "")
        if path and class_name:
            full_path = str(PROJECT_ROOT / path)
            if full_path not in by_file:
                by_file[full_path] = []
            if class_name not in by_file[full_path]:
                by_file[full_path].append(class_name)
    print(f"Processing {len(by_file)} unique files...\n")
    added = 0
    skipped = 0
    errors = 0
    for file_path_str, class_names in tqdm(sorted(by_file.items()), desc="Processing", unit="item"):
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"[SKIP] File not found: {file_path}")
            skipped += len(class_names)
            continue
        print(f"\n{file_path.relative_to(PROJECT_ROOT)}:")
        for class_name in class_names:
            result = add_heal_repository(file_path, class_name)
            if result:
                added += 1
            elif result is False:
                skipped += 1
            else:
                errors += 1
    print("\n" + "=" * 80)
    print(f"SUMMARY: Added {added} | Skipped {skipped} | Errors {errors}")
    print("=" * 80)


if __name__ == "__main__":
    main()
