"""
Phase 3 Consolidation Test Suite

Tests for validating the MCP Gateway and SemanticCache consolidation.

Test Cases:
- TC-MCP-001: Verify SovereignMCPGateway operation_stats
- TC-MCP-002: Verify MCPOperationMixin delegates to gateway
- TC-CACHE-001: Verify canonical SemanticCacheManager has Phase 3 marker
- TC-CACHE-002: Verify L5 SemanticCacheManager raises ImportError
- TC-CACHE-003: Verify SemanticCacheMixin delegates to L4
- TC-MCP-006: Verify all legacy clients raise ImportError
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))


class TestPhase3Consolidation(unittest.TestCase):
    """
    Test suite for Phase 3 consolidation: MCP Gateway + SemanticCache unification.
    """

    def test_mcp_001_gateway_operation_stats(self):
        """
        TC-MCP-001: Verify SovereignMCPGateway has operation_stats.
        """
        print("\n" + "=" * 60)
        print("TC-MCP-001: SovereignMCPGateway operation_stats")
        print("=" * 60)

        # Check source file for operation_stats
        source_file = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L2_execution"
            / "mcp"
            / "SovereignMCPGateway.py"
        )

        with open(source_file) as f:
            content = f.read()

        # Verify operation_stats exists
        has_operation_stats = "operation_stats" in content
        has_audit_method = (
            "def _audit(self, operation: str, success: bool, latency_ms: float)" in content
        )
        has_phase3_marker = "[PHASE 3 MIGRATION]" in content or "[PHASE 3]" in content
        has_llm_route = "async def llm_route" in content
        has_kg_query = "async def kg_query" in content
        has_archive_op = "async def archive_operation" in content

        self.assertTrue(has_operation_stats, "SovereignMCPGateway must have operation_stats")
        self.assertTrue(has_audit_method, "SovereignMCPGateway must have _audit method")
        self.assertTrue(has_phase3_marker, "Must have PHASE 3 migration marker")
        self.assertTrue(has_llm_route, "Must have llm_route method")
        self.assertTrue(has_kg_query, "Must have kg_query method")
        self.assertTrue(has_archive_op, "Must have archive_operation method")

        print("✅ SovereignMCPGateway has all required components")

    def test_mcp_002_mixin_delegates_to_gateway(self):
        """
        TC-MCP-002: Verify MCPOperationMixin delegates to gateway.
        """
        print("\n" + "=" * 60)
        print("TC-MCP-002: MCPOperationMixin Gateway Delegation")
        print("=" * 60)

        source_file = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L2_execution"
            / "mcp"
            / "mcp_operation_mixin.py"
        )

        with open(source_file) as f:
            content = f.read()

        # Verify mixin delegates to gateway
        has_gateway_import = (
            "from agentic_core.L2_execution.mcp.SovereignMCPGateway import get_mcp_gateway"
            in content
        )
        has_mcp_llm_route = "async def mcp_llm_route" in content
        has_mcp_kg_query = "async def mcp_kg_query" in content
        has_mcp_archive_op = "async def mcp_archive_op" in content
        has_phase3_marker = "[PHASE 3 MIGRATION]" in content

        self.assertTrue(has_gateway_import, "Mixin must import get_mcp_gateway")
        self.assertTrue(has_mcp_llm_route, "Mixin must have mcp_llm_route")
        self.assertTrue(has_mcp_kg_query, "Mixin must have mcp_kg_query")
        self.assertTrue(has_mcp_archive_op, "Mixin must have mcp_archive_op")
        self.assertTrue(has_phase3_marker, "Must have PHASE 3 migration marker")

        print("✅ MCPOperationMixin correctly delegates to SovereignMCPGateway")

    def test_cache_001_canonical_manager_phase3_marker(self):
        """
        TC-CACHE-001: Verify canonical SemanticCacheManager has Phase 3 marker.
        """
        print("\n" + "=" * 60)
        print("TC-CACHE-001: Canonical SemanticCacheManager Phase 3 Marker")
        print("=" * 60)

        source_file = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L4_state"
            / "memory"
            / "SemanticCacheManager.py"
        )

        with open(source_file) as f:
            content = f.read()

        # Verify Phase 3 marker exists
        has_phase3_marker = "[PHASE 3 MIGRATION]" in content
        has_canonical_note = (
            "ONLY SemanticCacheManager" in content or "canonical" in content.lower()
        )

        self.assertTrue(
            has_phase3_marker, "Canonical SemanticCacheManager must have PHASE 3 marker"
        )
        self.assertTrue(has_canonical_note, "Must indicate this is the canonical implementation")

        print("✅ Canonical SemanticCacheManager has Phase 3 migration marker")

    def test_cache_002_l5_guardrails_deprecated(self):
        """
        TC-CACHE-002: Verify L5/guardrails/SemanticCacheManager is archived.

        [PHASE 3 MIGRATION] This file has been moved to archived/.
        """
        print("\n" + "=" * 60)
        print("TC-CACHE-002: L5 Guardrails SemanticCacheManager Deprecation")
        print("=" * 60)

        from pathlib import Path

        # Verify file is in archives/
        archived_path = (
            Path(__file__).parents[2] / "archives" / "L5_guardrails_SemanticCacheManager.py"
        )
        original_path = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L5_safety"
            / "guardrails"
            / "SemanticCacheManager.py"
        )

        self.assertTrue(archived_path.exists(), "SemanticCacheManager must be in archives/")
        self.assertFalse(
            original_path.exists(), "SemanticCacheManager must not be in original location"
        )

        print("✅ L5/guardrails/SemanticCacheManager correctly archived")

    def test_cache_003_mixin_delegates_to_l4(self):
        """
        TC-CACHE-003: Verify SemanticCacheMixin delegates to L4.
        """
        print("\n" + "=" * 60)
        print("TC-CACHE-003: SemanticCacheMixin L4 Delegation")
        print("=" * 60)

        source_file = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L4_state"
            / "memory"
            / "semantic_cache_mixin.py"
        )

        with open(source_file) as f:
            content = f.read()

        # Verify mixin delegates to L4
        has_l4_import = (
            "from agentic_core.L4_state.memory.SemanticCacheManager import SemanticCacheManager"
            in content
        )
        has_semantic_recall = "async def semantic_recall" in content
        has_semantic_learn = "async def semantic_learn" in content
        has_phase3_marker = "[PHASE 3 MIGRATION]" in content

        self.assertTrue(has_l4_import, "Mixin must import from L4_state")
        self.assertTrue(has_semantic_recall, "Mixin must have semantic_recall")
        self.assertTrue(has_semantic_learn, "Mixin must have semantic_learn")
        self.assertTrue(has_phase3_marker, "Must have PHASE 3 migration marker")

        print("✅ SemanticCacheMixin correctly delegates to L4 canonical implementation")

    def test_mcp_006_legacy_clients_archived(self):
        """
        TC-MCP-006: Verify all legacy MCP clients are fully moved to archives/.
        """
        print("\n" + "=" * 60)
        print("TC-MCP-006: Legacy MCP Clients Full Archival")
        print("=" * 60)

        legacy_files = [
            ("llm_router_mcp_client.py", "L2_execution/mcp"),
            ("archive_client.py", "L2_execution/mcp"),
            ("knowledge_graph_sovereign_graph_client.py", "L2_execution/mcp"),
            ("caching_redis_mcp_client.py", "L2_execution/mcp"),
            ("shared_mcp_client.py", "L2_execution/mcp"),
        ]

        project_root = Path(__file__).parents[2]
        archived_dir = project_root / "archives"

        for filename, subpath in legacy_files:
            # Check file is in archives/
            archived_file = archived_dir / filename
            self.assertTrue(archived_file.exists(), f"{filename} must be in archives/")

            # Check file does NOT exist in original location (no tombstone)
            original_file = project_root / "agentic_core" / subpath / filename
            self.assertFalse(
                original_file.exists(), f"{filename} must be fully deleted from {subpath}"
            )

            print(f"  ✓ {filename} fully archived (no tombstone)")

        # Also check L5 cognition cache
        cognition_cache = archived_dir / "L5_cognition_SemanticCacheManager.py"
        self.assertTrue(cognition_cache.exists(), "L5 cognition cache must be archived")
        print("  ✓ L5_cognition_SemanticCacheManager.py archived")

        print("✅ All legacy clients fully archived with no tombstones")


def run_tests():
    """Run tests using unittest runner."""
    print("=" * 80)
    print("PHASE 3 CONSOLIDATION TEST SUITE")
    print("=" * 80)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase3Consolidation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success: {result.wasSuccessful()}")

    if result.wasSuccessful():
        print("\n✅ 100% PASS REQUIRED - ACHIEVED")
    else:
        print("\n❌ 100% PASS REQUIRED - NOT ACHIEVED")

    print("=" * 80)

    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
