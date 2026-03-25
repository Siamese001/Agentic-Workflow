"""
Phase 2 Configuration & Base Integration Test Runner.

Runs the Phase 2 tests directly, bypassing pytest configuration issues.
"""

import asyncio
import sys
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_authorize_and_execute("p2", "test_engine", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_engine", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_engine", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_engine", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_engine", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_engine", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_engine", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_engine", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_engine", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_engine", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_engine", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_engine", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_engine", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_engine", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_engine", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_engine", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_engine", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_engine", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_engine", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_engine", "exec_snapshot_link")
from apps_shared.config.pipeline_constants_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_engine")
# REMOVED: _emit_applies_guardrail("p0", "test_engine", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_engine", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_engine", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,  # noqa: E402
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_engine", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_engine", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_engine", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_engine", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_engine", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_engine", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_engine", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_engine", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_engine", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_engine", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_engine", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_engine", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_engine", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_engine", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_engine", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_engine", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_engine", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_engine", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_engine", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_engine", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_engine", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_engine", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_engine", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_engine", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_engine", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_engine", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_engine", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_engine", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_engine", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_engine", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_engine", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_engine", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_engine", "write_through")
# REMOVED: _emit_writes_through("p1", "test_engine", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_engine", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_engine", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_engine", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_engine", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_engine", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_engine", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_engine", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_engine", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_engine", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_engine", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_engine", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_engine", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_engine", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_engine", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_engine")
# REMOVED: _emit_gated_by_confidence("p1", "test_engine", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_engine")
# REMOVED: emit_determinism_digest("p0", "test_engine")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all Phase 2 configuration and integration tests."""
    print("=" * 70)
    print("PHASE 2 CONFIGURATION & BASE INTEGRATION TESTS")
    print("=" * 70)

    from apps_rg.config.AgentSpec import AgentSpec, OrchestrationTopology
    from apps_rg.config.sovereign_config_loader_config import SovereignConfigLoader
    from apps_rg.engines.base_resume_engine import BaseRGEngine

    from apps_rg.engines.sovereign_context import SovereignContext

    passed = 0
    failed = 0

    # Test 1: Schema Validation Success
    print("\n[TEST 1] test_schema_validation_success")
    try:
        data = {
            "phases": {"PHASE1": ["AGENT_A"]},
            "agents": {
                "AGENT_A": {
                    "name": "AGENT_A",
                    "module_path": "path.to.module",
                    "inputs": [],
                    "outputs": [],
                },
            },
        }
        topology = OrchestrationTopology(**data)
        assert topology.phases["PHASE1"] == ["AGENT_A"]
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 2: Schema Validation Missing Agent
    print("\n[TEST 2] test_schema_validation_missing_agent")
    try:
        data = {"phases": {"PHASE1": ["GHOST_AGENT"]}, "agents": {}}
        try:
            OrchestrationTopology(**data)
            print("  ❌ FAILED: Expected ValueError")
            failed += 1
        except ValueError:
            print("  ✅ PASSED")
            passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 3: Agent Spec Defaults
    print("\n[TEST 3] test_agent_spec_defaults")
    try:
        spec = AgentSpec(name="TEST", module_path="test.path")
        assert spec.timeout_sec == 30
        assert spec.criticality == "required"
        assert spec.inputs == []
        assert spec.outputs == []
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 4: Context Integration
    print("\n[TEST 4] test_context_integration")
    try:
        ctx = SovereignContext()
        assert ctx.buffer is not None
        assert ctx.trace is not None
        ctx.add_signal("TEST_SIGNAL")
        assert "TEST_SIGNAL" in ctx.signals
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 5: Context Record Result
    print("\n[TEST 5] test_context_record_result")
    try:
        ctx = SovereignContext()
        ctx.record_result("TestAgent", True, "Test passed", {"data": 123})
        traces = ctx.trace.get_traces()
        assert len(traces) >= 1
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 6: Context Mission ID
    print("\n[TEST 6] test_context_mission_id")
    try:
        ctx = SovereignContext(mission_id="MISSION_001")
        assert ctx.mission_id == "MISSION_001"
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 7: Sovereign Loader Default Scaffold
    print("\n[TEST 7] test_sovereign_loader_default_scaffold")
    try:
        SovereignConfigLoader.reset()
        topology = SovereignConfigLoader._get_default_scaffold()
        assert "HOP1" in topology.phases
        assert "HOP1_CLERK" in topology.agents
        assert topology.agents["HOP1_CLERK"].module_path.startswith("apps_rg")
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 8: Base Engine Telemetry Wrapper (async)
    print("\n[TEST 8] test_base_engine_telemetry_wrapper")
    try:

        async def run_test():
            ctx = SovereignContext()

            class TestEngine(BaseRGEngine):
                async def execute(self):
                    return "DONE"

            engine = TestEngine(ctx)
            result = await engine.run()

            assert result == "DONE"
            summary = ctx.trace.get_summary()
            assert summary["total_spans"] == 1
            assert summary["completed"] == 1

        asyncio.run(run_test())
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 9: Base Engine Failure Tracking (async)
    print("\n[TEST 9] test_base_engine_failure_tracking")
    try:

        async def run_test():
            ctx = SovereignContext()

            class FailingEngine(BaseRGEngine):
                async def execute(self):
                    raise ValueError("Intentional failure")

            engine = FailingEngine(ctx)

            try:
                await engine.run()
                return False  # Should have raised
            except ValueError:
                pass

            summary = ctx.trace.get_summary()
            assert summary["failures"] == 1
            return True

        result = asyncio.run(run_test())
        if result:
            print("  ✅ PASSED")
            passed += 1
        else:
            print("  ❌ FAILED: Expected ValueError")
            failed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Test 10: Topology Version
    print("\n[TEST 10] test_topology_version")
    try:
        data = {"phases": {"P1": ["A1"]}, "agents": {"A1": {"name": "A1", "module_path": "test"}}}
        topology = OrchestrationTopology(**data)
        assert topology.version == "2.5.0"
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1

    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - Phase 2 Configuration & Base Integration is HARDENED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED - Fix before proceeding to Phase 3")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
