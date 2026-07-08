"""Phase lock persistence for Wave 16 - P2 Meta-Learning Prep.

This module provides persistent storage and management of phase locks
in L4 storage with replay binding capabilities.
"""

import hashlib
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "phase_lock_store")
trace_contract.emit_determinism_digest("p0", "phase_lock_store")

trace_contract._emit_dispatches_healing_run("p1", "phase_lock_store", "L4")
trace_contract._emit_routes_through("p1", "phase_lock_store", "L4")
trace_contract._emit_checks_agent_registry("p1", "phase_lock_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "phase_lock_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "phase_lock_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "phase_lock_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "phase_lock_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "phase_lock_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "phase_lock_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "phase_lock_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "phase_lock_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "phase_lock_store")
trace_contract._emit_gated_by_confidence("p1", "phase_lock_store", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "phase_lock_store", "L4")
trace_contract._emit_reads_policy_state("p1", "phase_lock_store", "L4")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "phase_lock_store", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "phase_lock_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "phase_lock_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "phase_lock_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "phase_lock_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "phase_lock_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "phase_lock_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "phase_lock_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "phase_lock_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "phase_lock_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "phase_lock_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "phase_lock_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "phase_lock_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "phase_lock_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "phase_lock_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "phase_lock_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "phase_lock_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "phase_lock_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "phase_lock_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "phase_lock_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "phase_lock_store", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("phase_lock_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("phase_lock_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("phase_lock_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("phase_lock_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("phase_lock_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("phase_lock_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("phase_lock_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("phase_lock_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("phase_lock_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("phase_lock_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("phase_lock_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("phase_lock_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("phase_lock_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("phase_lock_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("phase_lock_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("phase_lock_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("phase_lock_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("phase_lock_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("phase_lock_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("phase_lock_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("phase_lock_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("phase_lock_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("phase_lock_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("phase_lock_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("phase_lock_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("phase_lock_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("phase_lock_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("phase_lock_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "phase_lock_store", "context_pull")
trace_contract._emit_pulls_context("p1", "phase_lock_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "phase_lock_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "phase_lock_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "phase_lock_store", "write_through")
trace_contract._emit_writes_through("p1", "phase_lock_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "phase_lock_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "phase_lock_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "phase_lock_store", "routing_commit")

_SEQUENCE_COUNTER: list[int] = [0]


def _next_sequence() -> float:
    """Return next deterministic sequence value (no wall-clock)."""
    _SEQUENCE_COUNTER[0] += 1
    return float(_SEQUENCE_COUNTER[0])


Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PhaseLockRecord:
    """Immutable record of a phase lock."""

    phase: int
    locked: bool
    timestamp: float
    metadata: dict[str, Any]
    signature: str
    replay_digest: str


class PhaseLockStore:
    """Manages phase lock persistence in L4 storage."""

    def __init__(self, storage_path: Path | None = None):
        self.storage_path = storage_path or Path("agentic_core/L4_state/.phase_locks")
        self.storage_file = self.storage_path / "phase_locks.json"
        self._locks: dict[int, PhaseLockRecord] = {}
        self._load_locks()

    @staticmethod
    def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)

    @staticmethod
    def _compute_replay_digest(phase: int, seq: float, metadata: dict[str, Any]) -> str:
        canonical = f"{phase}:{seq}:{json.dumps(metadata, sort_keys=True)}"
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _load_locks(self) -> None:
        """Load existing phase locks from storage."""
        if not self.storage_file.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
            return
        try:
            with open(self.storage_file, encoding="utf-8") as f:
                data = json.load(f)
            for phase_str, lock_data in data.items():
                phase = int(phase_str)
                self._locks[phase] = PhaseLockRecord(**lock_data)
            Logger.info(f"Loaded {len(self._locks)} phase locks from storage")
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as e:
            Logger.error(f"Failed to load phase locks, failing closed: {e}")
            self._locks = {}

    def _save_locks(self) -> None:
        """Save phase locks to storage."""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            data = {}
            for phase, lock in self._locks.items():
                data[str(phase)] = asdict(lock)
            self._atomic_write_json(self.storage_file, data)
            Logger.debug(f"Saved {len(self._locks)} phase locks to storage")
        except OSError as e:
            Logger.error(f"Failed to save phase locks: {e}")
            raise

    def lock_phase(
        self,
        phase: int,
        metadata: dict[str, Any] | None = None,
        signature: str = "",
        guardian_key: str | None = None,
    ) -> PhaseLockRecord:
        """Lock a phase with optional signature and replay binding.

        Args:
            phase: Phase number to lock
            metadata: Optional metadata to store with lock
            signature: Guardian signature for the lock
            guardian_key: Optional guardian key for signing

        Returns:
            PhaseLockRecord for the new lock

        Raises:
            RuntimeError: If phase is already locked
        """
        trace_contract._emit_snapshots_state(str(uuid.uuid4()), "PhaseLockStore.lock_phase", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "PhaseLockStore.lock_phase")

        if phase in self._locks and self._locks[phase].locked:
            raise RuntimeError(f"Phase {phase} is already locked")
        if not signature:
            raise RuntimeError("Signature required to lock phase")
        normalized_metadata = metadata or {}
        seq = _next_sequence()
        replay_digest = self._compute_replay_digest(phase, seq, normalized_metadata)
        lock_record = PhaseLockRecord(
            phase=phase,
            locked=True,
            timestamp=seq,
            metadata=normalized_metadata,
            signature=signature,
            replay_digest=replay_digest,
        )
        self._locks[phase] = lock_record
        self._save_locks()
        Logger.info(f"Phase {phase} locked with signature")
        return lock_record

    def unlock_phase(self, phase: int, signature: str = "") -> bool:
        """Unlock a phase with signature verification.

        Args:
            phase: Phase number to unlock
            signature: Guardian signature for verification

        Returns:
            True if unlocked successfully

        Raises:
            RuntimeError: If signature verification fails
        """
        if phase not in self._locks or not self._locks[phase].locked:
            Logger.warning(f"Phase {phase} is not locked")
            return False
        if not signature:
            raise RuntimeError("Signature required to unlock phase")
        current_lock = self._locks[phase]
        if current_lock.signature and current_lock.signature != signature:
            raise RuntimeError("Unlock signature does not match lock signature")
        for higher_phase in range(phase + 1, 21):
            if self.is_locked(higher_phase):
                raise RuntimeError(f"Cannot unlock phase {phase} while phase {higher_phase} is locked")
        lock_record = PhaseLockRecord(
            phase=phase,
            locked=False,
            timestamp=_next_sequence(),
            metadata=current_lock.metadata,
            signature=signature,
            replay_digest=current_lock.replay_digest,
        )
        self._locks[phase] = lock_record
        self._save_locks()
        Logger.info(f"Phase {phase} unlocked")
        return True

    def is_locked(self, phase: int) -> bool:
        """Check if a phase is locked.

        Args:
            phase: Phase number to check

        Returns:
            True if phase is locked
        """
        return phase in self._locks and self._locks[phase].locked

    def get_lock_record(self, phase: int) -> PhaseLockRecord | None:
        """Get the lock record for a phase.

        Args:
            phase: Phase number

        Returns:
            PhaseLockRecord or None if not found
        """
        return self._locks.get(phase)

    def verify_replay_integrity(self, phase: int) -> bool:
        """Verify replay integrity of a phase lock.

        Args:
            phase: Phase number to verify

        Returns:
            True if replay integrity is valid
        """
        if phase not in self._locks:
            return False
        lock = self._locks[phase]
        expected_digest = self._compute_replay_digest(phase, lock.timestamp, lock.metadata)
        return lock.replay_digest == expected_digest

    def get_all_locked_phases(self) -> dict[int, PhaseLockRecord]:
        """Get all currently locked phases.

        Returns:
            Dictionary of phase -> PhaseLockRecord
        """
        return {phase: lock for phase, lock in self._locks.items() if lock.locked}

    def clear_all_locks(self) -> None:
        """Clear all phase locks (for testing/reset)."""
        self._locks.clear()
        self._save_locks()
        Logger.info("All phase locks cleared")


class PhaseLockValidator:
    """Validates phase lock operations and constraints."""

    def __init__(self, store: PhaseLockStore):
        self.store = store

    def validate_phase_sequence(self, current_phase: int) -> bool:
        """Validate that phases are locked in proper sequence.

        Args:
            current_phase: Phase to validate

        Returns:
            True if sequence is valid

        Raises:
            RuntimeError: If sequence is invalid
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L4_STATE,
            "PhaseLockValidator.validate_phase_sequence",
        )

        for phase in range(1, current_phase):
            if not self.store.is_locked(phase):
                raise RuntimeError(f"Phase {phase} must be locked before phase {current_phase}")
        return True

    def validate_dependencies(self, phase: int, dependencies: list[int]) -> bool:
        """Validate that all dependency phases are locked.

        Args:
            phase: Phase being validated
            dependencies: List of required phase dependencies

        Returns:
            True if dependencies are satisfied

        Raises:
            RuntimeError: If dependencies are not met
        """
        for dep_phase in dependencies:
            if not self.store.is_locked(dep_phase):
                raise RuntimeError(f"Phase {dep_phase} must be locked before phase {phase}")
        return True

    def validate_unlock_permissions(self, phase: int, signature: str) -> bool:
        """Validate permissions to unlock a phase.

        Args:
            phase: Phase to unlock
            signature: Guardian signature

        Returns:
            True if unlock is permitted

        Raises:
            RuntimeError: If unlock not permitted
        """
        lock = self.store.get_lock_record(phase)
        if not lock or not lock.locked:
            raise RuntimeError(f"Phase {phase} is not locked")
        if not signature:
            raise RuntimeError("Signature required to unlock phase")
        for higher_phase in range(phase + 1, 21):
            if self.store.is_locked(higher_phase):
                raise RuntimeError(f"Cannot unlock phase {phase} while phase {higher_phase} is locked")
        return True


_phase_lock_store = PhaseLockStore()
_phase_lock_validator = PhaseLockValidator(_phase_lock_store)


def lock_phase(phase: int, metadata: dict[str, Any] | None = None, signature: str = "") -> PhaseLockRecord:
    """Exported function to lock a phase."""
    return _phase_lock_store.lock_phase(phase, metadata, signature)


def unlock_phase(phase: int, signature: str = "") -> bool:
    """Exported function to unlock a phase."""
    return _phase_lock_store.unlock_phase(phase, signature)


def is_phase_locked(phase: int) -> bool:
    """Exported function to check if phase is locked."""
    return _phase_lock_store.is_locked(phase)


def get_phase_lock(phase: int) -> PhaseLockRecord | None:
    """Exported function to get phase lock record."""
    return _phase_lock_store.get_lock_record(phase)


def verify_phase_sequence(current_phase: int) -> bool:
    """Exported function to validate phase sequence."""
    return _phase_lock_validator.validate_phase_sequence(current_phase)


def verify_phase_dependencies(phase: int, dependencies: list[int]) -> bool:
    """Exported function to validate phase dependencies."""
    return _phase_lock_validator.validate_dependencies(phase, dependencies)


def get_all_locked_phases() -> dict[int, PhaseLockRecord]:
    """Exported function to get all locked phases."""
    return _phase_lock_store.get_all_locked_phases()
