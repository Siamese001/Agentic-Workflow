#!/usr/bin/env python3
"""
Run all Canon Validator Engine tests
"""
import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

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

# Now import and run tests

if __name__ == "__main__":
    # Run all canon validator tests
    test_files = [
        "test_canon_validator_functional.py",
        "test_canon_validator_tool_use.py",
        "test_canon_validator_governance.py",
        "test_canon_validator_security.py",
        "test_canon_validator_integration.py"
    ]

    exit_code = pytest.main(test_files + ["-v", "--tb=short"])
    sys.exit(exit_code)

