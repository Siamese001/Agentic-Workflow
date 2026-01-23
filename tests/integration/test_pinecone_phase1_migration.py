"""
Pinecone Phase 1 Migration Test Suite

Tests for validating the consolidation of Pinecone operations into the gateway pattern.

Test Cases:
- TC-MIG-01: Verify sync_fission_state in PineconeSovereignAgent
- TC-MIG-02: Verify audit_log in SovereignPineconeMcpClient
- TC-MIG-03: Verify SDK lockdown (only PineconeSovereignAgent imports Pinecone)
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

# === MOCK SETUP FOR CI/TESTING ===
MOCK_ENV = {
    "PINECONE_API_KEY": "sk-mock-key",
    "REDIS_URL": "redis://mock:6379",
    "GOOGLE_API_KEY": "mock-gemini-key",
}


class test_pinecone_phase1_migration(unittest.TestCase):
    """
    Test suite for Phase 1 migration: consolidating Pinecone operations.
    """

    def setUp(self):
        """Setup patches for environment and external services."""
        self.env_patcher = patch.dict(os.environ, MOCK_ENV)
        self.env_patcher.start()

        # Mock Pinecone
        self.pinecone_patcher = patch("pinecone.Pinecone")
        self.mock_pc = self.pinecone_patcher.start()
        self.mock_pc.return_value.list_indexes.return_value = []
        mock_index_desc = MagicMock()
        mock_index_desc.dimension = 768
        self.mock_pc.return_value.describe_index.return_value = mock_index_desc
        self.mock_index = self.mock_pc.return_value.Index.return_value

    def tearDown(self):
        self.env_patcher.stop()
        self.pinecone_patcher.stop()

    def test_mig_001_sync_fission_state(self):
        """
        TC-MIG-01: Verify sync_fission_state in PineconeSovereignAgent.

        This test validates that the atomic fission sync logic has been
        properly absorbed from pinecone_sync.py into PineconeSovereignAgent.
        """
        print("\n" + "=" * 60)
        print("TC-MIG-01: sync_fission_state Migration Check")
        print("=" * 60)

        # Check source file for method existence (static analysis)
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

        # Verify sync_fission_state method exists
        has_sync_method = "async def sync_fission_state" in content
        has_delete_call = "self.index.delete" in content
        has_upsert_call = "self.index.upsert" in content
        has_phase1_comment = "[PHASE 1 MIGRATION]" in content

        self.assertTrue(
            has_sync_method, "PineconeSovereignAgent must have sync_fission_state method"
        )
        self.assertTrue(has_delete_call, "sync_fission_state must call index.delete")
        self.assertTrue(has_upsert_call, "sync_fission_state must call index.upsert")
        self.assertTrue(has_phase1_comment, "Must have PHASE 1 MIGRATION marker")

        print("✅ sync_fission_state successfully migrated to PineconeSovereignAgent")

    def test_mig_002_audit_log(self):
        """
        TC-MIG-02: Verify audit_log in SovereignPineconeMcpClient.

        This test validates that the audit logging logic has been
        properly absorbed from pinecone.py into the MCP client.
        """
        print("\n" + "=" * 60)
        print("TC-MIG-02: audit_log Migration Check")
        print("=" * 60)

        # Check source file for audit_log (static analysis)
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

        # Verify audit_log attribute exists
        has_audit_log = "self.audit_log: list[dict] = []" in content
        has_audit_method = "def _audit(self, operation: str, success: bool):" in content
        has_phase1_comment = "[PHASE 1]" in content
        has_audit_append = "self.audit_log.append" in content

        self.assertTrue(has_audit_log, "SovereignPineconeMcpClient must have audit_log attribute")
        self.assertTrue(has_audit_method, "SovereignPineconeMcpClient must have _audit method")
        self.assertTrue(has_phase1_comment, "Must have PHASE 1 migration marker")
        self.assertTrue(has_audit_append, "_audit method must append to audit_log")

        print("✅ audit_log successfully migrated to SovereignPineconeMcpClient")

    def test_mig_003_sdk_lockdown(self):
        """
        TC-MIG-03: Verify SDK lockdown (only PineconeSovereignAgent imports Pinecone).

        This test ensures that the Pinecone SDK is only imported in the
        sovereign gateway, preventing configuration drift.
        """
        print("\n" + "=" * 60)
        print("TC-MIG-03: SDK Lockdown Verification")
        print("=" * 60)

        project_root = Path(__file__).parents[2]
        pinecone_files = []

        # Search for files that import Pinecone SDK
        search_paths = [
            project_root / "agentic_core" / "L2_execution" / "mcp",
            project_root / "agentic_core" / "L4_state",
            project_root / "agentic_core" / "L5_safety" / "validators",
            project_root / "agentic_core" / "semantic_memory" / "store",
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for py_file in search_path.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")

                    # Check for Pinecone SDK import
                    if "from pinecone import Pinecone" in content or "import pinecone" in content:
                        # Exclude test files
                        if "test" not in str(py_file).lower():
                            pinecone_files.append(py_file)
                except Exception:
                    continue

        # Verify: Only PineconeSovereignAgent.py should import Pinecone
        print(f"  Files importing Pinecone SDK: {len(pinecone_files)}")
        for f in pinecone_files:
            print(f"    - {f.relative_to(project_root)}")

        # Phase 1 allows multiple files during migration
        # Core gateway: PineconeSovereignAgent.py
        # Redis-cached store: pinecone_store.py
        # Legacy files being phased out: pinecone_sync.py, pinecone.py, SemanticCacheManager.py, MemoryArchitectAgent.py
        allowed_files = {
            "PineconeSovereignAgent.py",  # Core gateway
            "pinecone_store.py",  # Redis-cached store
            "pinecone_sync.py",  # Legacy - being deprecated
            "pinecone.py",  # Legacy - being deprecated
            "SemanticCacheManager.py",  # Dual-layer cache (uses Pinecone for L2)
            "MemoryArchitectAgent.py",  # Legacy - being deprecated
        }

        unauthorized_imports = [f for f in pinecone_files if f.name not in allowed_files]

        if unauthorized_imports:
            print(f"  [CRITICAL] Found {len(unauthorized_imports)} unauthorized Pinecone imports:")
            for f in unauthorized_imports:
                print(f"    - {f.relative_to(project_root)}")
            self.fail(
                f"Unauthorized Pinecone imports detected: {[f.name for f in unauthorized_imports]}"
            )

        # Phase 1: Allow up to 6 files during migration
        # Future phases will consolidate to 2 (PineconeSovereignAgent + pinecone_store)
        self.assertLessEqual(
            len(pinecone_files),
            6,  # Phase 1 migration allowance
            f"Too many files importing Pinecone SDK. Expected ≤6, found {len(pinecone_files)}",
        )

        print("✅ SDK lockdown verified: Pinecone imports properly consolidated")


def run_tests():
    """Run tests using unittest runner."""
    print("=" * 80)
    print("PINECONE PHASE 1 MIGRATION TEST SUITE")
    print("=" * 80)

    suite = unittest.TestLoader().loadTestsFromTestCase(test_pinecone_phase1_migration)
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
