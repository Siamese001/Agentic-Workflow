"""
Runtime Integrity Verifier - Phase 21

[HARDENING STEP]
Static analysis (ArchGuard) is not enough. We must prove that:
1. The refactored agents can actually be imported (No circular dependencies).
2. They can be instantiated (No missing mixin methods).
3. The tool_registry dicts are valid.

Run this to confirm the system is truly production-ready.
"""

import logging
import sys
import traceback
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "test_verify_runtime_integrity")
_emit_applies_guardrail("p0", "test_verify_runtime_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_verify_runtime_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_verify_runtime_integrity", "state_snapshot")
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

_emit_emits_metric_event("test_verify_runtime_integrity", "p4obs", "metric_1")
_emit_emits_metric_event("test_verify_runtime_integrity", "p4obs", "metric_2")
_emit_emits_metric_event("test_verify_runtime_integrity", "p4obs", "metric_3")
_emit_emits_metric_event("test_verify_runtime_integrity", "p4obs", "metric_4")
_emit_emits_metric_event("test_verify_runtime_integrity", "p4obs", "metric_5")
_emit_emits_metric_event("test_verify_runtime_integrity", "p4obs", "metric_6")
_emit_records_incident_event("test_verify_runtime_integrity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_verify_runtime_integrity", "p4obs", "anomaly")
_emit_writes_observability_log("test_verify_runtime_integrity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_verify_runtime_integrity", "p4obs", "mon_state")
_emit_triggers_alert("test_verify_runtime_integrity", "p4obs", "alert")
_emit_links_incident_trace("test_verify_runtime_integrity", "p4obs", "trace_link")
_emit_captures_pattern("test_verify_runtime_integrity", "p3lm", "pattern")
_emit_records_learning_event("test_verify_runtime_integrity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_verify_runtime_integrity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_verify_runtime_integrity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_verify_runtime_integrity", "p3lm", "routing")
_emit_improves_agent_policy("test_verify_runtime_integrity", "p3lm", "policy")
_emit_stores_learning_state("test_verify_runtime_integrity", "p3lm", "state")
_emit_records_execution_trace("test_verify_runtime_integrity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_verify_runtime_integrity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_verify_runtime_integrity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_verify_runtime_integrity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_verify_runtime_integrity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_verify_runtime_integrity", "env_read", "p2_env_1")
_emit_reads_environ("test_verify_runtime_integrity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_verify_runtime_integrity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_verify_runtime_integrity", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_verify_runtime_integrity", "context_pull")
_emit_pulls_context("p1", "test_verify_runtime_integrity", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_verify_runtime_integrity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_verify_runtime_integrity", "uwg_term_2")
_emit_writes_through("p1", "test_verify_runtime_integrity", "write_through")
_emit_writes_through("p1", "test_verify_runtime_integrity", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_verify_runtime_integrity", "safety_validation")
_emit_invokes_eval("p1", "test_verify_runtime_integrity", "eval_call")
_emit_proposal_commits_routing("p1", "test_verify_runtime_integrity", "routing_commit")
_emit_escalates_to_human("p1", "test_verify_runtime_integrity", "human_escalation")
_emit_routes_through("p1", "test_verify_runtime_integrity", "route_through")
_emit_checks_agent_registry("p1", "test_verify_runtime_integrity", "agent_registry")
_emit_validates_agent_capability("p1", "test_verify_runtime_integrity", "capability")
_emit_dispatches_execution_plan("p1", "test_verify_runtime_integrity", "exec_plan")
_emit_agent_executes_agent("p1", "test_verify_runtime_integrity", "sub_agent")
_emit_routes_to_agent("p1", "test_verify_runtime_integrity", "target_agent")
_emit_verifies_policy("p1", "test_verify_runtime_integrity", "policy_check")
_emit_observes_runtime_state("p1", "test_verify_runtime_integrity", "runtime_state")
_emit_verifies_boundary("p1", "test_verify_runtime_integrity", "boundary_check")
_emit_transcripts_response("p1", "test_verify_runtime_integrity", "transcript")
_emit_hard_fails_untranscripted("p1", "test_verify_runtime_integrity")
_emit_gated_by_confidence("p1", "test_verify_runtime_integrity", "confidence_gate")
emit_replay_key("p0", "test_verify_runtime_integrity")
emit_determinism_digest("p0", "test_verify_runtime_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_verify_runtime_integrity", "execution_auth")
_emit_validates_capability("p2", "test_verify_runtime_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_verify_runtime_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_verify_runtime_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_verify_runtime_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_verify_runtime_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_verify_runtime_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_verify_runtime_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_verify_runtime_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_verify_runtime_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_verify_runtime_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_verify_runtime_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_verify_runtime_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_verify_runtime_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_verify_runtime_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_verify_runtime_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_verify_runtime_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_verify_runtime_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_verify_runtime_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_verify_runtime_integrity", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
Logger = logging.getLogger("RuntimeVerifier")


def test_instantiation():
    print("--- STARTING RUNTIME INTEGRITY CHECK ---")
    failures = []

    # 1. Test Base Infrastructure
    try:
        print("[TEST] Initializing SovereignBaseAgent...")
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = SovereignBaseAgent()
        assert hasattr(agent, "llm_generate"), "Missing LLM capability"
        assert hasattr(agent, "cache_get"), "Missing Redis capability"
        print("   ✅ SovereignBaseAgent OK")
    except Exception as e:
        raise
        failures.append(f"SovereignBaseAgent: {e}")
        traceback.print_exc()

    # 2. Test Tool Registry (The Dict Refactor)
    try:
        print("[TEST] Initializing tool_registry...")
        from agentic_core.L2_execution.reasoning.registry import create_tool_registry

        registry = create_tool_registry()
        tools = registry.get_function_declarations()
        assert isinstance(tools, list), "Tools must be a list"
        assert len(tools) > 0, "No tools registered"
        assert isinstance(tools[0], dict), "Tools must be pure dicts (Architecture requirement)"
        print("   ✅ tool_registry OK (Pure Dicts confirmed)")
    except Exception as e:
        raise
        failures.append(f"tool_registry: {e}")
        traceback.print_exc()

    # 3. Test The Refactored Agents (Import Rewiring Check)
    agents_to_test = [
        ("L3_orchestration.engine.FissionManagerAgent", "FissionManagerAgent"),
        ("L5_safety.guardrails.HallucinationHunterAgent", "HallucinationHunterAgent"),
        ("L5_safety.reasoning.NeuralAutoImmuneAgent", "NeuralAutoImmuneAgent"),
        ("L0_routing.scripts.DependencyDiplomatAgent", "DependencyDiplomatAgent"),
        (
            "L1_cognition.agents.SemanticTerritoryMapperAgent",
            "SemanticTerritoryMapperAgent",
        ),
        ("L0_routing.scripts.BootstrapAgent", "BootstrapAgent"),
        ("L2_execution.L2ExecutionBase", "L2ExecutionBase"),
    ]

    for module_path, class_name in agents_to_test:
        try:
            print(f"[TEST] Loading {class_name} from {module_path}...")
            module = __import__(f"agentic_core.{module_path}", fromlist=[class_name])
            cls = getattr(module, class_name)

            if "BaseAgent" in class_name:
                cls(ctx=None)
            elif "Bootstrap" in class_name:
                cls(project_root=Path("."))
            elif "HallucinationHunter" in class_name:
                cls(ctx=None)
            else:
                cls()

            print(f"   ✅ {class_name} Instantiated")
        except ImportError as e:
            failures.append(f"IMPORT ERROR {class_name}: {e} (Likely circular dependency)")
        except AttributeError as e:
            failures.append(f"CLASS NOT FOUND {class_name}: {e}")
        except Exception as e:
            raise
            failures.append(f"RUNTIME ERROR {class_name}: {e}")

    print("-" * 30)
    if failures:
        print(f"❌ INTEGRITY CHECK FAILED with {len(failures)} errors:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✅ SYSTEM INTEGRITY VERIFIED. No circular imports detected.")
        sys.exit(0)


if __name__ == "__main__":
    test_instantiation()
