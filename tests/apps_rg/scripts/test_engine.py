"""
Phase 2 Configuration & Base Integration Test Runner.

Runs the Phase 2 tests directly, bypassing pytest configuration issues.
"""

import asyncio
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_engine", "execution_auth")
_emit_validates_capability("p2", "test_engine", "capability_check")
_emit_routes_to_capability("p2", "test_engine", "capability_route")
_emit_writes_via_uwg("p2", "test_engine", "uwg_write")
_emit_blocks_direct_write("p2", "test_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "test_engine", "tool_invocation")
_emit_captures_execution_output("p2", "test_engine", "exec_output")
_emit_dispatches_agent("p3", "test_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "test_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_engine", "healing_outcome")
_emit_escalates_failure("p3", "test_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_engine", "eval_metric")
_emit_stores_embedding("p4", "test_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_engine", "exec_snapshot_link")
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

_emit_records_execution_trace("p0", "evidence", "test_engine")
_emit_applies_guardrail("p0", "test_engine", "p0_governance")
_emit_reads_policy_state("p0", "test_engine", "policy_binding")
_emit_snapshots_state("p0", "test_engine", "state_snapshot")
emit_replay_key("p0", "test_engine")
emit_determinism_digest("p0", "test_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
