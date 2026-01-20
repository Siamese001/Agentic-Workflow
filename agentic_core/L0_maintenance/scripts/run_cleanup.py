"""
Execution script for backup decommissioning.

Phase 6: Global Migration Execution

This script removes deprecated backup directories and enforces
the single SSOT backup location at archives/healing_backups/.

Usage:
    python -m agentic_core.L0_maintenance.scripts.run_cleanup
"""
from __future__ import annotations

from agentic_core.utils.backup_manager import BackupManager
from agentic_core.utils.project_root import get_project_root


def main():
    """Execute legacy backup cleanup."""
    root = get_project_root()
    print(f"Scanning for legacy backups in: {root}")
    
    # Detect legacy directories
    legacy = BackupManager.get_legacy_backup_dirs(root)
    if not legacy:
        print("No legacy backups found. Repository is clean.")
        return 0

    print(f"Found {len(legacy)} legacy directories: {[d.name for d in legacy]}")
    
    # Remove legacy directories
    count = BackupManager.decommission_legacy_backups(root)
    print(f"Successfully removed {count} legacy directories.")
    
    return count


if __name__ == "__main__":
    main()
