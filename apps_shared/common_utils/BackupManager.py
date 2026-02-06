"""
Centralized SSOT for managing backup directories and cleanup policies.

This module replaces the 4 competing backup patterns identified in the SSOT audit:
- archives/healing_backups/ (CORRECT - now enforced)
- .sovereign_healing_backup/ (DEPRECATED)
- .governance_healer_backups/ (NON-STANDARD)
- .canon_memory/backups/ (NON-STANDARD)

All agents should use BackupManager for backup operations.
"""

import shutil
from datetime import datetime
from pathlib import Path


class BackupManager:
    """
    Centralized backup directory management.
    SSOT Location: archives/healing_backups/<category>/
    """

    # SSOT Constant for backup root
    BACKUP_ROOT = Path("archives/healing_backups")

    @classmethod
    def get_backup_dir(
        cls,
        category: str,
        project_root: str | Path | None = None,
        timestamped: bool = True,
    ) -> Path:
        """
        Get a standardized backup directory path.

        Args:
            category: The sub-bucket for backups (e.g., 'filesystem', 'structure')
            project_root: Root of the repository (defaults to CWD)
            timestamped: If True, appends YYYYMMDD_HHMMSS subdirectory

        Returns:
            Path: The fully resolved, created directory path
        """
        root = Path(project_root) if project_root else Path.cwd()
        base_path = root / cls.BACKUP_ROOT / category

        if timestamped:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = base_path / timestamp
        else:
            final_path = base_path

        final_path.mkdir(parents=True, exist_ok=True)
        return final_path

    @classmethod
    def cleanup_old_backups(
        cls,
        category: str,
        keep_last_n: int = 10,
        project_root: str | Path | None = None,
    ) -> int:
        """
        Remove old backups for a specific category, keeping only the N most recent.

        Returns:
            int: Number of backup directories removed
        """
        root = Path(project_root) if project_root else Path.cwd()
        category_dir = root / cls.BACKUP_ROOT / category

        if not category_dir.exists():
            return 0

        # List all subdirectories, sort by name (timestamp guarantees chronological order)
        backups = sorted(
            [d for d in category_dir.iterdir() if d.is_dir()],
            key=lambda x: x.name,
            reverse=True,
        )

        removed_count = 0
        if len(backups) > keep_last_n:
            to_remove = backups[keep_last_n:]
            for backup in to_remove:
                try:
                    shutil.rmtree(backup)
                    removed_count += 1
                except OSError as e:
                    print(f"Error cleaning up backup {backup}: {e}")

        return removed_count

    @classmethod
    def backup_file(
        cls,
        target_file: str | Path,
        category: str = "misc",
        project_root: str | Path | None = None,
    ) -> Path | None:
        """
        Quickly backup a single file to a timestamped location.

        Args:
            target_file: Path to the file to backup
            category: Backup category (e.g., 'filesystem', 'structure')
            project_root: Root of the repository (defaults to CWD)

        Returns:
            Path to the backup file, or None if source doesn't exist
        """
        src = Path(target_file)
        if not src.exists():
            return None

        dest_dir = cls.get_backup_dir(category, project_root, timestamped=True)
        dest_file = dest_dir / src.name
        shutil.copy2(src, dest_file)
        return dest_file

    @classmethod
    def list_backups(cls, category: str, project_root: str | Path | None = None) -> list[Path]:
        """
        List all backup directories for a category.

        Args:
            category: Backup category to list
            project_root: Root of the repository (defaults to CWD)

        Returns:
            List of backup directory paths, sorted newest first
        """
        root = Path(project_root) if project_root else Path.cwd()
        category_dir = root / cls.BACKUP_ROOT / category

        if not category_dir.exists():
            return []

        return sorted(
            [d for d in category_dir.iterdir() if d.is_dir()],
            key=lambda x: x.name,
            reverse=True,
        )

    @classmethod
    def restore_backup(
        cls,
        backup_path: str | Path,
        target_path: str | Path,
        overwrite: bool = False,
    ) -> bool:
        """
        Restore files from a backup directory to a target location.

        Args:
            backup_path: Path to the backup directory
            target_path: Path to restore files to
            overwrite: If True, overwrite existing files

        Returns:
            True if restore succeeded, False otherwise
        """
        backup = Path(backup_path)
        target = Path(target_path)

        if not backup.exists():
            return False

        try:
            if backup.is_file():
                if target.exists() and not overwrite:
                    return False
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
            else:
                # Restore directory contents
                for item in backup.iterdir():
                    dest = target / item.name
                    if dest.exists() and not overwrite:
                        continue
                    if item.is_file():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest)
                    else:
                        shutil.copytree(item, dest, dirs_exist_ok=overwrite)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    @classmethod
    def decommission_legacy_backups(cls, project_root: str | Path | None = None) -> int:
        """
        Final cleanup of deprecated backup directories.

        Removes legacy backup directories that are no longer used:
        - .sovereign_healing_backup/
        - .governance_healer_backups/

        Args:
            project_root: Root of the repository (defaults to CWD)

        Returns:
            int: Number of legacy directories removed
        """
        root = Path(project_root) if project_root else Path.cwd()
        legacy_dirs = [".sovereign_healing_backup", ".governance_healer_backups"]
        removed_count = 0

        for legacy_name in legacy_dirs:
            legacy_path = root / legacy_name
            if legacy_path.exists() and legacy_path.is_dir():
                try:
                    shutil.rmtree(legacy_path)
                    removed_count += 1
                    print(f"Removed legacy backup directory: {legacy_path}")
                except OSError as e:
                    print(f"Error removing legacy backup {legacy_path}: {e}")

        return removed_count

    @classmethod
    def get_legacy_backup_dirs(cls, project_root: str | Path | None = None) -> list[Path]:
        """
        List any legacy backup directories that still exist.

        Args:
            project_root: Root of the repository (defaults to CWD)

        Returns:
            List of legacy backup directory paths that exist
        """
        root = Path(project_root) if project_root else Path.cwd()
        legacy_dirs = [".sovereign_healing_backup", ".governance_healer_backups"]

        existing = []
        for legacy_name in legacy_dirs:
            legacy_path = root / legacy_name
            if legacy_path.exists() and legacy_path.is_dir():
                existing.append(legacy_path)

        return existing
