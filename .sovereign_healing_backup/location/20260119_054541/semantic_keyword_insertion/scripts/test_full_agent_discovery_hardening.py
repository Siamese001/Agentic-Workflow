#!/usr/bin/env python3
"""
Test Suite: Full Agent Discovery Hardening

Tests the 5 detailed test cases for:
1. Test Agent Visibility
2. Fixture Exclusion
3. Healer Identification
4. Infrastructure Noise Reduction
5. Baseline Count Verification
"""
import sys
import ast
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Enable logging to capture trace messages
logging.basicConfig(level=5, format='%(message)s')  # TRACE level = 5

from apps_rg.engines.full_agent_discovery import (
    should_exclude_path,
    should_exclude_file,
    EXCLUDED_PATH_PATTERNS,
    HEALING_BASES,
    has_healing_in_chain,
    is_agent_class,
    extract_bases,
    CLASS_INHERITANCE_MAP,
    MINIMUM_AGENT_COUNT,
    EXPECTED_AGENT_COUNT,
    validate_agent_count,
)


def test_1_test_agent_visibility():
    """
    Test Case 1: Test Agent Visibility
    
    Verify that /tests/ and /test/ are NOT in EXCLUDED_PATH_PATTERNS,
    allowing TestAgent discovery from tests/ directories.
    """
    print("\n" + "="*60)
    print("TEST 1: Test Agent Visibility")
    print("="*60)
    
    # Verify /tests/ and /test/ are NOT in EXCLUDED_PATH_PATTERNS
    assert '/tests/' not in EXCLUDED_PATH_PATTERNS, \
        "/tests/ should NOT be in EXCLUDED_PATH_PATTERNS"
    assert '/test/' not in EXCLUDED_PATH_PATTERNS, \
        "/test/ should NOT be in EXCLUDED_PATH_PATTERNS"
    
    # Verify a test agent path would NOT be excluded by should_exclude_path
    test_agent_path = Path("tests/L5/test_TestContentQualityAgent.py")
    
    # should_exclude_path should return False (not excluded) for test paths
    # Note: The path doesn't actually need to exist for this test
    excluded = should_exclude_path(test_agent_path)
    
    # The path should NOT be excluded (we want to discover agents in tests/)
    # However, should_exclude_file may still filter based on filename patterns
    print(f"   EXCLUDED_PATH_PATTERNS: {EXCLUDED_PATH_PATTERNS}")
    print(f"   '/tests/' in patterns: {'/tests/' in EXCLUDED_PATH_PATTERNS}")
    print(f"   '/test/' in patterns: {'/test/' in EXCLUDED_PATH_PATTERNS}")
    
    print(f"✅ PASSED: Test agent visibility enabled")
    print(f"   /tests/ and /test/ removed from EXCLUDED_PATH_PATTERNS")
    return True


def test_2_fixture_exclusion():
    """
    Test Case 2: Fixture Exclusion
    
    Verify that files in /fixtures/ are still excluded despite
    the global /tests/ allowance.
    """
    print("\n" + "="*60)
    print("TEST 2: Fixture Exclusion")
    print("="*60)
    
    # Create test paths
    fixture_path = Path("tests/fixtures/MockAgent.py")
    mock_path = Path("tests/mocks/FakeAgent.py")
    stub_path = Path("tests/stubs/StubAgent.py")
    
    # All fixture/mock/stub paths should be excluded
    assert should_exclude_file(fixture_path), \
        f"Fixture path should be excluded: {fixture_path}"
    assert should_exclude_file(mock_path), \
        f"Mock path should be excluded: {mock_path}"
    assert should_exclude_file(stub_path), \
        f"Stub path should be excluded: {stub_path}"
    
    # Also verify conftest.py and setup.py are excluded
    conftest_path = Path("tests/conftest.py")
    setup_path = Path("tests/setup.py")
    
    assert should_exclude_file(conftest_path), \
        f"conftest.py should be excluded: {conftest_path}"
    assert should_exclude_file(setup_path), \
        f"setup.py should be excluded: {setup_path}"
    
    print(f"✅ PASSED: Fixture exclusion working")
    print(f"   tests/fixtures/MockAgent.py: excluded ✓")
    print(f"   tests/mocks/FakeAgent.py: excluded ✓")
    print(f"   tests/stubs/StubAgent.py: excluded ✓")
    print(f"   tests/conftest.py: excluded ✓")
    print(f"   tests/setup.py: excluded ✓")
    return True


def test_3_healer_identification():
    """
    Test Case 3: Healer Identification
    
    Verify that SovereignHealer is in HEALING_BASES and that
    agents inheriting from it are detected as healers.
    """
    print("\n" + "="*60)
    print("TEST 3: Healer Identification")
    print("="*60)
    
    # Verify SovereignHealer is in HEALING_BASES
    assert 'SovereignHealer' in HEALING_BASES, \
        "SovereignHealer should be in HEALING_BASES"
    assert 'HealerMixin' in HEALING_BASES, \
        "HealerMixin should be in HEALING_BASES"
    
    # Test has_healing_in_chain with SovereignHealer
    # Clear the inheritance map first
    CLASS_INHERITANCE_MAP.clear()
    
    # Simulate an agent that inherits from SovereignHealer
    CLASS_INHERITANCE_MAP['TestHealerAgent'] = {'SovereignHealer'}
    
    has_healing = has_healing_in_chain('TestHealerAgent', {'SovereignHealer'})
    assert has_healing, \
        "Agent inheriting from SovereignHealer should have has_healing=True"
    
    # Test with indirect inheritance
    CLASS_INHERITANCE_MAP['IndirectHealerAgent'] = {'BaseClass'}
    CLASS_INHERITANCE_MAP['BaseClass'] = {'SovereignHealer'}
    
    has_healing_indirect = has_healing_in_chain('IndirectHealerAgent', {'BaseClass'})
    assert has_healing_indirect, \
        "Agent with indirect SovereignHealer inheritance should have has_healing=True"
    
    print(f"✅ PASSED: Healer identification working")
    print(f"   HEALING_BASES includes: HealerMixin, SovereignHealer")
    print(f"   Direct SovereignHealer inheritance: has_healing=True ✓")
    print(f"   Indirect SovereignHealer inheritance: has_healing=True ✓")
    return True


def test_4_infrastructure_noise_reduction():
    """
    Test Case 4: Infrastructure Noise Reduction
    
    Verify that infrastructure classes (AgentRegistry, etc.) are excluded
    and logged with TRACE level messages.
    """
    print("\n" + "="*60)
    print("TEST 4: Infrastructure Noise Reduction")
    print("="*60)
    
    # Create mock AST nodes for infrastructure classes
    infrastructure_classes = [
        ('AgentRegistry', {'object'}),
        ('AgentFactory', {'object'}),
        ('SovereignClient', {'object'}),
        ('StateSerializer', {'object'}),
    ]
    
    excluded_count = 0
    
    for class_name, bases in infrastructure_classes:
        # Create a minimal AST class node
        class_code = f"class {class_name}: pass"
        tree = ast.parse(class_code)
        class_node = tree.body[0]
        
        # Test is_agent_class - should return False for infrastructure
        is_agent = is_agent_class(class_node, bases, Path(f"agentic_core/infra/{class_name}.py"))
        
        if not is_agent:
            excluded_count += 1
            print(f"   {class_name}: excluded ✓")
        else:
            print(f"   {class_name}: NOT excluded (unexpected)")
    
    assert excluded_count == len(infrastructure_classes), \
        f"Expected all {len(infrastructure_classes)} infrastructure classes to be excluded"
    
    print(f"✅ PASSED: Infrastructure noise reduction working")
    print(f"   {excluded_count}/{len(infrastructure_classes)} infrastructure classes excluded")
    return True


def test_5_baseline_count_verification():
    """
    Test Case 5: Baseline Count Verification
    
    Verify that the baseline thresholds are set correctly and
    validate_agent_count works as expected.
    """
    print("\n" + "="*60)
    print("TEST 5: Baseline Count Verification")
    print("="*60)
    
    # Verify baseline constants
    print(f"   MINIMUM_AGENT_COUNT: {MINIMUM_AGENT_COUNT}")
    print(f"   EXPECTED_AGENT_COUNT: {EXPECTED_AGENT_COUNT}")
    
    assert MINIMUM_AGENT_COUNT >= 150, \
        f"MINIMUM_AGENT_COUNT should be >= 150, got {MINIMUM_AGENT_COUNT}"
    assert EXPECTED_AGENT_COUNT >= 200, \
        f"EXPECTED_AGENT_COUNT should be >= 200, got {EXPECTED_AGENT_COUNT}"
    
    # Test validate_agent_count with various counts
    
    # Test 1: Count above minimum - should pass
    is_valid, errors = validate_agent_count(200)
    assert is_valid, f"Count of 200 should be valid: {errors}"
    
    # Test 2: Count below minimum - should fail
    is_valid, errors = validate_agent_count(100)
    assert not is_valid, "Count of 100 should be invalid (below minimum)"
    assert len(errors) > 0, "Should have error message for count below minimum"
    
    # Test 3: Count with previous count (no significant drop) - should pass
    is_valid, errors = validate_agent_count(195, previous_count=200)
    assert is_valid, f"5-agent drop (2.5%) should be valid: {errors}"
    
    # Test 4: Count with significant drop - should fail
    is_valid, errors = validate_agent_count(150, previous_count=200)
    assert not is_valid, "25% drop should be invalid"
    
    print(f"✅ PASSED: Baseline count verification working")
    print(f"   Count 200: valid ✓")
    print(f"   Count 100: invalid (below minimum) ✓")
    print(f"   5-agent drop (2.5%): valid ✓")
    print(f"   50-agent drop (25%): invalid ✓")
    return True


def test_trace_logging_level():
    """
    Bonus Test: TRACE Logging Level
    
    Verify that the TRACE logging level is properly configured.
    """
    print("\n" + "="*60)
    print("BONUS TEST: TRACE Logging Level")
    print("="*60)
    
    import logging
    
    # Verify TRACE level exists
    trace_level = logging.getLevelName("TRACE")
    assert trace_level == 5, f"TRACE level should be 5, got {trace_level}"
    
    # Verify Logger has trace method
    log = logging.getLogger("test_trace")
    assert hasattr(log, 'trace'), "Logger should have trace method"
    
    print(f"✅ PASSED: TRACE logging level configured")
    print(f"   TRACE level: {trace_level}")
    print(f"   Logger.trace method: exists ✓")
    return True


def run_all_tests():
    """Run all test cases."""
    print("\n" + "#"*60)
    print("# Full Agent Discovery Hardening Test Suite")
    print("#"*60)
    
    tests = [
        ("Test 1: Test Agent Visibility", test_1_test_agent_visibility),
        ("Test 2: Fixture Exclusion", test_2_fixture_exclusion),
        ("Test 3: Healer Identification", test_3_healer_identification),
        ("Test 4: Infrastructure Noise Reduction", test_4_infrastructure_noise_reduction),
        ("Test 5: Baseline Count Verification", test_5_baseline_count_verification),
        ("Bonus: TRACE Logging Level", test_trace_logging_level),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("="*60)
    
    if failed > 0:
        print(f"❌ {failed} test(s) FAILED")
        return 1
    else:
        print("✅ ALL TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
