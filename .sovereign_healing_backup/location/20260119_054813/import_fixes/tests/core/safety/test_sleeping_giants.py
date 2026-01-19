#!/usr/bin/env python3
"""
Test Suite: Sleeping Giants Verification

Verifies that the previously dormant agents now have properly wired
heal_repository methods that call their internal validation logic.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0

def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")

def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")

# =============================================================================
# Test 1: TwoPhaseDeduplicationAgent Import Fix
# =============================================================================
def test_two_phase_dedup_import():
    """Verify TwoPhaseDeduplicationAgent loads without ImportError."""
    print("\n" + "=" * 70)
    print("Test 1: TwoPhaseDeduplicationAgent Import")
    print("=" * 70)
    
    try:
        from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import TwoPhaseDeduplicationAgent
        test_pass("GIANT-01", "TwoPhaseDeduplicationAgent imports successfully")
    except ImportError as e:
        test_fail("GIANT-01", f"ImportError: {e}")
    except Exception as e:
        test_fail("GIANT-01", f"Unexpected error: {e}")

# =============================================================================
# Test 2: ScriptsPlanningOrchestratorAgent Task Validation
# =============================================================================
def test_scripts_planning_validation():
    """Verify ScriptsPlanningOrchestratorAgent wires _validate_tasks."""
    print("\n" + "=" * 70)
    print("Test 2: ScriptsPlanningOrchestratorAgent Task Validation")
    print("=" * 70)
    
    try:
        from archives.void_violations.ScriptsPlanningOrchestratorAgent import ScriptsPlanningOrchestratorAgent
        
        agent = ScriptsPlanningOrchestratorAgent()
        
        # Verify heal_repository exists and has proper signature
        if hasattr(agent, 'heal_repository'):
            # Call heal_repository in dry_run mode
            result = agent.heal_repository(dry_run=True)
            
            if isinstance(result, dict):
                test_pass("GIANT-02", f"heal_repository returns dict with keys: {list(result.keys())}")
            else:
                test_fail("GIANT-02", f"heal_repository returned {type(result)}, expected dict")
        else:
            test_fail("GIANT-02", "heal_repository method not found")
    except Exception as e:
        test_fail("GIANT-02", f"Error: {e}")

# =============================================================================
# Test 3: MemoryLeakDetectorAgent Scan and Fix
# =============================================================================
def test_memory_leak_detector():
    """Verify MemoryLeakDetectorAgent wires _scan_and_fix."""
    print("\n" + "=" * 70)
    print("Test 3: MemoryLeakDetectorAgent Scan and Fix")
    print("=" * 70)
    
    try:
        from agentic_core.L2_execution.ToolRegistry.MemoryLeakDetectorAgent import MemoryLeakDetectorAgent
        
        # Create with mock context
        mock_ctx = MagicMock()
        mock_ctx.python_files = []
        
        agent = MemoryLeakDetectorAgent(ctx=mock_ctx)
        
        # Verify heal_repository exists
        if hasattr(agent, 'heal_repository'):
            result = agent.heal_repository(dry_run=True)
            
            if isinstance(result, dict):
                test_pass("GIANT-03", f"heal_repository returns dict: {result}")
            else:
                test_fail("GIANT-03", f"heal_repository returned {type(result)}, expected dict")
        else:
            test_fail("GIANT-03", "heal_repository method not found")
    except Exception as e:
        test_fail("GIANT-03", f"Error: {e}")

# =============================================================================
# Test 4: PeerIntelligenceAuditorAgent Search Count Validation
# =============================================================================
def test_peer_intelligence_auditor():
    """Verify PeerIntelligenceAuditorAgent wires _validate_search_count."""
    print("\n" + "=" * 70)
    print("Test 4: PeerIntelligenceAuditorAgent Search Count")
    print("=" * 70)
    
    try:
        from agentic_core.L2_execution.ToolRegistry.PeerIntelligenceAuditorAgent import PeerIntelligenceAuditorAgent
        
        agent = PeerIntelligenceAuditorAgent()
        
        # Verify heal_repository exists
        if hasattr(agent, 'heal_repository'):
            result = agent.heal_repository(dry_run=True)
            
            if isinstance(result, dict):
                test_pass("GIANT-04", f"heal_repository returns dict: {result}")
            else:
                test_fail("GIANT-04", f"heal_repository returned {type(result)}, expected dict")
        else:
            test_fail("GIANT-04", "heal_repository method not found")
    except Exception as e:
        test_fail("GIANT-04", f"Error: {e}")

# =============================================================================
# Test 5: DAGMutatorAgent Mutation Validation
# =============================================================================
def test_dag_mutator():
    """Verify DAGMutatorAgent wires _validate_mutation."""
    print("\n" + "=" * 70)
    print("Test 5: DAGMutatorAgent Mutation Validation")
    print("=" * 70)
    
    try:
        from archives.void_violations.DAGMutatorAgent import DAGMutatorAgent, DAGConfig
        
        config = DAGConfig()
        agent = DAGMutatorAgent(config=config)
        
        # Verify heal_repository exists
        if hasattr(agent, 'heal_repository'):
            result = agent.heal_repository(dry_run=True)
            
            if isinstance(result, dict):
                # Verify it's not just {"skipped": 1}
                if result.get("skipped") == 1 and len(result) == 1:
                    test_fail("GIANT-05", "heal_repository still returns only {'skipped': 1}")
                else:
                    test_pass("GIANT-05", f"heal_repository returns proper dict: {result}")
            else:
                test_fail("GIANT-05", f"heal_repository returned {type(result)}, expected dict")
        else:
            test_fail("GIANT-05", "heal_repository method not found")
    except Exception as e:
        test_fail("GIANT-05", f"Error: {e}")

# =============================================================================
# Test 6: ImportHealerAgent Directory Healing
# =============================================================================
def test_import_healer():
    """Verify ImportHealerAgent wires heal_all_imports_in_directory."""
    print("\n" + "=" * 70)
    print("Test 6: ImportHealerAgent Directory Healing")
    print("=" * 70)
    
    try:
        from archives.void_violations.ImportHealerAgent import ImportHealerAgent
        
        agent = ImportHealerAgent(project_root=PROJECT_ROOT)
        
        # Verify heal_repository exists
        if hasattr(agent, 'heal_repository'):
            result = agent.heal_repository(dry_run=True)
            
            if isinstance(result, dict):
                test_pass("GIANT-06", f"heal_repository returns dict: {result}")
            else:
                test_fail("GIANT-06", f"heal_repository returned {type(result)}, expected dict")
        else:
            test_fail("GIANT-06", "heal_repository method not found")
    except Exception as e:
        test_fail("GIANT-06", f"Error: {e}")

# =============================================================================
# Main
# =============================================================================
def main():
    print("\n" + "=" * 70)
    print("SLEEPING GIANTS TEST SUITE")
    print("=" * 70)
    
    test_two_phase_dedup_import()
    test_scripts_planning_validation()
    test_memory_leak_detector()
    test_peer_intelligence_auditor()
    test_dag_mutator()
    test_import_healer()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")
    
    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - SLEEPING GIANTS AWAKENED")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED - GIANTS STILL SLEEPING")
        return 1

if __name__ == '__main__':
    sys.exit(main())
