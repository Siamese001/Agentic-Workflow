#!/usr/bin/env python3
"""
Simple test runner for Canon Validator Engine tests
"""
from unittest.mock import Mock
import sys
from pathlib import Path
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock all external dependencies

sys.modules['connection_manager'] = Mock()
sys.modules['llm_client'] = Mock()
sys.modules['canon_keys'] = Mock()
sys.modules['redisvl.extensions.llmcache'] = Mock()
sys.modules['redisvl.extensions.cache.llm'] = Mock()
sys.modules['mcp_hardening'] = Mock()
sys.modules['core_utils'] = Mock()
sys.modules['mcp11_get_current_time'] = Mock()
sys.modules['mcp11_convert_time'] = Mock()
sys.modules['redis_client'] = Mock()

# Import and run individual test functions


def test_functional_compliance():
    """Run functional compliance tests"""
    print("\n🔬 Running Functional & Compliance Tests (L1/L2)...")

    try:
        # Import after mocking
        from test_canon_validator_functional import TestFunctionalCompliance

        # Create test instance
        test = TestFunctionalCompliance()

        # Run tests manually
        test.mock_validator = test.mock_validator()
        test.test_fc001_standard_violation_detection(test.mock_validator)
        print("  ✅ FC-001: Standard Violation Detection - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_fc002_compliant_code_validation(test.mock_validator)
        print("  ✅ FC-002: Compliant Code Validation - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_fc004_config_override_l1(test.mock_validator)
        print("  ✅ FC-004: Config Override (L1) - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_violation_with_auto_repair(test.mock_validator)
        print("  ✅ Auto-Repair Functionality - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_cache_hit_performance(test.mock_validator)
        print("  ✅ Cache Hit Performance - PASSED")

        return True
    except Exception as e:
        print(f"  ❌ Functional Compliance Test Failed: {e}")
        traceback.print_exc()
        return False


def test_tool_use_llm_logic():
    """Run tool-use & LLM logic tests"""
    print("\n🔧 Running Tool-Use & LLM Logic Tests (L1/L5)...")

    try:
        from test_canon_validator_tool_use import TestToolUseLLMLogic

        test = TestToolUseLLMLogic()

        test.mock_validator = test.mock_validator()
        test.test_tl002_tool_selection_execution(test.mock_validator)
        print("  ✅ TL-002: Tool Selection & Execution - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_llm_response_validation(test.mock_validator)
        print("  ✅ LLM Response Validation - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_tool_argument_sanitization(test.mock_validator)
        print("  ✅ Tool Argument Sanitization - PASSED")

        return True
    except Exception as e:
        print(f"  ❌ Tool-Use & LLM Logic Test Failed: {e}")
        traceback.print_exc()
        return False


def test_governance_resilience():
    """Run governance & resilience tests"""
    print("\n🛡️ Running Governance & Resilience Tests (L3/L4/L5)...")

    try:
        from test_canon_validator_governance import TestGovernanceResilience

        test = TestGovernanceResilience()

        test.mock_validator = test.mock_validator()
        test.test_gr003_temporal_awareness_l4(test.mock_validator)
        print("  ✅ GR-003: Temporal Awareness (L4) - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_state_consistency_l4(test.mock_validator)
        print("  ✅ State Consistency (L4) - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_cost_tracking_enforcement(test.mock_validator)
        print("  ✅ Cost Tracking Enforcement - PASSED")

        return True
    except Exception as e:
        print(f"  ❌ Governance & Resilience Test Failed: {e}")
        traceback.print_exc()
        return False


def test_security_edge_cases():
    """Run security & edge case tests"""
    print("\n🔒 Running Security & Edge Case Tests (L1-L5)...")

    try:
        from test_canon_validator_security import TestSecurityEdgeCases

        test = TestSecurityEdgeCases()

        test.mock_validator = test.mock_validator()
        test.test_se001_self_correction_denial(test.mock_validator)
        print("  ✅ SE-001: Self-Correction Denial - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_se002_tool_argument_injection(test.mock_validator)
        print("  ✅ SE-002: Tool Argument Injection - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_se003_binary_non_code_input(test.mock_validator)
        print("  ✅ SE-003: Binary/Non-Code Input - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_se004_no_change_execution_caching(test.mock_validator)
        print("  ✅ SE-004: No-Change Execution - PASSED")

        test.mock_validator = test.mock_validator()
        test.test_prompt_injection_attempts(test.mock_validator)
        print("  ✅ Prompt Injection Attempts - PASSED")

        return True
    except Exception as e:
        print(f"  ❌ Security & Edge Case Test Failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all test suites"""
    print("="*80)
    print("🧪 CANON VALIDATOR ENGINE TEST SUITE")
    print("="*80)

    all_passed = True

    # Run all test suites
    all_passed &= test_functional_compliance()
    all_passed &= test_tool_use_llm_logic()
    all_passed &= test_governance_resilience()
    all_passed &= test_security_edge_cases()

    # Summary
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n📊 Test Summary:")
        print("  - Functional & Compliance (L1/L2): ✅ PASSED")
        print("  - Tool-Use & LLM Logic (L1/L5): ✅ PASSED")
        print("  - Governance & Resilience (L3/L4/L5): ✅ PASSED")
        print("  - Security & Edge Cases (L1-L5): ✅ PASSED")
        print("\n🎯 Canon Validator Engine is ready for deployment!")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nPlease review the test failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

