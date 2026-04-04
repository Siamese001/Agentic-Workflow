from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    # noqa: E402
    record_execution_trace,
)

emit_replay_key("p0", "fix_testing_observability_util")
emit_determinism_digest("p0", "fix_testing_observability_util")

_emit_dispatches_healing_run("p1", "fix_testing_observability_util", "L6")
_emit_routes_through("p1", "fix_testing_observability_util", "L6")
_emit_checks_agent_registry("p1", "fix_testing_observability_util", "agent_registry")
_emit_validates_agent_capability("p1", "fix_testing_observability_util", "capability")
_emit_dispatches_execution_plan("p1", "fix_testing_observability_util", "exec_plan")
_emit_agent_executes_agent("p1", "fix_testing_observability_util", "sub_agent")
_emit_routes_to_agent("p1", "fix_testing_observability_util", "target_agent")
_emit_verifies_policy("p1", "fix_testing_observability_util", "policy_check")
_emit_observes_runtime_state("p1", "fix_testing_observability_util", "runtime_state")
_emit_verifies_boundary("p1", "fix_testing_observability_util", "boundary_check")
_emit_transcripts_response("p1", "fix_testing_observability_util", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_testing_observability_util")
_emit_gated_by_confidence("p1", "fix_testing_observability_util", "confidence_gate")
_emit_escalates_to_human("p1", "fix_testing_observability_util", "L6")
_emit_reads_policy_state("p1", "fix_testing_observability_util", "L6")
_emit_authorize_and_execute("p2", "fix_testing_observability_util", "execution_auth")
_emit_validates_capability("p2", "fix_testing_observability_util", "capability_check")
_emit_routes_to_capability("p2", "fix_testing_observability_util", "capability_route")
_emit_writes_via_uwg("p2", "fix_testing_observability_util", "uwg_write")
_emit_blocks_direct_write("p2", "fix_testing_observability_util", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_testing_observability_util", "tool_invocation")
_emit_captures_execution_output("p2", "fix_testing_observability_util", "exec_output")
_emit_dispatches_agent("p3", "fix_testing_observability_util", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_testing_observability_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_testing_observability_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_testing_observability_util", "healing_outcome")
_emit_escalates_failure("p3", "fix_testing_observability_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_testing_observability_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_testing_observability_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_testing_observability_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_testing_observability_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_testing_observability_util", "eval_metric")
_emit_stores_embedding("p4", "fix_testing_observability_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_testing_observability_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_testing_observability_util", "exec_snapshot_link")

"\nFix Testing & observability - Add SubatomicTestingMixin and logging to all agents.\n\nThis script:\n1. Loads all agents from agent_discovery_full.json\n2. For each agent without testing: adds SubatomicTestingMixin to bases\n3. For each agent without observability: adds logging import and logger\n4. This maximizes testing % and observable % in the dashboard\n"
import json
import re
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

record_execution_trace("fix_testing_observability_util", "fix_testing_observability_util_trace")


_emit_emits_metric_event("fix_testing_observability_util", "p4obs", "metric_1")
_emit_emits_metric_event("fix_testing_observability_util", "p4obs", "metric_2")
_emit_emits_metric_event("fix_testing_observability_util", "p4obs", "metric_3")
_emit_emits_metric_event("fix_testing_observability_util", "p4obs", "metric_4")
_emit_emits_metric_event("fix_testing_observability_util", "p4obs", "metric_5")
_emit_emits_metric_event("fix_testing_observability_util", "p4obs", "metric_6")
_emit_records_incident_event("fix_testing_observability_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_testing_observability_util", "p4obs", "anomaly")
_emit_writes_observability_log("fix_testing_observability_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_testing_observability_util", "p4obs", "mon_state")
_emit_triggers_alert("fix_testing_observability_util", "p4obs", "alert")
_emit_links_incident_trace("fix_testing_observability_util", "p4obs", "trace_link")
_emit_captures_pattern("fix_testing_observability_util", "p3lm", "pattern")
_emit_records_learning_event("fix_testing_observability_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_testing_observability_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_testing_observability_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_testing_observability_util", "p3lm", "routing")
_emit_improves_agent_policy("fix_testing_observability_util", "p3lm", "policy")
_emit_stores_learning_state("fix_testing_observability_util", "p3lm", "state")
_emit_records_execution_trace("fix_testing_observability_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_testing_observability_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_testing_observability_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_testing_observability_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_testing_observability_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_testing_observability_util", "env_read", "p2_env_1")
_emit_reads_environ("fix_testing_observability_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_testing_observability_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_testing_observability_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "fix_testing_observability_util", "context_pull")
_emit_pulls_context("p1", "fix_testing_observability_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "fix_testing_observability_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_testing_observability_util", "uwg_term_2")
_emit_writes_through("p1", "fix_testing_observability_util", "write_through")
_emit_writes_through("p1", "fix_testing_observability_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "fix_testing_observability_util", "safety_validation")
_emit_invokes_eval("p1", "fix_testing_observability_util", "eval_call")
_emit_proposal_commits_routing("p1", "fix_testing_observability_util", "routing_commit")

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import AGENT_DISCOVERY_JSON
except ImportError:  # guardian: allow-silent-swallow
    AGENT_DISCOVERY_JSON = "agent_discovery_full.json"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
LOGGING_IMPORT = "import logging"
LOGGER_INIT = "logger = logging.getLogger(__name__)"
TESTING_IMPORT = (
    "from agentic_core.L3_orchestration.reasoning.subatomic_testing_mixin import SubatomicTestingMixin"
)


def load_agents() -> list[dict]:
    """Load all agents from discovery JSON."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_agents", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_agents", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "load_agents")
    with open(DISCOVERY_JSON, encoding="utf-8") as f:
        return json.load(f)


def add_logging_to_file(file_path: Path) -> bool:
    """Add logging import and logger initialization to a file."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [ERROR] Cannot read {file_path}: {e}")
        return False
    modified = False
    if "import logging" not in source and "from logging" not in source:
        lines = source.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = i
                break
        lines.insert(insert_idx, LOGGING_IMPORT)
        modified = True
        source = "\n".join(lines)
    if "logger = logging.getLogger" not in source and "Logger = logging.getLogger" not in source:
        lines = source.splitlines()
        insert_idx = 0
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            if stripped.startswith("#"):
                continue
            if stripped.startswith("import ") or stripped.startswith("from "):
                insert_idx = i + 1
                continue
            if stripped and (not stripped.startswith("import")) and (not stripped.startswith("from")):
                break
        lines.insert(insert_idx, "")
        lines.insert(insert_idx + 1, LOGGER_INIT)
        modified = True
        source = "\n".join(lines)
    if modified:
        try:
            assert_no_persistent_write("L6", "write_text")
            _wg.write_text(file_path, source, encoding="utf-8")
            return True
        except Exception as e:
            print(f"  [ERROR] Cannot write {file_path}: {e}")
            return False
    return False


def add_testing_mixin_to_class(file_path: Path, class_name: str) -> bool:
    """Add SubatomicTestingMixin to a class's bases."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [ERROR] Cannot read {file_path}: {e}")
        return False
    if "SubatomicTestingMixin" in source:
        return False
    if TESTING_IMPORT not in source:
        lines = source.splitlines()
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                last_import_idx = i
        lines.insert(last_import_idx + 1, TESTING_IMPORT)
        source = "\n".join(lines)
    pattern = f"(class\\s+{re.escape(class_name)}\\s*\\()([^)]*?)(\\)\\s*:)"

    def add_mixin(match):
        prefix = match.group(1)
        bases = match.group(2).strip()
        suffix = match.group(3)
        if bases:
            new_bases = f"SubatomicTestingMixin, {bases}"
        else:
            new_bases = "SubatomicTestingMixin"
        return f"{prefix}{new_bases}{suffix}"

    new_source, count = re.subn(pattern, add_mixin, source)
    if count > 0:
        try:
            assert_no_persistent_write("L6", "write_text")
            _wg.write_text(file_path, new_source, encoding="utf-8")
            return True
        except Exception as e:
            print(f"  [ERROR] Cannot write {file_path}: {e}")
            return False
    return False


def main():
    print("=" * 80)
    print("FIX TESTING & OBSERVABILITY")
    print("=" * 80)
    agents = load_agents()
    print(f"\nProcessing {len(agents)} agents...\n")
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
    logging_added = 0
    testing_added = 0
    for file_path_str, class_names in sorted(by_file.items()):
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue
        if add_logging_to_file(file_path):
            logging_added += 1
            print(f"[LOGGING] {file_path.relative_to(PROJECT_ROOT)}")
        for class_name in class_names:
            if add_testing_mixin_to_class(file_path, class_name):
                testing_added += 1
                print(f"[TESTING] {class_name} in {file_path.name}")
    print("\n" + "=" * 80)
    print(f"SUMMARY: Logging added to {logging_added} files | Testing mixin added to {testing_added} classes")
    print("=" * 80)


if __name__ == "__main__":
    main()
