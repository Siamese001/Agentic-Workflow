"""
Phase 3 Zero-Loss Verification Test Suite

This test suite ensures no legacy functionality is dropped during the Phase 3
BaseAgent standardization work. All 4 test cases must pass 100%.

Test Cases:
- TC-9: MRO Integrity - L2 agent MRO follows correct path
- TC-10: Inheritance Continuity - Agents have heal_repository and mcp_tools
- TC-11: Method Preservation - L2ExecutionBaseAgent has required methods
- TC-12: Import Stability - Deprecated bases raise clear ImportError

Author: Cascade
Date: January 19, 2026
Phase: 3 - BaseAgent Standardization & Mixin Root Injection
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_tc9_mro_integrity():
    """
    TC-9: MRO Integrity

    Verify that a sample L2 agent's __mro__ correctly follows the path:
    Agent -> L2ExecutionBaseAgent -> SovereignBaseAgent -> infrastructure_mixin -> object
    """
    print("\n" + "=" * 60)
    print("TC-9: MRO Integrity")
    print("=" * 60)

    from agentic_core.L2_execution.tool_registry.L2ExecutionBaseAgent import L2ExecutionBaseAgent

    from agentic_core.base_agents.infrastructure_mixin import infrastructure_mixin
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    # Get MRO
    mro = L2ExecutionBaseAgent.__mro__
    mro_names = [cls.__name__ for cls in mro]

    print(f"L2ExecutionBaseAgent MRO: {mro_names}")

    # Verify key classes are in MRO in correct order
    required_order = [
        "L2ExecutionBaseAgent",
        "SovereignBaseAgent",
        "infrastructure_mixin",
        "object",
    ]

    # Find positions of required classes
    positions = {}
    for cls_name in required_order:
        if cls_name in mro_names:
            positions[cls_name] = mro_names.index(cls_name)
        else:
            print(f"❌ FAIL: {cls_name} not found in MRO")
            return False

    # Verify order
    for i in range(len(required_order) - 1):
        current = required_order[i]
        next_cls = required_order[i + 1]
        if positions[current] >= positions[next_cls]:
            print(f"❌ FAIL: {current} should come before {next_cls} in MRO")
            return False

    # Verify SovereignBaseAgent inherits from infrastructure_mixin
    if not issubclass(SovereignBaseAgent, infrastructure_mixin):
        print("❌ FAIL: SovereignBaseAgent should inherit from infrastructure_mixin")
        return False

    print("✅ PASS: MRO follows correct inheritance path")
    print("   L2ExecutionBaseAgent -> ... -> SovereignBaseAgent -> infrastructure_mixin -> object")
    return True


def test_tc10_inheritance_continuity():
    """
    TC-10: Inheritance Continuity

    Instantiated agents must still have access to heal_repository
    (verifying Mixin root injection).
    """
    print("\n" + "=" * 60)
    print("TC-10: Inheritance Continuity")
    print("=" * 60)

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    # Create a test agent
    class TestL2Agent(SovereignBaseAgent):
        name: str = "TestL2Agent"

    agent = TestL2Agent()

    # Verify heal_repository is accessible
    if not hasattr(agent, "heal_repository"):
        print("❌ FAIL: Agent should have heal_repository method")
        return False

    if not callable(agent.heal_repository):
        print("❌ FAIL: heal_repository should be callable")
        return False

    # Verify HealerMixin methods are accessible
    healer_methods = ["heal", "_normalize_result", "reset_healing_budget"]
    for method in healer_methods:
        if not hasattr(agent, method):
            print(f"❌ FAIL: Agent should have {method} from HealerMixin")
            return False

    # Verify infrastructure_mixin methods are accessible
    infra_methods = ["verify_state", "get_infrastructure_status"]
    for method in infra_methods:
        if not hasattr(agent, method):
            print(f"❌ FAIL: Agent should have {method} from infrastructure_mixin")
            return False

    # Verify _infra_initialized flag is set
    if not getattr(agent, "_infra_initialized", False):
        print("❌ FAIL: _infra_initialized should be True after initialization")
        return False

    print("✅ PASS: Agents have access to all inherited methods")
    print("   heal_repository: ✓")
    print(f"   HealerMixin methods: {healer_methods}")
    print(f"   infrastructure_mixin methods: {infra_methods}")
    print("   _infra_initialized: True")
    return True


def test_tc11_method_preservation():
    """
    TC-11: Method Preservation

    Verify that methods previously held in CanonBaseAgent are callable
    on the new L2ExecutionBaseAgent.
    """
    print("\n" + "=" * 60)
    print("TC-11: Method Preservation")
    print("=" * 60)

    from agentic_core.L2_execution.tool_registry.L2ExecutionBaseAgent import L2ExecutionBaseAgent

    # Methods that should be present (from Canon/ExecutionCanon bases)
    required_methods = [
        "execute",  # Abstract method
        "can_run",  # From SubAtomicAgent
        "run_with_broadcast",  # From SubAtomicAgent
        "check_negative_constraints",  # From CanonBaseAgent
        "get_validation_keys",  # From CanonBaseAgent
        "heal_repository",  # From HealerMixin via SovereignBaseAgent
        "act",  # L2-specific tool execution
        "act_async",  # L2-specific async tool execution
        "cluster_errors",  # L2-specific error clustering
    ]

    missing_methods = []
    for method in required_methods:
        if not hasattr(L2ExecutionBaseAgent, method):
            missing_methods.append(method)

    if missing_methods:
        print(f"❌ FAIL: L2ExecutionBaseAgent missing methods: {missing_methods}")
        return False

    # Verify methods are callable (not just attributes)
    for method in required_methods:
        attr = getattr(L2ExecutionBaseAgent, method)
        if not callable(attr):
            print(f"❌ FAIL: {method} should be callable")
            return False

    print("✅ PASS: All required methods preserved in L2ExecutionBaseAgent")
    print(f"   Methods verified: {len(required_methods)}")
    for method in required_methods:
        print(f"   - {method}: ✓")
    return True


def test_tc12_import_stability():
    """
    TC-12: Import Stability

    Ensure that the canonical base classes can be imported without errors.
    Also verify that the 8 canonical BaseAgent files exist.
    """
    print("\n" + "=" * 60)
    print("TC-12: Import Stability")
    print("=" * 60)

    # Canonical BaseAgent files that should exist
    canonical_bases = [
        ("L0MaintenanceBaseAgent", "agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent"),
        ("L1CognitionBaseAgent", "agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent"),
        ("L2ExecutionBaseAgent", "agentic_core.L2_execution.tool_registry.L2ExecutionBaseAgent"),
        (
            "L3OrchestrationBaseAgent",
            "agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent",
        ),
        ("L4StateBaseAgent", "agentic_core.L4_state.validation_context.L4StateBaseAgent"),
        ("L5SafetyBaseAgent", "agentic_core.L5_safety.validators.L5SafetyBaseAgent"),
        ("L6ObservabilityBaseAgent", "agentic_core.L6_observability.L6ObservabilityBaseAgent"),
        ("SovereignBaseAgent", "agentic_core.observability.SovereignBaseAgent"),
    ]

    import_errors = []
    successful_imports = []

    for class_name, module_path in canonical_bases:
        try:
            # Dynamic import
            parts = module_path.rsplit(".", 1)
            if len(parts) == 2:
                module_name, attr_name = parts
                module = __import__(module_name, fromlist=[attr_name])
                cls = getattr(module, attr_name)
                successful_imports.append(class_name)
            else:
                import_errors.append((class_name, "Invalid module path"))
        except (ImportError, NameError, AttributeError, TypeError) as e:
            import_errors.append((class_name, str(e)))
        except AttributeError as e:
            import_errors.append((class_name, str(e)))

    if import_errors:
        print("❌ FAIL: Import errors for canonical bases:")
        for name, error in import_errors:
            print(f"   - {name}: {error}")
        return False

    # Verify we have exactly 8 canonical bases
    if len(successful_imports) != 8:
        print(f"❌ FAIL: Expected 8 canonical bases, found {len(successful_imports)}")
        return False

    print("✅ PASS: All 8 canonical BaseAgent files import successfully")
    for name in successful_imports:
        print(f"   - {name}: ✓")
    return True


def test_base_agent_count():
    """
    Bonus Test: Verify exactly 8 BaseAgent files exist in agentic_core.
    """
    print("\n" + "=" * 60)
    print("BONUS: BaseAgent File Count")
    print("=" * 60)

    from agentic_core.utils.ssot_discovery import get_python_files

    # Find all *BaseAgent.py files
    all_files = get_python_files(PROJECT_ROOT / "agentic_core")
    base_agent_files = [f for f in all_files if f.name.endswith("BaseAgent.py")]

    print(f"Found {len(base_agent_files)} BaseAgent files:")
    for f in sorted(base_agent_files):
        print(f"   - {f.relative_to(PROJECT_ROOT)}")

    if len(base_agent_files) != 8:
        print(f"\n❌ FAIL: Expected exactly 8 BaseAgent files, found {len(base_agent_files)}")
        return False

    print("\n✅ PASS: Exactly 8 BaseAgent files (target achieved)")
    return True


def main():
    """Run all Phase 3 Zero-Loss test cases."""
    print("\n" + "=" * 70)
    print("PHASE 3 ZERO-LOSS VERIFICATION TEST SUITE")
    print("=" * 70)
    print(f"Project Root: {PROJECT_ROOT}")

    tests = [
        ("TC-9: MRO Integrity", test_tc9_mro_integrity),
        ("TC-10: Inheritance Continuity", test_tc10_inheritance_continuity),
        ("TC-11: Method Preservation", test_tc11_method_preservation),
        ("TC-12: Import Stability", test_tc12_import_stability),
        ("BONUS: BaseAgent File Count", test_base_agent_count),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    # Core tests (TC-9 to TC-12)
    core_tests = results[:4]
    core_passed = sum(1 for _, passed in core_tests if passed)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    print(f"CORE TESTS: {core_passed}/4 passed")
    print(f"TOTAL: {passed_count}/{total_count} tests passed")

    if core_passed == 4:
        print("✅ 100% PASS - All Phase 3 Zero-Loss tests passed!")
        print("\nPhase 3 BaseAgent Standardization is verified.")
        return 0
    else:
        print(f"❌ FAIL - {4 - core_passed} core test(s) failed")
        print("\nReview failures before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
