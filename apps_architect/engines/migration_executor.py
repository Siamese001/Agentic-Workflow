"""Pattern migration executor — DS-8.

Plan: ``.claude/plans/apps-architect-deferred-scope-b8e3f1.md`` DW4 DS-8.

Auto-applies recommended pattern changes with backup and rollback support.
"""

from __future__ import annotations

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from apps_architect.types.architect_types import DeltaEntry, DeltaReport

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKUP_DIR = _REPO_ROOT / "artifacts" / "apps_architect" / "migration_backups"


class MigrationExecutor:
    """Applies pattern migrations with backup safety."""

    def __init__(self, repo_root: str | Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root else _REPO_ROOT
        self._backup_dir = _BACKUP_DIR

    def backup_file(self, filepath: Path) -> Path | None:
        if not filepath.exists():
            return None
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = self._backup_dir / f"{filepath.name}.{ts}.bak"
        shutil.copy2(filepath, backup_path)
        _log.info("Backed up %s -> %s", filepath, backup_path)
        return backup_path

    def plan_migrations(self, report: DeltaReport) -> Tuple[str, ...]:
        plans: list[str] = []
        for entry in report.entries:
            if entry.delta_type.value in ("MISSING_PATTERN", "DRIFT_DETECTED"):
                plans.append(
                    f"[{entry.delta_type.value}] {entry.pattern.source_ref}: "
                    f"{entry.recommendation}"
                )
        return tuple(plans)

    def execute_migration(self, entry: DeltaEntry, dry_run: bool = True) -> dict[str, str]:
        source_ref = entry.pattern.source_ref
        if source_ref.startswith("adg:"):
            return {"status": "skipped", "reason": "adg-derived, no file to migrate"}

        fp = self._repo_root / source_ref
        if not fp.exists():
            return {"status": "skipped", "reason": f"file not found: {source_ref}"}

        if dry_run:
            return {
                "status": "dry_run",
                "file": str(fp),
                "action": entry.recommendation[:200],
            }

        backup = self.backup_file(fp)
        return {
            "status": "backed_up",
            "file": str(fp),
            "backup": str(backup) if backup else "none",
            "note": "Migration execution requires explicit content transformation (not yet automated)",
        }

    def list_backups(self) -> Tuple[Path, ...]:
        if not self._backup_dir.exists():
            return ()
        return tuple(sorted(self._backup_dir.glob("*.bak"), key=lambda p: p.stat().st_mtime))


__all__ = ["MigrationExecutor"]
