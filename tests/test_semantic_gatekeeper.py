#!/usr/bin/env python3
"""
Test script for Semantic Gatekeeper and Hybrid Semantic Cache

This script tests:
1. Redis connection and index creation
2. Vector embedding generation
3. Pattern storage and retrieval
4. L5 Safety Protocol enforcement
"""

import sys
import time

from core.semantic_gatekeeper import SemanticGatekeeper


def test_redis_connection():
    """Test basic Redis connectivity."""
    # print("🔌 Testing Redis connection...")  # [Security Fix]

    try:
        gatekeeper = SemanticGatekeeper()
        # print("✅ Redis connection successful")  # [Security Fix]
        return gatekeeper
    except Exception as e:
pass
pass
pass
# print(f"❌ Redis connection failed: {e}")  # [Security Fix]
        return None


def test_pattern_storage(gatekeeper):
    """Test storing and retrieving patterns."""
    # print("\n📝 Testing pattern storage...")  # [Security Fix]

    # Test safe pattern
    safe_action = "Format code with autopep8"
    safe_code = "def hello():\n    print('Hello World')"

    entry_id = gatekeeper.record_pattern(
        action=safe_action,
        code=safe_code,
        agent_name="StructuralLinter",
        pattern_type="format",
        files_touched=3,
        success=True
    )

    # print(f"✅ Stored safe pattern: {entry_id}")  # [Security Fix]

    # Test dangerous pattern (failure)
    dangerous_action = "Encapsulate all globals across entire codebase"
    dangerous_code = "GLOBAL_VAR = 'dangerous'"

    entry_id = gatekeeper.record_pattern(
        action=dangerous_action,
        code=dangerous_code,
        agent_name="ArchitecturalRefactorAgent",
        pattern_type="refactor",
        files_touched=686,
        success=False
    )

    # print(f"✅ Stored dangerous pattern: {entry_id}")  # [Security Fix]

    return safe_action, dangerous_action


def test_safety_gate(gatekeeper, safe_action, dangerous_action):
    """Test the safety gating functionality."""
    # print("\n🛡️ Testing L5 Safety Protocol...")  # [Security Fix]

    # Test safe action
    # print(f"Testing safe action: {safe_action}")  # [Security Fix]
    is_safe = gatekeeper.consult_canon(safe_action)
    # print(f"✅ Safe action result: {'ALLOWED' if is_safe else 'BLOCKED'}")  # [Security Fix]

    # Test dangerous action
    # print(f"Testing dangerous action: {dangerous_action}")  # [Security Fix]
    is_safe = gatekeeper.consult_canon(dangerous_action)
    # print(f"✅ Dangerous action result: {'ALLOWED' if is_safe else 'BLOCKED'}")  # [Security Fix]

    # Test new dangerous action
    new_dangerous = "Refactor 100+ files in single operation"
    # print(f"Testing new dangerous action: {new_dangerous}")  # [Security Fix]
    is_safe = gatekeeper.consult_canon(new_dangerous)
    # print(  # [Security Fix]
        f"✅ New dangerous action result: {'ALLOWED' if is_safe else 'BLOCKED'}")


def test_vector_search(gatekeeper):
    """Test vector similarity search."""
    # print("\n🔍 Testing vector similarity search...")  # [Security Fix]

    # Search for similar patterns
    query = "Format Python code"
    results = gatekeeper._search_similar_patterns(
        gatekeeper.embed_action(query),
        threshold = 0.5,
        max_results = 5
    )

    # print(f"✅ Found {results.total_found} similar patterns")  # [Security Fix]
    # print(f"   Safe patterns: {results.safe_count}")  # [Security Fix]
    # print(f"   Blocked patterns: {results.blocked_count}")  # [Security Fix]
    # print(f"   Query time: {results.query_time_ms:.2f}ms")  # [Security Fix]


def test_safety_stats(gatekeeper):
    """Test safety statistics retrieval."""
    # print("\n📊 Testing safety statistics...")  # [Security Fix]

    stats = gatekeeper.get_safety_stats()

    if "error" not in stats:
        # print(f"✅ Total patterns: {stats['total_patterns']}")  # [Security Fix]
        # print(f"   Validated: {stats['validated']}")  # [Security Fix]
        # print(f"   Failed: {stats['failed']}")  # [Security Fix]
        # print(f"   Blocked: {stats['blocked']}")  # [Security Fix]
        # print(f"   Safety ratio: {stats['safety_ratio']:.2%}")  # [Security Fix]
    else:
        # print(f"❌ Error getting stats: {stats['error']}")  # [Security Fix]


def main():
    """Run all tests."""
    # print("🚀 Starting Semantic Gatekeeper Tests\n")  # [Security Fix]

    # Test Redis connection
    gatekeeper = test_redis_connection()
    if not gatekeeper:
        # print("\n❌ Cannot proceed without Redis connection")  # [Security Fix]
        sys.exit(1)

    # Test pattern storage
    safe_action, dangerous_action = test_pattern_storage(gatekeeper)

    # Give Redis a moment to index
    time.sleep(1)

    # Test safety gating
    test_safety_gate(gatekeeper, safe_action, dangerous_action)

    # Test vector search
    test_vector_search(gatekeeper)

    # Test statistics
    test_safety_stats(gatekeeper)

    # print("\n✅ All tests completed successfully!")  # [Security Fix]
    # print("\n📋 Summary:")  # [Security Fix]
    # print("   - Redis Stack is running and accessible")  # [Security Fix]
    # print("   - Vector index created successfully")  # [Security Fix]
    # print("   - Patterns stored with safety metadata")  # [Security Fix]
    # print("   - L5 Safety Protocol is enforced")  # [Security Fix]
    # print("   - Semantic search is functional")  # [Security Fix]


if __name__ == "__main__":
    main()

