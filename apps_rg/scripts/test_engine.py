"""
Phase 2 Configuration & Base Integration Test Runner.

Runs the Phase 2 tests directly, bypassing pytest configuration issues.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all Phase 2 configuration and integration tests."""
    print("=" * 70)
    print("PHASE 2 CONFIGURATION & BASE INTEGRATION TESTS")
    print("=" * 70)

    from apps_rg.engines.base_resume_engine import BaseRGEngine
    from apps_rg.engines.sovereign_context import SovereignContext

    from apps_rg.config.AgentSpec import AgentSpec, OrchestrationTopology
    from apps_rg.config.sovereign_config_loader_config import SovereignConfigLoader

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
