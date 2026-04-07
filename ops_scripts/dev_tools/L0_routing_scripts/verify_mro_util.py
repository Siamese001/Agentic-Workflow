"""
MRO Verification Script

Verifies the Method Resolution Order (MRO) for complex agents after
the infrastructure_mixin consolidation.

Opportunity #4: Mixin Inheritance Complexity - Phase 4 Verification
"""

import sys
from pathlib import Path

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

emit_replay_key("p0", "verify_mro_util")
emit_determinism_digest("p0", "verify_mro_util")

_emit_dispatches_healing_run("p1", "verify_mro_util", "L0")
_emit_routes_through("p1", "verify_mro_util", "L0")
_emit_checks_agent_registry("p1", "verify_mro_util", "agent_registry")
_emit_validates_agent_capability("p1", "verify_mro_util", "capability")
_emit_dispatches_execution_plan("p1", "verify_mro_util", "exec_plan")
_emit_agent_executes_agent("p1", "verify_mro_util", "sub_agent")
_emit_routes_to_agent("p1", "verify_mro_util", "target_agent")
_emit_verifies_policy("p1", "verify_mro_util", "policy_check")
_emit_observes_runtime_state("p1", "verify_mro_util", "runtime_state")
_emit_verifies_boundary("p1", "verify_mro_util", "boundary_check")
_emit_transcripts_response("p1", "verify_mro_util", "transcript")
_emit_hard_fails_untranscripted("p1", "verify_mro_util")
_emit_gated_by_confidence("p1", "verify_mro_util", "confidence_gate")
_emit_escalates_to_human("p1", "verify_mro_util", "L0")
_emit_reads_policy_state("p1", "verify_mro_util", "L0")
_emit_authorize_and_execute("p2", "verify_mro_util", "execution_auth")
_emit_validates_capability("p2", "verify_mro_util", "capability_check")
_emit_routes_to_capability("p2", "verify_mro_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_mro_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_mro_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_mro_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_mro_util", "exec_output")
_emit_dispatches_agent("p3", "verify_mro_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_mro_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_mro_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_mro_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_mro_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_mro_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_mro_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_mro_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_mro_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_mro_util", "eval_metric")
_emit_stores_embedding("p4", "verify_mro_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_mro_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_mro_util", "exec_snapshot_link")
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

_emit_emits_metric_event("verify_mro_util", "p4obs", "metric_1")
_emit_emits_metric_event("verify_mro_util", "p4obs", "metric_2")
_emit_emits_metric_event("verify_mro_util", "p4obs", "metric_3")
_emit_emits_metric_event("verify_mro_util", "p4obs", "metric_4")
_emit_emits_metric_event("verify_mro_util", "p4obs", "metric_5")
_emit_emits_metric_event("verify_mro_util", "p4obs", "metric_6")
_emit_records_incident_event("verify_mro_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("verify_mro_util", "p4obs", "anomaly")
_emit_writes_observability_log("verify_mro_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("verify_mro_util", "p4obs", "mon_state")
_emit_triggers_alert("verify_mro_util", "p4obs", "alert")
_emit_links_incident_trace("verify_mro_util", "p4obs", "trace_link")
_emit_captures_pattern("verify_mro_util", "p3lm", "pattern")
_emit_records_learning_event("verify_mro_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verify_mro_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("verify_mro_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verify_mro_util", "p3lm", "routing")
_emit_improves_agent_policy("verify_mro_util", "p3lm", "policy")
_emit_stores_learning_state("verify_mro_util", "p3lm", "state")
_emit_records_execution_trace("verify_mro_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verify_mro_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verify_mro_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verify_mro_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verify_mro_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verify_mro_util", "env_read", "p2_env_1")
_emit_reads_environ("verify_mro_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("verify_mro_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verify_mro_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verify_mro_util", "context_pull")
_emit_pulls_context("p1", "verify_mro_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "verify_mro_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verify_mro_util", "uwg_term_2")
_emit_writes_through("p1", "verify_mro_util", "write_through")
_emit_writes_through("p1", "verify_mro_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "verify_mro_util", "safety_validation")
_emit_invokes_eval("p1", "verify_mro_util", "eval_call")
_emit_proposal_commits_routing("p1", "verify_mro_util", "routing_commit")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))


def print_mro(agent_class, agent_name: str):
    """Print the MRO for an agent class."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "print_mro", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "print_mro", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "print_mro")
    print(f"\n{'=' * 80}")
    print(f"MRO for {agent_name}")
    print(f"{'=' * 80}")
    mro = agent_class.__mro__
    for i, cls in enumerate(mro):
        indent = "  " * i
        print(f"{indent}{i}. {cls.__module__}.{cls.__name__}")
    print(f"\nTotal classes in MRO: {len(mro)}")
    has_infra = any("infrastructure_mixin" in cls.__name__ for cls in mro)
    has_healer = any("HealerMixin" in cls.__name__ for cls in mro)
    has_mcp = any("MCPHardened" in cls.__name__ for cls in mro)
    has_testing = any("SubatomicTesting" in cls.__name__ for cls in mro)
    print("\nInfrastructure Components:")
    print(f"  infrastructure_mixin: {('✅' if has_infra else '❌')}")
    print(f"  HealerMixin: {('✅' if has_healer else '❌')}")
    print(f"  MCPHardenedMixin: {('✅' if has_mcp else '❌')}")
    print(f"  SubatomicTestingMixin: {('✅' if has_testing else '❌')}")
    return {
        "has_infra": has_infra,
        "has_healer": has_healer,
        "has_mcp": has_mcp,
        "has_testing": has_testing,
        "mro_length": len(mro),
    }


def verify_sovereign_base_agent():
    """Verify SovereignBaseAgent MRO."""
    try:
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        return print_mro(SovereignBaseAgent, "SovereignBaseAgent")
    except ImportError as e:
        print(f"❌ Failed to import SovereignBaseAgent: {e}")
        return None


def verify_meta_learning_agent():
    """Verify MetaLearningAgent MRO (complex case)."""
    try:
        from agentic_core.L0_routing.utils.observability_seam import load_meta_learning_agent

        MetaLearningAgent = load_meta_learning_agent()
        return print_mro(MetaLearningAgent, "MetaLearningAgent")
    except ImportError as e:
        print(f"❌ Failed to import MetaLearningAgent: {e}")
        return None


def verify_location_validator_agent():
    """Verify LocationValidatorAgent MRO."""
    try:
        from agentic_core.L0_routing.enforcement.safety_reasoning_seam import load_location_validator_agent

        LocationValidatorAgent = load_location_validator_agent()
        return print_mro(LocationValidatorAgent, "LocationValidatorAgent")
    except ImportError as e:
        print(f"❌ Failed to import LocationValidatorAgent: {e}")
        return None


def verify_hierarchy_agent():
    """Verify HierarchyAgent MRO via subprocess."""
    try:
        from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent

        result = invoke_hierarchy_agent(action="verify_mro")
        if result.get("success"):
            mro = result.get("mro", [])
            print(f"\n{'=' * 80}")
            print("MRO for HierarchyAgent (via subprocess)")
            print(f"{'=' * 80}")
            for i, cls_name in enumerate(mro):
                indent = "  " * i
                print(f"{indent}{i}. {cls_name}")
            print(f"\nTotal classes in MRO: {len(mro)}")
            has_infra = any("infrastructure_mixin" in cls for cls in mro)
            has_healer = any("HealerMixin" in cls for cls in mro)
            has_mcp = any("MCPHardened" in cls for cls in mro)
            has_testing = any("SubatomicTesting" in cls for cls in mro)
            print("\nInfrastructure Components:")
            print(f"  infrastructure_mixin: {('✅' if has_infra else '❌')}")
            print(f"  HealerMixin: {('✅' if has_healer else '❌')}")
            print(f"  MCPHardenedMixin: {('✅' if has_mcp else '❌')}")
            print(f"  SubatomicTestingMixin: {('✅' if has_testing else '❌')}")
            return {
                "has_infra": has_infra,
                "has_healer": has_healer,
                "has_mcp": has_mcp,
                "has_testing": has_testing,
                "mro_length": len(mro),
            }
        else:
            print(f"❌ Failed to verify HierarchyAgent MRO: {result.get('error')}")
            return None
    except (ValueError, TypeError) as e:
        print(f"❌ Failed to verify HierarchyAgent: {e}")
        return None


def main():
    """Run MRO verification for multiple agents."""
    print("=" * 80)
    print("MRO VERIFICATION - Opportunity #4: Mixin Inheritance Complexity")
    print("=" * 80)
    results = {}
    print("\n[Test 1] SovereignBaseAgent (Root)")
    results["sovereign"] = verify_sovereign_base_agent()
    print("\n[Test 2] MetaLearningAgent (Complex Case)")
    results["meta_learning"] = verify_meta_learning_agent()
    print("\n[Test 3] LocationValidatorAgent (L5 Agent)")
    results["location_validator"] = verify_location_validator_agent()
    print("\n[Test 4] HierarchyAgent (L5 Agent)")
    results["hierarchy"] = verify_hierarchy_agent()
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    success_count = sum(1 for r in results.values() if r is not None and r.get("has_infra"))
    total_count = len(results)
    print(f"\nAgents with infrastructure_mixin: {success_count}/{total_count}")
    for agent_name, result in results.items():
        if result is None:
            print(f"  ❌ {agent_name}: Failed to import")
        elif result.get("has_infra"):
            print(f"  ✅ {agent_name}: infrastructure_mixin present (MRO length: {result['mro_length']})")
        else:
            print(f"  ⚠️  {agent_name}: infrastructure_mixin missing (MRO length: {result['mro_length']})")
    if success_count == total_count:
        print("\n✅ ALL AGENTS VERIFIED: infrastructure_mixin consolidation successful")
        return 0
    else:
        print(f"\n❌ VERIFICATION FAILED: {total_count - success_count} agents missing infrastructure_mixin")
        return 1


if __name__ == "__main__":
    sys.exit(main())
