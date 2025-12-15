#!/usr/bin/env python3
"""
🧭 Hydrofoil Engine Test Utilities

Shared utilities for all Hydrofoil audit tests
"""

from canon_validator import CanonValidator
import sys
from pathlib import Path
from unittest.mock import Mock

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

# Import validator


def create_hydrofoil_validator():
    """Create a validator with Hydrofoil-configured mocks"""
    validator = CanonValidator()

    # Mock LLM - The Navigation AI
    validator.llm = Mock()
    validator.llm.generate_plan = Mock()

    # Mock embedding - The Depth Sounder
    validator.embed_fn = Mock(return_value=[0.1] * 768)

    # Mock Pinecone - The Navigation Charts
    validator.pinecone = Mock()
    validator.pinecone.query = Mock(return_value={'matches': []})
    validator.pinecone.upsert = Mock()

    # Mock Redis Cache - The Captain's Log
    validator.cache = Mock()
    validator.cache.check = Mock(return_value=None)
    validator.cache.store = Mock()

    # Mock Connection Manager - The Rigging Control
    validator.cm = Mock()
    validator.cm.get_pinecone_index = Mock(return_value=validator.pinecone)
    validator.cm.get_embedding = Mock(return_value=[0.1] * 768)

    return validator


def create_hydrofoil_validator_no_whitelist():
    """
    Create a validator with whitelist check disabled for testing.
    This ensures the full validation pipeline is exercised.
    """
    validator = create_hydrofoil_validator()

    # Store original validate method
    original_validate = validator.validate

    def validate_no_whitelist(content, auto_repair=False):
        # Simply append a non-whitelisted function call to force full validation
        # This bypasses the whitelist check without complex patching
        enhanced_content = content + "\ncustom_test_function()"
        return original_validate(enhanced_content, auto_repair)

    validator.validate = validate_no_whitelist
    return validator


def create_hydrofoil_validator_with_cache():
    """Create a validator with working cache for testing cache behavior"""
    validator = create_hydrofoil_validator()

    # Setup cache that can be manipulated
    cache_data = {}

    def mock_cache_check(key):
        return cache_data.get(key)

    def mock_cache_store(key, value):
        cache_data[key] = value
        return True

    validator.cache.check = Mock(side_effect=mock_cache_check)
    validator.cache.store = Mock(side_effect=mock_cache_store)

    return validator


def assert_layer_result(result, expected_status, layer, message_contains=None):
    """Helper to assert layer-specific test results"""
    assert result["status"] == expected_status, f"{layer}: Expected {expected_status}, got {result['status']}"

    if message_contains:
        assert message_contains in result.get(
            "reasoning", ""), f"{layer}: Message should contain '{message_contains}'"

    return True


def print_layer_result(test_name, layer, status, details=None):
    """Helper to print layer-specific test results"""
    icon = "✅" if status == "PASSED" else "❌"
    print(f"  {icon} {test_name} ({layer}): {status}")
    if details:
        print(f"    📝 {details}")


# Layer-specific constants
LAYER_COMPONENTS = {
    "L1": {"Filesystem", "GitKraken", "Tool Access"},
    "L2": {"Figma", "Design Tokens"},
    "L3": {"Brave Search", "Pinecone", "Cost Governance"},
    "L4": {"Redis", "Time Server", "Atomic Transactions"},
    "L5": {"MEMemory", "Audit Log", "Policy Layer"}
}

# Test code patterns that bypass whitelist
NON_WHITELISTED_PATTERNS = [
    "def custom_function():",
    "def validate_data():",
    "def process_request():",
    "def execute_task():",
    "custom_function()",
    "validate_data()",
    "process_request()",
    "execute_task()"
]

