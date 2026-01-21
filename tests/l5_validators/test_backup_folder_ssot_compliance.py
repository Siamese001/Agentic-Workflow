#!/usr/bin/env python3
"""
Test Suite: .sovereign_healing_backup Folder SSOT Compliance

RCA: The .sovereign_healing_backup folder was created without SSOT approval.
This test suite verifies that all backup folder creation is SSOT-compliant.

Responsible Agents:
1. FilesystemAgent (L5_safety/validators)
2. LocationAgent (L5_safety/validators)
3. NamingAgent (L5_safety/validators)
4. HealingTransactionManager (L4_state/ledger)

Test Cases:
1. SSOT Compliance - Verify backup folder is defined in structure_blueprint.py
2. FilesystemAgent Backup Location - Verify SSOT-approved location
3. LocationAgent Backup Location - Verify SSOT-approved location
4. NamingAgent Backup Location - Verify SSOT-approved location
5. HealingTransactionManager Backup Location - Verify SSOT-approved location
6. Root Folder SSOT Enforcement - Verify no unauthorized root folders
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.structure_blueprint import (
    SCOPE_SUMMARY_EXCLUSIONS,
    SOVEREIGN_REGISTRY,
    get_validated_project_root,
)


class BackupFolderSSOTTester:
    """Test harness for backup folder SSOT compliance."""

    def __init__(self):
        self.project_root = get_validated_project_root()
        self.test_results = []

    def test_1_ssot_compliance(self):
        """Test 1: Verify .sovereign_healing_backup is in SSOT.

        The folder must be explicitly defined in SOVEREIGN_REGISTRY
        or documented as an approved root folder.
        """
        print("\n" + "=" * 70)
        print("TEST 1: SSOT Compliance for Backup Folder")
        print("=" * 70)

        # Check if folder is in SOVEREIGN_REGISTRY
        in_registry = ".sovereign_healing_backup" in SOVEREIGN_REGISTRY

        # Check if folder is in exclusions (acknowledged but not approved)
        in_exclusions = ".sovereign_healing_backup" in SCOPE_SUMMARY_EXCLUSIONS

        print(f"   In SOVEREIGN_REGISTRY: {in_registry}")
        print(f"   In SCOPE_SUMMARY_EXCLUSIONS: {in_exclusions}")

        if in_registry:
            print("   ✅ TEST 1 PASSED: Folder is SSOT-approved in SOVEREIGN_REGISTRY")
            return True
        elif in_exclusions:
            print("   ⚠️  TEST 1 WARNING: Folder is excluded but NOT approved for creation")
            print("   ❌ TEST 1 FAILED: Folder must be in SOVEREIGN_REGISTRY to be created")
            return False
        else:
            print("   ❌ TEST 1 FAILED: Folder is not in SSOT at all")
            return False

    def test_2_filesystem_agent_backup_location(self):
        """Test 2: Verify FilesystemAgent uses SSOT-approved backup location."""
        print("\n" + "=" * 70)
        print("TEST 2: FilesystemAgent Backup Location")
        print("=" * 70)

        try:
            from agentic_core.L5_safety.validators.FilesystemAgent import get_filesystem_agent

            agent = get_filesystem_agent(self.project_root)
            backup_dir_str = str(agent.backup_dir)

            print(f"   Backup directory: {backup_dir_str}")

            # Check if backup_dir uses SSOT-approved location
            is_ssot_approved = (
                ".sovereign_healing_backup" in SOVEREIGN_REGISTRY or "archives" in backup_dir_str
            )

            if is_ssot_approved:
                print("   ✅ TEST 2 PASSED: FilesystemAgent uses SSOT-approved location")
                return True
            else:
                print("   ❌ TEST 2 FAILED: FilesystemAgent uses non-SSOT location")
                print(f"      Location: {backup_dir_str}")
                return False

        except Exception as e:
            print(f"   ❌ TEST 2 FAILED: Error loading FilesystemAgent: {e}")
            return False

    def test_3_location_agent_backup_location(self):
        """Test 3: Verify LocationAgent uses SSOT-approved backup location."""
        print("\n" + "=" * 70)
        print("TEST 3: LocationAgent Backup Location")
        print("=" * 70)

        try:
            from agentic_core.L5_safety.validators.LocationAgent import get_location_agent

            agent = get_location_agent(self.project_root)

            # LocationAgent creates backup_dir in _initialize_backup_dir method
            # We need to check the method implementation
            import inspect

            source = inspect.getsource(agent._initialize_backup_dir)

            print("   Checking _initialize_backup_dir method...")

            # Check if method uses SSOT-approved location
            uses_ssot_location = (
                ".sovereign_healing_backup" in SOVEREIGN_REGISTRY or "archives" in source
            )

            if uses_ssot_location:
                print("   ✅ TEST 3 PASSED: LocationAgent uses SSOT-approved location")
                return True
            else:
                print("   ❌ TEST 3 FAILED: LocationAgent uses non-SSOT location")
                print("      Method creates: .sovereign_healing_backup/location/{timestamp}")
                return False

        except Exception as e:
            print(f"   ❌ TEST 3 FAILED: Error inspecting LocationAgent: {e}")
            return False

    def test_4_naming_agent_backup_location(self):
        """Test 4: Verify NamingAgent uses SSOT-approved backup location."""
        print("\n" + "=" * 70)
        print("TEST 4: NamingAgent Backup Location")
        print("=" * 70)

        try:
            # NamingAgent creates backups in heal_repository method
            # Check if it uses SSOT-approved location
            naming_agent_path = (
                self.project_root / "agentic_core" / "L5_safety" / "validators" / "NamingAgent.py"
            )

            if not naming_agent_path.exists():
                print("   ⚠️  TEST 4 SKIPPED: NamingAgent.py not found")
                return True  # Skip test if file doesn't exist

            content = naming_agent_path.read_text(encoding="utf-8")

            # Check if NamingAgent uses .sovereign_healing_backup
            uses_backup_folder = ".sovereign_healing_backup" in content

            print(f"   Uses .sovereign_healing_backup: {uses_backup_folder}")

            if uses_backup_folder:
                # Check if folder is SSOT-approved
                is_ssot_approved = ".sovereign_healing_backup" in SOVEREIGN_REGISTRY

                if is_ssot_approved:
                    print("   ✅ TEST 4 PASSED: NamingAgent uses SSOT-approved location")
                    return True
                else:
                    print("   ❌ TEST 4 FAILED: NamingAgent uses non-SSOT location")
                    return False
            else:
                print("   ✅ TEST 4 PASSED: NamingAgent does not create backup folder")
                return True

        except Exception as e:
            print(f"   ❌ TEST 4 FAILED: Error checking NamingAgent: {e}")
            return False

    def test_5_healing_transaction_manager_backup_location(self):
        """Test 5: Verify HealingTransactionManager uses SSOT-approved backup location."""
        print("\n" + "=" * 70)
        print("TEST 5: HealingTransactionManager Backup Location")
        print("=" * 70)

        try:
            from agentic_core.L4_state.ledger.healing_transaction_manager import (
                HealingTransactionManager,
            )

            manager = HealingTransactionManager()
            backup_dir_str = str(manager.backup_dir)

            print(f"   Backup directory: {backup_dir_str}")

            # Check if backup_dir uses SSOT-approved location
            is_ssot_approved = (
                ".sovereign_healing_backup" in SOVEREIGN_REGISTRY or "archives" in backup_dir_str
            )

            if is_ssot_approved:
                print("   ✅ TEST 5 PASSED: HealingTransactionManager uses SSOT-approved location")
                return True
            else:
                print("   ❌ TEST 5 FAILED: HealingTransactionManager uses non-SSOT location")
                print(f"      Location: {backup_dir_str}")
                return False

        except Exception as e:
            print(f"   ❌ TEST 5 FAILED: Error loading HealingTransactionManager: {e}")
            return False

    def test_6_root_folder_ssot_enforcement(self):
        """Test 6: Verify no unauthorized root folders are created."""
        print("\n" + "=" * 70)
        print("TEST 6: Root Folder SSOT Enforcement")
        print("=" * 70)

        try:
            # Get all directories at root level
            root_dirs = [
                d for d in os.listdir(self.project_root) if os.path.isdir(self.project_root / d)
            ]

            # Get approved folders from SOVEREIGN_REGISTRY
            approved_folders = set(SOVEREIGN_REGISTRY.keys())

            # Add other known approved folders
            approved_folders.update(
                [
                    "scripts",
                    "docs",
                    "archives",
                    "reports",
                    "data",
                    "node_modules",
                    ".venv",
                    "venv",
                    "env",
                    ".git",
                    ".github",
                    "__pycache__",
                    "coverage_html",
                    "htmlcov",
                    ".pytest_cache",
                    ".ruff_cache",
                    ".mypy_cache",
                    ".coverage",
                ]
            )

            # Check for unauthorized folders
            unauthorized = set(root_dirs) - approved_folders

            # Filter out hidden folders that are system-generated
            unauthorized_visible = {f for f in unauthorized if not f.startswith(".")}

            print(f"   Total root directories: {len(root_dirs)}")
            print(f"   Approved folders: {len(approved_folders)}")
            print(f"   Unauthorized visible folders: {len(unauthorized_visible)}")

            if unauthorized_visible:
                print(f"   ⚠️  Unauthorized folders found: {unauthorized_visible}")

            # Check specifically for .sovereign_healing_backup
            has_backup_folder = ".sovereign_healing_backup" in root_dirs
            backup_folder_approved = ".sovereign_healing_backup" in SOVEREIGN_REGISTRY

            print(f"\n   .sovereign_healing_backup exists: {has_backup_folder}")
            print(f"   .sovereign_healing_backup approved: {backup_folder_approved}")

            if has_backup_folder and not backup_folder_approved:
                print("   ❌ TEST 6 FAILED: .sovereign_healing_backup exists but not SSOT-approved")
                return False
            elif has_backup_folder and backup_folder_approved:
                print("   ✅ TEST 6 PASSED: .sovereign_healing_backup is SSOT-approved")
                return True
            else:
                print("   ✅ TEST 6 PASSED: No unauthorized root folders")
                return True

        except Exception as e:
            print(f"   ❌ TEST 6 FAILED: Error checking root folders: {e}")
            return False

    def run_all_tests(self):
        """Run all 6 test cases and report results."""
        print("\n" + "=" * 70)
        print("BACKUP FOLDER SSOT COMPLIANCE TEST SUITE")
        print("=" * 70)
        print(f"Project Root: {self.project_root}")

        tests = [
            ("SSOT Compliance", self.test_1_ssot_compliance),
            ("FilesystemAgent Backup Location", self.test_2_filesystem_agent_backup_location),
            ("LocationAgent Backup Location", self.test_3_location_agent_backup_location),
            ("NamingAgent Backup Location", self.test_4_naming_agent_backup_location),
            (
                "HealingTransactionManager Backup Location",
                self.test_5_healing_transaction_manager_backup_location,
            ),
            ("Root Folder SSOT Enforcement", self.test_6_root_folder_ssot_enforcement),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                passed = test_func()
                results.append((test_name, passed))
            except Exception as e:
                print(f"\n   ❌ TEST FAILED WITH EXCEPTION: {e}")
                import traceback

                traceback.print_exc()
                results.append((test_name, False))

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)

        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {test_name}")

        print(f"\nTotal: {passed_count}/{total_count} tests passed")

        if passed_count == total_count:
            print("\n🎉 ALL TESTS PASSED!")
            print("\nNext Steps:")
            print(
                "  1. Add .sovereign_healing_backup to SOVEREIGN_REGISTRY in structure_blueprint.py"
            )
            print("  2. Re-run tests to verify SSOT compliance")
            return 0
        else:
            print(f"\n⚠️  {total_count - passed_count} TEST(S) FAILED")
            print("\nRequired Fix:")
            print(
                "  Add .sovereign_healing_backup to SOVEREIGN_REGISTRY in structure_blueprint.py:"
            )
            print("")
            print("  SOVEREIGN_REGISTRY: Any = {")
            print("      # ... existing entries ...")
            print("      '.sovereign_healing_backup': {")
            print("          'depth': 2,")
            print("          'subfolders': ['filesystem', 'location', 'naming', 'transactions'],")
            print("          'purpose': 'Backup directory for healing operations',")
            print("          'volatile': True,")
            print("      }")
            print("  }")
            return 1


if __name__ == "__main__":
    tester = BackupFolderSSOTTester()
    sys.exit(tester.run_all_tests())
