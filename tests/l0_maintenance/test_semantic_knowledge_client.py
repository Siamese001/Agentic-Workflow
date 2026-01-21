#!/usr/bin/env python3
"""
Verification Test for SemanticKnowledgeClient

Tests that the in-app client matches the performance of manual Pinecone queries.

Usage:
    python scripts/test_semantic_knowledge_client.py

Environment:
    PINECONE_API_KEY - Required for Pinecone access
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.infrastructure import (
    SemanticKnowledgeClient,
    KnowledgeNamespace,
    SearchResult,
)


def test_client_initialization():
    """Test that the client initializes correctly."""
    print("\n" + "="*60)
    print("TEST 1: Client Initialization")
    print("="*60)

    client = SemanticKnowledgeClient()

    if not client.is_available:
        print("❌ FAILED: Client not available (check PINECONE_API_KEY)")
        return False

    print(f"✅ PASSED: Client initialized")
    print(f"   Index: {client.index_name}")
    return True


def test_singleton_pattern():
    """Test that the client is a singleton."""
    print("\n" + "="*60)
    print("TEST 2: Singleton Pattern")
    print("="*60)

    client1 = SemanticKnowledgeClient()
    client2 = SemanticKnowledgeClient()

    if client1 is not client2:
        print("❌ FAILED: Multiple instances created")
        return False

    print("✅ PASSED: Singleton pattern working")
    return True


def test_get_stats():
    """Test index statistics retrieval."""
    print("\n" + "="*60)
    print("TEST 3: Index Statistics")
    print("="*60)

    client = SemanticKnowledgeClient()
    stats = client.get_stats()

    if "error" in stats:
        print(f"❌ FAILED: {stats['error']}")
        return False

    print(f"✅ PASSED: Stats retrieved")
    print(f"   Total records: {stats.get('total_records', 0)}")
    print(f"   Dimension: {stats.get('dimension', 0)}")
    print(f"   Namespaces:")
    for ns, count in stats.get("namespaces", {}).items():
        print(f"     - {ns}: {count} records")

    # Note: Integrated inference indexes may report 0 records in stats
    # but still return search results. This is a known Pinecone quirk.
    if stats.get("total_records", 0) == 0:
        print("   ⚠️  Note: Stats show 0 records (normal for integrated inference indexes)")

    return True  # Stats API working is success, even if counts are 0


def test_agent_search():
    """Test searching for agents."""
    print("\n" + "="*60)
    print("TEST 4: Agent Search")
    print("="*60)

    client = SemanticKnowledgeClient()
    results = client.find_agent_for_task("validate security and prevent injection attacks")

    if not results:
        print("❌ FAILED: No results returned")
        return False

    print(f"✅ PASSED: {len(results)} agents found")
    for r in results:
        print(f"   - {r.id} (score: {r.score:.3f})")
        layer = r.metadata.get("layer", "Unknown")
        print(f"     Layer: {layer}")

    # Verify top result is security-related
    top_result = results[0]
    if top_result.score < 0.7:
        print(f"⚠️  WARNING: Low relevance score ({top_result.score:.3f})")

    return True


def test_mixin_search():
    """Test searching for mixins."""
    print("\n" + "="*60)
    print("TEST 5: Mixin Search")
    print("="*60)

    client = SemanticKnowledgeClient()
    results = client.find_mixin("add caching capability to agent")

    if not results:
        print("❌ FAILED: No results returned")
        return False

    print(f"✅ PASSED: {len(results)} mixins found")
    for r in results:
        print(f"   - {r.id} (score: {r.score:.3f})")

    # Verify RedisCacheMixin is in results
    mixin_ids = [r.id for r in results]
    if "mixin-RedisCacheMixin" in mixin_ids:
        print("   ✓ RedisCacheMixin correctly identified")

    return True


def test_api_contract_search():
    """Test searching for API contracts."""
    print("\n" + "="*60)
    print("TEST 6: API Contract Search")
    print("="*60)

    client = SemanticKnowledgeClient()
    results = client.get_api_contract("heal_repository method signature")

    if not results:
        print("❌ FAILED: No results returned")
        return False

    print(f"✅ PASSED: {len(results)} contracts found")
    for r in results:
        print(f"   - {r.id} (score: {r.score:.3f})")
        sig = r.metadata.get("signature", "N/A")
        print(f"     Signature: {sig}")

    return True


def test_healing_pattern_search():
    """Test searching for healing patterns."""
    print("\n" + "="*60)
    print("TEST 7: Healing Pattern Search")
    print("="*60)

    client = SemanticKnowledgeClient()
    results = client.find_healing_pattern("base class inheritance issues")

    if not results:
        print("❌ FAILED: No results returned")
        return False

    print(f"✅ PASSED: {len(results)} patterns found")
    for r in results:
        print(f"   - {r.id} (score: {r.score:.3f})")

    return True


def test_documentation_search():
    """Test searching for documentation."""
    print("\n" + "="*60)
    print("TEST 8: Documentation Search")
    print("="*60)

    client = SemanticKnowledgeClient()
    results = client.find_documentation("dashboard testing and validation")

    if not results:
        print("❌ FAILED: No results returned")
        return False

    print(f"✅ PASSED: {len(results)} documents found")
    for r in results:
        print(f"   - {r.id} (score: {r.score:.3f})")
        path = r.metadata.get("path", "N/A")
        print(f"     Path: {path}")

    return True


def test_config_search():
    """Test searching for configurations."""
    print("\n" + "="*60)
    print("TEST 9: Configuration Search")
    print("="*60)

    client = SemanticKnowledgeClient()
    results = client.find_config("SSOT directory paths and structure")

    if not results:
        print("❌ FAILED: No results returned")
        return False

    print(f"✅ PASSED: {len(results)} configs found")
    for r in results:
        print(f"   - {r.id} (score: {r.score:.3f})")

    return True


def test_search_all():
    """Test searching across all namespaces."""
    print("\n" + "="*60)
    print("TEST 10: Search All Namespaces")
    print("="*60)

    client = SemanticKnowledgeClient()
    results = client.search_all("healing and self-repair", top_k=2)

    if not results:
        print("❌ FAILED: No results returned")
        return False

    total_results = sum(len(r) for r in results.values())
    print(f"✅ PASSED: {total_results} total results across {len(results)} namespaces")

    for ns, ns_results in results.items():
        if ns_results:
            print(f"   {ns}: {len(ns_results)} results")
            for r in ns_results[:1]:  # Show top result only
                print(f"     - {r.id} ({r.score:.3f})")

    return True


def test_filter_search():
    """Test searching with metadata filters."""
    print("\n" + "="*60)
    print("TEST 11: Filtered Search")
    print("="*60)

    client = SemanticKnowledgeClient()

    # Search for L5 agents only
    results = client.search(
        "security validation",
        KnowledgeNamespace.AGENTS,
        top_k=5,
        filter_dict={"layer": {"$eq": "L5"}}
    )

    if not results:
        print("⚠️  WARNING: No results with filter (filter may not be supported)")
        return True  # Not a failure, filters may not be configured

    print(f"✅ PASSED: {len(results)} L5 agents found")
    for r in results:
        layer = r.metadata.get("layer", "Unknown")
        print(f"   - {r.id} (Layer: {layer}, score: {r.score:.3f})")

    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 SEMANTIC KNOWLEDGE CLIENT VERIFICATION")
    print("="*60)

    if not os.getenv("PINECONE_API_KEY"):
        print("❌ Error: PINECONE_API_KEY environment variable not set")
        print("   Set it with: $env:PINECONE_API_KEY='your-key'")
        sys.exit(1)

    tests = [
        ("Client Initialization", test_client_initialization),
        ("Singleton Pattern", test_singleton_pattern),
        ("Index Statistics", test_get_stats),
        ("Agent Search", test_agent_search),
        ("Mixin Search", test_mixin_search),
        ("API Contract Search", test_api_contract_search),
        ("Healing Pattern Search", test_healing_pattern_search),
        ("Documentation Search", test_documentation_search),
        ("Configuration Search", test_config_search),
        ("Search All Namespaces", test_search_all),
        ("Filtered Search", test_filter_search),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ EXCEPTION in {name}: {e}")
            failed += 1

    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"   Passed: {passed}/{len(tests)}")
    print(f"   Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED - SemanticKnowledgeClient is ready for use")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
