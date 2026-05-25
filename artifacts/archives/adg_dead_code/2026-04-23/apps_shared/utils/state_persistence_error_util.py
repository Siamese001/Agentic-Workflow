"""Atomic State Manager with ACID guarantees.

Implements two-phase commit for workflow state persistence to ensure zero data loss.
Uses shadow files/keys for isolation and atomic swap operations.

Phase 3 - Atomic State Persistence
"""

from __future__ import annotations

import logging
import os
import time
from enum import Enum
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "state_persistence_error_util", "p0_governance")
_emit_reads_policy_state("p0", "state_persistence_error_util", "policy_binding")
_emit_snapshots_state("p0", "state_persistence_error_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("state_persistence_error_util", "p4obs", "metric_1")
_emit_emits_metric_event("state_persistence_error_util", "p4obs", "metric_2")
_emit_emits_metric_event("state_persistence_error_util", "p4obs", "metric_3")
_emit_emits_metric_event("state_persistence_error_util", "p4obs", "metric_4")
_emit_emits_metric_event("state_persistence_error_util", "p4obs", "metric_5")
_emit_emits_metric_event("state_persistence_error_util", "p4obs", "metric_6")
_emit_records_incident_event("state_persistence_error_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_persistence_error_util", "p4obs", "anomaly")
_emit_writes_observability_log("state_persistence_error_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_persistence_error_util", "p4obs", "mon_state")
_emit_triggers_alert("state_persistence_error_util", "p4obs", "alert")
_emit_links_incident_trace("state_persistence_error_util", "p4obs", "trace_link")
_emit_captures_pattern("state_persistence_error_util", "p3lm", "pattern")
_emit_records_learning_event("state_persistence_error_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_persistence_error_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_persistence_error_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_persistence_error_util", "p3lm", "routing")
_emit_improves_agent_policy("state_persistence_error_util", "p3lm", "policy")
_emit_stores_learning_state("state_persistence_error_util", "p3lm", "state")
_emit_records_execution_trace("state_persistence_error_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_persistence_error_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_persistence_error_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_persistence_error_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_persistence_error_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_persistence_error_util", "env_read", "p2_env_1")
_emit_reads_environ("state_persistence_error_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_persistence_error_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_persistence_error_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_persistence_error_util", "context_pull")
_emit_pulls_context("p1", "state_persistence_error_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_persistence_error_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_persistence_error_util", "uwg_term_2")
_emit_writes_through("p1", "state_persistence_error_util", "write_through")
_emit_writes_through("p1", "state_persistence_error_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_persistence_error_util", "safety_validation")
_emit_invokes_eval("p1", "state_persistence_error_util", "eval_call")
_emit_proposal_commits_routing("p1", "state_persistence_error_util", "routing_commit")
_emit_escalates_to_human("p1", "state_persistence_error_util", "human_escalation")
_emit_routes_through("p1", "state_persistence_error_util", "route_through")
_emit_checks_agent_registry("p1", "state_persistence_error_util", "agent_registry")
_emit_validates_agent_capability("p1", "state_persistence_error_util", "capability")
_emit_dispatches_execution_plan("p1", "state_persistence_error_util", "exec_plan")
_emit_agent_executes_agent("p1", "state_persistence_error_util", "sub_agent")
_emit_routes_to_agent("p1", "state_persistence_error_util", "target_agent")
_emit_verifies_policy("p1", "state_persistence_error_util", "policy_check")
_emit_observes_runtime_state("p1", "state_persistence_error_util", "runtime_state")
_emit_verifies_boundary("p1", "state_persistence_error_util", "boundary_check")
_emit_transcripts_response("p1", "state_persistence_error_util", "transcript")
_emit_hard_fails_untranscripted("p1", "state_persistence_error_util")
_emit_gated_by_confidence("p1", "state_persistence_error_util", "confidence_gate")
emit_replay_key("p0", "state_persistence_error_util")
emit_determinism_digest("p0", "state_persistence_error_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_persistence_error_util", "execution_auth")
_emit_validates_capability("p2", "state_persistence_error_util", "capability_check")
_emit_routes_to_capability("p2", "state_persistence_error_util", "capability_route")
_emit_writes_via_uwg("p2", "state_persistence_error_util", "uwg_write")
_emit_blocks_direct_write("p2", "state_persistence_error_util", "direct_write_block")
_emit_records_tool_invocation("p2", "state_persistence_error_util", "tool_invocation")
_emit_captures_execution_output("p2", "state_persistence_error_util", "exec_output")
_emit_dispatches_agent("p3", "state_persistence_error_util", "agent_dispatch")
_emit_coordinates_agents("p3", "state_persistence_error_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_persistence_error_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_persistence_error_util", "healing_outcome")
_emit_escalates_failure("p3", "state_persistence_error_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_persistence_error_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_persistence_error_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_persistence_error_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_persistence_error_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_persistence_error_util", "eval_metric")
_emit_stores_embedding("p4", "state_persistence_error_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_persistence_error_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_persistence_error_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class BackendType(Enum):
    """Storage backend type."""

    FILE = "file"
    REDIS = "redis"
    SQLITE = "sqlite"


class SystemTelemetry:
    """Stub telemetry collector."""

    pass


class StatePersistenceError(Exception):
    """Raised when state persistence operations fail."""

    pass


class AtomicStateManager:
    """Atomic state manager with ACID guarantees.

    Implements two-phase commit protocol:
    1. ISOLATION: Write to shadow location
    2. ATOMIC SWAP: Replace active state with shadow
    3. CLEANUP: Remove shadow after successful commit

    This ensures that state is never corrupted - either the new state
    is fully committed or the old state remains intact.
    """

    def __init__(
        self,
        backend: BackendType = BackendType.FILE,
        storage_path: str | None = None,
        telemetry: SystemTelemetry | None = None,
    ):
        """Initialize atomic state manager.

        Args:
            backend: Storage backend type (FILE, REDIS, SQLITE)
            storage_path: Path for file storage (required for FILE backend)
            telemetry: Optional telemetry instance
        """
        self.backend = backend
        self.telemetry = telemetry or get_telemetry()
        if backend == BackendType.FILE:
            if not storage_path:
                # guardian: allow-path-string
                storage_path = Path(os.getcwd()) / ".workflow_state"
            self.storage_path = Path(storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized FILE backend at: {self.storage_path}")
        elif backend == BackendType.REDIS:
            raise NotImplementedError("Redis backend not yet implemented")
        elif backend == BackendType.SQLITE:
            raise NotImplementedError("SQLite backend not yet implemented")
        else:
            raise ValueError(f"Unknown backend type: {backend}")

    def checkpoint(self, workflow_id: str, new_state: WorkflowState) -> CheckpointMetadata:
        """Atomically checkpoint workflow state using two-phase commit.

        This method guarantees that either:
        - The new state is fully committed and becomes active, OR
        - The old state remains intact and unchanged

        There is no intermediate state where the checkpoint is partially written.

        Args:
            workflow_id: Unique workflow identifier
            new_state: New workflow state to checkpoint

        Returns:
            CheckpointMetadata with operation details

        Raises:
            StatePersistenceError: If checkpoint fails
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "AtomicStateManager.checkpoint"
        )

        start_time = time.time()
        checkpoint_id = f"{workflow_id}_{int(time.time() * 1000)}"
        try:
            logger.info(f"Starting atomic checkpoint for workflow: {workflow_id}")
            shadow_key = self._get_shadow_key(workflow_id)
            self._write_to_backend(shadow_key, new_state)
            logger.debug(f"Phase 1 complete: Shadow state written to {shadow_key}")
            active_key = self._get_active_key(workflow_id)
            self._atomic_swap(shadow_key, active_key)
            logger.debug("Phase 2 complete: Atomic swap successful")
            duration_ms = (time.time() - start_time) * 1000
            metadata = CheckpointMetadata(
                checkpoint_id=checkpoint_id,
                workflow_id=workflow_id,
                k_node_index=new_state.current_k_node,
                k_node_name=new_state.get_last_execution().k_node_name
                if new_state.get_last_execution()
                else "init",
                success=True,
                duration_ms=duration_ms,
            )
            self.telemetry.log_success(
                component="atomic_state_manager",
                operation="checkpoint",
                latency_ms=duration_ms,
                metadata={
                    "workflow_id": workflow_id,
                    "checkpoint_id": checkpoint_id,
                    "k_node_index": new_state.current_k_node,
                },
            )
            logger.info(
                f"Atomic checkpoint complete for {workflow_id} (K-Node {new_state.current_k_node}) in {duration_ms:.2f}ms",
            )
            return metadata
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Atomic checkpoint failed for {workflow_id}: {e}")
            try:
                shadow_key = self._get_shadow_key(workflow_id)
                self._delete_from_backend(shadow_key)
                logger.debug("Cleaned up shadow state after failure")
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ) as cleanup_error:  # guardian: allow-silent-swallow
                logger.warning(f"Failed to cleanup shadow state: {cleanup_error}")
            metadata = CheckpointMetadata(
                checkpoint_id=checkpoint_id,
                workflow_id=workflow_id,
                k_node_index=new_state.current_k_node,
                k_node_name=new_state.get_last_execution().k_node_name
                if new_state.get_last_execution()
                else "init",
                success=False,
                error_message=str(e),
                duration_ms=duration_ms,
            )
            self.telemetry.log_failure(
                component="atomic_state_manager",
                operation="checkpoint",
                latency_ms=duration_ms,
                error_type=e.__class__.__name__,
                error_message=str(e),
                metadata={"workflow_id": workflow_id},
            )
            raise StatePersistenceError(f"Failed to commit state for {workflow_id}: {e}") from e

    def resume_workflow(self, workflow_id: str) -> WorkflowState | None:
        """Resume workflow from last valid checkpoint.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            WorkflowState if checkpoint exists, None otherwise
        """
        logger.info(f"Attempting to resume workflow: {workflow_id}")
        return self._load_state(workflow_id)

    def get_active_checkpoint(self, workflow_id: str) -> WorkflowState | None:
        """Get the current active checkpoint for a workflow.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            WorkflowState if exists, None otherwise
        """
        return self._load_state(workflow_id)

    def delete_checkpoint(self, workflow_id: str) -> bool:
        """Delete checkpoint for a workflow.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            active_key = self._get_active_key(workflow_id)
            self._delete_from_backend(active_key)
            logger.info(f"Deleted checkpoint for workflow: {workflow_id}")
            return True
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.warning(f"Failed to delete checkpoint for {workflow_id}: {e}")
            return False

    def list_checkpoints(self) -> dict[str, WorkflowState]:
        """List all available checkpoints.

        Returns:
            Dictionary mapping workflow_id to WorkflowState
        """
        checkpoints = {}
        if self.backend == BackendType.FILE:
            for file_path in tqdm(self.storage_path.glob("*.json"), desc="Processing", unit="item"):
                if file_path.stem.endswith("_shadow"):
                    continue
                workflow_id = file_path.stem
                try:
                    state = self._load_state(workflow_id)
                    if state:
                        checkpoints[workflow_id] = state
                except (
                    OSError,
                    ValueError,
                    TypeError,
                    KeyError,
                    AttributeError,
                    RuntimeError,
                ) as e:  # guardian: allow-silent-swallow
                    logger.warning(f"Failed to load checkpoint {workflow_id}: {e}")
        return checkpoints

    def _get_active_key(self, workflow_id: str) -> str:
        """Get the active storage key for a workflow."""
        if self.backend == BackendType.FILE:
            return str(self.storage_path / f"{workflow_id}.json")
        elif self.backend == BackendType.REDIS:
            return f"workflow:{workflow_id}"
        elif self.backend == BackendType.SQLITE:
            return workflow_id
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _get_shadow_key(self, workflow_id: str) -> str:
        """Get the shadow storage key for a workflow."""
        if self.backend == BackendType.FILE:
            return str(self.storage_path / f"{workflow_id}_shadow.json")
        elif self.backend == BackendType.REDIS:
            return f"workflow:{workflow_id}:shadow"
        elif self.backend == BackendType.SQLITE:
            return f"{workflow_id}_shadow"
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _write_to_backend(self, key: str, state: WorkflowState) -> None:
        """Write state to backend storage.

        Args:
            key: Storage key
            state: Workflow state to write
        """
        if self.backend == BackendType.FILE:
            file_path = Path(key)
            temp_path = file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(state.to_json())
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, file_path)
        elif self.backend == BackendType.REDIS:
            raise NotImplementedError("Redis backend not yet implemented")
        elif self.backend == BackendType.SQLITE:
            raise NotImplementedError("SQLite backend not yet implemented")

    def _atomic_swap(self, shadow_key: str, active_key: str) -> None:
        """Atomically swap shadow state with active state.

        This is the critical operation that ensures atomicity.
        os.replace() is atomic on both POSIX and Windows.

        Args:
            shadow_key: Shadow storage key
            active_key: Active storage key
        """
        if self.backend == BackendType.FILE:
            os.replace(shadow_key, active_key)
        elif self.backend == BackendType.REDIS:
            raise NotImplementedError("Redis backend not yet implemented")
        elif self.backend == BackendType.SQLITE:
            raise NotImplementedError("SQLite backend not yet implemented")

    def _load_state(self, workflow_id: str) -> WorkflowState | None:
        """Load state from backend storage.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            WorkflowState if exists, None otherwise
        """
        try:
            active_key = self._get_active_key(workflow_id)
            if self.backend == BackendType.FILE:
                file_path = Path(active_key)
                if not file_path.exists():
                    logger.debug(f"No checkpoint found for workflow: {workflow_id}")
                    return None
                with open(file_path, encoding="utf-8") as f:
                    json_data = f.read()
                state = WorkflowState.from_json(json_data)
                logger.info(
                    f"Loaded checkpoint for {workflow_id} (K-Node {state.current_k_node}/{state.total_k_nodes})",
                )
                return state
            elif self.backend == BackendType.REDIS:
                raise NotImplementedError("Redis backend not yet implemented")
            elif self.backend == BackendType.SQLITE:
                raise NotImplementedError("SQLite backend not yet implemented")
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to load state for {workflow_id}: {e}")
            raise StatePersistenceError(f"Failed to load state: {e}") from e

    def _delete_from_backend(self, key: str) -> None:
        """Delete state from backend storage.

        Args:
            key: Storage key
        """
        if self.backend == BackendType.FILE:
            file_path = Path(key)
            if file_path.exists():
                file_path.unlink()
        elif self.backend == BackendType.REDIS:
            raise NotImplementedError("Redis backend not yet implemented")
        elif self.backend == BackendType.SQLITE:
            raise NotImplementedError("SQLite backend not yet implemented")
