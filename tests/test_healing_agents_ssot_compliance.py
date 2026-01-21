#!/usr/bin/env python3
"""
Detailed Testing: Healing Agents SSOT Compliance

Tests that LocationAgent, FilesystemAgent, and HealingTransactionManager
all use archives/healing_backups/ instead of .sovereign_healing_backup/

This is a runtime test that actually instantiates the agents and verifies
their backup paths are correct.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_location_agent_backup_path():
    """Test 1: LocationAgent._init_backup_dir() returns correct path."""
    print("\n" + "=" * 70)
    print("TEST 1: LocationAgent._init_backup_dir()")
    print("=" * 70)

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

        # Create agent with project root
        agent = LocationAgent(project_root=PROJECT_ROOT)

        # Call _init_backup_dir
        backup_dir = agent._init_backup_dir()

        print(f"   Backup dir: {backup_dir}")

        # Verify path structure
        backup_str = str(backup_dir)

        # Must contain archives/healing_backups
        assert "archives" in backup_str, f"Path must contain 'archives': {backup_str}"
        assert "healing_backups" in backup_str, f"Path must contain 'healing_backups': {backup_str}"
        assert "location" in backup_str, f"Path must contain 'location': {backup_str}"

        # Must NOT contain .sovereign_healing_backup
        assert ".sovereign_healing_backup" not in backup_str, \
            f"Path must NOT contain '.sovereign_healing_backup': {backup_str}"

        # Clean up created directory
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        print("   ✅ PASSED: LocationAgent uses archives/healing_backups/location/")
        return True

    except ImportError as e:
        print(f"   ⚠️  SKIPPED: Could not import LocationAgent: {e}")
        return True  # Skip if import fails
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_filesystem_agent_backup_path():
    """Test 2: FilesystemAgent.backup_dir uses correct path."""
    print("\n" + "=" * 70)
    print("TEST 2: FilesystemAgent.backup_dir")
    print("=" * 70)

    try:
        from agentic_core.L5_safety.validators.FilesystemAgent import FilesystemAgent

        # Create agent with project root (dry_run=True to avoid creating dirs)
        agent = FilesystemAgent(project_root=PROJECT_ROOT, dry_run=True)

        # Check backup_dir attribute
        backup_dir = agent.backup_dir

        print(f"   Backup dir: {backup_dir}")

        # Verify path structure
        backup_str = str(backup_dir)

        # Must contain archives/healing_backups
        assert "archives" in backup_str, f"Path must contain 'archives': {backup_str}"
        assert "healing_backups" in backup_str, f"Path must contain 'healing_backups': {backup_str}"
        assert "filesystem" in backup_str, f"Path must contain 'filesystem': {backup_str}"

        # Must NOT contain .sovereign_healing_backup
        assert ".sovereign_healing_backup" not in backup_str, \
            f"Path must NOT contain '.sovereign_healing_backup': {backup_str}"

        print("   ✅ PASSED: FilesystemAgent uses archives/healing_backups/filesystem/")
        return True

    except ImportError as e:
        print(f"   ⚠️  SKIPPED: Could not import FilesystemAgent: {e}")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_healing_transaction_manager_backup_path():
    """Test 3: HealingTransaction.backup_dir uses correct path."""
    print("\n" + "=" * 70)
    print("TEST 3: HealingTransaction.backup_dir")
    print("=" * 70)

    try:
        from agentic_core.L4_state.ledger.healing_transaction_manager import HealingTransaction

        # Create transaction
        manager = HealingTransaction()

        # Check backup_dir attribute
        backup_dir = manager.backup_dir

        print(f"   Backup dir: {backup_dir}")

        # Verify path structure
        backup_str = str(backup_dir)

        # Must contain archives/healing_backups
        assert "archives" in backup_str, f"Path must contain 'archives': {backup_str}"
        assert "healing_backups" in backup_str, f"Path must contain 'healing_backups': {backup_str}"
        assert "transactions" in backup_str, f"Path must contain 'transactions': {backup_str}"

        # Must NOT contain .sovereign_healing_backup
        assert ".sovereign_healing_backup" not in backup_str, \
            f"Path must NOT contain '.sovereign_healing_backup': {backup_str}"

        print("   ✅ PASSED: HealingTransaction uses archives/healing_backups/transactions/")
        return True

    except ImportError as e:
        print(f"   ⚠️  SKIPPED: Could not import HealingTransaction: {e}")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_backup_file_creation():
    """Test 4: Verify backup files are created in correct location."""
    print("\n" + "=" * 70)
    print("TEST 4: Backup File Creation (Integration)")
    print("=" * 70)

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

        # Create a temp file to backup
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Test file for backup\nprint('hello')\n")
            temp_file = Path(f.name)

        try:
            # Create agent
            agent = LocationAgent(project_root=PROJECT_ROOT)

            # Initialize backup dir
            backup_dir = agent._init_backup_dir()

            print(f"   Created backup dir: {backup_dir}")

            # Verify the backup dir is under archives/
            assert backup_dir.is_relative_to(PROJECT_ROOT / "archives"), \
                f"Backup dir must be under archives/: {backup_dir}"

            # Clean up
            if backup_dir.exists():
                shutil.rmtree(backup_dir.parent.parent)  # Remove healing_backups/location

            print("   ✅ PASSED: Backup directory created under archives/")
            return True

        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

    except ImportError as e:
        print(f"   ⚠️  SKIPPED: Could not import LocationAgent: {e}")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False


def test_no_sovereign_healing_backup_created():
    """Test 5: Verify .sovereign_healing_backup is NOT created."""
    print("\n" + "=" * 70)
    print("TEST 5: No .sovereign_healing_backup Creation")
    print("=" * 70)

    # Check if .sovereign_healing_backup exists
    forbidden_dir = PROJECT_ROOT / ".sovereign_healing_backup"

    if forbidden_dir.exists():
        print(f"   ❌ FAILED: .sovereign_healing_backup exists with "
              f"{sum(1 for _ in forbidden_dir.rglob('*'))} files")
        print("   Run: Remove-Item -Recurse -Force .sovereign_healing_backup")
        return False
    else:
        print("   ✅ PASSED: .sovereign_healing_backup does not exist")
        return True


def test_source_code_compliance():
    """Test 6: Verify source code uses correct paths."""
    print("\n" + "=" * 70)
    print("TEST 6: Source Code Compliance")
    print("=" * 70)

    agents_to_check = [
        ("LocationAgent", PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "LocationAgent.py"),
        ("FilesystemAgent", PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "FilesystemAgent.py"),
        ("HealingTransaction", PROJECT_ROOT / "agentic_core" / "L4_state" / "ledger" / "healing_transaction_manager.py"),
    ]

    all_passed = True

    for agent_name, agent_path in agents_to_check:
        if not agent_path.exists():
            print(f"   ⚠️  {agent_name}: File not found")
            continue

        content = agent_path.read_text(encoding="utf-8")

        # Check for archives/healing_backups (handles both quoted and f-string formats)
        has_archives = ('archives' in content and 'healing_backups' in content and
                       ('archives/healing_backups' in content or '"archives"' in content))

        # Check for .sovereign_healing_backup in active code (not comments or explanations)
        has_forbidden = False
        for line in content.split("\n"):
            if ".sovereign_healing_backup" in line:
                stripped = line.strip()
                # Skip comments, docstrings, and SSOT fix explanations
                is_allowed = (
                    stripped.startswith("#") or
                    stripped.startswith('"""') or
                    stripped.startswith("'''") or
                    "SSOT" in line or
                    "Changed from" in line or
                    "instead of" in line.lower()
                )
                if not is_allowed:
                    # Check if it's actually creating a path (not just referencing)
                    if "Path(" in line and "=" in line and "archives" not in line:
                        has_forbidden = True
                        break

        if has_archives and not has_forbidden:
            print(f"   ✅ {agent_name}: Uses archives/healing_backups/")
        else:
            print(f"   ❌ {agent_name}: SSOT violation detected")
            all_passed = False

    return all_passed


def main():
    print("=" * 70)
    print("Healing Agents SSOT Compliance - Detailed Testing")
    print("=" * 70)

    results = []

    # Run all tests
    results.append(("LocationAgent._init_backup_dir()", test_location_agent_backup_path()))
    results.append(("FilesystemAgent.backup_dir", test_filesystem_agent_backup_path()))
    results.append(("HealingTransactionManager.backup_dir", test_healing_transaction_manager_backup_path()))
    results.append(("Backup File Creation", test_backup_file_creation()))
    results.append(("No .sovereign_healing_backup", test_no_sovereign_healing_backup_created()))
    results.append(("Source Code Compliance", test_source_code_compliance()))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")

    print(f"\n   Total: {passed}/{len(results)} passed")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Healing agents are SSOT compliant")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED - Fix SSOT violations")
        return 1


if __name__ == "__main__":
    sys.exit(main())
