#!/usr/bin/env python3
"""
Debug test to verify whitelist bypass functionality
"""

import sys
from pathlib import Path
from unittest.mock import Mock

from canon_validator import CanonValidator

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


def test_whitelist_behavior():
    """Test how whitelist behaves with different code patterns"""

    validator = CanonValidator()

    # Mock the LLM to return a simple response
    validator.llm = Mock()
    validator.llm.generate_plan.return_value = {
        "status": "rejected",
        "reasoning": "Test violation"
    }

    # Mock embedding
    validator.embed_fn = Mock(return_value=[0.1] * 768)

    # Mock cache and pinecone
    validator.cache = Mock()
    validator.cache.check = Mock(return_value=None)
    validator.pinecone = Mock()
    validator.pinecone.query = Mock(return_value={'matches': []})
    validator.pinecone.upsert = Mock()

    # Test cases
    test_cases = [
        ("print('hello')", "Should skip - whitelisted"),
        ("custom_function()", "Should validate - not whitelisted"),
        ("def custom_function():\n    pass", "Should skip - no function call"),
        ("x = custom_function()", "Should skip - assignment"),
        ("# comment\ncustom_function()", "Should validate - non-whitelisted call"),
    ]

    for code, description in test_cases:
        # print(f"\nTesting: {description}")  # [Security Fix]
        # print(f"Code: {repr(code)}")  # [Security Fix]

        result = validator.validate(code)
        # print(f"Result: {result['status']}")  # [Security Fix]
        # print(f"Reasoning: {result.get('reasoning', 'N/A')}")  # [Security Fix]

        if "skipping validation" in result.get('reasoning', ''):
            # print("  -> WHITELIST BYPASSED VALIDATION")  # [Security Fix]
        else:
            # print("  -> FULL VALIDATION EXECUTED")  # [Security Fix]


if __name__ == "__main__":
    test_whitelist_behavior()

