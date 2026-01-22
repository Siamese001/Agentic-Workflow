"""
Redis Phase 2 Migration Test Suite

Tests for validating the Redis consolidation into RedisSovereignAgent gateway pattern.

Test Cases:
- TC-REDIS-MIG-01: Verify operation_stats tracking in RedisSovereignAgent
- TC-REDIS-MIG-02: Verify SDK lockdown (only RedisSovereignAgent imports redis)
- TC-REDIS-MIG-03: Verify redis_cache_tools.py is archived
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))


class TestRedisPhase2Migration(unittest.TestCase):
    """
    Test suite for Phase 2 migration: consolidating Redis operations.
    """

    def test_redis_mig_001_operation_stats(self):
        """
        TC-REDIS-MIG-01: Verify operation_stats tracking in RedisSovereignAgent.

        This test validates that the audit and telemetry logic has been
        properly absorbed into RedisSovereignAgent.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-MIG-01: operation_stats Tracking")
        print("=" * 60)

        # Check source file for operation_stats
        from pathlib import Path

        source_file = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "L5_safety"
            / "validators"
            / "RedisSovereignAgent.py"
        )

        with open(source_file) as f:
            content = f.read()

        # Verify operation_stats exists
        has_operation_stats = "operation_stats" in content
        has_audit_method = "def _audit(self, operation: str, key: str, success: bool)" in content
        has_phase2_marker = "[PHASE 2 MIGRATION]" in content or "[PHASE 2]" in content
        has_total_counter = 'operation_stats["total"]' in content

        self.assertTrue(has_operation_stats, "RedisSovereignAgent must have operation_stats")
        self.assertTrue(has_audit_method, "RedisSovereignAgent must have _audit method")
        self.assertTrue(has_phase2_marker, "Must have PHASE 2 migration marker")
        self.assertTrue(has_total_counter, "_audit must increment total counter")

        print("✅ operation_stats successfully added to RedisSovereignAgent")

    def test_redis_mig_002_sdk_lockdown(self):
        """
        TC-REDIS-MIG-02: Verify SDK lockdown (only RedisSovereignAgent imports redis).

        This test ensures that the Redis SDK is only imported in the
        sovereign gateway, preventing configuration drift.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-MIG-02: SDK Lockdown Verification")
        print("=" * 60)

        project_root = Path(__file__).parents[2]
        redis_files = []

        # Search for files that import Redis SDK
        search_paths = [
            project_root / "agentic_core" / "L2_execution",
            project_root / "agentic_core" / "L4_state",
            project_root / "agentic_core" / "L5_safety" / "validators",
            project_root / "agentic_core" / "utils" / "core_extensions",
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for py_file in search_path.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")

                    # Check for Redis SDK import (not redis_cache_mixin or other wrappers)
                    if "import redis" in content and "from redis" in content:
                        # Exclude test files and archived files
                        if "test" not in str(py_file).lower() and "archived" not in str(py_file):
                            redis_files.append(py_file)
                except Exception:
                    continue

        # Verify: Only RedisSovereignAgent.py should import Redis
        print(f"  Files importing Redis SDK: {len(redis_files)}")
        for f in redis_files:
            print(f"    - {f.relative_to(project_root)}")

        # Phase 2 allows RedisSovereignAgent only
        allowed_files = {"RedisSovereignAgent.py"}
        unauthorized_imports = [f for f in redis_files if f.name not in allowed_files]

        if unauthorized_imports:
            print(f"  [CRITICAL] Found {len(unauthorized_imports)} unauthorized Redis imports:")
            for f in unauthorized_imports:
                print(f"    - {f.relative_to(project_root)}")
            self.fail(
                f"Unauthorized Redis imports detected: {[f.name for f in unauthorized_imports]}"
            )

        # Phase 2: Only RedisSovereignAgent should import redis
        self.assertLessEqual(
            len(redis_files),
            1,  # Only RedisSovereignAgent.py
            f"Too many files importing Redis SDK. Expected ≤1, found {len(redis_files)}",
        )

        print("✅ SDK lockdown verified: Redis imports properly consolidated")

    def test_redis_mig_003_redis_cache_tools_archived(self):
        """
        TC-REDIS-MIG-03: Verify redis_cache_tools.py is archived.

        This test ensures that legacy Redis tools have been archived.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-MIG-03: redis_cache_tools.py Archival")
        print("=" * 60)

        from pathlib import Path

        # Verify file is in archived/
        archived_path = (
            Path(__file__).parents[2] / "agentic_core" / "archived" / "redis_cache_tools.py"
        )

        self.assertTrue(archived_path.exists(), "redis_cache_tools.py must be in archived/")

        # Also verify redis.py is archived
        redis_archived = Path(__file__).parents[2] / "agentic_core" / "archived" / "redis.py"
        self.assertTrue(redis_archived.exists(), "redis.py must be in archived/")

        print("✅ redis_cache_tools.py and redis.py successfully archived")

    def test_redis_mig_004_mixin_uses_sovereign_gateway(self):
        """
        TC-REDIS-MIG-04: Verify RedisCacheMixin uses RedisSovereignAgent.

        This test validates that the mixin has been updated to use the
        hardened singleton gateway.
        """
        print("\n" + "=" * 60)
        print("TC-REDIS-MIG-04: Mixin Gateway Redirection")
        print("=" * 60)

        from pathlib import Path

        source_file = (
            Path(__file__).parents[2]
            / "agentic_core"
            / "utils"
            / "core_extensions"
            / "redis_cache_mixin.py"
        )

        with open(source_file) as f:
            content = f.read()

        # Verify mixin uses RedisSovereignAgent
        has_sovereign_import = (
            "from agentic_core.L5_safety.validators.RedisSovereignAgent import RedisSovereignAgent"
            in content
        )
        has_phase2_marker = "[PHASE 2 MIGRATION]" in content
        has_gateway_call = "gateway = RedisSovereignAgent" in content
        has_get_client = "gateway.get_client()" in content

        # Should NOT have old import
        has_old_import = "caching_redis_mcp_client" in content

        self.assertTrue(has_sovereign_import, "Mixin must import RedisSovereignAgent")
        self.assertTrue(has_phase2_marker, "Must have PHASE 2 migration marker")
        self.assertTrue(has_gateway_call, "Must instantiate RedisSovereignAgent")
        self.assertTrue(has_get_client, "Must call gateway.get_client()")
        self.assertFalse(has_old_import, "Must not import caching_redis_mcp_client")

        print("✅ RedisCacheMixin successfully redirected to RedisSovereignAgent")


def run_tests():
    """Run tests using unittest runner."""
    print("=" * 80)
    print("REDIS PHASE 2 MIGRATION TEST SUITE")
    print("=" * 80)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestRedisPhase2Migration)
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
