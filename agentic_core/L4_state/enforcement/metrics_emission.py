"""Metrics emission enforcement for Wave 16 - P2 Meta-Learning Prep.

This module provides:
- Single authoritative emission control-spine chokepoint
- Runtime guard rejecting duplicate emissions per trace_id
- Blast radius containment for meta-learning proposals
- Phase lock persistence and activation flags
"""

import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmissionRecord:
    """Record of a metrics emission to prevent duplicates."""

    trace_id: str
    artifact_type: str
    emission_timestamp: float
    artifact_hash: str


@dataclass(frozen=True)
class BlastRadiusConfig:
    """Configuration for blast radius containment."""

    max_blast_radius_per_proposal: int = 1000
    max_state_surface_bytes: int = 10000000


@dataclass(frozen=True)
class ActivationFlags:
    """L4-persisted, signed, replay-bound activation flags for Wave 16."""

    execution_hardened: bool = False
    mutation_surface_zero: bool = False
    guardian_coverage: float = 0.0
    freeze_authority_active: bool = False
    meta_learning_prepared: bool = False
    blast_radius_containment_active: bool = False
    meta_learning_enabled: bool = False
    semantic_clock_tick: int = 0
    replay_digest_hash: str = ""
    signature: str = ""


class MetricsEmissionEnforcer:
    """Enforces single authoritative metrics emission and blast radius containment."""

    _instance: Optional["MetricsEmissionEnforcer"] = None
    _emissions: dict[str, EmissionRecord] = {}
    _blast_radius_config: BlastRadiusConfig = BlastRadiusConfig()

    def __new__(cls) -> "MetricsEmissionEnforcer":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def single_authoritative_emission(self, trace_id: str, artifact_type: str, artifact: Any) -> None:
        """Single control-spine chokepoint for all metrics emissions.

        Args:
            trace_id: Execution trace identifier
            artifact_type: Type of metric artifact being emitted
            artifact: The artifact being emitted

        Raises:
            RuntimeError: If duplicate emission detected
            ValueError: If blast radius exceeded
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "MetricsEmissionEnforcer.single_authoritative_emission"
        )

        emission_key = f"{trace_id}:{artifact_type}"
        if emission_key in self._emissions:
            existing = self._emissions[emission_key]
            raise RuntimeError(
                f"Duplicate emission detected for trace_id={trace_id}, artifact_type={artifact_type}. Previous emission at {existing.emission_timestamp}"
            )
        blast_radius = self._calculate_blast_radius(artifact)
        if blast_radius > self._blast_radius_config.max_blast_radius_per_proposal:
            raise ValueError(
                f"Blast radius {blast_radius} exceeds maximum {self._blast_radius_config.max_blast_radius_per_proposal}"
            )
        import hashlib

        artifact_hash = hashlib.sha256(str(artifact).encode()).hexdigest()
        record = EmissionRecord(
            trace_id=trace_id,
            artifact_type=artifact_type,
            emission_timestamp=time.time(),
            artifact_hash=artifact_hash,
        )
        self._emissions[emission_key] = record
        Logger.info(
            f"Authorized emission: trace_id={trace_id}, type={artifact_type}, blast_radius={blast_radius}"
        )

    def _calculate_blast_radius(self, artifact: Any) -> int:
        """Calculate deterministic blast radius bound to explicit state surface.

        Args:
            artifact: The artifact to calculate blast radius for

        Returns:
            Integer blast radius value
        """
        if hasattr(artifact, "__dict__"):
            mutable_attrs = sum(
                (1 for k, v in artifact.__dict__.items() if not isinstance(v, (int, float, str, bool, tuple)))
            )
            return mutable_attrs
        return 1

    def verify_emission_chokepoint(self, trace_id: str, artifact_type: str) -> bool:
        """Verify that emission went through the authorized chokepoint.

        Args:
            trace_id: Execution trace identifier
            artifact_type: Type of metric artifact

        Returns:
            True if emission was authorized, False otherwise
        """
        emission_key = f"{trace_id}:{artifact_type}"
        return emission_key in self._emissions

    def clear_emissions_for_trace(self, trace_id: str) -> None:
        """Clear emission records for a specific trace (for testing/cleanup).

        Args:
            trace_id: Trace ID to clear records for
        """
        keys_to_remove = [k for k in self._emissions.keys() if k.startswith(f"{trace_id}:")]
        for key in keys_to_remove:
            del self._emissions[key]


class BlastRadiusEnforcer:
    """Enforces blast radius containment for meta-learning proposals."""

    def __init__(self, config: BlastRadiusConfig | None = None):
        self.config = config or BlastRadiusConfig()

    def validate_blast_radius(self, proposal: Any, state_surface_bytes: int) -> bool:
        """Validate that proposal blast radius is within limits.

        Args:
            proposal: Meta-learning proposal to validate
            state_surface_bytes: Size of state surface in bytes

        Returns:
            True if blast radius is acceptable

        Raises:
            ValueError: If blast radius exceeds limits
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "BlastRadiusEnforcer.validate_blast_radius"
        )

        if state_surface_bytes > self.config.max_state_surface_bytes:
            raise ValueError(
                f"State surface {state_surface_bytes} bytes exceeds maximum {self.config.max_state_surface_bytes} bytes"
            )
        proposal_radius = self._calculate_proposal_radius(proposal)
        if proposal_radius > self.config.max_blast_radius_per_proposal:
            raise ValueError(
                f"Blast radius {proposal_radius} exceeds maximum {self.config.max_blast_radius_per_proposal}"
            )
        return True

    def _calculate_proposal_radius(self, proposal: Any) -> int:
        """Deterministic blast radius calculation for proposals.

        Args:
            proposal: Proposal to calculate radius for

        Returns:
            Integer blast radius
        """
        if hasattr(proposal, "__dict__"):
            return len(proposal.__dict__)
        return 1


class PhaseLockStore:
    """Persists and restores phase lock state in L4."""

    _lock_file = Path("agentic_core/L4_state/.phase_lock.json")

    def persist(self, phase: int, locked: bool, metadata: dict | None = None) -> None:
        """Persist phase lock state to L4 storage.

        Args:
            phase: Phase number to lock
            locked: Whether the phase is locked
            metadata: Optional metadata to store with lock
        """
        _emit_writes_through(str(uuid.uuid4()), "PhaseLockStore.persist", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "PhaseLockStore.persist")

        import json
        import os

        lock_data = {"phase": phase, "locked": locked, "metadata": metadata or {}, "timestamp": time.time()}
        os.makedirs(self._lock_file.parent, exist_ok=True)
        with open(self._lock_file, "w") as f:
            json.dump(lock_data, f, indent=2)
        Logger.info(f"Phase lock persisted: phase={phase}, locked={locked}")

    def restore(self) -> dict | None:
        """Restore phase lock state from L4 storage.

        Returns:
            Lock data dictionary or None if not found
        """
        import json

        if not self._lock_file.exists():
            return None
        try:
            with open(self._lock_file) as f:
                lock_data = json.load(f)
            Logger.info(f"Phase lock restored: phase={lock_data.get('phase')}")
            return lock_data
        except Exception as e:
            Logger.error(f"Failed to restore phase lock: {e}")
            return None

    def is_locked(self, phase: int) -> bool:
        """Check if a specific phase is locked.

        Args:
            phase: Phase number to check

        Returns:
            True if phase is locked
        """
        lock_data = self.restore()
        if lock_data is None:
            return False
        return lock_data.get("phase") == phase and lock_data.get("locked", False)


class ActivationFlagsStore:
    """Manages L4-persisted, signed, replay-bound activation flags."""

    _flags_file = Path("agentic_core/L4_state/.activation_flags.json")

    def persist_flags(self, flags: ActivationFlags) -> None:
        """Persist activation flags to L4 with signature.

        Args:
            flags: Activation flags to persist
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ActivationFlagsStore.persist_flags")

        import json
        import os

        flags_data = {
            "execution_hardened": flags.execution_hardened,
            "mutation_surface_zero": flags.mutation_surface_zero,
            "guardian_coverage": flags.guardian_coverage,
            "freeze_authority_active": flags.freeze_authority_active,
            "meta_learning_prepared": flags.meta_learning_prepared,
            "blast_radius_containment_active": flags.blast_radius_containment_active,
            "meta_learning_enabled": flags.meta_learning_enabled,
            "semantic_clock_tick": flags.semantic_clock_tick,
            "replay_digest_hash": flags.replay_digest_hash,
            "signature": flags.signature,
            "timestamp": time.time(),
        }
        os.makedirs(self._flags_file.parent, exist_ok=True)
        with open(self._flags_file, "w") as f:
            json.dump(flags_data, f, indent=2)
        Logger.info("Activation flags persisted to L4")

    def restore_flags(self) -> ActivationFlags | None:
        """Restore activation flags from L4.

        Returns:
            ActivationFlags or None if not found
        """
        import json

        if not self._flags_file.exists():
            return None
        try:
            with open(self._flags_file) as f:
                flags_data = json.load(f)
            flags = ActivationFlags(
                execution_hardened=flags_data.get("execution_hardened", False),
                mutation_surface_zero=flags_data.get("mutation_surface_zero", False),
                guardian_coverage=flags_data.get("guardian_coverage", 0.0),
                freeze_authority_active=flags_data.get("freeze_authority_active", False),
                meta_learning_prepared=flags_data.get("meta_learning_prepared", False),
                blast_radius_containment_active=flags_data.get("blast_radius_containment_active", False),
                meta_learning_enabled=flags_data.get("meta_learning_enabled", False),
                semantic_clock_tick=flags_data.get("semantic_clock_tick", 0),
                replay_digest_hash=flags_data.get("replay_digest_hash", ""),
                signature=flags_data.get("signature", ""),
            )
            Logger.info("Activation flags restored from L4")
            return flags
        except Exception as e:
            Logger.error(f"Failed to restore activation flags: {e}")
            return None


_metrics_enforcer = MetricsEmissionEnforcer()
_blast_enforcer = BlastRadiusEnforcer()
_phase_lock_store = PhaseLockStore()
_activation_store = ActivationFlagsStore()


def single_authoritative_emission(trace_id: str, artifact_type: str, artifact: Any) -> None:
    """Exported function for single authoritative emission."""
    _metrics_enforcer.single_authoritative_emission(trace_id, artifact_type, artifact)


def validate_blast_radius(proposal: Any, state_surface_bytes: int) -> bool:
    """Exported function for blast radius validation."""
    return _blast_enforcer.validate_blast_radius(proposal, state_surface_bytes)


def persist_phase_lock(phase: int, locked: bool, metadata: dict | None = None) -> None:
    """Exported function for phase lock persistence."""
    _phase_lock_store.persist(phase, locked, metadata)


def restore_phase_lock() -> dict | None:
    """Exported function for phase lock restoration."""
    return _phase_lock_store.restore()


def persist_activation_flags(flags: ActivationFlags) -> None:
    """Exported function for activation flags persistence."""
    _activation_store.persist_flags(flags)


def restore_activation_flags() -> ActivationFlags | None:
    """Exported function for activation flags restoration."""
    return _activation_store.restore_flags()
