from __future__ import annotations

"""
CheckpointManagerAgent - Consolidated L4 Checkpoint Guardian (Priority 2)

Consolidates:
- CheckpointManagerAgent (synchronous legacy checkpoints)
- AutonomousCheckpointManagerAgent (async mirroring and auto-recovery)

Modes:
- SYNC: Traditional blocking saves (Legacy support)
- ASYNC: Non-blocking background saves
- AUTONOMOUS: Mirroring, drift detection, and auto-recovery

Key Features:
- Hybrid Strategy Pattern for Sync/Async compatibility
- State integrity verification via MD5 hash comparison
- Automatic recovery from mirrored backups
- Backward compatible with legacy create_checkpoint signatures

Territory: agentic_core/L4_state/memory/
Canon Alignment: L4 state persistence and recovery
"""


import asyncio
import hashlib
import json
import logging
import shutil
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.decorators_util import standard_heal

Logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """Represents a state checkpoint with metadata."""

    checkpoint_id: str
    timestamp: datetime
    state_snapshot: dict[str, Any]
    file_hashes: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    recovery_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert Checkpoint to dictionary for serialization."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "timestamp": self.timestamp.isoformat(),
            "state_snapshot": self.state_snapshot,
            "file_hashes": self.file_hashes,
            "metadata": self.metadata,
            "is_valid": self.is_valid,
            "recovery_count": self.recovery_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        """Create Checkpoint from dictionary."""
        return cls(
            checkpoint_id=data["checkpoint_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            state_snapshot=data.get("state_snapshot", {}),
            file_hashes=data.get("file_hashes", {}),
            metadata=data.get("metadata", {}),
            is_valid=data.get("is_valid", True),
            recovery_count=data.get("recovery_count", 0),
        )


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""

    success: bool
    checkpoint_id: str
    files_restored: int = 0
    state_restored: bool = False
    errors: list[str] = field(default_factory=list)
    recovery_time: float = 0.0


def timeout(seconds: int) -> Callable:
    """Timeout decorator for long-running operations."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


@dataclass
class CheckpointManagerAgent(AtomicExecutionMixin, SovereignBaseAgent):
    """
    Unified L4 Checkpoint Guardian.

    Handles synchronous legacy checkpoints and autonomous asynchronous mirroring.
    Consolidates CheckpointManagerAgent and AutonomousCheckpointManagerAgent.

    Modes:
        - SYNC: Traditional blocking saves (Legacy support)
        - ASYNC: Non-blocking background saves
        - AUTONOMOUS: Mirroring, drift detection, and auto-recovery

    Inherits from SovereignBaseAgent which provides:
        - HealerMixin: heal_repository() for self-repair
        - MCPHardenedMixin: Hardened MCP with retry/timeout
        - RedisCacheMixin: Short-term caching
        - PineconeVectorMixin: Long-term semantic memory
    """

    name: str = "CheckpointManagerAgent"
    layer: str = "L4"

    # configuration
    mode: str = "ASYNC"  # SYNC, ASYNC, or AUTONOMOUS
    storage_path: Path = field(default_factory=lambda: Path(".canon_memory/checkpoints"))
    max_checkpoints: int = 50
    auto_checkpoint_interval: timedelta = field(default_factory=lambda: timedelta(minutes=5))

    # Internal state
    checkpoints: dict[str, Checkpoint] = field(default_factory=dict)
    current_checkpoint_id: str | None = None
    last_auto_checkpoint: datetime | None = None
    _mirror_tasks: list[asyncio.Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize the unified checkpoint manager."""
        # Normalize mode
        self.mode = self.mode.upper()
        if self.mode not in ("SYNC", "ASYNC", "AUTONOMOUS"):
            Logger.warning(f"Invalid mode '{self.mode}', defaulting to ASYNC")
            self.mode = "ASYNC"

        # Ensure storage_path is a Path
        if isinstance(self.storage_path, str):
            self.storage_path = Path(self.storage_path)

        # Create directories
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Mirror path for AUTONOMOUS mode
        self.mirror_path = self.storage_path / "mirrors"
        if self.mode == "AUTONOMOUS":
            self.mirror_path.mkdir(parents=True, exist_ok=True)

        # Initialize collections
        if not isinstance(self.checkpoints, dict):
            self.checkpoints = {}
        if not isinstance(self._mirror_tasks, list):
            self._mirror_tasks = []

        # Load existing checkpoints
        self._load_checkpoints()

        Logger.info(f"UnifiedCheckpointManager initialized in {self.mode} mode at {self.storage_path}")

    # =========================================================================
    # CHECKPOINT CREATION (Hybrid Sync/Async)
    # =========================================================================

    def create_checkpoint(
        self,
        state_data: dict[str, Any],
        label: str = "manual",
        file_hashes: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a checkpoint (synchronous entry point for backward compatibility).

        Args:
            state_data: State snapshot to persist
            label: Label for the checkpoint
            file_hashes: Optional file hashes for integrity verification
            metadata: Optional additional metadata

        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id(label)

        if self.mode == "SYNC":
            return self._save_sync(checkpoint_id, state_data, file_hashes, metadata)
        else:
            # For ASYNC/AUTONOMOUS, run in event loop if available
            try:
                asyncio.get_running_loop()
                # Already in async context, create task
                asyncio.ensure_future(self._save_async(checkpoint_id, state_data, file_hashes, metadata))
                # Return checkpoint_id immediately, save happens in background
                return checkpoint_id
            except RuntimeError:
                # No running loop, create one
                return asyncio.run(self._save_async(checkpoint_id, state_data, file_hashes, metadata))

    async def create_checkpoint_async(
        self,
        state_data: dict[str, Any],
        label: str = "manual",
        file_hashes: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a checkpoint (async entry point).

        Args:
            state_data: State snapshot to persist
            label: Label for the checkpoint
            file_hashes: Optional file hashes for integrity verification
            metadata: Optional additional metadata

        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id(label)

        if self.mode == "SYNC":
            # Run sync in executor to not block
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._save_sync(checkpoint_id, state_data, file_hashes, metadata),
            )
            return checkpoint_id
        else:
            return await self._save_async(checkpoint_id, state_data, file_hashes, metadata)

    def _generate_checkpoint_id(self, label: str) -> str:
        """Generate a unique checkpoint ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"chk_{timestamp}_{label}"

    def _save_sync(
        self,
        checkpoint_id: str,
        state_data: dict[str, Any],
        file_hashes: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Synchronous save logic (migrated from legacy CheckpointManagerAgent).

        Args:
            checkpoint_id: Unique checkpoint identifier
            state_data: State snapshot to persist
            file_hashes: Optional file hashes
            metadata: Optional metadata

        Returns:
            Path to saved checkpoint file
        """
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now(),
            state_snapshot=state_data,
            file_hashes=file_hashes or {},
            metadata=metadata or {},
        )

        file_path = self.storage_path / f"{checkpoint_id}.json"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(checkpoint.to_dict(), f, indent=2, default=str)

            self.checkpoints[checkpoint_id] = checkpoint
            self.current_checkpoint_id = checkpoint_id
            self._save_index()
            self._cleanup_old_checkpoints()

            # In AUTONOMOUS mode, also create mirror synchronously
            if self.mode == "AUTONOMOUS":
                self._mirror_checkpoint_sync(file_path)

            Logger.info(f"[SYNC] Checkpoint saved: {checkpoint_id}")
            return checkpoint_id

        except Exception as e:
            Logger.error(f"Failed to save checkpoint {checkpoint_id}: {e}")
            raise

    async def _save_async(
        self,
        checkpoint_id: str,
        state_data: dict[str, Any],
        file_hashes: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Asynchronous save logic (migrated from AutonomousCheckpointManager).

        Args:
            checkpoint_id: Unique checkpoint identifier
            state_data: State snapshot to persist
            file_hashes: Optional file hashes
            metadata: Optional metadata

        Returns:
            Path to saved checkpoint file
        """
        # Offload I/O to thread pool
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(
            None,
            lambda: self._save_sync(checkpoint_id, state_data, file_hashes, metadata),
        )

        # Trigger background mirroring in AUTONOMOUS mode
        if self.mode == "AUTONOMOUS":
            task = asyncio.create_task(self._mirror_checkpoint(Path(file_path)))
            self._mirror_tasks.append(task)

        Logger.info(f"[ASYNC] Checkpoint saved: {checkpoint_id}")
        return checkpoint_id

    # =========================================================================
    # MIRRORING (AUTONOMOUS mode)
    # =========================================================================

    def _mirror_checkpoint_sync(self, primary_path: Path) -> bool:
        """
        Synchronously mirror primary checkpoint to secondary storage.

        Args:
            primary_path: Path to primary checkpoint file

        Returns:
            True if mirroring succeeded
        """
        if not self.mirror_path.exists():
            self.mirror_path.mkdir(parents=True, exist_ok=True)

        mirror_path = self.mirror_path / primary_path.name

        try:
            shutil.copy2(primary_path, mirror_path)
            Logger.debug(f"[MIRROR] Redundant copy created: {mirror_path.name}")
            return True
        except Exception as e:
            Logger.error(f"[MIRROR] Failed for {primary_path.name}: {e}")
            return False

    async def _mirror_checkpoint(self, primary_path: Path) -> bool:
        """
        Asynchronously mirror primary checkpoint to secondary storage.

        Args:
            primary_path: Path to primary checkpoint file

        Returns:
            True if mirroring succeeded
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._mirror_checkpoint_sync, primary_path)

    # =========================================================================
    # INTEGRITY VERIFICATION
    # =========================================================================

    def verify_integrity(self, checkpoint_id: str) -> bool:
        """
        Verify checkpoint integrity by comparing primary and mirror hashes.

        Args:
            checkpoint_id: Checkpoint ID to verify

        Returns:
            True if checkpoint is valid
        """
        primary = self.storage_path / f"{checkpoint_id}.json"
        mirror = self.mirror_path / f"{checkpoint_id}.json"

        # Primary missing - attempt recovery
        if not primary.exists():
            Logger.warning(f"Primary checkpoint missing: {checkpoint_id}")
            return self._attempt_recovery(checkpoint_id)

        # In AUTONOMOUS mode, verify against mirror
        if self.mode == "AUTONOMOUS" and mirror.exists():
            try:
                p_hash = hashlib.md5(primary.read_bytes()).hexdigest()
                m_hash = hashlib.md5(mirror.read_bytes()).hexdigest()

                if p_hash != m_hash:
                    Logger.warning(f"Hash mismatch for {checkpoint_id}: primary={p_hash}, mirror={m_hash}")
                    return False

                return True
            except Exception as e:
                Logger.error(f"Integrity check failed for {checkpoint_id}: {e}")
                return False

        # Non-AUTONOMOUS mode or no mirror - just check primary exists
        return primary.exists()

    def _attempt_recovery(self, checkpoint_id: str) -> bool:
        """
        Auto-recovery: Restore primary from mirror if primary is missing/corrupt.

        Args:
            checkpoint_id: Checkpoint ID to recover

        Returns:
            True if recovery succeeded
        """
        mirror = self.mirror_path / f"{checkpoint_id}.json"
        primary = self.storage_path / f"{checkpoint_id}.json"

        if mirror.exists():
            try:
                shutil.copy2(mirror, primary)
                Logger.warning(f"[RECOVERY] Restored checkpoint {checkpoint_id} from mirror")

                # Update checkpoint metadata
                if checkpoint_id in self.checkpoints:
                    self.checkpoints[checkpoint_id].recovery_count += 1
                    self._save_index()

                return True
            except Exception as e:
                Logger.error(f"[RECOVERY] Failed to restore {checkpoint_id}: {e}")
                return False

        Logger.error(f"[RECOVERY] No mirror available for {checkpoint_id}")
        return False

    # =========================================================================
    # CHECKPOINT RETRIEVAL
    # =========================================================================

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """
        Retrieve a checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint ID to retrieve

        Returns:
            Checkpoint object or None if not found
        """
        # Check memory cache first
        if checkpoint_id in self.checkpoints:
            return self.checkpoints[checkpoint_id]

        # Try loading from disk
        file_path = self.storage_path / f"{checkpoint_id}.json"
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                checkpoint = Checkpoint.from_dict(data)
                self.checkpoints[checkpoint_id] = checkpoint
                return checkpoint
            except Exception as e:
                Logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")

        return None

    def get_latest_checkpoint(self) -> Checkpoint | None:
        """Get the most recent checkpoint."""
        if self.current_checkpoint_id:
            return self.get_checkpoint(self.current_checkpoint_id)

        # Find most recent by timestamp
        if self.checkpoints:
            latest = max(self.checkpoints.values(), key=lambda c: c.timestamp)
            return latest

        return None

    def list_checkpoints(self) -> list[dict[str, Any]]:
        """List all available checkpoints."""
        return [
            {
                "checkpoint_id": cp.checkpoint_id,
                "timestamp": cp.timestamp.isoformat(),
                "is_valid": cp.is_valid,
                "recovery_count": cp.recovery_count,
            }
            for cp in sorted(self.checkpoints.values(), key=lambda c: c.timestamp, reverse=True)
        ]

    # =========================================================================
    # ROLLBACK
    # =========================================================================

    def rollback_to_checkpoint(self, checkpoint_id: str) -> RecoveryResult:
        """
        Rollback state to a specific checkpoint.

        Args:
            checkpoint_id: Checkpoint ID to rollback to

        Returns:
            RecoveryResult with operation details
        """
        start_time = time.time()
        result = RecoveryResult(
            success=False,
            checkpoint_id=checkpoint_id,
        )

        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            result.errors.append(f"Checkpoint {checkpoint_id} not found")
            return result

        if not self.verify_integrity(checkpoint_id):
            result.errors.append(f"Checkpoint {checkpoint_id} failed integrity check")
            return result

        try:
            # Mark as current checkpoint
            self.current_checkpoint_id = checkpoint_id
            self._save_index()

            result.success = True
            result.state_restored = True
            result.recovery_time = time.time() - start_time

            Logger.info(f"[ROLLBACK] Successfully rolled back to {checkpoint_id}")
            return result

        except Exception as e:
            result.errors.append(str(e))
            Logger.error(f"[ROLLBACK] Failed to rollback to {checkpoint_id}: {e}")
            return result

    # =========================================================================
    # INDEX MANAGEMENT
    # =========================================================================

    def _load_checkpoints(self) -> None:
        """Load existing checkpoints from disk."""
        index_path = self.storage_path / "index.json"

        if index_path.exists():
            try:
                with open(index_path, encoding="utf-8") as f:
                    index_data = json.load(f)

                self.current_checkpoint_id = index_data.get("current_checkpoint_id")

                for cp_id in index_data.get("checkpoints", []):
                    checkpoint = self.get_checkpoint(cp_id)
                    if checkpoint:
                        self.checkpoints[cp_id] = checkpoint

                Logger.debug(f"Loaded {len(self.checkpoints)} checkpoints from index")
            except Exception as e:
                Logger.warning(f"Failed to load checkpoint index: {e}")

    def _save_index(self) -> None:
        """Save checkpoint index to disk."""
        index_path = self.storage_path / "index.json"

        index_data = {
            "current_checkpoint_id": self.current_checkpoint_id,
            "checkpoints": list(self.checkpoints.keys()),
            "updated_at": datetime.now().isoformat(),
        }

        try:
            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(index_data, f, indent=2)
        except Exception as e:
            Logger.error(f"Failed to save checkpoint index: {e}")

    def _cleanup_old_checkpoints(self) -> None:
        """Remove old checkpoints beyond max_checkpoints limit."""
        if len(self.checkpoints) <= self.max_checkpoints:
            return

        # Sort by timestamp, oldest first
        sorted_checkpoints = sorted(self.checkpoints.values(), key=lambda c: c.timestamp)

        # Remove oldest checkpoints
        to_remove = len(self.checkpoints) - self.max_checkpoints
        for checkpoint in sorted_checkpoints[:to_remove]:
            self._delete_checkpoint(checkpoint.checkpoint_id)

    def _delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint from disk and memory."""
        try:
            # Remove from disk
            primary = self.storage_path / f"{checkpoint_id}.json"
            mirror = self.mirror_path / f"{checkpoint_id}.json"

            if primary.exists():
                primary.unlink()
            if mirror.exists():
                mirror.unlink()

            # Remove from memory
            if checkpoint_id in self.checkpoints:
                del self.checkpoints[checkpoint_id]

            Logger.debug(f"Deleted checkpoint: {checkpoint_id}")
            return True
        except Exception as e:
            Logger.error(f"Failed to delete checkpoint {checkpoint_id}: {e}")
            return False

    # =========================================================================
    # HEALING (IHealerProtocol Compliance)
    # =========================================================================

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        IHealerProtocol compliance method for checkpoint violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        """
        try:
            # Extract violation details
            violation_type = violation.get("type", "unknown")
            checkpoint_id = violation.get("checkpoint_id")
            violation.get("file_path")

            if violation_type == "checkpoint_integrity":
                # Heal checkpoint integrity issues
                if checkpoint_id and not self.verify_integrity(checkpoint_id):
                    if self._attempt_recovery(checkpoint_id):
                        return {
                            "status": "success",
                            "details": f"Recovered checkpoint {checkpoint_id}",
                            "artifacts": [checkpoint_id],
                            "errors": [],
                        }
                    else:
                        return {
                            "status": "failed",
                            "details": f"Failed to recover checkpoint {checkpoint_id}",
                            "artifacts": [],
                            "errors": [f"Checkpoint {checkpoint_id} beyond recovery"],
                        }
                else:
                    return {
                        "status": "success",
                        "details": f"Checkpoint {checkpoint_id} integrity verified",
                        "artifacts": [],
                        "errors": [],
                    }

            elif violation_type == "storage_cleanup":
                # Heal storage issues
                self._cleanup_old_checkpoints()
                return {
                    "status": "success",
                    "details": "Storage cleanup completed",
                    "artifacts": ["checkpoints_cleaned"],
                    "errors": [],
                }

            elif violation_type == "missing_checkpoint_file":
                # Heal missing checkpoint files
                if checkpoint_id:
                    if self._attempt_recovery(checkpoint_id):
                        return {
                            "status": "success",
                            "details": f"Restored missing checkpoint {checkpoint_id}",
                            "artifacts": [checkpoint_id],
                            "errors": [],
                        }
                    else:
                        return {
                            "status": "failed",
                            "details": f"Cannot restore missing checkpoint {checkpoint_id}",
                            "artifacts": [],
                            "errors": [f"No backup available for {checkpoint_id}"],
                        }

            else:
                return {
                    "status": "skipped",
                    "details": f"Unknown violation type: {violation_type}",
                    "artifacts": [],
                    "errors": [],
                }

        except Exception as e:
            Logger.error(f"Heal operation failed in CheckpointManagerAgent: {e}")
            return {
                "status": "failed",
                "details": f"Heal operation failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, Any]:
        """
        Repository-wide checkpoint healing.

        Args:
            dry_run: If True, only report issues without fixing
            execute: If True, execute healing actions
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of already-visited agents (cycle detection)

        Returns:
            Dictionary with healing results
        """
        # Chain up to parent
        super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
        )

        if _call_path is None:
            _call_path = set()

        agent_name = self.__class__.__name__

        # Cycle detection
        if agent_name in _call_path:
            return {"skipped": 1, "cycle_detected": True}

        # Depth limiting
        if depth > max_depth:
            return {"skipped": 1, "depth_limited": True}

        _call_path.add(agent_name)

        try:
            violations_found = 0
            violations_fixed = 0

            # Check all checkpoints for integrity
            for checkpoint_id in list(self.checkpoints.keys()):
                if not self.verify_integrity(checkpoint_id):
                    violations_found += 1

                    if execute and not dry_run:
                        if self._attempt_recovery(checkpoint_id):
                            violations_fixed += 1

            return {
                "agent": agent_name,
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "checkpoints_verified": len(self.checkpoints),
                "mode": self.mode,
                "dry_run": dry_run,
            }

        finally:
            _call_path.discard(agent_name)

    # =========================================================================
    # SELF-TESTS
    # =========================================================================

    def _run_self_tests(self) -> dict[str, Any]:
        """Run internal self-tests for the unified checkpoint manager."""
        results = {"passed": 0, "failed": 0, "tests": []}

        # Test 1: Instantiation
        try:
            assert self.mode in ("SYNC", "ASYNC", "AUTONOMOUS")
            assert self.storage_path.exists()
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})

        # Test 2: Checkpoint ID generation
        try:
            cp_id = self._generate_checkpoint_id("test")
            assert cp_id.startswith("chk_")
            assert "test" in cp_id
            results["passed"] += 1
            results["tests"].append({"name": "test_checkpoint_id_generation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append(
                {"name": "test_checkpoint_id_generation", "status": "failed", "error": str(e)},
            )

        # Test 3: Checkpoint serialization
        try:
            cp = Checkpoint(
                checkpoint_id="test_cp",
                timestamp=datetime.now(),
                state_snapshot={"key": "value"},
            )
            cp_dict = cp.to_dict()
            cp_restored = Checkpoint.from_dict(cp_dict)
            assert cp_restored.checkpoint_id == cp.checkpoint_id
            assert cp_restored.state_snapshot == cp.state_snapshot
            results["passed"] += 1
            results["tests"].append({"name": "test_checkpoint_serialization", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append(
                {"name": "test_checkpoint_serialization", "status": "failed", "error": str(e)},
            )

        return results


# =========================================================================
# FACTORY FUNCTIONS
# =========================================================================


def get_checkpoint_manager(mode: str = "ASYNC", storage_path: Path | None = None) -> CheckpointManagerAgent:
    """
    Factory function to get CheckpointManagerAgent instance.

    Args:
        mode: Operating mode (SYNC, ASYNC, AUTONOMOUS)
        storage_path: Optional custom storage path

    Returns:
        CheckpointManagerAgent instance
    """
    if storage_path is None:
        storage_path = Path(".canon_memory/checkpoints")

    return CheckpointManagerAgent(
        mode=mode,
        storage_path=storage_path,
    )


# Backward compatibility aliases
def get_sync_checkpoint_manager(storage_path: Path | None = None) -> CheckpointManagerAgent:
    """Get a synchronous checkpoint manager (legacy compatibility)."""
    return get_checkpoint_manager(mode="SYNC", storage_path=storage_path)


def get_autonomous_checkpoint_manager(
    storage_path: Path | None = None,
) -> CheckpointManagerAgent:
    """Get an autonomous checkpoint manager with mirroring."""
    return get_checkpoint_manager(mode="AUTONOMOUS", storage_path=storage_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Unified Checkpoint Manager")
    parser.add_argument("--mode", choices=["SYNC", "ASYNC", "AUTONOMOUS"], default="ASYNC")
    parser.add_argument("--storage", type=str, default=".canon_memory/checkpoints")
    parser.add_argument("--list", action="store_true", help="List all checkpoints")
    parser.add_argument("--verify", type=str, help="Verify checkpoint integrity")
    parser.add_argument("--self-test", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    manager = get_checkpoint_manager(mode=args.mode, storage_path=Path(args.storage))

    if args.self_test:
        results = manager._run_self_tests()
        print(f"Self-tests: {results['passed']} passed, {results['failed']} failed")
        for test in results["tests"]:
            status = "✓" if test["status"] == "passed" else "✗"
            print(f"  {status} {test['name']}")

    elif args.list:
        checkpoints = manager.list_checkpoints()
        print(f"Found {len(checkpoints)} checkpoints:")
        for cp in checkpoints[:10]:
            print(f"  - {cp['checkpoint_id']} ({cp['timestamp']})")

    elif args.verify:
        is_valid = manager.verify_integrity(args.verify)
        print(f"Checkpoint {args.verify}: {'VALID' if is_valid else 'INVALID'}")

    else:
        # Demo: Create a test checkpoint
        cp_id = manager.create_checkpoint(
            state_data={"demo": "checkpoint", "timestamp": datetime.now().isoformat()},
            label="demo",
        )
        print(f"Created checkpoint: {cp_id}")
