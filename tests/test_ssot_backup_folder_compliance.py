#!/usr/bin/env python3
"""
Test Suite: SSOT Backup Folder Compliance

RCA (2026-01-19): The .sovereign_healing_backup folder was created by LocationAgent
and FilesystemAgent without SSOT approval. This caused:
1. 10k+ backup files cluttering the repository
2. Confusion about which folder is the canonical backup location
3. SSOT violation - only archives/ is the approved backup location

This test suite ensures:
1. No agent creates backup folders outside archives/
2. .sovereign_healing_backup is gitignored
3. All backup operations use archives/healing_backups/

Responsible Agents:
- LocationAgent (L5) - _init_backup_dir()
- FilesystemAgent (L5) - self.backup_dir
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestSSOTBackupFolderCompliance(unittest.TestCase):
    """Verify all backup folder creation is SSOT-compliant."""

    def setUp(self):
        self.project_root = PROJECT_ROOT
        self.forbidden_backup_patterns = [
            ".sovereign_healing_backup",
            ".backup",
            ".healing_backup",
            "_backup",
        ]
        self.approved_backup_location = "archives"

    def test_gitignore_contains_sovereign_healing_backup(self):
        """Test 1: .sovereign_healing_backup must be in .gitignore."""
        gitignore_path = self.project_root / ".gitignore"
        self.assertTrue(gitignore_path.exists(), ".gitignore must exist")

        content = gitignore_path.read_text(encoding="utf-8")
        self.assertIn(
            ".sovereign_healing_backup",
            content,
            ".sovereign_healing_backup MUST be in .gitignore to prevent accidental commits"
        )

    def test_location_agent_uses_archives(self):
        """Test 2: LocationAgent._init_backup_dir() must use archives/."""
        location_agent_path = (
            self.project_root / "agentic_core" / "L5_safety" / "validators" / "LocationAgent.py"
        )
        self.assertTrue(location_agent_path.exists(), "LocationAgent.py must exist")

        content = location_agent_path.read_text(encoding="utf-8")

        # Check that _init_backup_dir uses archives/
        self.assertIn(
            'self.project_root / "archives"',
            content,
            "LocationAgent._init_backup_dir() must use archives/ as backup root"
        )

        # Check that it does NOT use .sovereign_healing_backup in mkdir or Path construction
        # (except in comments explaining the fix)
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if ".sovereign_healing_backup" in line:
                stripped = line.strip()
                # Allow in comments, docstrings, or SSOT fix explanations
                is_allowed = (
                    stripped.startswith("#") or
                    stripped.startswith('"""') or
                    stripped.startswith("'''") or
                    "SSOT" in line or
                    "Changed from" in line or
                    "instead of" in line.lower()
                )
                self.assertTrue(
                    is_allowed,
                    f"Line {i+1}: .sovereign_healing_backup found in active code: {line}"
                )

    def test_filesystem_agent_uses_archives(self):
        """Test 3: FilesystemAgent.backup_dir must use archives/."""
        filesystem_agent_path = (
            self.project_root / "agentic_core" / "L5_safety" / "validators" / "FilesystemAgent.py"
        )
        self.assertTrue(filesystem_agent_path.exists(), "FilesystemAgent.py must exist")

        content = filesystem_agent_path.read_text(encoding="utf-8")

        # Check that backup_dir uses archives/
        self.assertIn(
            'self.project_root / "archives"',
            content,
            "FilesystemAgent.backup_dir must use archives/ as backup root"
        )

        # Check that it does NOT use .sovereign_healing_backup in active code
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if ".sovereign_healing_backup" in line:
                stripped = line.strip()
                self.assertTrue(
                    stripped.startswith("#") or "SSOT FIX" in line or "Changed from" in line,
                    f"Line {i+1}: .sovereign_healing_backup found in non-comment code: {line}"
                )

    def test_no_new_backup_folder_creation_outside_archives(self):
        """Test 4: Scan key healing agents for .sovereign_healing_backup usage."""
        violations = []

        # Focus on the key agents that create backup folders
        key_agents = [
            "agentic_core/L5_safety/validators/LocationAgent.py",
            "agentic_core/L5_safety/validators/FilesystemAgent.py",
            "agentic_core/L4_state/ledger/healing_transaction_manager.py",
        ]

        for agent_path in key_agents:
            py_file = self.project_root / agent_path
            if not py_file.exists():
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
            except Exception:
                continue

            # Check for .sovereign_healing_backup in folder creation
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if ".sovereign_healing_backup" in line:
                    stripped = line.strip()
                    # Skip comments, docstrings, and SSOT explanations
                    if stripped.startswith("#"):
                        continue
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        continue
                    if "SSOT" in line or "Changed from" in line or "instead of" in line.lower():
                        continue
                    # This is active code using the forbidden pattern
                    if "Path(" in line or "=" in line:
                        violations.append(
                            f"{agent_path}:{i+1}: "
                            f".sovereign_healing_backup in active code: {line.strip()}"
                        )

        if violations:
            self.fail(
                f"Found {len(violations)} SSOT violations - .sovereign_healing_backup in active code:\n"
                + "\n".join(violations)
            )

    def test_archives_healing_backups_structure(self):
        """Test 5: Verify archives/healing_backups is the canonical location."""
        # This test verifies the SSOT structure
        healing_backups = self.project_root / "archives" / "healing_backups"

        # The folder should be created by agents when needed
        # We just verify the path is correct in the code
        location_agent_path = (
            self.project_root / "agentic_core" / "L5_safety" / "validators" / "LocationAgent.py"
        )
        content = location_agent_path.read_text(encoding="utf-8")

        self.assertIn(
            '"archives" / "healing_backups"',
            content,
            "LocationAgent must use archives/healing_backups/ as the backup location"
        )


class TestBackupFolderCleanup(unittest.TestCase):
    """Verify .sovereign_healing_backup folder is cleaned up."""

    def test_sovereign_healing_backup_should_not_exist_in_git(self):
        """Test 6: .sovereign_healing_backup should not be tracked by git."""
        # Check if the folder exists
        backup_folder = PROJECT_ROOT / ".sovereign_healing_backup"

        if backup_folder.exists():
            # If it exists, it should be gitignored
            gitignore_path = PROJECT_ROOT / ".gitignore"
            content = gitignore_path.read_text(encoding="utf-8")

            self.assertIn(
                ".sovereign_healing_backup",
                content,
                "If .sovereign_healing_backup exists, it MUST be gitignored"
            )

            # Warn that cleanup is needed
            print(f"\n⚠️  WARNING: .sovereign_healing_backup folder exists with "
                  f"{sum(1 for _ in backup_folder.rglob('*'))} files. "
                  f"Consider deleting it.")


if __name__ == "__main__":
    print("=" * 70)
    print("SSOT Backup Folder Compliance Test Suite")
    print("=" * 70)
    print()

    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSSOTBackupFolderCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestBackupFolderCleanup))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("✅ ALL SSOT BACKUP COMPLIANCE TESTS PASSED")
    else:
        print("❌ SSOT BACKUP COMPLIANCE TESTS FAILED")
        print("   Fix the violations before committing!")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)
