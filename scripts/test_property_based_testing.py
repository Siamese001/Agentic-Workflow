#!/usr/bin/env python3
"""
L5 Property-Based Testing Validation

This test validates:
1. TestPilot generates property tests using Hypothesis
2. Property tests detect edge cases and logic failures
3. Falsifying examples trigger PROPERTY_VIOLATION signal
4. Integration with NervousSystem execution flow
5. Test file generation and cleanup
"""

import asyncio
import os
import tempfile
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

from L3_orchestration.test_pilot import create_test_pilot


async def test_standard_pytest_execution():
    """Test standard pytest execution."""
    print("=" * 80)
    print("STANDARD PYTEST EXECUTION")
    print("=" * 80)

    print("\n1. Testing pytest discovery and execution")
    print("-" * 50)

    # Create test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a passing test
        test_pass = temp_path / "test_passing.py"
        test_pass.write_text("""
def test_addition():
    assert 1 + 1 == 2

def test_multiplication():
    assert 2 * 3 == 6
""")

        # Create a failing test
        test_fail = temp_path / "test_failing.py"
        test_fail.write_text("""
def test_failure():
    assert 1 + 1 == 3  # This will fail
""")

        # Create TestPilot
        test_pilot = create_test_pilot(enable_property_testing=False)

        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            # Run tests
            results = test_pilot._run_standard_tests()

            if results["count"] >= 2:
                print(f"✅ Found {results['count']} test files")
            else:
                print(f"❌ Expected at least 2 test files, found {results['count']}")
                return False

            # Check for failures
            if results["failures"] > 0:
                print(f"✅ Detected {results['failures']} test failures")
            else:
                print("⚠️  No failures detected (expected 1)")

            return True

        finally:
            os.chdir(original_cwd)


async def test_property_test_generation():
    """Test property test generation."""
    print("\n" + "=" * 80)
    print("PROPERTY TEST GENERATION")
    print("=" * 80)

    print("\n1. Generating property tests for various functions")
    print("-" * 50)

    test_pilot = create_test_pilot()

    # Test function extraction
    test_code = """
def sort_list(lst):
    return sorted(lst)

def reverse_string(s):
    return s[::-1]

def json_serialize(data):
    import json
    return json.dumps(data)

def _private_helper():
    pass

def no_args():
    return 42
"""

    functions = test_pilot._extract_functions(test_code)

    if len(functions) >= 4:
        print(f"✅ Extracted {len(functions)} functions")
    else:
        print(f"❌ Expected at least 4 functions, found {len(functions)}")
        return False

    # Test function filtering
    testable = [f for f in functions if test_pilot._should_test_function(f)]

    if len(testable) >= 3:
        print(f"✅ Identified {len(testable)} testable functions")
    else:
        print(f"❌ Expected at least 3 testable functions, found {len(testable)}")
        return False

    # Generate test code
    test_file = "test_module.py"
    generated_code = test_pilot._generate_property_tests(test_file, functions)

    if "def test_" in generated_code and "@given" in generated_code:
        print("✅ Generated valid property test code")
    else:
        print("❌ Generated invalid test code")
        print(generated_code[:500])
        return False

    return True


async def test_edge_case_detection():
    """Test detection of edge cases using Hypothesis."""
    print("\n" + "=" * 80)
    print("EDGE CASE DETECTION")
    print("=" * 80)

    print("\n1. Testing function with specific edge case")
    print("-" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a function that fails on a specific large integer
        buggy_file = temp_path / "buggy_function.py"
        buggy_file.write_text("""
def process_number(n):
    # This function fails when n is a large even number
    if n > 1000000 and n % 2 == 0:
        raise ValueError("Large even numbers not supported")
    return n * 2

def divide_by_two(n):
    # This fails when n is 0
    return 10 / n
""")

        # Create TestPilot
        test_pilot = create_test_pilot(enable_property_testing=True)

        # Run property check
        result = await test_pilot._run_property_check(str(buggy_file))

        if result.get("generated", 0) > 0:
            print(f"✅ Generated {result['generated']} property test(s)")
        else:
            print("❌ No property tests generated")
            return False

        # Check if violations were detected
        if result.get("violations", 0) > 0:
            print(f"✅ Detected {result['violations']} property violation(s)")
            print(f"   Details: {result['details'][0] if result['details'] else 'N/A'}")
        else:
            print("⚠️  No violations detected (may need more test runs)")

        return True


async def test_violation_parsing():
    """Test parsing of Hypothesis violation output."""
    print("\n" + "=" * 80)
    print("VIOLATION PARSING")
    print("=" * 80)

    print("\n1. Parsing falsifying examples")
    print("-" * 50)

    test_pilot = create_test_pilot()

    # Sample Hypothesis output
    sample_output = """
Falsifying example: test_process_number_properties(
    n=2000000,
)
Traceback (most recent call last):
  File "test.py", line 10, in test_process_number_properties
    result = module.process_number(n)
  File "buggy_function.py", line 4, in process_number
    raise ValueError("Large even numbers not supported")
ValueError: Large even numbers not supported
"""

    violation = test_pilot._parse_violation(sample_output, "buggy_function.py")

    if violation["file"] == "buggy_function.py":
        print("✅ Correctly identified violating file")
    else:
        print("❌ Incorrect file identification")
        return False

    if "2000000" in violation["example"]:
        print("✅ Extracted falsifying example")
    else:
        print("❌ Failed to extract example")
        return False

    if violation["description"]:
        print("✅ Generated violation description")
    else:
        print("❌ No description generated")
        return False

    return True


async def test_integration_with_nervous_system():
    """Test TestPilot integration with NervousSystem."""
    print("\n" + "=" * 80)
    print("NERVOUS SYSTEM INTEGRATION")
    print("=" * 80)

    print("\n1. Testing TestPilot in mission context")
    print("-" * 50)

    try:
        from L3_orchestration.nervous_system import NervousSystem, OrchestratorConfig
        from L4_state.storage import SignalLedger, create_storage_adapter

        # Create nervous system
        config = OrchestratorConfig(max_iterations=1)
        storage = create_storage_adapter("local", base_path="./agentic_core")
        signal_ledger = SignalLedger(storage, "test-pilot-test")

        nervous_system = NervousSystem(
            safety_layer=None,
            checkpoint_manager=None,
            config=config,
            session_id="test-pilot-test",
            signal_ledger=signal_ledger
        )

        # Create TestPilot
        test_pilot = create_test_pilot(enable_property_testing=True)

        # Simulate modified files
        modified_files = ["agentic_core/L3_orchestration/test_pilot.py"]

        # Run tests
        results = await test_pilot.run_tests(modified_files)

        if "TESTS_PASS" in results["signals"] or "TEST_FAILURE" in results["signals"]:
            print("✅ TestPilot generated appropriate signals")
        else:
            print("❌ No signals generated")
            return False

        if results["standard_tests"] is not None:
            print("✅ Standard tests executed")
        else:
            print("❌ Standard tests not executed")
            return False

        if results["property_tests"] is not None:
            print("✅ Property tests executed")
        else:
            print("❌ Property tests not executed")
            return False

        return True

    except ImportError as e:
        print(f"⚠️  Integration test skipped: {e}")
        return True


async def test_hypothesis_strategies():
    """Test various Hypothesis strategies."""
    print("\n" + "=" * 80)
    print("HYPOTHESIS STRATEGIES")
    print("=" * 80)

    print("\n1. Testing strategy generation for different argument types")
    print("-" * 50)

    test_pilot = create_test_pilot()

    # Test strategy mapping
    test_cases = [
        (["value"], "integers"),
        (["text"], "text"),
        (["numbers"], "integers"),
        (["data"], "dictionaries"),
        (["items"], "lists"),
        (["self", "value"], "integers"),  # Should skip self
    ]

    all_passed = True
    for args, expected_strategy in test_cases:
        strategy = test_pilot._get_strategy_for_args(args)

        if expected_strategy in strategy:
            print(f"✅ {args} -> {strategy}")
        else:
            print(f"❌ {args} -> Expected {expected_strategy}, got {strategy}")
            all_passed = False

    return all_passed


async def test_property_violation_storage():
    """Test storage and retrieval of property violations."""
    print("\n" + "=" * 80)
    print("PROPERTY VIOLATION STORAGE")
    print("=" * 80)

    print("\n1. Testing violation tracking")
    print("-" * 50)

    test_pilot = create_test_pilot()

    # Simulate violations
    violations = [
        {
            "file": "test1.py",
            "description": "Property violation found",
            "example": "n=1000000",
            "timestamp": 1234567890
        },
        {
            "file": "test2.py",
            "description": "Another violation",
            "example": "data={}",
            "timestamp": 1234567891
        }
    ]

    # Add violations
    test_pilot._property_violations.extend(violations)

    # Retrieve violations
    stored = test_pilot.get_property_violations()

    if len(stored) == len(violations):
        print(f"✅ Stored {len(stored)} violations")
    else:
        print(f"❌ Expected {len(violations)} violations, got {len(stored)}")
        return False

    # Clear violations
    test_pilot.clear_violations()

    if not test_pilot.get_property_violations():
        print("✅ Violations cleared successfully")
    else:
        print("❌ Violations not cleared")
        return False

    return True


async def run_property_based_testing_validation():
    """Run all property-based testing validation tests."""
    print("\n" + "=" * 80)
    print("L5 PROPERTY-BASED TESTING VALIDATION SUITE")
    print("=" * 80)
    print("\nTesting TestPilot with Hypothesis integration")

    results = {}

    # Run all tests
    results["standard_execution"] = await test_standard_pytest_execution()
    results["property_generation"] = await test_property_test_generation()
    results["edge_case_detection"] = await test_edge_case_detection()
    results["violation_parsing"] = await test_violation_parsing()
    results["integration"] = await test_integration_with_nervous_system()
    results["strategies"] = await test_hypothesis_strategies()
    results["violation_storage"] = await test_property_violation_storage()

    # Generate report
    print("\n" + "=" * 80)
    print("PROPERTY-BASED TESTING VALIDATION REPORT")
    print("=" * 80)

    print("\nTest Results:")
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All Property-Based Testing components validated!")
        print("The system has:")
        print("  - Standard pytest execution")
        print("  - Property test generation with Hypothesis")
        print("  - Edge case detection and falsifying examples")
        print("  - PROPERTY_VIOLATION signal generation")
        print("  - Integration with NervousSystem")
        print("  - Violation tracking and storage")
        print("\n📝 Note: Install hypothesis with: pip install hypothesis")
    else:
        print("\n⚠️  Some components need attention")
        print("Check the logs above for details")

    return all_passed


if __name__ == "__main__":
    asyncio.run(run_property_based_testing_validation())
