from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg

"\nStateManagementAgent - Consolidated L4 State Controller (Phase 5)\n\nConsolidates:\n- ManifestManagerAgent (manifest inventory and serialization)\n- MemoryManagerAgent (physical memory cleanup and persistence)\n- AutonomousStateGuardianAgent (drift detection and integrity monitoring)\n\nKey Features:\n- Unified state controller coordinating manifest and physical storage\n- Atomic state transactions preventing race conditions\n- Autonomous heartbeat for continuous integrity checks\n- Ghost state detection (files without manifest entries)\n- Orphan entry detection (manifest entries without files)\n- Resource synchronization with registry agents\n\nTerritory: agentic_core/L4_state/memory/\nCanon Alignment: L4 state persistence, integrity, and recovery\n"
import asyncio
import hashlib
import json
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from agentic_core.utils.ssot_discovery_validator import get_data_files

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.determinism.execution_proof_emitter import ExecutionProofEmitter
from agentic_core.L2_execution.enforcement.write_governor_mixin import WriteGovernorMixin
from agentic_core.L4_persistence.lifecycle.lifecycle_policy_applier import (
    apply_simple_lifecycle_policy,
)
from agentic_core.L4_state.authority.run_state_authority import get_run_state_authority
from agentic_core.L5_safety.enforcement.policy_action_contract import (
    ActionClass,
    PolicyEnforcementError,
    enforce_policy_before_action,
)
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)
_proof_emitter = ExecutionProofEmitter("L3.StateManagementAgent")


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


@dataclass
class StateManagementAgent(WriteGovernorMixin, SovereignBaseAgent):
    """
    Unified L4 State Controller.

    Manages the manifest inventory, physical memory cleanup, and integrity guardianship.
    Consolidates ManifestManager, MemoryManager, and AutonomousStateGuardian.

    Features:
    - Atomic state transactions (manifest + physical storage)
    - Continuous integrity monitoring via heartbeat
    - Ghost/orphan detection and resolution
    - Resource synchronization with registry agents
    - Automatic cleanup with configurable retention

    Inherits from SovereignBaseAgent which provides:
        - HealerMixin: heal_repository() for self-repair
        - MCPHardenedMixin: Hardened MCP with retry/timeout
        - RedisCacheMixin: Short-term caching
        - PineconeVectorMixin: Long-term semantic memory
    """

    name: str = "StateManagementAgent"
    layer: str = "L4"
    memory_root: Path = field(default_factory=lambda: Path(".canon_memory"))
    heartbeat_interval: int = 300
    retention_days: int = 7
    max_entries: int = 1000
    _manifest: dict[str, StateEntry] = field(default_factory=dict)
    _lock: threading.RLock = field(default_factory=threading.RLock)
    _heartbeat_task: asyncio.Task | None = None
    _last_integrity_check: datetime = field(default_factory=datetime.now)
    _is_recovering: bool = False
    _registry_callbacks: list[Callable] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize the unified state management agent."""
        if isinstance(self.memory_root, str):
            self.memory_root = Path(self.memory_root)
        if not isinstance(self._manifest, dict):
            self._manifest = {}
        if not isinstance(self._registry_callbacks, list):
            self._registry_callbacks = []
        if not hasattr(self, "_lock") or self._lock is None:
            self._lock = threading.RLock()
        self._ensure_infrastructure()
        self._load_manifest()
        Logger.info(f"StateManagementAgent initialized at {self.memory_root}")

    def _ensure_infrastructure(self) -> None:
        """Ensure directories exist and manifest is initialized."""
        _wg.ensure_dir(self.memory_root)
        _wg.ensure_dir(self.memory_root / "conversations")
        _wg.ensure_dir(self.memory_root / "results")
        _wg.ensure_dir(self.memory_root / "state")
        _wg.ensure_dir(self.memory_root / "checkpoints")
        self.manifest_path = self.memory_root / "manifest.json"
        self.manifest_backup = self.memory_root / "manifest.json.bak"
        if not self.manifest_path.exists():
            self._write_manifest_raw(
                {
                    "version": "2.0",
                    "created_at": datetime.now().isoformat(),
                    "entries": {},
                    "stats": {"total_entries": 0, "last_cleanup": None, "last_integrity_check": None},
                }
            )

    @property
    def manifest_path(self) -> Path:
        return self.memory_root / "manifest.json"

    @manifest_path.setter
    def manifest_path(self, value: Path) -> None:
        pass

    @property
    def manifest_backup(self) -> Path:
        return self.memory_root / "manifest.json.bak"

    @manifest_backup.setter
    def manifest_backup(self, value: Path) -> None:
        pass

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
                    except Exception as e:
                        raise
                        Logger.warning(f"Failed to load manifest entry {key}: {e}")
                Logger.debug(f"Loaded {len(self._manifest)} manifest entries")
            except Exception as e:
                raise
                Logger.error(f"Failed to load manifest: {e}")
                if self.manifest_backup.exists():
                    Logger.info("Attempting to restore from backup...")
                    _wg.copy_file(self.manifest_backup, self.manifest_path)
                    self._load_manifest()

    def _save_manifest(self) -> None:
        """Save manifest to disk with backup."""
        with self._lock:
            if self.manifest_path.exists():
                _wg.copy_file(self.manifest_path, self.manifest_backup)
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
        _wg.write_json(self.manifest_path, data, indent=2)

    def _read_manifest_raw(self) -> dict[str, Any]:
        """Read raw manifest data from disk."""
        with open(self.manifest_path, encoding="utf-8") as f:
            return json.load(f)

    def set_state(self, key: str, data: Any, metadata: dict[str, Any] | None = None) -> str:
        """
        Atomically set state data with manifest tracking.

        Args:
            key: Unique key for the state entry
            data: Data to persist (will be JSON serialized)
            metadata: Optional metadata

        Returns:
            File path where data was stored
        """
        _emit_records_execution_trace(key, LayerSegment.L3_ORCHESTRATION, f"StateManagementAgent.set_state:{key}")
        with _proof_emitter.proof_op(f"set_state:{key}"):
            pass
        try:
            enforce_policy_before_action(
                action_name=f"set_state:{key}",
                action_class=ActionClass.PERSISTENT_MUTATION,
                actor_id="StateManagementAgent",
            )
        except PolicyEnforcementError as _pee:
            Logger.error("Policy blocked set_state %s: %s", key, _pee)
            return ""
        _rsa = get_run_state_authority()
        _rsa.commit(key, data, actor_id="StateManagementAgent", reason_code="set_state")
        _rsa.snapshot_state(f"state_set:{key}", run_id="StateManagementAgent")
        with self._lock:
            file_path = self.memory_root / "state" / f"{key}.json"
            data_json = json.dumps(data, sort_keys=True, default=str)
            file_hash = hashlib.md5(data_json.encode()).hexdigest()
            _wg.ensure_dir(file_path.parent)
            _wg.write_json(file_path, data, indent=2)
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
            self._mcp8_mirror_set(key, data)

            # P3/L4: Apply state lifecycle governance for write operations
            try:
                state_namespace = f"state_memory.{key}"
                apply_simple_lifecycle_policy(
                    state_namespace=state_namespace,
                    access_type="write",
                    actor_id="StateManagementAgent",
                )
                Logger.debug(
                    "STATE_LIFECYCLE_GOVERNED namespace=%s operation=set_state",
                    state_namespace,
                )
            except Exception as _lifecycle_exc:
                Logger.error("STATE_LIFECYCLE_ERROR: %s", _lifecycle_exc)
                # Continue - lifecycle failure should not block state operations

            Logger.debug(f"State set: {key}")
            return str(file_path)

    def _mcp8_mirror_set(self, key: str, data: Any) -> None:
        """Mirror state to MCP memory server (mcp8) for cross-session persistence.

        Non-blocking — failures are logged but never propagate to callers.
        L4 file-based state remains the authoritative source of truth.
        """
        try:
            from mcp8_add_observations import mcp8_add_observations
            from mcp8_create_entities import mcp8_create_entities
            from mcp8_search_nodes import mcp8_search_nodes

            entity_name = f"state:{key}"
            observation = json.dumps(data, sort_keys=True, default=str)
            existing = mcp8_search_nodes(query=entity_name)
            nodes = existing.get("entities", []) if isinstance(existing, dict) else []
            if any(n.get("name") == entity_name for n in nodes):
                mcp8_add_observations(observations=[{"entityName": entity_name, "contents": [observation]}])
            else:
                mcp8_create_entities(
                    entities=[
                        {
                            "name": entity_name,
                            "entityType": "StateEntry",
                            "observations": [observation],
                        }
                    ]
                )
            Logger.debug(f"[mcp8] Mirrored state: {key}")
        except ImportError:
            pass
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.debug(f"[mcp8] Mirror failed for {key}: {e}")

    def get_state(self, key: str) -> Any | None:
        """
        Get state data by key.

        Args:
            key: State entry key

        Returns:
            Deserialized data or None if not found
        """
        get_run_state_authority().observe_runtime_state(
            "get_state", stage=key, actor_id="StateManagementAgent"
        )

        # P3/L4: Apply state lifecycle governance for read operations
        try:
            state_namespace = f"state_memory.{key}"
            apply_simple_lifecycle_policy(
                state_namespace=state_namespace,
                access_type="read",
                actor_id="StateManagementAgent",
            )
        except Exception as _lifecycle_exc:
            Logger.error("STATE_LIFECYCLE_ERROR: %s", _lifecycle_exc)
            # Continue - lifecycle failure should not block state operations

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
            except Exception as e:
                Logger.error(f"Failed to read state {key}: {e}")
                return None

    def delete_state(self, key: str) -> bool:
        """
        Atomically delete state data and manifest entry.

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
                _wg.remove_file(file_path)
            del self._manifest[key]
            self._save_manifest()
            self._notify_registry_update(key, "delete")
            Logger.debug(f"State deleted: {key}")
            return True

    def list_states(self, prefix: str | None = None) -> list[str]:
        """
        List all state keys, optionally filtered by prefix.

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
        """
        Synchronize manifest with physical disk state.
        Detects ghosts (unmapped files) and orphans (missing files).

        Returns:
            IntegrityReport with findings
        """
        with self._lock:
            self._last_integrity_check = datetime.now()
            physical_files: set[str] = set()
            for subdir in ["state", "conversations", "results", "checkpoints"]:
                subdir_path = self.memory_root / subdir
                if subdir_path.exists():
                    json_files = get_data_files(subdir_path, extensions=[".json"])
                    for file_path in json_files:
                        if file_path.name != "manifest.json":
                            rel_path = str(file_path.relative_to(self.memory_root))
                            physical_files.add(rel_path)
            manifest_files = {entry.file_path for entry in self._manifest.values()}
            ghost_files = list(physical_files - manifest_files)
            orphan_entries = list(manifest_files - physical_files)
            hash_mismatches = []
            for key, entry in self._manifest.items():
                file_path = self.memory_root / entry.file_path
                if file_path.exists():
                    try:
                        with open(file_path, "rb") as f:
                            current_hash = hashlib.md5(f.read()).hexdigest()
                        if current_hash != entry.file_hash:
                            hash_mismatches.append(key)
                    except Exception:
                        raise
                        pass
            if ghost_files:
                Logger.warning(f"Ghost files detected (unmapped): {len(ghost_files)}")
                for ghost in ghost_files[:5]:
                    Logger.warning(f"  - {ghost}")
            if orphan_entries:
                Logger.error(f"Orphan entries detected (missing files): {len(orphan_entries)}")
                for orphan in orphan_entries[:5]:
                    Logger.error(f"  - {orphan}")
            if hash_mismatches:
                Logger.warning(f"Hash mismatches detected: {len(hash_mismatches)}")
                for mismatch in hash_mismatches[:5]:
                    Logger.warning(f"  - {mismatch}")
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
        """
        Repair integrity issues found in validation.

        Args:
            report: Optional pre-computed integrity report

        Returns:
            Dictionary with repair counts
        """
        if report is None:
            report = self.validate_and_sync()
        with self._lock:
            self._is_recovering = True
            try:
                repaired = {"ghosts_mapped": 0, "orphans_removed": 0, "hashes_updated": 0}
                for ghost in report.ghost_files:
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
                for orphan in report.orphan_entries:
                    for key, entry in list(self._manifest.items()):
                        if entry.file_path == orphan:
                            del self._manifest[key]
                            repaired["orphans_removed"] += 1
                            break
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
            finally:
                self._is_recovering = False

    def perform_cleanup(self, retention_days: int | None = None) -> dict[str, int]:
        """
        Prune old state data based on retention policy.

        Args:
            retention_days: Days to retain (default: self.retention_days)

        Returns:
            Dictionary with cleanup counts
        """
        if retention_days is None:
            retention_days = self.retention_days
        with self._lock:
            cutoff = datetime.now() - timedelta(days=retention_days)
            cleaned = {"entries_removed": 0, "files_deleted": 0, "bytes_freed": 0}
            keys_to_remove = []
            for key, entry in self._manifest.items():
                if entry.updated_at < cutoff:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                entry = self._manifest[key]
                file_path = self.memory_root / entry.file_path
                if file_path.exists():
                    cleaned["bytes_freed"] += file_path.stat().st_size
                    _wg.remove_file(file_path)
                    cleaned["files_deleted"] += 1
                del self._manifest[key]
                cleaned["entries_removed"] += 1
            self._save_manifest()
            self.validate_and_sync()
            Logger.info(f"Cleanup complete (retention: {retention_days} days): {cleaned}")
            return cleaned

    def register_callback(self, callback: Callable[[str, str], None]) -> None:
        """
        Register a callback for state change notifications.

        Args:
            callback: Function(key, action) to call on state changes
        """
        self._registry_callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[str, str], None]) -> None:
        """Unregister a callback."""
        if callback in self._registry_callbacks:
            self._registry_callbacks.remove(callback)

    def _notify_registry_update(self, key: str, action: str) -> None:
        """Notify all registered callbacks of a state change."""
        for callback in self._registry_callbacks:
            try:
                callback(key, action)
            except Exception as e:
                raise
                Logger.warning(f"Registry callback failed: {e}")

    async def start_heartbeat(self) -> None:
        """Start the autonomous integrity monitoring heartbeat."""
        if self._heartbeat_task is not None:
            return
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        Logger.info(f"Heartbeat started (interval: {self.heartbeat_interval}s)")

    async def stop_heartbeat(self) -> None:
        """Stop the autonomous heartbeat."""
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
            Logger.info("Heartbeat stopped")

    async def _heartbeat_loop(self) -> None:
        """Main heartbeat loop for continuous integrity monitoring."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                report = self.validate_and_sync()
                if not report.is_healthy:
                    Logger.warning("Integrity issues detected, initiating repair...")
                    self.repair_integrity(report)
            except asyncio.CancelledError:
                break
            except Exception as e:
                raise
                Logger.error(f"Heartbeat error: {e}")

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        IHealerProtocol compliance method for state management violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        """
        try:
            violation_type = violation.get("type", "unknown")
            state_key = violation.get("state_key")
            file_path = violation.get("file_path")
            if violation_type == "manifest_corruption":
                try:
                    if self.manifest_path.exists():
                        backup_path = self.manifest_backup
                        _wg.copy_file(self.manifest_path, backup_path)
                    self._load_manifest()
                    return {
                        "status": "success",
                        "details": "Manifest restored from backup or recreated",
                        "artifacts": ["manifest.json"],
                        "errors": [],
                    }
                except Exception as e:
                    return {
                        "status": "failed",
                        "details": f"Failed to restore manifest: {str(e)}",
                        "artifacts": [],
                        "errors": [str(e)],
                    }
            elif violation_type == "orphaned_state_entry":
                if state_key:
                    if self.delete_state(state_key):
                        return {
                            "status": "success",
                            "details": f"Removed orphaned state entry: {state_key}",
                            "artifacts": [state_key],
                            "errors": [],
                        }
                    else:
                        return {
                            "status": "skipped",
                            "details": f"State entry not found: {state_key}",
                            "artifacts": [],
                            "errors": [],
                        }
            elif violation_type == "ghost_file":
                if file_path:
                    try:
                        file_path_obj = Path(file_path)
                        if file_path_obj.exists():
                            rel_path = str(file_path_obj.relative_to(self.memory_root))
                            key = file_path_obj.stem
                            with open(file_path_obj, "rb") as f:
                                file_hash = hashlib.md5(f.read()).hexdigest()
                            now = datetime.now()
                            self._manifest[key] = StateEntry(
                                key=key,
                                file_path=rel_path,
                                file_hash=file_hash,
                                created_at=now,
                                updated_at=now,
                                metadata={"auto_mapped": True},
                            )
                            self._save_manifest()
                            return {
                                "status": "success",
                                "details": f"Mapped ghost file to manifest: {rel_path}",
                                "artifacts": [key],
                                "errors": [],
                            }
                        else:
                            return {
                                "status": "skipped",
                                "details": f"Ghost file not found: {file_path}",
                                "artifacts": [],
                                "errors": [],
                            }
                    except Exception as e:
                        return {
                            "status": "failed",
                            "details": f"Failed to map ghost file: {str(e)}",
                            "artifacts": [],
                            "errors": [str(e)],
                        }
            elif violation_type == "integrity_repair":
                report = self.validate_and_sync()
                if not report.is_healthy:
                    repair_results = self.repair_integrity(report)
                    return {
                        "status": "success",
                        "details": f"Integrity repaired: {repair_results}",
                        "artifacts": ["integrity_repair"],
                        "errors": [],
                    }
                else:
                    return {
                        "status": "success",
                        "details": "State integrity verified - no repair needed",
                        "artifacts": [],
                        "errors": [],
                    }
            else:
                return {
                    "status": "skipped",
                    "details": f"Unknown violation type: {violation_type}",
                    "artifacts": [],
                    "errors": [],
                }
        except Exception as e:
            Logger.error(f"Heal operation failed in StateManagementAgent: {e}")
            return {
                "status": "failed",
                "details": f"Heal operation failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, Any]:
        """
        Repository-wide state healing.

        Args:
            dry_run: If True, only report issues without fixing
            execute: If True, execute healing actions
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of already-visited agents (cycle detection)

        Returns:
            Dictionary with healing results
        """
        super().heal_repository(
            dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path
        )
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            report = self.validate_and_sync()
            results = {
                "agent": agent_name,
                "ghost_files": len(report.ghost_files),
                "orphan_entries": len(report.orphan_entries),
                "hash_mismatches": len(report.hash_mismatches),
                "is_healthy": report.is_healthy,
                "dry_run": dry_run,
            }
            if execute and (not dry_run) and (not report.is_healthy):
                repair_results = self.repair_integrity(report)
                results["repair"] = repair_results
            return results
        finally:
            _call_path.discard(agent_name)

    def _run_self_tests(self) -> dict[str, Any]:
        """Run internal self-tests for the unified state management agent."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self.name == "StateManagementAgent"
            assert self.memory_root.exists()
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        try:
            test_key = "_self_test_key"
            test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
            self.set_state(test_key, test_data)
            retrieved = self.get_state(test_key)
            assert retrieved is not None
            assert retrieved["test"] == "data"
            self.delete_state(test_key)
            results["passed"] += 1
            results["tests"].append({"name": "test_set_get_state", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_set_get_state", "status": "failed", "error": str(e)})
        try:
            report = self.validate_and_sync()
            assert isinstance(report, IntegrityReport)
            assert hasattr(report, "is_healthy")
            results["passed"] += 1
            results["tests"].append({"name": "test_integrity_check", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_integrity_check", "status": "failed", "error": str(e)})
        try:
            assert self.manifest_path.exists()
            with open(self.manifest_path) as f:
                manifest_data = json.load(f)
            assert "version" in manifest_data
            assert "entries" in manifest_data
            results["passed"] += 1
            results["tests"].append({"name": "test_manifest_persistence", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append(
                {"name": "test_manifest_persistence", "status": "failed", "error": str(e)}
            )
        return results


def get_state_manager(memory_root: Path | None = None) -> StateManagementAgent:
    """
    Factory function to get StateManagementAgent instance.

    Args:
        memory_root: Optional memory root path

    Returns:
        StateManagementAgent instance
    """
    if memory_root is None:
        memory_root = Path(".canon_memory")
    return StateManagementAgent(memory_root=memory_root)


def get_manifest_manager(memory_root: Path | None = None) -> StateManagementAgent:
    """Get state manager (legacy ManifestManager compatibility)."""
    return get_state_manager(memory_root)


def get_memory_manager(memory_root: Path | None = None) -> StateManagementAgent:
    """Get state manager (legacy MemoryManager compatibility)."""
    return get_state_manager(memory_root)


def get_state_guardian(memory_root: Path | None = None) -> StateManagementAgent:
    """Get state manager (legacy StateGuardian compatibility)."""
    return get_state_manager(memory_root)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Unified State Management Agent")
    parser.add_argument("--root", type=str, default=".canon_memory", help="Memory root directory")
    parser.add_argument("--validate", action="store_true", help="Run integrity validation")
    parser.add_argument("--repair", action="store_true", help="Repair integrity issues")
    parser.add_argument("--cleanup", action="store_true", help="Run cleanup")
    parser.add_argument("--retention", type=int, default=7, help="Retention days for cleanup")
    parser.add_argument("--self-test", action="store_true", help="Run self-tests")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    manager = get_state_manager(Path(args.root))
    if args.self_test:
        results = manager._run_self_tests()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Self-tests: {results['passed']} passed, {results['failed']} failed")
            for test in results["tests"]:
                status = "✓" if test["status"] == "passed" else "✗"
                print(f"  {status} {test['name']}")
    elif args.validate:
        report = manager.validate_and_sync()
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print("\nIntegrity Report:")
            print(f"  Healthy: {report.is_healthy}")
            print(f"  Ghost files: {len(report.ghost_files)}")
            print(f"  Orphan entries: {len(report.orphan_entries)}")
            print(f"  Hash mismatches: {len(report.hash_mismatches)}")
    elif args.repair:
        report = manager.validate_and_sync()
        if not report.is_healthy:
            results = manager.repair_integrity(report)
            print(f"Repair results: {results}")
        else:
            print("No integrity issues to repair")
    elif args.cleanup:
        results = manager.perform_cleanup(args.retention)
        print(f"Cleanup results: {results}")
    else:
        print(f"State manager initialized at {manager.memory_root}")
        print(f"  Entries: {len(manager._manifest)}")
        print("  Use --validate, --repair, --cleanup, or --self-test")
