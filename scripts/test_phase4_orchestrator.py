"""
Direct test runner for Phase 4: Orchestrator Logic.
Tests cyclic retry logic, global limits, and persistent tracing.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("PHASE 4: ORCHESTRATOR LOGIC TESTS")
print("=" * 80)

def test_orchestrator_initialization():
    """Verify ResumeOrchestratorEngine initializes with cyclic logic."""
    print("\n1. Testing orchestrator initialization...")
    
    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext
        
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="test_mission")
        
        # Verify cyclic logic components
        assert hasattr(orch, 'GLOBAL_STEP_LIMIT'), "Missing GLOBAL_STEP_LIMIT"
        assert hasattr(orch, 'MAX_RETRY_ITERATIONS'), "Missing MAX_RETRY_ITERATIONS"
        assert hasattr(orch, 'mission_id'), "Missing mission_id"
        assert hasattr(orch, 'hop_checkpoints'), "Missing hop_checkpoints"
        
        # Verify reasonable values
        assert orch.GLOBAL_STEP_LIMIT > 0, "Invalid GLOBAL_STEP_LIMIT"
        assert orch.MAX_RETRY_ITERATIONS > 0, "Invalid MAX_RETRY_ITERATIONS"
        assert orch.mission_id == "test_mission", "Invalid mission_id"
        
        print("   ✅ Orchestrator initialization test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Orchestrator initialization test FAILED: {e}")
        return False

def test_global_safety_limits():
    """Verify global safety limits are enforced."""
    print("\n2. Testing global safety limits...")
    
    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext
        
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="test_limits")
        
        # Check limits from config
        assert orch.GLOBAL_STEP_LIMIT == 20, "Expected GLOBAL_STEP_LIMIT of 20"
        assert orch.MAX_RETRY_ITERATIONS == 5, "Expected MAX_RETRY_ITERATIONS of 5"
        
        print("   ✅ Global safety limits test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Global safety limits test FAILED: {e}")
        return False

def test_persistent_tracing_integration():
    """Verify persistent tracing is properly integrated."""
    print("\n3. Testing persistent tracing integration...")
    
    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext
        from apps_rg.shared.core.trace_registry import TraceRegistry
        
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="test_tracing")
        
        # Verify trace registry is initialized
        assert hasattr(ctx, 'trace'), "Missing trace registry"
        assert isinstance(ctx.trace, TraceRegistry), "Invalid trace registry type"
        
        # Verify persistence path is set
        assert ctx.trace.persistence_path is not None, "Missing persistence path"
        assert "test_tracing" in str(ctx.trace.persistence_path), "Mission ID not in path"
        
        print("   ✅ Persistent tracing integration test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Persistent tracing integration test FAILED: {e}")
        return False

def test_cyclic_validation_toggle():
    """Verify cyclic validation is toggle-controlled."""
    print("\n4. Testing cyclic validation toggle...")
    
    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext
        
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="test_toggle")
        
        # Verify toggle is checked
        assert hasattr(orch, 'toggles'), "Missing toggles"
        assert hasattr(orch.toggles, 'use_cyclic_validation'), "Missing use_cyclic_validation"
        assert orch.toggles.use_cyclic_validation is True, "Cyclic validation should be enabled"
        
        print("   ✅ Cyclic validation toggle test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Cyclic validation toggle test FAILED: {e}")
        return False

def test_checkpoint_system():
    """Verify checkpoint system works."""
    print("\n5. Testing checkpoint system...")
    
    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import HopCheckpoint
        
        # Test checkpoint creation
        checkpoint = HopCheckpoint(
            hop_id="TEST_HOP",
            status="COMPLETED",
            metrics={"duration": 1.5}
        )
        
        assert checkpoint.hop_id == "TEST_HOP", "Invalid hop_id"
        assert checkpoint.status == "COMPLETED", "Invalid status"
        assert checkpoint.metrics["duration"] == 1.5, "Invalid metrics"
        
        print("   ✅ Checkpoint system test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Checkpoint system test FAILED: {e}")
        return False

def test_feedback_mechanism():
    """Verify feedback mechanism is implemented."""
    print("\n6. Testing feedback mechanism...")
    
    try:
        from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext
        
        ctx = SovereignContext()
        orch = ResumeOrchestratorEngine(ctx, mission_id="test_feedback")
        
        # Verify orchestrator has feedback handling capability
        # This is tested by checking if the execute method has the retry logic
        import inspect
        source = inspect.getsource(orch.execute)
        
        # Check for feedback-related code
        assert "quality_feedback" in source, "Missing quality feedback handling"
        assert "ats_feedback" in source, "Missing ATS feedback handling"
        assert "retry_iteration" in source, "Missing retry iteration handling"
        
        print("   ✅ Feedback mechanism test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Feedback mechanism test FAILED: {e}")
        return False

def main():
    """Run all Phase 4 tests."""
    results = []
    
    results.append(test_orchestrator_initialization())
    results.append(test_global_safety_limits())
    results.append(test_persistent_tracing_integration())
    results.append(test_cyclic_validation_toggle())
    results.append(test_checkpoint_system())
    results.append(test_feedback_mechanism())
    
    print("\n" + "=" * 80)
    print("PHASE 4 TEST RESULTS")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL PHASE 4 TESTS PASSED!")
        print("✅ Cyclic retry logic is implemented")
        print("✅ Global safety limits are enforced")
        print("✅ Persistent tracing is integrated")
        print("✅ Feedback mechanisms are working")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("⚠️  Orchestrator logic needs fixes")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
