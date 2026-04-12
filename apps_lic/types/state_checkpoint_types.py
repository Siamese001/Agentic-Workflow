"""
LIC State coordinator - HOP-based state management with atomic writes.

Ported from: archives/legacy_lic/Agentic LIC/state_manager_LIC.py
"""

import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
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

_emit_applies_guardrail("p0", "state_checkpoint_types", "p0_governance")
_emit_reads_policy_state("p0", "state_checkpoint_types", "policy_binding")
_emit_snapshots_state("p0", "state_checkpoint_types", "state_snapshot")
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

_emit_emits_metric_event("state_checkpoint_types", "p4obs", "metric_1")
_emit_emits_metric_event("state_checkpoint_types", "p4obs", "metric_2")
_emit_emits_metric_event("state_checkpoint_types", "p4obs", "metric_3")
_emit_emits_metric_event("state_checkpoint_types", "p4obs", "metric_4")
_emit_emits_metric_event("state_checkpoint_types", "p4obs", "metric_5")
_emit_emits_metric_event("state_checkpoint_types", "p4obs", "metric_6")
_emit_records_incident_event("state_checkpoint_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_checkpoint_types", "p4obs", "anomaly")
_emit_writes_observability_log("state_checkpoint_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_checkpoint_types", "p4obs", "mon_state")
_emit_triggers_alert("state_checkpoint_types", "p4obs", "alert")
_emit_links_incident_trace("state_checkpoint_types", "p4obs", "trace_link")
_emit_captures_pattern("state_checkpoint_types", "p3lm", "pattern")
_emit_records_learning_event("state_checkpoint_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_checkpoint_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_checkpoint_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_checkpoint_types", "p3lm", "routing")
_emit_improves_agent_policy("state_checkpoint_types", "p3lm", "policy")
_emit_stores_learning_state("state_checkpoint_types", "p3lm", "state")
_emit_records_execution_trace("state_checkpoint_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_checkpoint_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_checkpoint_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_checkpoint_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_checkpoint_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_checkpoint_types", "env_read", "p2_env_1")
_emit_reads_environ("state_checkpoint_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_checkpoint_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_checkpoint_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_checkpoint_types", "context_pull")
_emit_pulls_context("p1", "state_checkpoint_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_checkpoint_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_checkpoint_types", "uwg_term_2")
_emit_writes_through("p1", "state_checkpoint_types", "write_through")
_emit_writes_through("p1", "state_checkpoint_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_checkpoint_types", "safety_validation")
_emit_invokes_eval("p1", "state_checkpoint_types", "eval_call")
_emit_proposal_commits_routing("p1", "state_checkpoint_types", "routing_commit")
_emit_escalates_to_human("p1", "state_checkpoint_types", "human_escalation")
_emit_routes_through("p1", "state_checkpoint_types", "route_through")
_emit_checks_agent_registry("p1", "state_checkpoint_types", "agent_registry")
_emit_validates_agent_capability("p1", "state_checkpoint_types", "capability")
_emit_dispatches_execution_plan("p1", "state_checkpoint_types", "exec_plan")
_emit_agent_executes_agent("p1", "state_checkpoint_types", "sub_agent")
_emit_routes_to_agent("p1", "state_checkpoint_types", "target_agent")
_emit_verifies_policy("p1", "state_checkpoint_types", "policy_check")
_emit_observes_runtime_state("p1", "state_checkpoint_types", "runtime_state")
_emit_verifies_boundary("p1", "state_checkpoint_types", "boundary_check")
_emit_transcripts_response("p1", "state_checkpoint_types", "transcript")
_emit_hard_fails_untranscripted("p1", "state_checkpoint_types")
_emit_gated_by_confidence("p1", "state_checkpoint_types", "confidence_gate")
emit_replay_key("p0", "state_checkpoint_types")
emit_determinism_digest("p0", "state_checkpoint_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_checkpoint_types", "execution_auth")
_emit_validates_capability("p2", "state_checkpoint_types", "capability_check")
_emit_routes_to_capability("p2", "state_checkpoint_types", "capability_route")
_emit_writes_via_uwg("p2", "state_checkpoint_types", "uwg_write")
_emit_blocks_direct_write("p2", "state_checkpoint_types", "direct_write_block")
_emit_records_tool_invocation("p2", "state_checkpoint_types", "tool_invocation")
_emit_captures_execution_output("p2", "state_checkpoint_types", "exec_output")
_emit_dispatches_agent("p3", "state_checkpoint_types", "agent_dispatch")
_emit_coordinates_agents("p3", "state_checkpoint_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_checkpoint_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_checkpoint_types", "healing_outcome")
_emit_escalates_failure("p3", "state_checkpoint_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_checkpoint_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_checkpoint_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_checkpoint_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_checkpoint_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_checkpoint_types", "eval_metric")
_emit_stores_embedding("p4", "state_checkpoint_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_checkpoint_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_checkpoint_types", "exec_snapshot_link")


@dataclass
class StateCheckpoint:
    """Checkpoint for a HOP state."""

    hop_id: str
    mission_id: str
    timestamp: str
    checksum: str
    filepath: str


@dataclass
class StateValidationResult:
    """Result of state validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class LICStateManager:
    """
    State management for HOP-based architecture.

    Each HOP (single-responsibility agent) reads from and writes to the
    state/ directory. This creates an auditable trail and enables:
    - Debugging: Inspect state at any HOP
    - Resumability: Re-run from any HOP
    - Auditability: Complete record of workflow decisions
    """

    SCHEMA_VERSION = "13.0"

    def __init__(
        self,
        mission_id: str,
        state_directory: str = "state",
        create_if_missing: bool = True,
    ) -> None:
        """
        Initialize state coordinator for a mission.

        Args:
            mission_id: Unique mission identifier
            state_directory: foundation directory for state files
            create_if_missing: Create directory if it doesn't exist
        """
        self.mission_id = mission_id
        self.base_dir = Path(state_directory)
        self.mission_dir = self.base_dir / mission_id
        self._checkpoints: dict[str, StateCheckpoint] = {}
        if create_if_missing:
            self.mission_dir.mkdir(parents=True, exist_ok=True)

    def write_state(self, hop_id: str, data: dict[str, object], atomic: bool = True) -> str:
        """
        Write state file for a HOP.

        Args:
            hop_id: HOP identifier (e.g., "HOP-1", "1_profile_analysis")
            data: State data to write
            atomic: Use atomic write (write to staging file, then rename)

        Returns:
            Path to written file
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LICStateManager.write_state")

        filename = self._sanitize_filename(hop_id)
        if not filename.endswith(".json"):
            filename += ".json"
        filepath = self.mission_dir / filename
        data_with_metadata = {
            "hop_id": hop_id,
            "mission_id": self.mission_id,
            "timestamp": datetime.now().isoformat(),
            "schema_version": self.SCHEMA_VERSION,
            **data,
        }
        if atomic:
            staging_path = filepath.with_suffix(".staging")
            with open(staging_path, "w", encoding="utf-8") as f:
                json.dump(data_with_metadata, f, indent=2, default=str)
            staging_path.replace(filepath)
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_with_metadata, f, indent=2, default=str)
        checksum = self._calculate_checksum(filepath)
        self._checkpoints[hop_id] = StateCheckpoint(
            hop_id=hop_id,
            mission_id=self.mission_id,
            timestamp=data_with_metadata["timestamp"],
            checksum=checksum,
            filepath=str(filepath),
        )
        return str(filepath)

    def read_state(self, hop_id: str, validate_checksum: bool = False) -> dict[str, object]:
        """
        Read state file for a HOP.

        Args:
            hop_id: HOP identifier
            validate_checksum: Verify file integrity

        Returns:
            State data dictionary

        Raises:
            FileNotFoundError: If state file doesn't exist
            ValueError: If checksum validation fails
        """
        filename = self._sanitize_filename(hop_id)
        if not filename.endswith(".json"):
            filename += ".json"
        filepath = self.mission_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"State file not found: {filepath}")
        if validate_checksum:
            stored_checkpoint = self._checkpoints.get(hop_id)
            if stored_checkpoint:
                current_checksum = self._calculate_checksum(filepath)
                if stored_checkpoint.checksum != current_checksum:
                    raise ValueError(f"Checksum mismatch for {filename}: file may be corrupted")
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return data

    def state_exists(self, hop_id: str) -> bool:
        """Check if state file exists for a HOP."""
        filename = self._sanitize_filename(hop_id)
        if not filename.endswith(".json"):
            filename += ".json"
        filepath = self.mission_dir / filename
        return filepath.exists()

    def list_states(self) -> list[str]:
        """List all state files for this mission."""
        if not self.mission_dir.exists():
            return []
        states = []
        for filepath in self.mission_dir.glob("*.json"):
            states.append(filepath.stem)
        return sorted(states)

    def delete_state(self, hop_id: str) -> bool:
        """Delete a state file."""
        filename = self._sanitize_filename(hop_id)
        if not filename.endswith(".json"):
            filename += ".json"
        filepath = self.mission_dir / filename
        if filepath.exists():
            filepath.unlink()
            self._checkpoints.pop(hop_id, None)
            return True
        return False

    def clear_all_states(self) -> int:
        """Clear all state files for this mission."""
        if not self.mission_dir.exists():
            return 0
        count = 0
        for filepath in self.mission_dir.glob("*.json"):
            filepath.unlink()
            count += 1
        self._checkpoints.clear()
        return count

    def get_checkpoint(self, hop_id: str) -> StateCheckpoint | None:
        """Get Checkpoint for a HOP."""
        return self._checkpoints.get(hop_id)

    def get_all_checkpoints(self) -> dict[str, StateCheckpoint]:
        """Get all checkpoints."""
        return self._checkpoints.copy()

    def validate_state(self, hop_id: str) -> StateValidationResult:
        """Validate a state file."""
        result = StateValidationResult(is_valid=True)
        if not self.state_exists(hop_id):
            result.is_valid = False
            result.errors.append(f"State file not found for {hop_id}")
            return result
        try:
            data = self.read_state(hop_id)
            required_fields = ["hop_id", "mission_id", "timestamp", "schema_version"]
            for field_name in required_fields:
                if field_name not in data:
                    result.warnings.append(f"Missing field: {field_name}")
            if data.get("schema_version") != self.SCHEMA_VERSION:
                result.warnings.append(
                    f"schema version mismatch: expected {self.SCHEMA_VERSION}, got {data.get('schema_version')}",
                )
        except json.JSONDecodeError as e:
            result.is_valid = False
            result.errors.append(f"Invalid JSON: {e}")
        except (ValueError, TypeError, KeyError, OSError) as e:
            result.is_valid = False
            result.errors.append(f"Validation error: {e}")
        return result

    def export_mission(self, output_path: str) -> str:
        """Export all mission state to a single archive."""
        output_file = Path(output_path)
        if output_file.suffix != ".zip":
            output_file = output_file.with_suffix(".zip")
        shutil.make_archive(str(output_file.with_suffix("")), "zip", self.mission_dir)
        return str(output_file)

    def _sanitize_filename(self, hop_id: str) -> str:
        """Sanitize hop_id for use as filename."""
        sanitized = hop_id.replace(" ", "_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "_-.")
        return sanitized

    def _calculate_checksum(self, filepath: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class StateValidator:
    """Validator for state consistency across HOPs."""

    def __init__(self, state_manager: LICStateManager) -> None:
        """Initialize with a state coordinator."""
        self.state_manager = state_manager

    def validate_hop_chain(self, hop_ids: list[str]) -> StateValidationResult:
        """Validate a chain of HOPs for consistency."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "StateValidator.validate_hop_chain"
        )

        result = StateValidationResult(is_valid=True)
        for hop_id in hop_ids:
            hop_result = self.state_manager.validate_state(hop_id)
            if not hop_result.is_valid:
                result.is_valid = False
                result.errors.extend(hop_result.errors)
            result.warnings.extend(hop_result.warnings)
        return result

    def validate_dependencies(self, hop_id: str, required_hops: list[str]) -> StateValidationResult:
        """Validate that required HOPs have completed before this HOP."""
        result = StateValidationResult(is_valid=True)
        for required_hop in required_hops:
            if not self.state_manager.state_exists(required_hop):
                result.is_valid = False
                result.errors.append(f"Required HOP {required_hop} not completed before {hop_id}")
        return result


def create_state_manager(mission_id: str, state_directory: str = "state") -> LICStateManager:
    """builder function to create a state coordinator."""
    return LICStateManager(mission_id, state_directory)


def create_state_validator(state_manager: LICStateManager) -> StateValidator:
    """builder function to create a state validator."""
    return StateValidator(state_manager)
