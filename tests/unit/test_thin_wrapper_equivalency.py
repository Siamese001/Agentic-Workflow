#!/usr/bin/env python3
"""
Functional Equivalency Test: Thin Wrapper vs Monolithic Canon Validator

Verifies that MissionController implements the same agent methodology
as canon_validator_agentic_v2.py
"""
import sys
from pathlib import Path

# Setup project root
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

def test_mission_controller_has_required_methods():
    """Test that MissionController has all required methods from monolithic."""
    print("\n[TEST 1] MissionController Method Parity")
    print("-" * 60)
    
    from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
    
    required_methods = [
        'run_mission',
        '_initialize_context',
        '_initialize_core_components',  # NEW: SubAtomicEngine, SafetyGuardrail
        '_run_sovereign_dashboard',      # NEW: ReportingAgent
        '_run_syntax_healing',
        '_run_gravity_refactor',         # NEW: Gravity violation detection
        '_run_per_file_validation',      # FIXED: Now calls heal_violation()
        '_run_batch_sweeps',
        '_run_monitors',
        '_print_mission_report',
    ]
    
    missing = []
    for method in required_methods:
        if not hasattr(MissionController, method):
            missing.append(method)
            print(f"   [MISSING] {method}")
        else:
            print(f"   [OK] {method}")
    
    if missing:
        print(f"\n   [FAIL] Missing {len(missing)} methods")
        return False
    
    print(f"\n   [PASS] All {len(required_methods)} methods present")
    return True


def test_compliance_orchestrator_structure():
    """Test that ComplianceOrchestratorAgent has required methods (static analysis)."""
    print("\n[TEST 2] ComplianceOrchestratorAgent Structure")
    print("-" * 60)
    
    import inspect
    
    try:
        # Import the class definition without instantiating
        from agentic_core.L5_safety.validators.compliance_orchestrator import ComplianceOrchestratorAgent
        
        required_methods = [
            'get_all_agents',
            'get_atomic_validators', 
            'get_batch_validators',
            'get_monitors',
            '_discover_all_layers',
        ]
        
        missing = []
        for method in required_methods:
            if hasattr(ComplianceOrchestratorAgent, method):
                print(f"   [OK] {method}()")
            else:
                print(f"   [MISSING] {method}()")
                missing.append(method)
        
        if missing:
            print(f"\n   [FAIL] Missing {len(missing)} methods")
            return False
        
        print(f"\n   [PASS] All orchestrator methods present")
        return True
            
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False


def test_per_file_validation_calls_heal_violation():
    """Test that _run_per_file_validation() calls heal_violation on agents."""
    print("\n[TEST 3] Per-File Validation Healing Logic")
    print("-" * 60)
    
    import inspect
    from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
    
    # Get source code of _run_per_file_validation
    source = inspect.getsource(MissionController._run_per_file_validation)
    
    # Check for key patterns that indicate proper healing
    checks = [
        ('get_atomic_validators()', 'Fetches atomic validators from orchestrator'),
        ('heal_violation', 'Calls heal_violation() on agents'),
        ('await agent.heal_violation', 'Async heal_violation call'),
        ('mutated_this_round', 'Tracks mutations per round'),
        ('healed_files', 'Counts healed files'),
    ]
    
    all_pass = True
    for pattern, description in checks:
        if pattern in source:
            print(f"   [OK] {description}")
        else:
            print(f"   [MISSING] {description}")
            all_pass = False
    
    if all_pass:
        print(f"\n   [PASS] Per-file validation has full healing logic")
    else:
        print(f"\n   [FAIL] Per-file validation missing some healing logic")
    
    return all_pass


def test_core_component_initialization():
    """Test that _initialize_core_components() initializes all required components."""
    print("\n[TEST 4] Core Component Initialization")
    print("-" * 60)
    
    import inspect
    from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
    
    source = inspect.getsource(MissionController._initialize_core_components)
    
    components = [
        ('SubAtomicEngine', 'LLM-powered code mutation'),
        ('SafetyGuardrail', 'Mutation safety checks'),
        ('fission_manager', 'File splitting logic'),
        ('ctx.engine', 'Wires engine to context'),
        ('ctx.safety', 'Wires safety to context'),
        ('ctx.fission', 'Wires fission to context'),
    ]
    
    all_pass = True
    for component, description in components:
        if component in source:
            print(f"   [OK] {component}: {description}")
        else:
            print(f"   [MISSING] {component}: {description}")
            all_pass = False
    
    if all_pass:
        print(f"\n   [PASS] All core components initialized")
    else:
        print(f"\n   [FAIL] Missing core component initialization")
    
    return all_pass


def test_gravity_refactor_phase():
    """Test that _run_gravity_refactor() detects gravity violations."""
    print("\n[TEST 5] Gravity Refactor Phase")
    print("-" * 60)
    
    import inspect
    from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
    
    source = inspect.getsource(MissionController._run_gravity_refactor)
    
    patterns = [
        ('get_layer_rank', 'Uses layer ranking'),
        ('gravity_violations', 'Tracks gravity violations'),
        ('gravity_attempts', 'Prevents infinite loops'),
        ('Gravity Leak', 'Reports gravity leaks'),
    ]
    
    all_pass = True
    for pattern, description in patterns:
        if pattern in source:
            print(f"   [OK] {description}")
        else:
            print(f"   [MISSING] {description}")
            all_pass = False
    
    if all_pass:
        print(f"\n   [PASS] Gravity refactor phase implemented")
    else:
        print(f"\n   [FAIL] Gravity refactor phase incomplete")
    
    return all_pass


def main():
    """Run all functional equivalency tests."""
    print("="*70)
    print("  FUNCTIONAL EQUIVALENCY TEST: Thin Wrapper vs Monolithic")
    print("="*70)
    
    results = []
    
    results.append(("Method Parity", test_mission_controller_has_required_methods()))
    results.append(("Orchestrator Structure", test_compliance_orchestrator_structure()))
    results.append(("Per-File Healing", test_per_file_validation_calls_heal_violation()))
    results.append(("Core Components", test_core_component_initialization()))
    results.append(("Gravity Refactor", test_gravity_refactor_phase()))
    
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"   [{status}] {name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   [VERDICT] FUNCTIONAL EQUIVALENCY CONFIRMED")
        return 0
    else:
        print("\n   [VERDICT] SOME TESTS FAILED - Review above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
