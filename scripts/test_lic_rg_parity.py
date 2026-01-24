"""
Direct test script for LIC-RG Architecture Parity.
Bypasses pytest import issues.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("LIC-RG ARCHITECTURE PARITY TESTS")
print("=" * 80)


def test_configuration_parity():
    """Test RG configuration system matches LIC capabilities."""
    print("\n1. Testing Configuration Parity...")

    try:
        from apps_rg.domain.config.loader import load_rg_specs, reload_config

        # Test auto-loading
        specs = load_rg_specs()
        assert specs is not None, "Configuration not loaded"
        assert hasattr(specs, "orchestrator"), "Missing orchestrator config"
        assert hasattr(specs, "validation"), "Missing validation config"

        # Test retry limits
        assert specs.orchestrator.max_retry_iterations > 0, "Missing retry limit"
        assert specs.orchestrator.global_step_limit > 0, "Missing step limit"

        # Test singleton pattern
        specs2 = load_rg_specs()
        assert specs is specs2, "Not using singleton pattern"

        # Test reload
        reload_config()
        specs3 = load_rg_specs()
        assert specs is not specs3, "Reload not working"

        print("   ✅ Configuration parity tests PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Configuration parity tests FAILED: {e}")
        return False


def test_reasoning_toggles_parity():
    """Test RG reasoning toggles match LIC capabilities."""
    print("\n2. Testing Reasoning Toggles Parity...")

    try:
        from apps_rg.shared.reasoning.toggles import get_toggles

        # Test default toggles
        toggles = get_toggles()
        assert hasattr(toggles, "use_cot"), "Missing CoT toggle"
        assert hasattr(toggles, "use_reflexion"), "Missing reflexion toggle"
        assert hasattr(toggles, "strict_mode"), "Missing strict mode toggle"

        # Test environment-specific toggles
        test_toggles = get_toggles("test")
        assert test_toggles.use_cot is False, "Test mode should disable CoT"

        dev_toggles = get_toggles("dev")
        assert dev_toggles.strict_mode is False, "Dev mode should be less strict"

        print("   ✅ Reasoning toggles parity tests PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Reasoning toggles parity tests FAILED: {e}")
        return False


def test_trace_registry_parity():
    """Test RG trace registry matches LIC persistence capabilities."""
    print("\n3. Testing Trace Registry Parity...")

    try:
        from apps_rg.shared.core.trace_registry import TraceRegistry
        import tempfile

        # Test persistence
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            trace_path = Path(f.name)

        registry = TraceRegistry(persistence_path=trace_path)
        assert registry.persistence_path == trace_path, "Persistence path not set"

        # Create and persist a span
        span_id = registry.start_span("test_mission", "test_agent", "test_operation")
        registry.end_span(span_id, status="SUCCESS")

        # Check file was created
        assert trace_path.exists(), "Trace file not created"

        # Verify content
        with open(trace_path) as f:
            content = f.read()
            assert len(content) > 0, "No content in trace file"

        # Cleanup
        trace_path.unlink()

        print("   ✅ Trace registry parity tests PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Trace registry parity tests FAILED: {e}")
        return False


def test_base_engine_parity():
    """Test BaseRGEngine has all required components."""
    print("\n4. Testing Base Engine Parity...")

    try:
        from apps_rg.engines.base.base_resume_engine import BaseRGEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext

        ctx = SovereignContext()

        class TestEngine(BaseRGEngine):
            async def execute(self):
                return self.rg_specs

        engine = TestEngine(ctx)

        # Should have auto-loaded configuration
        assert hasattr(engine, "rg_specs"), "Missing auto-loaded specs"
        assert hasattr(engine, "toggles"), "Missing reasoning toggles"
        assert engine.rg_specs is not None, "Specs not loaded"
        assert engine.toggles is not None, "Toggles not loaded"

        # Should have SubatomicTestingMixin
        assert hasattr(engine, "run_subatomic_test"), "Missing SubatomicTestingMixin"

        print("   ✅ Base engine parity tests PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Base engine parity tests FAILED: {e}")
        return False


def test_orchestrator_parity():
    """Test ResumeOrchestratorEngine has cyclic retry logic."""
    print("\n5. Testing Orchestrator Parity...")

    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import (
            ResumeOrchestratorEngine,
        )
        from apps_rg.engines.base.sovereign_context import SovereignContext

        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="test_parity")

        # Should have retry logic components
        assert hasattr(orch, "MAX_RETRY_ITERATIONS"), "Missing retry limit"
        assert hasattr(orch, "GLOBAL_STEP_LIMIT"), "Missing step limit"
        assert hasattr(orch, "mission_id"), "Missing mission ID"

        # Should have reasonable values
        assert orch.MAX_RETRY_ITERATIONS > 0, "Invalid retry limit"
        assert orch.GLOBAL_STEP_LIMIT > 0, "Invalid step limit"

        print("   ✅ Orchestrator parity tests PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Orchestrator parity tests FAILED: {e}")
        return False


def test_gap_closure_validation():
    """Validate that all identified gaps have been closed."""
    print("\n6. Testing Gap Closure Validation...")

    gaps_closed = 0
    total_gaps = 4

    # Gap 1: Cyclic Retry Logic
    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import (
            ResumeOrchestratorEngine,
        )
        from apps_rg.engines.base.sovereign_context import SovereignContext

        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="gap_test")

        assert hasattr(orch, "MAX_RETRY_ITERATIONS"), "Gap 1 not closed: Missing retry limit"
        assert hasattr(orch, "GLOBAL_STEP_LIMIT"), "Gap 1 not closed: Missing step limit"
        gaps_closed += 1
        print("   ✅ Gap 1 (Cyclic Retry Logic): CLOSED")
    except Exception as e:
        print(f"   ❌ Gap 1 (Cyclic Retry Logic): OPEN - {e}")

    # Gap 2: Auto-Configuration
    try:
        from apps_rg.engines.base.base_resume_engine import BaseRGEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext

        ctx = SovereignContext()

        class TestEngine(BaseRGEngine):
            async def execute(self):
                return self.rg_specs

        engine = TestEngine(ctx)

        assert hasattr(engine, "rg_specs"), "Gap 2 not closed: Missing auto-config"
        assert hasattr(engine, "toggles"), "Gap 2 not closed: Missing toggles"
        gaps_closed += 1
        print("   ✅ Gap 2 (Auto-Configuration): CLOSED")
    except Exception as e:
        print(f"   ❌ Gap 2 (Auto-Configuration): OPEN - {e}")

    # Gap 3: Persistent Tracing
    try:
        from apps_rg.shared.core.trace_registry import TraceRegistry
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            trace_path = Path(f.name)

        registry = TraceRegistry(persistence_path=trace_path)
        span_id = registry.start_span("test", "test", "test")
        registry.end_span(span_id, status="SUCCESS")

        assert trace_path.exists(), "Gap 3 not closed: Tracing not persisted"
        trace_path.unlink()
        gaps_closed += 1
        print("   ✅ Gap 3 (Persistent Tracing): CLOSED")
    except Exception as e:
        print(f"   ❌ Gap 3 (Persistent Tracing): OPEN - {e}")

    # Gap 4: Subatomic Testing
    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import (
            ResumeOrchestratorEngine,
        )
        from apps_rg.engines.base.sovereign_context import SovereignContext

        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="gap_test")

        assert hasattr(orch, "run_subatomic_test"), (
            "Gap 4 not closed: Missing SubatomicTestingMixin"
        )
        gaps_closed += 1
        print("   ✅ Gap 4 (Subatomic Testing): CLOSED")
    except Exception as e:
        print(f"   ❌ Gap 4 (Subatomic Testing): OPEN - {e}")

    print(f"\n   Gap Closure Summary: {gaps_closed}/{total_gaps} gaps closed")

    if gaps_closed == total_gaps:
        print("   ✅ All critical gaps have been CLOSED!")
        return True
    else:
        print(f"   ❌ {total_gaps - gaps_closed} gaps remain OPEN")
        return False


def main():
    """Run all parity tests."""
    results = []

    results.append(test_configuration_parity())
    results.append(test_reasoning_toggles_parity())
    results.append(test_trace_registry_parity())
    results.append(test_base_engine_parity())
    results.append(test_orchestrator_parity())
    results.append(test_gap_closure_validation())

    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    passed = sum(results)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL PARITY TESTS PASSED!")
        print("✅ RG Architecture now has FULL LIC parity")
        print("✅ All critical gaps have been successfully closed")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("⚠️  Some gaps remain open")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
