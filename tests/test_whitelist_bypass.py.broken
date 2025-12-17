#!/usr/bin/env python3
"""
Test the whitelist bypass functionality directly
"""

import sys
from pathlib import Path
from unittest.mock import Mock

from hydrofoil_test_utils import create_hydrofoil_validator_no_whitelist

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


def test_whitelist_bypass():
    """Test if the whitelist bypass works"""

    # print("Testing whitelist bypass...")  # [Security Fix]

    # Create validator with whitelist bypass
    validator = create_hydrofoil_validator_no_whitelist()

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

    # Test with a simple string that would normally be skipped
    test_code = "simple_code_string"

    # print(f"Original code: {repr(test_code)}")  # [Security Fix]

    result = validator.validate(test_code)

    # print(f"Result status: {result['status']}")  # [Security Fix]
    # print(f"Result reasoning: {result.get('reasoning', 'N/A')}")  # [Security Fix]

    if "skipping validation" in result.get('reasoning', ''):
        # print("❌ FAILED: Whitelist bypass didn't work")  # [Security Fix]
    else:
        # print("✅ SUCCESS: Full validation executed")  # [Security Fix]


if __name__ == "__main__":
    test_whitelist_bypass()

