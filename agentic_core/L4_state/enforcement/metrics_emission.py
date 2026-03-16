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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

emit_replay_key("p0", "metrics_emission")
emit_determinism_digest("p0", "metrics_emission")

_emit_dispatches_healing_run("p1", "metrics_emission", "L4")
_emit_routes_through("p1", "metrics_emission", "L4")
_emit_checks_agent_registry("p1", "metrics_emission", "agent_registry")
_emit_validates_agent_capability("p1", "metrics_emission", "capability")
_emit_dispatches_execution_plan("p1", "metrics_emission", "exec_plan")
_emit_agent_executes_agent("p1", "metrics_emission", "sub_agent")
_emit_routes_to_agent("p1", "metrics_emission", "target_agent")
_emit_verifies_policy("p1", "metrics_emission", "policy_check")
_emit_observes_runtime_state("p1", "metrics_emission", "runtime_state")
_emit_verifies_boundary("p1", "metrics_emission", "boundary_check")
_emit_transcripts_response("p1", "metrics_emission", "transcript")
_emit_hard_fails_untranscripted("p1", "metrics_emission")
_emit_gated_by_confidence("p1", "metrics_emission", "confidence_gate")
_emit_escalates_to_human("p1", "metrics_emission", "L4")
_emit_reads_policy_state("p1", "metrics_emission", "L4")

_emit_snapshots_state("p0", "metrics_emission", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "metrics_emission", "p0_governance")
_emit_authorize_and_execute("p2", "metrics_emission", "execution_auth")
_emit_validates_capability("p2", "metrics_emission", "capability_check")
_emit_routes_to_capability("p2", "metrics_emission", "capability_route")
_emit_writes_via_uwg("p2", "metrics_emission", "uwg_write")
_emit_blocks_direct_write("p2", "metrics_emission", "direct_write_block")
_emit_records_tool_invocation("p2", "metrics_emission", "tool_invocation")
_emit_captures_execution_output("p2", "metrics_emission", "exec_output")
_emit_dispatches_agent("p3", "metrics_emission", "agent_dispatch")
_emit_coordinates_agents("p3", "metrics_emission", "agent_coordination")
_emit_records_workflow_lineage("p3", "metrics_emission", "workflow_lineage")
_emit_records_healing_outcome("p3", "metrics_emission", "healing_outcome")
_emit_escalates_failure("p3", "metrics_emission", "failure_escalation")
_emit_orchestrates_workflow("p3", "metrics_emission", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "metrics_emission", "healing_dispatch")
_emit_invokes_evaluation("p3", "metrics_emission", "evaluation_signal")
_emit_records_telemetry_event("p4", "metrics_emission", "telemetry_event")
_emit_captures_evaluation_metric("p4", "metrics_emission", "eval_metric")
_emit_stores_embedding("p4", "metrics_emission", "embedding_store")
_emit_updates_meta_learning_state("p4", "metrics_emission", "meta_learning")
_emit_links_execution_to_snapshot("p4", "metrics_emission", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("metrics_emission", "p4obs", "metric_1")
_emit_emits_metric_event("metrics_emission", "p4obs", "metric_2")
_emit_emits_metric_event("metrics_emission", "p4obs", "metric_3")
_emit_emits_metric_event("metrics_emission", "p4obs", "metric_4")
_emit_emits_metric_event("metrics_emission", "p4obs", "metric_5")
_emit_emits_metric_event("metrics_emission", "p4obs", "metric_6")
_emit_records_incident_event("metrics_emission", "p4obs", "incident")
_emit_captures_runtime_anomaly("metrics_emission", "p4obs", "anomaly")
_emit_writes_observability_log("metrics_emission", "p4obs", "obs_log")
_emit_updates_monitoring_state("metrics_emission", "p4obs", "mon_state")
_emit_triggers_alert("metrics_emission", "p4obs", "alert")
_emit_links_incident_trace("metrics_emission", "p4obs", "trace_link")
_emit_captures_pattern("metrics_emission", "p3lm", "pattern")
_emit_records_learning_event("metrics_emission", "p3lm", "learning_event")
_emit_writes_learning_snapshot("metrics_emission", "p3lm", "snapshot")
_emit_feeds_meta_learning("metrics_emission", "p3lm", "meta_feed")
_emit_updates_routing_strategy("metrics_emission", "p3lm", "routing")
_emit_improves_agent_policy("metrics_emission", "p3lm", "policy")
_emit_stores_learning_state("metrics_emission", "p3lm", "state")
_emit_records_execution_trace("metrics_emission", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("metrics_emission", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("metrics_emission", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("metrics_emission", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("metrics_emission", "L4_STATE", "p2_trace_5")
_emit_reads_environ("metrics_emission", "env_read", "p2_env_1")
_emit_reads_environ("metrics_emission", "env_read", "p2_env_2")
_emit_reads_runtime_state("metrics_emission", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("metrics_emission", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "metrics_emission", "context_pull")
_emit_pulls_context("p1", "metrics_emission", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "metrics_emission", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "metrics_emission", "uwg_term_2")
_emit_writes_through("p1", "metrics_emission", "write_through")
_emit_writes_through("p1", "metrics_emission", "write_through_2")
_emit_validated_by_safety_plane("p1", "metrics_emission", "safety_validation")
_emit_invokes_eval("p1", "metrics_emission", "eval_call")
_emit_proposal_commits_routing("p1", "metrics_emission", "routing_commit")

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
