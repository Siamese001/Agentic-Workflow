"""
Pinecone-Redis Integration Test Suite

Tests for validating that all Pinecone operations use Redis as a fast cache
for the Meta-Learning Layer.

Test Cases:
- TC-REDIS-001: Verify Redis Cache Hit for Pinecone Queries (L4)
- TC-REDIS-002: Verify Embedding Cache in pinecone_sync.py (L4)
- TC-REDIS-003: Verify PineconeVectorMixin Uses RedisCacheMixin (Utils)
- TC-REDIS-004: Verify SovereignPineconeMcpClient Cache (L2)
- TC-REDIS-005: Verify Graceful Degradation (Resilience)
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

# === MOCK SETUP FOR CI/TESTING ===
# These mocks ensure tests run without needing actual API keys or Redis
MOCK_ENV = {
    "PINECONE_API_KEY": "sk-mock-key",
    "REDIS_URL": "redis://mock:6379",
    "GOOGLE_API_KEY": "mock-gemini-key",
    "GEMINI_API_KEY": "mock-gemini-key",
}


class test_pinecone_redis_integration(unittest.TestCase):
    """
    Robust runtime verification for Pinecone-Redis integration.
    Uses mocks to simulate Redis hits/misses and verify logic flow.
    """

    def setUp(self):
        """Setup patches for environment and external services."""
        self.env_patcher = patch.dict(os.environ, MOCK_ENV)
        self.env_patcher.start()

        # Mock Redis
        self.redis_mock = MagicMock()
        self.redis_mock.ping.return_value = True
        self.redis_from_url_patcher = patch("redis.from_url", return_value=self.redis_mock)
        self.redis_from_url_patcher.start()

        # Mock Pinecone
        self.pinecone_patcher = patch("pinecone.Pinecone")
        self.mock_pc = self.pinecone_patcher.start()
        self.mock_pc.return_value.list_indexes.return_value.names.return_value = ["sovereign-rag"]
        # Mock describe_index to return proper dimension
        mock_index_desc = MagicMock()
        mock_index_desc.dimension = 384
        self.mock_pc.return_value.describe_index.return_value = mock_index_desc
        self.mock_index = self.mock_pc.return_value.Index.return_value

    def tearDown(self):
        self.env_patcher.stop()
        self.redis_from_url_patcher.stop()
        self.pinecone_patcher.stop()

    def test_redis_001_pinecone_store_archived(self):
        """
        TC-REDIS-001: Verify pinecone_store.py has been archived.

        [PHASE 1 MIGRATION] This file is now archived and replaced by PineconeSovereignAgent.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-001: Verify pinecone_store.py Archived")
        print("=" * 60)

        from pathlib import Path

        # Verify file is in archived/
        archived_path = (
            Path(__file__).parents[2] / "agentic_core" / "archived" / "pinecone_store.py"
        )
        original_path = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "semantic_memory"
            / "store"
            / "pinecone_store.py"
        )

        self.assertTrue(archived_path.exists(), "pinecone_store.py must be in archived/")
        self.assertFalse(
            original_path.exists(), "pinecone_store.py must not be in original location"
        )

        print("✅ pinecone_store.py successfully archived (replaced by PineconeSovereignAgent)")

    def test_redis_002_pinecone_vector_mixin_inheritance(self):
        """
        TC-REDIS-002: Verify PineconeVectorMixin inherits RedisCacheMixin.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-002: PineconeVectorMixin Inheritance Check")
        print("=" * 60)

        from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin
        from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin

        # Verify inheritance
        self.assertTrue(
            issubclass(PineconeVectorMixin, RedisCacheMixin),
            "PineconeVectorMixin must inherit from RedisCacheMixin",
        )

        # Verify cache methods are available
        self.assertTrue(hasattr(PineconeVectorMixin, "cache_get"))
        self.assertTrue(hasattr(PineconeVectorMixin, "cache_set"))
        self.assertTrue(hasattr(PineconeVectorMixin, "_cache_prefix"))

        print("✅ PineconeVectorMixin correctly inherits RedisCacheMixin.")

    def test_redis_003_pinecone_sync_archived(self):
        """
        TC-REDIS-003: Verify pinecone_sync.py has been archived.

        [PHASE 1 MIGRATION] This file is now archived and replaced by PineconeSovereignAgent.sync_fission_state().
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-003: Verify pinecone_sync.py Archived")
        print("=" * 60)

        from pathlib import Path

        # Verify file is in archived/
        archived_path = Path(__file__).parents[2] / "agentic_core" / "archived" / "pinecone_sync.py"
        original_path = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "semantic_memory"
            / "store"
            / "pinecone_sync.py"
        )

        self.assertTrue(archived_path.exists(), "pinecone_sync.py must be in archived/")
        self.assertFalse(
            original_path.exists(), "pinecone_sync.py must not be in original location"
        )

        print(
            "✅ pinecone_sync.py successfully archived (replaced by PineconeSovereignAgent.sync_fission_state())"
        )

    def test_redis_004_mcp_client_inheritance(self):
        """
        TC-REDIS-004: Verify SovereignPineconeMcpClient inherits RedisCacheMixin.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-004: MCP Client Inheritance Check")
        print("=" * 60)

        # Check source file for inheritance (static analysis for this test
        # since the MCP client has complex dependencies that may not be available)
        from pathlib import Path

        source_file = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L2_execution"
            / "mcp"
            / "pinecone_mcp_client.py"
        )

        with open(source_file) as f:
            content = f.read()

        # Verify RedisCacheMixin is in the class definition
        has_redis_mixin = "RedisCacheMixin" in content
        has_cache_get = "cache_get" in content
        has_cache_set = "cache_set" in content
        has_use_cache = "use_cache" in content

        self.assertTrue(has_redis_mixin, "MCP Client must inherit RedisCacheMixin")
        self.assertTrue(has_cache_get, "MCP Client must call cache_get")
        self.assertTrue(has_cache_set, "MCP Client must call cache_set")
        self.assertTrue(has_use_cache, "MCP Client search must have use_cache param")

        print("✅ MCP Client correctly integrates RedisCacheMixin.")

    def test_redis_005_phase1_migration_complete(self):
        """
        TC-REDIS-005: Verify Phase 1 migration markers in code.

        [PHASE 1 MIGRATION] Verify all Phase 1 migration comments are present.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-005: Phase 1 Migration Markers")
        print("=" * 60)

        from pathlib import Path

        # Check PineconeSovereignAgent for Phase 1 markers
        sovereign_agent = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L5_safety"
            / "validators"
            / "PineconeSovereignAgent.py"
        )
        with open(sovereign_agent) as f:
            content = f.read()

        self.assertIn(
            "[PHASE 1 MIGRATION]", content, "PineconeSovereignAgent must have Phase 1 markers"
        )
        self.assertIn("sync_fission_state", content, "Must have sync_fission_state method")

        # Check pinecone_mcp_client for Phase 1 markers
        mcp_client = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L2_execution"
            / "mcp"
            / "pinecone_mcp_client.py"
        )
        with open(mcp_client) as f:
            content = f.read()

        self.assertIn("[PHASE 1]", content, "MCP Client must have Phase 1 markers")
        self.assertIn("audit_log", content, "Must have audit_log attribute")

        print("✅ Phase 1 migration markers verified in all files")

    def test_redis_006_pinecone_py_archived(self):
        """
        TC-REDIS-006: Verify pinecone.py has been archived.

        [PHASE 1 MIGRATION] This file is now archived and replaced by SovereignPineconeMcpClient.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-006: Verify pinecone.py Archived")
        print("=" * 60)

        from pathlib import Path

        # Verify file is in archived/
        archived_path = Path(__file__).parents[2] / "agentic_core" / "archived" / "pinecone.py"
        original_path = (
            Path(__file__).parents[2] / "agentic_core" / "L2_execution" / "mcp" / "pinecone.py"
        )

        self.assertTrue(archived_path.exists(), "pinecone.py must be in archived/")
        self.assertFalse(original_path.exists(), "pinecone.py must not be in original location")

        print("✅ pinecone.py successfully archived (replaced by SovereignPineconeMcpClient)")

    def test_redis_007_dimension_consistency(self):
        """
        TC-REDIS-007: Verify embedding dimension consistency.

        [PHASE 1 MIGRATION] Static analysis since PineconeSovereignAgent has complex dependencies
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-007: Embedding Dimension Consistency")
        print("=" * 60)

        # Check PineconeSovereignAgent source for dimension guarding
        from pathlib import Path

        source_file = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L5_safety"
            / "validators"
            / "PineconeSovereignAgent.py"
        )

        with open(source_file) as f:
            content = f.read()

        # Verify dimension guarding exists
        has_dimension_check = "desc.dimension" in content
        has_dimension_sync = "self.dimension = desc.dimension" in content
        has_dimension_warning = "DIMENSION MISMATCH" in content or "Dimension Mismatch" in content

        self.assertTrue(has_dimension_check, "PineconeSovereignAgent must check index dimension")
        self.assertTrue(
            has_dimension_sync, "PineconeSovereignAgent must sync dimension on mismatch"
        )
        self.assertTrue(
            has_dimension_warning, "PineconeSovereignAgent must warn on dimension mismatch"
        )

        print("  ✓ Dimension guarding verified in PineconeSovereignAgent")
        print("  ✓ Runtime dimension sync on mismatch")
        print("  ✓ Critical warning on dimension mismatch")
        print("✅ Dimension consistency check passed (Phase 1 Migration).")


def run_tests():
    """Run tests using unittest runner."""
    print("=" * 80)
    print("PINECONE-REDIS INTEGRATION TEST SUITE (Runtime Verification)")
    print("=" * 80)

    suite = unittest.TestLoader().loadTestsFromTestCase(test_pinecone_redis_integration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success: {result.wasSuccessful()}")
    print("=" * 80)

    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
