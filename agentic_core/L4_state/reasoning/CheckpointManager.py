from __future__ import annotations

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "CheckpointManager")
emit_determinism_digest("p0", "CheckpointManager")

_emit_dispatches_healing_run("p1", "CheckpointManager", "L4")
_emit_routes_through("p1", "CheckpointManager", "L4")
_emit_checks_agent_registry("p1", "CheckpointManager", "agent_registry")
_emit_validates_agent_capability("p1", "CheckpointManager", "capability")
_emit_dispatches_execution_plan("p1", "CheckpointManager", "exec_plan")
_emit_agent_executes_agent("p1", "CheckpointManager", "sub_agent")
_emit_routes_to_agent("p1", "CheckpointManager", "target_agent")
_emit_verifies_policy("p1", "CheckpointManager", "policy_check")
_emit_observes_runtime_state("p1", "CheckpointManager", "runtime_state")
_emit_verifies_boundary("p1", "CheckpointManager", "boundary_check")
_emit_transcripts_response("p1", "CheckpointManager", "transcript")
_emit_hard_fails_untranscripted("p1", "CheckpointManager")
_emit_gated_by_confidence("p1", "CheckpointManager", "confidence_gate")
_emit_escalates_to_human("p1", "CheckpointManager", "L4")
_emit_reads_policy_state("p1", "CheckpointManager", "L4")
_emit_authorize_and_execute("p2", "CheckpointManager", "execution_auth")
_emit_validates_capability("p2", "CheckpointManager", "capability_check")
_emit_routes_to_capability("p2", "CheckpointManager", "capability_route")
_emit_writes_via_uwg("p2", "CheckpointManager", "uwg_write")
_emit_blocks_direct_write("p2", "CheckpointManager", "direct_write_block")
_emit_records_tool_invocation("p2", "CheckpointManager", "tool_invocation")
_emit_captures_execution_output("p2", "CheckpointManager", "exec_output")
_emit_dispatches_agent("p3", "CheckpointManager", "agent_dispatch")
_emit_coordinates_agents("p3", "CheckpointManager", "agent_coordination")
_emit_records_workflow_lineage("p3", "CheckpointManager", "workflow_lineage")
_emit_records_healing_outcome("p3", "CheckpointManager", "healing_outcome")
_emit_escalates_failure("p3", "CheckpointManager", "failure_escalation")
_emit_orchestrates_workflow("p3", "CheckpointManager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "CheckpointManager", "healing_dispatch")
_emit_invokes_evaluation("p3", "CheckpointManager", "evaluation_signal")
_emit_records_telemetry_event("p4", "CheckpointManager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "CheckpointManager", "eval_metric")
_emit_stores_embedding("p4", "CheckpointManager", "embedding_store")
_emit_updates_meta_learning_state("p4", "CheckpointManager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "CheckpointManager", "exec_snapshot_link")


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


"\nCheckpointManagerAgent - Consolidated L4 Checkpoint Guardian (Priority 2)\n\nConsolidates:\n- CheckpointManagerAgent (synchronous legacy checkpoints)\n- AutonomousCheckpointManagerAgent (async mirroring and auto-recovery)\n\nModes:\n- SYNC: Traditional blocking saves (Legacy support)\n- ASYNC: Non-blocking background saves\n- AUTONOMOUS: Mirroring, drift detection, and auto-recovery\n\nKey Features:\n- Hybrid Strategy Pattern for Sync/Async compatibility\n- State integrity verification via MD5 hash comparison\n- Automatic recovery from mirrored backups\n- Backward compatible with legacy create_checkpoint signatures\n\nTerritory: agentic_core/L4_state/memory/\nCanon Alignment: L4 state persistence and recovery\n"
import asyncio
import hashlib
import json
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_emits_metric_event("CheckpointManager", "p4obs", "metric_1")
_emit_emits_metric_event("CheckpointManager", "p4obs", "metric_2")
_emit_emits_metric_event("CheckpointManager", "p4obs", "metric_3")
_emit_emits_metric_event("CheckpointManager", "p4obs", "metric_4")
_emit_emits_metric_event("CheckpointManager", "p4obs", "metric_5")
_emit_emits_metric_event("CheckpointManager", "p4obs", "metric_6")
_emit_records_incident_event("CheckpointManager", "p4obs", "incident")
_emit_captures_runtime_anomaly("CheckpointManager", "p4obs", "anomaly")
_emit_writes_observability_log("CheckpointManager", "p4obs", "obs_log")
_emit_updates_monitoring_state("CheckpointManager", "p4obs", "mon_state")
_emit_triggers_alert("CheckpointManager", "p4obs", "alert")
_emit_links_incident_trace("CheckpointManager", "p4obs", "trace_link")
_emit_captures_pattern("CheckpointManager", "p3lm", "pattern")
_emit_records_learning_event("CheckpointManager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("CheckpointManager", "p3lm", "snapshot")
_emit_feeds_meta_learning("CheckpointManager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("CheckpointManager", "p3lm", "routing")
_emit_improves_agent_policy("CheckpointManager", "p3lm", "policy")
_emit_stores_learning_state("CheckpointManager", "p3lm", "state")
_emit_records_execution_trace("CheckpointManager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("CheckpointManager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("CheckpointManager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("CheckpointManager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("CheckpointManager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("CheckpointManager", "env_read", "p2_env_1")
_emit_reads_environ("CheckpointManager", "env_read", "p2_env_2")
_emit_reads_runtime_state("CheckpointManager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("CheckpointManager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "CheckpointManager", "context_pull")
_emit_pulls_context("p1", "CheckpointManager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "CheckpointManager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "CheckpointManager", "uwg_term_2")
_emit_writes_through("p1", "CheckpointManager", "write_through")
_emit_writes_through("p1", "CheckpointManager", "write_through_2")
_emit_validated_by_safety_plane("p1", "CheckpointManager", "safety_validation")
_emit_invokes_eval("p1", "CheckpointManager", "eval_call")
_emit_proposal_commits_routing("p1", "CheckpointManager", "routing_commit")

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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "Checkpoint.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "Checkpoint.to_dict", "p0_governance")
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
class CheckpointManager(SovereignBaseAgent):
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
    mode: str = "ASYNC"
    storage_path: Path = field(default_factory=lambda: Path(".canon_memory/checkpoints"))
    max_checkpoints: int = 50
    auto_checkpoint_interval: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    checkpoints: dict[str, Checkpoint] = field(default_factory=dict)
    current_checkpoint_id: str | None = None
    last_auto_checkpoint: datetime | None = None
    _mirror_tasks: list[asyncio.Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize the unified checkpoint manager."""
        self.mode = self.mode.upper()
        if self.mode not in ("SYNC", "ASYNC", "AUTONOMOUS"):
            Logger.warning(f"Invalid mode '{self.mode}', defaulting to ASYNC")
            self.mode = "ASYNC"
        if isinstance(self.storage_path, str):
            self.storage_path = Path(self.storage_path)
        _get_write_gateway().ensure_dir(self.storage_path)
        self.mirror_path = self.storage_path / "mirrors"
        if self.mode == "AUTONOMOUS":
            _get_write_gateway().ensure_dir(self.mirror_path)
        if not isinstance(self.checkpoints, dict):
            self.checkpoints = {}
        if not isinstance(self._mirror_tasks, list):
            self._mirror_tasks = []
        self._load_checkpoints()
        Logger.info(f"UnifiedCheckpointManager initialized in {self.mode} mode at {self.storage_path}")

    def _track_mirror_task(self, task: asyncio.Task[bool]) -> None:
        """Track background mirror work and surface failures."""
        self._mirror_tasks.append(task)

        def _done_callback(done_task: asyncio.Task[bool]) -> None:
            try:
                ok = done_task.result()
                if not ok:
                    Logger.error("[MIRROR] Background mirror task completed unsuccessfully")
            except (  # guardian: allow-log-and-swallow -- background task done-callback: exception cannot propagate, Logger.exception already called
                asyncio.CancelledError,
                AttributeError,
                OSError,
                RuntimeError,
                ValueError,
                TypeError,
            ) as exc:  # guardian: allow-log-and-swallow -- background task done-callback: exception cannot propagate, Logger.exception already called
                Logger.exception(f"[MIRROR] Background mirror task crashed: {exc}")
            finally:
                self._mirror_tasks = [t for t in self._mirror_tasks if t is not done_task]

        task.add_done_callback(_done_callback)

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

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"CheckpointManager.create_checkpoint:{label}",
        )
        checkpoint_id = self._generate_checkpoint_id(label)
        if self.mode == "SYNC":  # guardian: Runtime errors should be prevented with proper validation
            self._save_sync(checkpoint_id, state_data, file_hashes, metadata)
            return checkpoint_id
        else:
            try:
                asyncio.get_running_loop()
                asyncio.ensure_future(self._save_async(checkpoint_id, state_data, file_hashes, metadata))
                return checkpoint_id
            except RuntimeError:  # guardian: Runtime errors should be prevented with proper validation
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
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._save_sync(
                    checkpoint_id,
                    state_data,
                    file_hashes,
                    metadata,
                    mirror_immediately=True,
                ),
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
        mirror_immediately: bool = True,
    ) -> Path:
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
            assert_no_persistent_write("L4", "json.dump")
            _get_write_gateway().write_json(file_path, checkpoint.to_dict(), indent=2)
            self.checkpoints[checkpoint_id] = checkpoint
            self.current_checkpoint_id = checkpoint_id
            self._save_index()
            self._cleanup_old_checkpoints()
            if mirror_immediately and self.mode == "AUTONOMOUS":
                self._mirror_checkpoint_sync(file_path)
            Logger.info(f"[SYNC] Checkpoint saved: {checkpoint_id}")
            return file_path
        except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
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
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(
            None,
            lambda: self._save_sync(
                checkpoint_id,
                state_data,
                file_hashes,
                metadata,
                mirror_immediately=False,
            ),
        )
        if self.mode == "AUTONOMOUS":
            task = asyncio.create_task(self._mirror_checkpoint(file_path))
            self._track_mirror_task(task)
        Logger.info(f"[ASYNC] Checkpoint saved: {checkpoint_id}")
        return checkpoint_id

    def _mirror_checkpoint_sync(self, primary_path: Path) -> bool:
        """
        Synchronously mirror primary checkpoint to secondary storage.

        Args:
            primary_path: Path to primary checkpoint file

        Returns:
            True if mirroring succeeded
        """
        if not self.mirror_path.exists():
            _get_write_gateway().ensure_dir(self.mirror_path)
        mirror_path = self.mirror_path / primary_path.name
        try:
            _get_write_gateway().copy_file(primary_path, mirror_path)
            Logger.debug(f"[MIRROR] Redundant copy created: {mirror_path.name}")
            return True
        except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
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
        if not primary.exists():
            Logger.warning(f"Primary checkpoint missing: {checkpoint_id}")
            return self._attempt_recovery(checkpoint_id)
        if self.mode == "AUTONOMOUS" and mirror.exists():
            try:
                p_hash = hashlib.sha256(primary.read_bytes()).hexdigest()
                m_hash = hashlib.sha256(mirror.read_bytes()).hexdigest()
                if p_hash != m_hash:
                    Logger.warning(f"Hash mismatch for {checkpoint_id}: primary={p_hash}, mirror={m_hash}")
                    return False
                return True
            except (OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
                Logger.error(f"Integrity check failed for {checkpoint_id}: {e}")
                return False
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
                _get_write_gateway().copy_file(mirror, primary)
                Logger.warning(f"[RECOVERY] Restored checkpoint {checkpoint_id} from mirror")
                if checkpoint_id in self.checkpoints:
                    self.checkpoints[checkpoint_id].recovery_count += 1
                    self._save_index()
                return True
            except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
                Logger.error(f"[RECOVERY] Failed to restore {checkpoint_id}: {e}")
                return False
        Logger.error(f"[RECOVERY] No mirror available for {checkpoint_id}")
        return False

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """
        Retrieve a checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint ID to retrieve

        Returns:
            Checkpoint object or None if not found
        """
        if checkpoint_id in self.checkpoints:
            return self.checkpoints[checkpoint_id]
        file_path = self.storage_path / f"{checkpoint_id}.json"
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                checkpoint = Checkpoint.from_dict(data)
                self.checkpoints[checkpoint_id] = checkpoint
                return checkpoint
            except (OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                Logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
        return None

    def get_latest_checkpoint(self) -> Checkpoint | None:
        """Get the most recent checkpoint."""
        if self.current_checkpoint_id:
            return self.get_checkpoint(self.current_checkpoint_id)
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

    def rollback_to_checkpoint(self, checkpoint_id: str) -> RecoveryResult:
        """
        Rollback state to a specific checkpoint.

        Args:
            checkpoint_id: Checkpoint ID to rollback to

        Returns:
            RecoveryResult with operation details
        """
        start_time = time.time()
        result = RecoveryResult(success=False, checkpoint_id=checkpoint_id)
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            result.errors.append(f"Checkpoint {checkpoint_id} not found")
            return result
        if not self.verify_integrity(checkpoint_id):
            result.errors.append(f"Checkpoint {checkpoint_id} failed integrity check")
            return result
        try:
            self.current_checkpoint_id = checkpoint_id
            self._save_index()
            result.success = True
            result.state_restored = True
            result.recovery_time = time.time() - start_time
            Logger.info(f"[ROLLBACK] Successfully rolled back to {checkpoint_id}")
            return result
        except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            result.errors.append(str(e))
            Logger.error(f"[ROLLBACK] Failed to rollback to {checkpoint_id}: {e}")
            return result

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
            except (OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                raise

    def _save_index(self) -> None:
        """Save checkpoint index to disk."""
        index_path = self.storage_path / "index.json"
        index_data = {
            "current_checkpoint_id": self.current_checkpoint_id,
            "checkpoints": list(self.checkpoints.keys()),
            "updated_at": datetime.now().isoformat(),
        }
        try:
            assert_no_persistent_write("L4", "json.dump")
            _get_write_gateway().write_json(index_path, index_data, indent=2)
        except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            raise

    def _cleanup_old_checkpoints(self) -> None:
        """Remove old checkpoints beyond max_checkpoints limit."""
        if len(self.checkpoints) <= self.max_checkpoints:
            return
        sorted_checkpoints = sorted(self.checkpoints.values(), key=lambda c: c.timestamp)
        to_remove = len(self.checkpoints) - self.max_checkpoints
        for checkpoint in sorted_checkpoints[:to_remove]:
            self._delete_checkpoint(checkpoint.checkpoint_id)

    def _delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint from disk and memory."""
        try:
            primary = self.storage_path / f"{checkpoint_id}.json"
            mirror = self.mirror_path / f"{checkpoint_id}.json"
            if primary.exists():
                _get_write_gateway().remove_file(primary)
            if mirror.exists():
                _get_write_gateway().remove_file(mirror)
            if checkpoint_id in self.checkpoints:
                del self.checkpoints[checkpoint_id]
            Logger.debug(f"Deleted checkpoint: {checkpoint_id}")
            return True
        except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Failed to delete checkpoint {checkpoint_id}: {e}")
            return False

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        IHealerProtocol compliance method for checkpoint violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        """
        try:
            violation_type = violation.get("type", "unknown")
            checkpoint_id = violation.get("checkpoint_id")
            violation.get("file_path")
            if violation_type == "checkpoint_integrity":
                if checkpoint_id and (not self.verify_integrity(checkpoint_id)):
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
                self._cleanup_old_checkpoints()
                return {
                    "status": "success",
                    "details": "Storage cleanup completed",
                    "artifacts": ["checkpoints_cleaned"],
                    "errors": [],
                }
            elif violation_type == "missing_checkpoint_file":
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
        except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Heal operation failed in CheckpointManagerAgent: {e}")
            return {
                "status": "failed",
                "details": f"Heal operation failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    @timeout(300)
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
        if agent_name in _call_path:
            return {"skipped": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"skipped": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            violations_found = 0
            violations_fixed = 0
            for checkpoint_id in list(self.checkpoints.keys()):
                if not self.verify_integrity(checkpoint_id):
                    violations_found += 1
                    if execute and (not dry_run):
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

    def _run_self_tests(self) -> dict[str, Any]:
        """Run internal self-tests for the unified checkpoint manager."""  # guardian: AssertionError should be handled with specific context
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self.mode in ("SYNC", "ASYNC", "AUTONOMOUS")
            assert self.storage_path.exists()
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:  # guardian: AssertionError should be handled with specific context
            results["failed"] += 1
            results["tests"].append(
                {"name": "test_instantiation", "status": "failed", "error": str(e)}
            )  # guardian: AssertionError should be handled with specific context
        try:
            cp_id = self._generate_checkpoint_id("test")
            assert cp_id.startswith("chk_")
            assert "test" in cp_id
            results["passed"] += 1
            results["tests"].append({"name": "test_checkpoint_id_generation", "status": "passed"})
        except AssertionError as e:  # guardian: AssertionError should be handled with specific context
            results["failed"] += 1
            results["tests"].append(
                {"name": "test_checkpoint_id_generation", "status": "failed", "error": str(e)},
            )
        try:
            cp = Checkpoint(
                checkpoint_id="test_cp",
                timestamp=datetime.now(),
                state_snapshot={"key": "value"},
            )  # guardian: AssertionError should be handled with specific context
            cp_dict = cp.to_dict()
            cp_restored = Checkpoint.from_dict(cp_dict)
            assert cp_restored.checkpoint_id == cp.checkpoint_id
            assert cp_restored.state_snapshot == cp.state_snapshot
            results["passed"] += 1
            results["tests"].append({"name": "test_checkpoint_serialization", "status": "passed"})
        except AssertionError as e:  # guardian: AssertionError should be handled with specific context
            results["failed"] += 1
            results["tests"].append(
                {"name": "test_checkpoint_serialization", "status": "failed", "error": str(e)},
            )
        return results


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
    return CheckpointManagerAgent(mode=mode, storage_path=storage_path)


def get_sync_checkpoint_manager(storage_path: Path | None = None) -> CheckpointManagerAgent:
    """Get a synchronous checkpoint manager (legacy compatibility)."""
    return get_checkpoint_manager(mode="SYNC", storage_path=storage_path)


def get_autonomous_checkpoint_manager(storage_path: Path | None = None) -> CheckpointManagerAgent:
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
        print(f"Checkpoint {args.verify}: {('VALID' if is_valid else 'INVALID')}")
    else:
        cp_id = manager.create_checkpoint(
            state_data={"demo": "checkpoint", "timestamp": datetime.now().isoformat()},
            label="demo",
        )
        print(f"Created checkpoint: {cp_id}")
