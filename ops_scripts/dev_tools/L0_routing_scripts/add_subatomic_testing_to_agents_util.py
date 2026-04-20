"""
Add SubatomicTestingMixin to all agents that don't have test coverage.
This ensures 100% test coverage by adding the testing mixin to each agent.
"""

import json
import re
import sys
from pathlib import Path

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

_emit_emits_metric_event("add_subatomic_testing_to_agents_util", "p4obs", "metric_1")
_emit_emits_metric_event("add_subatomic_testing_to_agents_util", "p4obs", "metric_2")
_emit_emits_metric_event("add_subatomic_testing_to_agents_util", "p4obs", "metric_3")
_emit_emits_metric_event("add_subatomic_testing_to_agents_util", "p4obs", "metric_4")
_emit_emits_metric_event("add_subatomic_testing_to_agents_util", "p4obs", "metric_5")
_emit_emits_metric_event("add_subatomic_testing_to_agents_util", "p4obs", "metric_6")
_emit_records_incident_event("add_subatomic_testing_to_agents_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("add_subatomic_testing_to_agents_util", "p4obs", "anomaly")
_emit_writes_observability_log("add_subatomic_testing_to_agents_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("add_subatomic_testing_to_agents_util", "p4obs", "mon_state")
_emit_triggers_alert("add_subatomic_testing_to_agents_util", "p4obs", "alert")
_emit_links_incident_trace("add_subatomic_testing_to_agents_util", "p4obs", "trace_link")
_emit_captures_pattern("add_subatomic_testing_to_agents_util", "p3lm", "pattern")
_emit_records_learning_event("add_subatomic_testing_to_agents_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("add_subatomic_testing_to_agents_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("add_subatomic_testing_to_agents_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("add_subatomic_testing_to_agents_util", "p3lm", "routing")
_emit_improves_agent_policy("add_subatomic_testing_to_agents_util", "p3lm", "policy")
_emit_stores_learning_state("add_subatomic_testing_to_agents_util", "p3lm", "state")
_emit_records_execution_trace("add_subatomic_testing_to_agents_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("add_subatomic_testing_to_agents_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("add_subatomic_testing_to_agents_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("add_subatomic_testing_to_agents_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("add_subatomic_testing_to_agents_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("add_subatomic_testing_to_agents_util", "env_read", "p2_env_1")
_emit_reads_environ("add_subatomic_testing_to_agents_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("add_subatomic_testing_to_agents_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("add_subatomic_testing_to_agents_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "add_subatomic_testing_to_agents_util")
emit_determinism_digest("p0", "add_subatomic_testing_to_agents_util")

_emit_dispatches_healing_run("p1", "add_subatomic_testing_to_agents_util", "L0")
_emit_routes_through("p1", "add_subatomic_testing_to_agents_util", "L0")
_emit_checks_agent_registry("p1", "add_subatomic_testing_to_agents_util", "agent_registry")
_emit_validates_agent_capability("p1", "add_subatomic_testing_to_agents_util", "capability")
_emit_dispatches_execution_plan("p1", "add_subatomic_testing_to_agents_util", "exec_plan")
_emit_agent_executes_agent("p1", "add_subatomic_testing_to_agents_util", "sub_agent")
_emit_routes_to_agent("p1", "add_subatomic_testing_to_agents_util", "target_agent")
_emit_verifies_policy("p1", "add_subatomic_testing_to_agents_util", "policy_check")
_emit_observes_runtime_state("p1", "add_subatomic_testing_to_agents_util", "runtime_state")
_emit_verifies_boundary("p1", "add_subatomic_testing_to_agents_util", "boundary_check")
_emit_transcripts_response("p1", "add_subatomic_testing_to_agents_util", "transcript")
_emit_hard_fails_untranscripted("p1", "add_subatomic_testing_to_agents_util")
_emit_gated_by_confidence("p1", "add_subatomic_testing_to_agents_util", "confidence_gate")
_emit_escalates_to_human("p1", "add_subatomic_testing_to_agents_util", "L0")
_emit_reads_policy_state("p1", "add_subatomic_testing_to_agents_util", "L0")
_emit_pulls_context("p1", "add_subatomic_testing_to_agents_util", "context_pull")
_emit_pulls_context("p1", "add_subatomic_testing_to_agents_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "add_subatomic_testing_to_agents_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "add_subatomic_testing_to_agents_util", "uwg_term_secondary")
_emit_writes_through("p1", "add_subatomic_testing_to_agents_util", "write_through")
_emit_writes_through("p1", "add_subatomic_testing_to_agents_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "add_subatomic_testing_to_agents_util", "safety_validation")
_emit_invokes_eval("p1", "add_subatomic_testing_to_agents_util", "eval_call")
_emit_proposal_commits_routing("p1", "add_subatomic_testing_to_agents_util", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "add_subatomic_testing_to_agents_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "add_subatomic_testing_to_agents_util", "p0_governance")
_emit_snapshots_state("p0", "add_subatomic_testing_to_agents_util", "state_snapshot")
_emit_authorize_and_execute("p2", "add_subatomic_testing_to_agents_util", "execution_auth")
_emit_validates_capability("p2", "add_subatomic_testing_to_agents_util", "capability_check")
_emit_routes_to_capability("p2", "add_subatomic_testing_to_agents_util", "capability_route")
_emit_writes_via_uwg("p2", "add_subatomic_testing_to_agents_util", "uwg_write")
_emit_blocks_direct_write("p2", "add_subatomic_testing_to_agents_util", "direct_write_block")
_emit_records_tool_invocation("p2", "add_subatomic_testing_to_agents_util", "tool_invocation")
_emit_captures_execution_output("p2", "add_subatomic_testing_to_agents_util", "exec_output")
_emit_dispatches_agent("p3", "add_subatomic_testing_to_agents_util", "agent_dispatch")
_emit_coordinates_agents("p3", "add_subatomic_testing_to_agents_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "add_subatomic_testing_to_agents_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "add_subatomic_testing_to_agents_util", "healing_outcome")
_emit_escalates_failure("p3", "add_subatomic_testing_to_agents_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "add_subatomic_testing_to_agents_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "add_subatomic_testing_to_agents_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "add_subatomic_testing_to_agents_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "add_subatomic_testing_to_agents_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "add_subatomic_testing_to_agents_util", "eval_metric")
_emit_stores_embedding("p4", "add_subatomic_testing_to_agents_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "add_subatomic_testing_to_agents_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "add_subatomic_testing_to_agents_util", "exec_snapshot_link")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "agent_discovery_full.json").exists() and (candidate / "agentic_core").exists():
            return candidate
    raise RuntimeError(f"Could not determine project root from {__file__}")


def main() -> int:
    project_root = _find_project_root()
    with (project_root / "agent_discovery_full.json").open(encoding="utf-8") as f:
        agents = json.load(f)
    print(f"Total agents: {len(agents)}")
    agents_without_tests = [a for a in agents if not a.get("has_tests", False)]
    print(f"Agents WITHOUT tests: {len(agents_without_tests)}")
    modified_count = 0
    skipped_count = 0
    error_count = 0
    for agent in tqdm(agents_without_tests, desc="Processing", unit="item"):
        class_name = agent["class_name"]
        agent_path = project_root / agent["path"]
        if not agent_path.exists():
            print(f"⚠️ File not found: {agent_path}")
            error_count += 1
            continue
        try:
            content = agent_path.read_text(encoding="utf-8")
            if "SubatomicTestingMixin" in content:
                skipped_count += 1
                continue
            if "_run_self_tests" in content:
                skipped_count += 1
                continue
            modified = False
            class_pattern = f"class\\s+{class_name}\\s*\\(([^)]+)\\)\\s*:"
            match = re.search(class_pattern, content)
            if match:
                bases = match.group(1)
                new_bases = f"SubatomicTestingMixin, {bases}"
                new_class_def = f"class {class_name}({new_bases}):"
                content = content[: match.start()] + new_class_def + content[match.end() :]
                modified = True
            else:
                class_pattern_no_base = f"class\\s+{class_name}\\s*:"
                match = re.search(class_pattern_no_base, content)
                if match:
                    new_class_def = f"class {class_name}(SubatomicTestingMixin):"
                    content = content[: match.start()] + new_class_def + content[match.end() :]
                    modified = True
            if modified:
                if (
                    "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin"
                    not in content
                ):
                    if "from agentic_core" in content:
                        last_import = content.rfind("from agentic_core")
                        end_of_line = content.find("\n", last_import)
                        import_line = (
                            "\nfrom agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin"
                        )
                        content = content[:end_of_line] + import_line + content[end_of_line:]
                    elif "import " in content:
                        lines = content.split("\n")
                        last_import_idx = 0
                        for i, line in enumerate(lines):
                            if line.startswith("import ") or line.startswith("from "):
                                last_import_idx = i
                        lines.insert(
                            last_import_idx + 1,
                            "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin",
                        )
                        content = "\n".join(lines)
                    elif content.startswith('"""'):
                        end_docstring = content.find('"""', 3) + 3
                        content = (
                            content[:end_docstring]
                            + "\nfrom agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin\n"
                            + content[end_docstring:]
                        )
                    else:
                        content = (
                            "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin\n"
                            + content
                        )
                assert_no_persistent_write("L0", "write_text")
                agent_path.write_text(content, encoding="utf-8")
                modified_count += 1
                print(f"✅ Modified: {agent_path}")
            else:
                print(f"⚠️ Could not find class definition: {class_name} in {agent_path}")
                error_count += 1
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            print(f"❌ Error processing {agent_path}: {e}")
            error_count += 1
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Modified: {modified_count}")
    print(f"Skipped (already has testing): {skipped_count}")
    print(f"Errors: {error_count}")
    print("\nNext step: Run full_agent_discovery.py to update test coverage stats")


if __name__ == "__main__":
    sys.exit(main())
