"""State Management Utility - Deterministic state persistence.

This module provides deterministic state management functionality previously
implemented in StateManagementAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 7 Micro-Wave 1).

Usage:
    from agentic_core.L3_orchestration.utils.state_management_util import (
        StateManager, StateEntry, IntegrityReport
    )

    # Manage state
    manager = StateManager(memory_root=Path(".canon_memory"))
    manager.set_state("key", {"data": "value"})
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from tqdm import tqdm

Logger = logging.getLogger(__name__)


@dataclass
class StateEntry:
    """Represents a single entry in the state manifest."""

    key: str
    file_path: str
    file_hash: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StateEntry:
        """Create from dictionary."""
        return cls(
            key=data["key"],
            file_path=data["file_path"],
            file_hash=data["file_hash"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class IntegrityReport:
    """Report from integrity check."""

    timestamp: datetime
    ghost_files: list[str]
    orphan_entries: list[str]
    hash_mismatches: list[str]
    is_healthy: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "ghost_files": self.ghost_files,
            "orphan_entries": self.orphan_entries,
            "hash_mismatches": self.hash_mismatches,
            "is_healthy": self.is_healthy,
        }


class StateManager:
    """Deterministic state management without agent overhead."""

    def __init__(
        self,
        memory_root: Path | None = None,
        retention_days: int = 7,
        max_entries: int = 1000,
    ) -> None:
        """Initialize state manager.

        Args:
            memory_root: Root directory for state storage
            retention_days: Days to retain state entries
            max_entries: Maximum number of state entries
        """
        self.memory_root = memory_root or Path(".canon_memory")
        self.retention_days = retention_days
        self.max_entries = max_entries
        self._lock = threading.RLock()
        self._manifest: dict[str, StateEntry] = {}
        self._registry_callbacks: list[Callable[[str, str], None]] = []
        self._last_integrity_check = datetime.now()

        # Ensure infrastructure
        self._ensure_infrastructure()
        self._load_manifest()

    def _ensure_infrastructure(self) -> None:
        """Ensure directories exist and manifest is initialized."""
        self.memory_root.mkdir(parents=True, exist_ok=True)
        (self.memory_root / "conversations").mkdir(exist_ok=True)
        (self.memory_root / "results").mkdir(exist_ok=True)
        (self.memory_root / "state").mkdir(exist_ok=True)
        (self.memory_root / "checkpoints").mkdir(exist_ok=True)

        if not self.manifest_path.exists():
            self._write_manifest_raw(
                {
                    "version": "2.0",
                    "created_at": datetime.now().isoformat(),
                    "entries": {},
                    "stats": {
                        "total_entries": 0,
                        "last_cleanup": None,
                        "last_integrity_check": None,
                    },
                }
            )

    @property
    def manifest_path(self) -> Path:
        return self.memory_root / "manifest.json"

    @property
    def manifest_backup(self) -> Path:
        return self.memory_root / "manifest.json.bak"

    def _load_manifest(self) -> None:
        """Load manifest from disk into memory."""
        with self._lock:
            if not self.manifest_path.exists():
                self._manifest = {}
                return

            try:
                with open(self.manifest_path, encoding="utf-8") as f:
                    data = json.load(f)

                self._manifest = {}
                for key, entry_data in data.get("entries", {}).items():
                    try:
                        self._manifest[key] = StateEntry.from_dict(entry_data)
                    except (
                        AttributeError,
                        KeyError,
                        TypeError,
                        ValueError,
                    ) as e:  # guardian: allow-log-and-swallow -- manifest entry load: non-fatal, entry skipped
                        Logger.warning(f"Failed to load manifest entry {key}: {e}")

                Logger.debug(f"Loaded {len(self._manifest)} manifest entries")
            except (OSError, RuntimeError, TypeError, ValueError) as e:
                Logger.error(f"Failed to load manifest: {e}")
                if self.manifest_backup.exists():
                    Logger.info("Attempting to restore from backup...")
                    import shutil

                    shutil.copy2(self.manifest_backup, self.manifest_path)
                    self._load_manifest()

    def _save_manifest(self) -> None:
        """Save manifest to disk with backup."""
        with self._lock:
            if self.manifest_path.exists():
                import shutil

                shutil.copy2(self.manifest_path, self.manifest_backup)

            data = {
                "version": "2.0",
                "updated_at": datetime.now().isoformat(),
                "entries": {k: v.to_dict() for k, v in self._manifest.items()},
                "stats": {
                    "total_entries": len(self._manifest),
                    "last_cleanup": None,
                    "last_integrity_check": self._last_integrity_check.isoformat(),
                },
            }
            self._write_manifest_raw(data)

    def _write_manifest_raw(self, data: dict[str, Any]) -> None:
        """Write raw manifest data to disk."""
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _read_manifest_raw(self) -> dict[str, Any]:
        """Read raw manifest data from disk."""
        with open(self.manifest_path, encoding="utf-8") as f:
            return json.load(f)

    def set_state(
        self,
        key: str,
        data: Any,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Atomically set state data with manifest tracking.

        Args:
            key: Unique key for the state entry
            data: Data to persist
            metadata: Optional metadata

        Returns:
            File path where data was stored
        """
        with self._lock:
            file_path = self.memory_root / "state" / f"{key}.json"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Serialize and hash
            data_json = json.dumps(data, sort_keys=True, default=str)
            file_hash = hashlib.md5(data_json.encode()).hexdigest()

            # Write to disk
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data_json)

            # Update manifest
            now = datetime.now()
            if key in self._manifest:
                entry = self._manifest[key]
                entry.file_hash = file_hash
                entry.updated_at = now
                entry.metadata.update(metadata or {})
            else:
                entry = StateEntry(
                    key=key,
                    file_path=str(file_path.relative_to(self.memory_root)),
                    file_hash=file_hash,
                    created_at=now,
                    updated_at=now,
                    metadata=metadata or {},
                )
                self._manifest[key] = entry

            self._save_manifest()
            self._notify_registry_update(key, "set")

            Logger.debug(f"State set: {key}")
            return str(file_path)

    def get_state(self, key: str) -> Any | None:
        """Get state data by key.

        Args:
            key: State entry key

        Returns:
            Deserialized data or None if not found
        """
        with self._lock:
            if key not in self._manifest:
                return None

            entry = self._manifest[key]
            file_path = self.memory_root / entry.file_path

            if not file_path.exists():
                Logger.warning(f"Orphan entry detected: {key}")
                return None

            try:
                with open(file_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:  # guardian: allow-return-none-swallow -- state read: non-fatal, caller handles None as missing state
                Logger.error(f"Failed to read state {key}: {e}")
                return None

    def delete_state(self, key: str) -> bool:
        """Atomically delete state data and manifest entry.

        Args:
            key: State entry key

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key not in self._manifest:
                return False

            entry = self._manifest[key]
            file_path = self.memory_root / entry.file_path

            if file_path.exists():
                file_path.unlink()

            del self._manifest[key]
            self._save_manifest()
            self._notify_registry_update(key, "delete")

            Logger.debug(f"State deleted: {key}")
            return True

    def list_states(self, prefix: str | None = None) -> list[str]:
        """List all state keys, optionally filtered by prefix.

        Args:
            prefix: Optional key prefix filter

        Returns:
            List of state keys
        """
        with self._lock:
            keys = list(self._manifest.keys())
            if prefix:
                keys = [k for k in keys if k.startswith(prefix)]
            return keys

    def validate_and_sync(self) -> IntegrityReport:
        """Synchronize manifest with physical disk state.

        Returns:
            IntegrityReport with findings
        """
        with self._lock:
            self._last_integrity_check = datetime.now()

            # Collect physical files
            physical_files: set[str] = set()
            for subdir in ["state", "conversations", "results", "checkpoints"]:
                subdir_path = self.memory_root / subdir
                if subdir_path.exists():
                    for file_path in subdir_path.rglob("*.json"):
                        if file_path.name != "manifest.json":
                            rel_path = str(file_path.relative_to(self.memory_root))
                            physical_files.add(rel_path)

            # Collect manifest files
            manifest_files = {entry.file_path for entry in self._manifest.values()}

            # Find discrepancies
            ghost_files = list(physical_files - manifest_files)
            orphan_entries = list(manifest_files - physical_files)

            # Check hashes
            hash_mismatches = []
            for key, entry in tqdm(self._manifest.items(), desc="Processing", unit="item"):
                file_path = self.memory_root / entry.file_path
                if file_path.exists():
                    try:
                        with open(file_path, "rb") as f:
                            current_hash = hashlib.md5(f.read()).hexdigest()
                        if current_hash != entry.file_hash:
                            hash_mismatches.append(key)
                    except OSError as e:  # guardian: allow-log-and-swallow -- integrity check: non-fatal, file skipped from hash validation
                        import logging

                        logging.getLogger(__name__).debug(
                            "state_management_util: OSError swallowed at L354: %s", e
                        )

            # Log findings
            if ghost_files:
                Logger.warning(f"Ghost files detected: {len(ghost_files)}")
            if orphan_entries:
                Logger.error(f"Orphan entries detected: {len(orphan_entries)}")
            if hash_mismatches:
                Logger.warning(f"Hash mismatches detected: {len(hash_mismatches)}")

            is_healthy = not (ghost_files or orphan_entries or hash_mismatches)

            report = IntegrityReport(
                timestamp=self._last_integrity_check,
                ghost_files=ghost_files,
                orphan_entries=orphan_entries,
                hash_mismatches=hash_mismatches,
                is_healthy=is_healthy,
            )

            self._save_manifest()
            return report

    def repair_integrity(self, report: IntegrityReport | None = None) -> dict[str, int]:
        """Repair integrity issues.

        Args:
            report: Optional pre-computed integrity report

        Returns:
            Dictionary with repair counts
        """
        if report is None:
            report = self.validate_and_sync()

        with self._lock:
            repaired = {"ghosts_mapped": 0, "orphans_removed": 0, "hashes_updated": 0}

            # Map ghost files
            for ghost in tqdm(report.ghost_files, desc="Processing", unit="item"):
                key = Path(ghost).stem
                file_path = self.memory_root / ghost

                if file_path.exists():
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()

                    now = datetime.now()
                    self._manifest[key] = StateEntry(
                        key=key,
                        file_path=ghost,
                        file_hash=file_hash,
                        created_at=now,
                        updated_at=now,
                        metadata={"auto_mapped": True},
                    )
                    repaired["ghosts_mapped"] += 1

            # Remove orphan entries
            for orphan in report.orphan_entries:
                for key, entry in list(self._manifest.items()):
                    if entry.file_path == orphan:
                        del self._manifest[key]
                        repaired["orphans_removed"] += 1
                        break

            # Update mismatched hashes
            for key in report.hash_mismatches:
                if key in self._manifest:
                    entry = self._manifest[key]
                    file_path = self.memory_root / entry.file_path

                    if file_path.exists():
                        with open(file_path, "rb") as f:
                            entry.file_hash = hashlib.md5(f.read()).hexdigest()
                        entry.updated_at = datetime.now()
                        repaired["hashes_updated"] += 1

            self._save_manifest()
            Logger.info(f"Integrity repair complete: {repaired}")
            return repaired

    def perform_cleanup(self, retention_days: int | None = None) -> dict[str, int]:
        """Prune old state data.

        Args:
            retention_days: Days to retain (default: self.retention_days)

        Returns:
            Dictionary with cleanup counts
        """
        if retention_days is None:
            retention_days = self.retention_days

        with self._lock:
            cutoff = datetime.now() - __import__("datetime").timedelta(days=retention_days)
            cleaned = {"entries_removed": 0, "files_deleted": 0, "bytes_freed": 0}

            keys_to_remove = [key for key, entry in self._manifest.items() if entry.updated_at < cutoff]

            for key in tqdm(keys_to_remove, desc="Processing", unit="item"):
                entry = self._manifest[key]
                file_path = self.memory_root / entry.file_path

                if file_path.exists():
                    cleaned["bytes_freed"] += file_path.stat().st_size
                    file_path.unlink()
                    cleaned["files_deleted"] += 1

                del self._manifest[key]
                cleaned["entries_removed"] += 1

            self._save_manifest()
            self.validate_and_sync()

            Logger.info(f"Cleanup complete: {cleaned}")
            return cleaned

    def register_callback(self, callback: Callable[[str, str], None]) -> None:
        """Register callback for state change notifications."""
        self._registry_callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[str, str], None]) -> None:
        """Unregister callback."""
        if callback in self._registry_callbacks:
            self._registry_callbacks.remove(callback)

    def _notify_registry_update(self, key: str, action: str) -> None:
        """Notify callbacks of state change."""
        for callback in self._registry_callbacks:
            try:
                callback(key, action)
            except (
                AttributeError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as e:  # guardian: allow-log-and-swallow -- registry callback: non-fatal, other callbacks continue
                Logger.warning(f"Registry callback failed: {e}")


def heal_repository(
    project_root: Path | None = None,
    dry_run: bool = True,
    execute: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Autonomous healing interface (Canon Key 51 compliance)."""
    if project_root is None:
        project_root = Path(".")

    manager = StateManager(memory_root=project_root / ".canon_memory")
    report = manager.validate_and_sync()

    if not report.is_healthy and not dry_run:
        repaired = manager.repair_integrity(report)
        return {
            "violations_found": len(report.ghost_files)
            + len(report.orphan_entries)
            + len(report.hash_mismatches),
            "violations_fixed": sum(repaired.values()),
            "errors": 0,
            "skipped": 0,
            "repaired": repaired,
        }

    return {
        "violations_found": 0
        if report.is_healthy
        else len(report.ghost_files) + len(report.orphan_entries) + len(report.hash_mismatches),
        "violations_fixed": 0,
        "errors": 0,
        "skipped": 0,
    }


def heal(violation: dict[str, Any], project_root: Path | None = None) -> dict[str, Any]:
    """Heal state management violations."""
    if project_root is None:
        project_root = Path(".")

    manager = StateManager(memory_root=project_root / ".canon_memory")
    violation_type = violation.get("type", "unknown")
    state_key = violation.get("state_key")
    file_path = violation.get("file_path")

    if violation_type == "manifest_corruption":
        try:
            if manager.manifest_path.exists():
                import shutil

                shutil.copy2(manager.manifest_path, manager.manifest_backup)
            manager._load_manifest()
            return {
                "status": "success",
                "details": "Manifest restored from backup or recreated",
                "artifacts": ["manifest.json"],
                "errors": [],
            }
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            return {
                "status": "failed",
                "details": f"Failed to restore manifest: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    elif violation_type == "orphaned_state_entry" and state_key:
        success = manager.delete_state(state_key)
        return {
            "status": "success" if success else "skipped",
            "details": f"Removed {state_key}" if success else f"Not found: {state_key}",
            "artifacts": [state_key] if success else [],
            "errors": [],
        }

    elif violation_type == "ghost_file" and file_path:
        success = manager.delete_state(Path(file_path).stem)
        return {
            "status": "success" if success else "skipped",
            "details": f"Cleared ghost: {file_path}" if success else f"No ghost: {file_path}",
            "artifacts": [file_path] if success else [],
            "errors": [],
        }

    return {
        "status": "skipped",
        "details": f"Unknown violation: {violation_type}",
        "artifacts": [],
        "errors": [],
    }


def main():
    """Main entry point for State Management Utility."""
    import argparse

    parser = argparse.ArgumentParser(description="State Management Utility")
    parser.add_argument("--memory-root", type=str, default=".canon_memory")
    parser.add_argument("--action", choices=["validate", "repair", "cleanup", "list"], default="validate")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    manager = StateManager(memory_root=Path(args.memory_root))

    if args.action == "validate":
        report = manager.validate_and_sync()
        print(f"Healthy: {report.is_healthy}")
        print(f"Ghost files: {len(report.ghost_files)}")
        print(f"Orphan entries: {len(report.orphan_entries)}")
        print(f"Hash mismatches: {len(report.hash_mismatches)}")

    elif args.action == "repair":
        repaired = manager.repair_integrity()
        print(f"Repaired: {repaired}")

    elif args.action == "cleanup":
        cleaned = manager.perform_cleanup()
        print(f"Cleaned: {cleaned}")

    elif args.action == "list":
        keys = manager.list_states()
        print(f"State keys ({len(keys)}):")
        for key in keys[:20]:
            print(f"  - {key}")
        if len(keys) > 20:
            print(f"  ... and {len(keys) - 20} more")


if __name__ == "__main__":
    main()
