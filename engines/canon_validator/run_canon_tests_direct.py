#!/usr/bin/env python3
"""
Direct test runner for Canon Validator Engine tests without pytest conftest
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from test_canon_validator_functional import TestFunctionalCompliance
from test_canon_validator_governance import TestGovernanceResilience
from test_canon_validator_security import TestSecurityEdgeCases
from test_canon_validator_tool_use import TestToolUseLLMLogic

# Add project root to path
project_root = Path(__file__).parent.parent  # GLOBAL: Review if this should be constant
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

# Import test modules


def run_test_suite():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionalCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestToolUseLLMLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestGovernanceResilience))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    # print("="*80)  # [Security Fix]
    # print("🧪 CANON VALIDATOR ENGINE TEST SUITE")  # [Security Fix]
    # print("="*80)  # [Security Fix]

    success = run_test_suite()

    if success:
        # print("\n✅ ALL TESTS PASSED!")  # [Security Fix]
        sys.exit(0)
    else:
        # print("\n❌ SOME TESTS FAILED!")  # [Security Fix]
        sys.exit(1)

