#!/usr/bin/env python3
"""
Test Suite: Phase 3 Manager & Enforcer Consolidation

MANDATORY 100% PASS RATE REQUIRED

Tests:
1. test_resource_concurrency - 10+ agents requesting budget simultaneously
2. test_budget_hard_cap - Execution halted at 100% exhaustion
3. test_vault_config_access - Config only accessible with SECURE_READER
4. test_enforcer_ssot_sync - SSOT registry updates immediately
5. test_sovereignty_protection - Block L3/L4 modifying L5 without exception
6. test_naming_law_compliance - Force-rename non-compliant classes
7. test_gravity_import_block - Reject layer hierarchy violations
"""

from __future__ import annotations

import concurrent.futures
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestResourceConcurrency(unittest.TestCase):
    """Test 1: Resource concurrency with 10+ simultaneous agents."""

    def test_resource_concurrency(self):
        """10+ agents requesting budget simultaneously without race conditions."""
        from agentic_core.L5_safety.policy_engine.ResourceManagerAgent import (
            AllocationStatus,
            ResourceType,
            ResourceManagerAgent,
        )

        manager = ResourceManagerAgent()
        manager.set_budget(ResourceType.BUDGET, total=1000.0)

        results = []
        errors = []

        def request_budget(agent_id: str, amount: float):
            try:
                result = manager.allocate(agent_id, ResourceType.BUDGET, amount)
                results.append((agent_id, result))
            except Exception as e:
                errors.append((agent_id, str(e)))

        # Launch 15 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for i in range(15):
                futures.append(executor.submit(request_budget, f"agent_{i}", 50.0))
            concurrent.futures.wait(futures)

        # Verify no errors
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")

        # Verify all requests were processed
        self.assertEqual(len(results), 15, "All 15 requests should be processed")

        # Verify budget tracking is consistent
        status = manager.get_budget_status(ResourceType.BUDGET)

        # With 1000 total and 15 requests of 50 each (750 needed),
        # all should be allocated
        allocated_count = sum(1 for _, r in results if r.status == AllocationStatus.ALLOCATED)
        self.assertGreater(allocated_count, 0, "Some allocations should succeed")

        # Verify no race conditions (used + available = total)
        self.assertAlmostEqual(
            status["used"] + status["available"],
            status["total"],
            places=2,
            msg="Budget accounting must be consistent",
        )


class TestBudgetHardCap(unittest.TestCase):
    """Test 2: Budget hard cap enforcement."""

    def test_budget_hard_cap(self):
        """Agent execution is strictly halted when budget reaches 100% exhaustion."""
        from agentic_core.L5_safety.policy_engine.ResourceManagerAgent import (
            AllocationStatus,
            ResourceType,
            ResourceManagerAgent,
        )

        manager = ResourceManagerAgent()
        manager.set_budget(ResourceType.BUDGET, total=100.0, hard_cap=True)

        # Allocate 100% of budget
        result1 = manager.allocate("agent_1", ResourceType.BUDGET, 100.0)
        self.assertEqual(result1.status, AllocationStatus.ALLOCATED)

        # Verify exhausted
        self.assertTrue(manager.is_exhausted(ResourceType.BUDGET))

        # Try to allocate more - should be EXHAUSTED
        result2 = manager.allocate("agent_2", ResourceType.BUDGET, 1.0)
        self.assertEqual(
            result2.status,
            AllocationStatus.EXHAUSTED,
            "Hard cap must halt execution at 100% exhaustion",
        )
        self.assertEqual(result2.amount, 0, "No budget should be allocated")


class TestVaultConfigAccess(unittest.TestCase):
    """Test 3: Vault configuration access control."""

    def test_vault_config_access(self):
        """Config keys are only accessible by agents with SECURE_READER permission."""
        from agentic_core.L5_safety.policy_engine.SecurityManagerAgent import (
            PermissionLevel,
            SecurityManagerAgent,
        )

        manager = SecurityManagerAgent()

        # Grant SECURE_WRITER to admin
        manager.grant_permission("admin", PermissionLevel.ADMIN, "system")
        manager.grant_permission("writer", PermissionLevel.SECURE_WRITER, "system")
        manager.grant_permission("reader", PermissionLevel.SECURE_READER, "system")

        # Set a secure config
        success = manager.set_config(
            "api_key",
            "secret_value_123",
            agent_id="writer",
            required_level=PermissionLevel.SECURE_READER,
        )
        self.assertTrue(success, "Writer should be able to set config")

        # Reader can access
        value = manager.get_config("api_key", agent_id="reader")
        self.assertEqual(value, "secret_value_123", "Reader should access config")

        # Unpermissioned agent cannot access
        value_denied = manager.get_config("api_key", agent_id="unpermissioned_agent")
        self.assertIsNone(
            value_denied,
            "Unpermissioned agent must NOT access secure config",
        )

        # Verify audit log captured the denial
        audit = manager.get_audit_log(agent_id="unpermissioned_agent")
        self.assertGreater(len(audit), 0, "Denial should be audited")
        self.assertFalse(audit[-1].success, "Audit should show denial")


class TestEnforcerSSOTSync(unittest.TestCase):
    """Test 4: SSOT registry synchronization."""

    def test_enforcer_ssot_sync(self):
        """Any refactor made by the enforcer is immediately updated in SSOT registry."""
        from agentic_core.L5_safety.policy_engine.CodeEnforcerAgent import (
            EnforcementConfig,
            CodeEnforcerAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create a mock SSOT registry
            ssot_path = tmpdir / "agent_discovery_full.json"
            ssot_path.write_text('{"agents": [], "count": 0}', encoding="utf-8")

            config = EnforcementConfig(ssot_registry_path=ssot_path)
            enforcer = CodeEnforcerAgent(project_root=tmpdir, config=config)

            # Sync registry
            registry = enforcer.sync_ssot_registry()
            self.assertIn("agents", registry, "Registry should be loaded")

            # Update registry
            success = enforcer.update_ssot_registry({"count": 10, "updated": True})
            self.assertTrue(success, "Registry update should succeed")

            # Verify update persisted
            import json

            updated = json.loads(ssot_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["count"], 10, "SSOT must be immediately updated")
            self.assertTrue(updated["updated"], "New fields must be added")


class TestSovereigntyProtection(unittest.TestCase):
    """Test 5: Sovereignty protection for L5 files."""

    def test_sovereignty_protection(self):
        """Block any L3/L4 agent attempting to modify an L5 file without signed exception."""
        from agentic_core.L5_safety.policy_engine.CodeEnforcerAgent import (
            CodeEnforcerAgent,
        )

        enforcer = CodeEnforcerAgent()

        # L3 trying to modify L5 file - should be blocked
        allowed, reason = enforcer.check_sovereignty(
            source_layer="L3",
            target_file=Path("agentic_core/L5_safety/validators/SomeAgent.py"),
        )
        self.assertFalse(allowed, "L3 must NOT modify L5 without exception")
        self.assertIn("Sovereignty violation", reason)

        # L4 trying to modify L5 file - should be blocked
        allowed, reason = enforcer.check_sovereignty(
            source_layer="L4",
            target_file=Path("agentic_core/L5_safety/validators/SomeAgent.py"),
        )
        self.assertFalse(allowed, "L4 must NOT modify L5 without exception")

        # Grant exception
        exception = enforcer.grant_exception(
            source_layer="L3",
            target_file=Path("agentic_core/L5_safety/validators/SomeAgent.py"),
            granted_by="admin",
            reason="Emergency hotfix",
        )
        self.assertIsNotNone(exception)

        # Now L3 should be allowed with exception
        allowed, reason = enforcer.check_sovereignty(
            source_layer="L3",
            target_file=Path("agentic_core/L5_safety/validators/SomeAgent.py"),
            agent_id="any_agent",
        )
        self.assertTrue(allowed, "L3 should be allowed with signed exception")
        self.assertIn("Signed exception", reason)


class TestNamingLawCompliance(unittest.TestCase):
    """Test 6: Naming convention enforcement."""

    def test_naming_law_compliance(self):
        """Force-rename any class not adhering to [Name]Agent suffix standard."""
        from agentic_core.L5_safety.policy_engine.StructureEnforcerAgent import (
            StructureViolationType,
            StructureEnforcerAgent,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create a non-compliant agent file
            bad_file = tmpdir / "BadNameAgent.py"
            bad_file.write_text(
                'class BadName:\n    """A badly named class."""\n    pass\n',
                encoding="utf-8",
            )

            enforcer = StructureEnforcerAgent(project_root=tmpdir)

            # Validate - should find naming violation
            violations = enforcer.validate_file(bad_file)
            naming_violations = [
                v for v in violations if v.violation_type == StructureViolationType.NAMING
            ]
            self.assertGreater(
                len(naming_violations),
                0,
                "Should detect naming violation",
            )
            self.assertIn("Agent", naming_violations[0].suggested_fix)

            # Force rename (dry run)
            result = enforcer.force_rename_class(bad_file, "BadName", "BadNameAgent", dry_run=True)
            self.assertIn("new_name", result)
            self.assertEqual(result["new_name"], "BadNameAgent")

            # Force rename (actual)
            result = enforcer.force_rename_class(bad_file, "BadName", "BadNameAgent", dry_run=False)
            self.assertTrue(result["applied"], "Rename should be applied")

            # Verify file was updated
            content = bad_file.read_text(encoding="utf-8")
            self.assertIn("class BadNameAgent", content)
            self.assertNotIn("class BadName:", content)


class TestGravityImportBlock(unittest.TestCase):
    """Test 7: Gravity import blocking."""

    def test_gravity_import_block(self):
        """Reject imports that bypass the defined layer hierarchy (e.g., L2 importing L5)."""
        from agentic_core.L5_safety.policy_engine.StructureEnforcerAgent import (
            StructureViolationType,
            StructureEnforcerAgent,
        )

        enforcer = StructureEnforcerAgent()

        # L2 importing L5 - should be blocked
        allowed, reason = enforcer.check_gravity_import("L2", "L5")
        self.assertFalse(allowed, "L2 must NOT import from L5")
        self.assertIn("Gravity violation", reason)

        # L3 importing L5 - should be blocked
        allowed, reason = enforcer.check_gravity_import("L3", "L5")
        self.assertFalse(allowed, "L3 must NOT import from L5")

        # L5 importing L3 - should be allowed (higher can import lower)
        allowed, reason = enforcer.check_gravity_import("L5", "L3")
        self.assertTrue(allowed, "L5 can import from L3")

        # L3 importing L2 - should be allowed
        allowed, reason = enforcer.check_gravity_import("L3", "L2")
        self.assertTrue(allowed, "L3 can import from L2")

        # Test with actual file content
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create L2 directory structure
            l2_dir = tmpdir / "agentic_core" / "L2_execution"
            l2_dir.mkdir(parents=True)

            # Create file with bad import
            bad_file = l2_dir / "BadImportAgent.py"
            bad_file.write_text(
                "from agentic_core.L5_safety.validators import SomeValidator\n"
                "class BadImportAgent:\n    pass\n",
                encoding="utf-8",
            )

            enforcer2 = StructureEnforcerAgent(project_root=tmpdir)
            violations = enforcer2.validate_file(bad_file)

            gravity_violations = [
                v for v in violations if v.violation_type == StructureViolationType.GRAVITY
            ]
            self.assertGreater(
                len(gravity_violations),
                0,
                "Should detect gravity violation in imports",
            )


if __name__ == "__main__":
    print("=" * 70)
    print("Phase 3 Manager & Enforcer Consolidation - MANDATORY 100% PASS")
    print("=" * 70)
    print()

    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestResourceConcurrency))
    suite.addTests(loader.loadTestsFromTestCase(TestBudgetHardCap))
    suite.addTests(loader.loadTestsFromTestCase(TestVaultConfigAccess))
    suite.addTests(loader.loadTestsFromTestCase(TestEnforcerSSOTSync))
    suite.addTests(loader.loadTestsFromTestCase(TestSovereigntyProtection))
    suite.addTests(loader.loadTestsFromTestCase(TestNamingLawCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestGravityImportBlock))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    total = result.testsRun

    if result.wasSuccessful():
        print(f"✅ ALL {total} TESTS PASSED - 100% PASS RATE ACHIEVED")
        print("   Phase 3 consolidation is APPROVED for deployment")
    else:
        print(f"❌ {passed}/{total} TESTS PASSED - BELOW 100% REQUIREMENT")
        print("   Phase 3 consolidation is BLOCKED until all tests pass")
        if result.failures:
            print("\n   Failures:")
            for test, _ in result.failures:
                print(f"   - {test}")
        if result.errors:
            print("\n   Errors:")
            for test, _ in result.errors:
                print(f"   - {test}")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)
