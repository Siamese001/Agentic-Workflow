"""
Phase 2 Zero-Loss Verification Test Suite

This test suite ensures no legacy functionality is dropped during the Phase 2
orchestrator unification work. All 4 test cases must pass 100%.

Test Cases:
- TC-5: Mode Parity - OrchestratorAgent(mode="healing") produces correct MissionResult
- TC-6: Registry Resolution - get_orchestrator returns IOrchestratorAgent
- TC-7: Graceful Fallback - Unknown mode raises descriptive ValueError
- TC-8: Discovery Integration - No rglob calls, uses ssot_discovery exclusively

Author: Cascade
Date: January 19, 2026
Phase: 2 - Orchestrator Unification
"""

import ast
import sys
import warnings
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_tc5_mode_parity():
    """
    TC-5: Mode Parity

    Verify OrchestratorAgent(mode="healing") produces the same
    MissionResult schema as expected from a legacy HealingOrchestratorAgent.
    """
    print("\n" + "=" * 60)
    print("TC-5: Mode Parity")
    print("=" * 60)

    from agentic_core.L3_orchestration.interfaces import MissionResult
    from agentic_core.L3_orchestration.OrchestratorAgent import OrchestratorAgent

    # Create orchestrator in healing mode
    orchestrator = OrchestratorAgent(mode="healing")

    # Verify mode is set correctly
    if orchestrator.mode.value != "healing":
        print(f"❌ FAIL: Mode should be 'healing', got '{orchestrator.mode.value}'")
        return False

    # Run a mission and verify result schema
    result = orchestrator.run_mission(agents=["TestAgent1", "TestAgent2"], dry_run=True)

    # Verify result is MissionResult
    if not isinstance(result, MissionResult):
        print(f"❌ FAIL: Result should be MissionResult, got {type(result)}")
        return False

    # Verify MissionResult has all required fields
    required_fields = [
        "success",
        "total_agents",
        "successful_agents",
        "failed_agents",
        "total_violations_found",
        "total_violations_fixed",
        "total_errors",
        "agent_results",
        "phase",
        "metadata",
    ]

    result_dict = result.to_dict()
    for field in required_fields:
        if field not in result_dict:
            print(f"❌ FAIL: MissionResult missing field: {field}")
            return False

    # Verify metadata contains mode
    if result.metadata.get("mode") != "healing":
        print("❌ FAIL: MissionResult metadata should contain mode='healing'")
        return False

    print("✅ PASS: OrchestratorAgent(mode='healing') produces correct MissionResult")
    print(f"   Mode: {orchestrator.mode.value}")
    print(f"   Result fields: {len(required_fields)} verified")
    print(f"   Metadata: {result.metadata}")
    return True


def test_tc6_registry_resolution():
    """
    TC-6: Registry Resolution

    Verify get_orchestrator returns an object that satisfies
    isinstance(obj, IOrchestratorAgent).
    """
    print("\n" + "=" * 60)
    print("TC-6: Registry Resolution")
    print("=" * 60)

    from agentic_core.L3_orchestration.interfaces import IOrchestratorAgent
    from agentic_core.L3_orchestration.orchestrator_registry import get_orchestrator

    # Test all valid modes
    modes = ["unified", "healing", "compliance", "ssot", "full"]

    for mode in modes:
        orchestrator = get_orchestrator(mode)

        if not isinstance(orchestrator, IOrchestratorAgent):
            print(f"❌ FAIL: get_orchestrator('{mode}') should return IOrchestratorAgent")
            return False

        # Verify it has required protocol methods
        required_methods = ["run_mission", "run_agent", "get_available_agents", "validate_mission"]
        for method in required_methods:
            if not hasattr(orchestrator, method):
                print(f"❌ FAIL: Orchestrator missing method: {method}")
                return False

    print("✅ PASS: get_orchestrator returns IOrchestratorAgent for all modes")
    print(f"   Tested modes: {modes}")
    print(f"   Protocol methods verified: {required_methods}")
    return True


def test_tc7_graceful_fallback():
    """
    TC-7: Graceful Fallback

    Verify that providing an unknown mode raises a descriptive ValueError
    rather than a crash.
    """
    print("\n" + "=" * 60)
    print("TC-7: Graceful Fallback")
    print("=" * 60)

    from agentic_core.L3_orchestration.orchestrator_registry import get_orchestrator

    # Test with invalid mode
    invalid_modes = ["invalid", "unknown", "legacy", ""]

    for invalid_mode in invalid_modes:
        try:
            orchestrator = get_orchestrator(invalid_mode)
            print(f"❌ FAIL: get_orchestrator('{invalid_mode}') should raise ValueError")
            return False
        except ValueError as e:
            error_msg = str(e)

            # Verify error message is descriptive
            if "Unknown orchestrator mode" not in error_msg:
                print("❌ FAIL: Error message should mention 'Unknown orchestrator mode'")
                print(f"   Got: {error_msg}")
                return False

            if invalid_mode not in error_msg:
                print(f"❌ FAIL: Error message should include the invalid mode '{invalid_mode}'")
                return False

            if "Available modes" not in error_msg:
                print("❌ FAIL: Error message should list available modes")
                return False

    print("✅ PASS: Unknown modes raise descriptive ValueError")
    print(f"   Tested invalid modes: {invalid_modes}")
    print("   Error message format verified")
    return True


def test_tc8_discovery_integration():
    """
    TC-8: Discovery Integration

    Ensure the Unified Orchestrator does NOT perform any rglob calls,
    exclusively using ssot_discovery.
    """
    print("\n" + "=" * 60)
    print("TC-8: Discovery Integration")
    print("=" * 60)

    # Read the OrchestratorAgent source code
    unified_path = PROJECT_ROOT / "agentic_core" / "L3_orchestration" / "OrchestratorAgent.py"

    if not unified_path.exists():
        print(f"❌ FAIL: OrchestratorAgent.py not found at {unified_path}")
        return False

    source_code = unified_path.read_text(encoding="utf-8")

    # Parse AST to find all method calls
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"❌ FAIL: Syntax error in OrchestratorAgent.py: {e}")
        return False

    # Check for rglob or glob calls
    rglob_calls = []
    glob_calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for .rglob() or .glob() method calls
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "rglob":
                    rglob_calls.append(ast.get_source_segment(source_code, node) or "rglob call")
                elif node.func.attr == "glob":
                    glob_calls.append(ast.get_source_segment(source_code, node) or "glob call")

    if rglob_calls:
        print("❌ FAIL: OrchestratorAgent contains rglob calls:")
        for call in rglob_calls:
            print(f"   - {call}")
        return False

    if glob_calls:
        print("❌ FAIL: OrchestratorAgent contains glob calls:")
        for call in glob_calls:
            print(f"   - {call}")
        return False

    # Verify ssot_discovery is imported
    if "ssot_discovery" not in source_code:
        print("❌ FAIL: OrchestratorAgent should import ssot_discovery")
        return False

    # Verify get_agent_files or get_python_files is used
    if "get_agent_files" not in source_code and "get_python_files" not in source_code:
        print("❌ FAIL: OrchestratorAgent should use get_agent_files or get_python_files")
        return False

    print("✅ PASS: OrchestratorAgent uses ssot_discovery exclusively")
    print("   - No rglob calls found")
    print("   - No glob calls found")
    print("   - ssot_discovery imported")
    print("   - get_agent_files/get_python_files used")
    return True


def test_deprecation_warnings():
    """
    Bonus Test: Verify deprecation warnings are emitted for legacy classes.
    """
    print("\n" + "=" * 60)
    print("BONUS: Deprecation Warnings")
    print("=" * 60)

    from agentic_core.L3_orchestration.orchestrator_registry import (
        ConsolidatedOrchestratorAgent,
        HealingOrchestratorAgent,
        SSOTOrchestratorAgent,
    )

    legacy_classes = [
        ("SSOTOrchestratorAgent", SSOTOrchestratorAgent),
        ("HealingOrchestratorAgent", HealingOrchestratorAgent),
        ("ConsolidatedOrchestratorAgent", ConsolidatedOrchestratorAgent),
    ]

    for class_name, cls in legacy_classes:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            instance = cls()

            if len(w) == 0:
                print(f"❌ FAIL: {class_name} should emit DeprecationWarning")
                return False

            if not issubclass(w[-1].category, DeprecationWarning):
                print(f"❌ FAIL: {class_name} should emit DeprecationWarning, got {w[-1].category}")
                return False

            if "deprecated" not in str(w[-1].message).lower():
                print("❌ FAIL: Warning message should mention 'deprecated'")
                return False

    print("✅ PASS: All legacy classes emit DeprecationWarning")
    print(f"   Tested: {[c[0] for c in legacy_classes]}")
    return True


def main():
    """Run all Phase 2 Zero-Loss test cases."""
    print("\n" + "=" * 70)
    print("PHASE 2 ZERO-LOSS VERIFICATION TEST SUITE")
    print("=" * 70)
    print(f"Project Root: {PROJECT_ROOT}")

    tests = [
        ("TC-5: Mode Parity", test_tc5_mode_parity),
        ("TC-6: Registry Resolution", test_tc6_registry_resolution),
        ("TC-7: Graceful Fallback", test_tc7_graceful_fallback),
        ("TC-8: Discovery Integration", test_tc8_discovery_integration),
        ("BONUS: Deprecation Warnings", test_deprecation_warnings),
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

    # Core tests (TC-5 to TC-8)
    core_tests = results[:4]
    core_passed = sum(1 for _, passed in core_tests if passed)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    print(f"CORE TESTS: {core_passed}/4 passed")
    print(f"TOTAL: {passed_count}/{total_count} tests passed")

    if core_passed == 4:
        print("✅ 100% PASS - All Phase 2 Zero-Loss tests passed!")
        print("\nPhase 2 Orchestrator Unification is verified and ready for Phase 3.")
        return 0
    else:
        print(f"❌ FAIL - {4 - core_passed} core test(s) failed")
        print("\nDO NOT proceed to Phase 3 until all core tests pass.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
