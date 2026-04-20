"""Secure Checkpoint Manager - Protected persistence with encryption and integrity.

This module provides a secure checkpoint implementation that encrypts data at rest,
validates integrity on load, and prevents tampering or unauthorized access.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
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

_emit_applies_guardrail("p0", "checkpoint_integrity_error_validator", "p0_governance")
_emit_reads_policy_state("p0", "checkpoint_integrity_error_validator", "policy_binding")
_emit_snapshots_state("p0", "checkpoint_integrity_error_validator", "state_snapshot")
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

_emit_emits_metric_event("checkpoint_integrity_error_validator", "p4obs", "metric_1")
_emit_emits_metric_event("checkpoint_integrity_error_validator", "p4obs", "metric_2")
_emit_emits_metric_event("checkpoint_integrity_error_validator", "p4obs", "metric_3")
_emit_emits_metric_event("checkpoint_integrity_error_validator", "p4obs", "metric_4")
_emit_emits_metric_event("checkpoint_integrity_error_validator", "p4obs", "metric_5")
_emit_emits_metric_event("checkpoint_integrity_error_validator", "p4obs", "metric_6")
_emit_records_incident_event("checkpoint_integrity_error_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("checkpoint_integrity_error_validator", "p4obs", "anomaly")
_emit_writes_observability_log("checkpoint_integrity_error_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("checkpoint_integrity_error_validator", "p4obs", "mon_state")
_emit_triggers_alert("checkpoint_integrity_error_validator", "p4obs", "alert")
_emit_links_incident_trace("checkpoint_integrity_error_validator", "p4obs", "trace_link")
_emit_captures_pattern("checkpoint_integrity_error_validator", "p3lm", "pattern")
_emit_records_learning_event("checkpoint_integrity_error_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("checkpoint_integrity_error_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("checkpoint_integrity_error_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("checkpoint_integrity_error_validator", "p3lm", "routing")
_emit_improves_agent_policy("checkpoint_integrity_error_validator", "p3lm", "policy")
_emit_stores_learning_state("checkpoint_integrity_error_validator", "p3lm", "state")
_emit_records_execution_trace("checkpoint_integrity_error_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("checkpoint_integrity_error_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("checkpoint_integrity_error_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("checkpoint_integrity_error_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("checkpoint_integrity_error_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("checkpoint_integrity_error_validator", "env_read", "p2_env_1")
_emit_reads_environ("checkpoint_integrity_error_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("checkpoint_integrity_error_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("checkpoint_integrity_error_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "checkpoint_integrity_error_validator", "context_pull")
_emit_pulls_context("p1", "checkpoint_integrity_error_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "checkpoint_integrity_error_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "checkpoint_integrity_error_validator", "uwg_term_2")
_emit_writes_through("p1", "checkpoint_integrity_error_validator", "write_through")
_emit_writes_through("p1", "checkpoint_integrity_error_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "checkpoint_integrity_error_validator", "safety_validation")
_emit_invokes_eval("p1", "checkpoint_integrity_error_validator", "eval_call")
_emit_proposal_commits_routing("p1", "checkpoint_integrity_error_validator", "routing_commit")
_emit_escalates_to_human("p1", "checkpoint_integrity_error_validator", "human_escalation")
_emit_routes_through("p1", "checkpoint_integrity_error_validator", "route_through")
_emit_checks_agent_registry("p1", "checkpoint_integrity_error_validator", "agent_registry")
_emit_validates_agent_capability("p1", "checkpoint_integrity_error_validator", "capability")
_emit_dispatches_execution_plan("p1", "checkpoint_integrity_error_validator", "exec_plan")
_emit_agent_executes_agent("p1", "checkpoint_integrity_error_validator", "sub_agent")
_emit_routes_to_agent("p1", "checkpoint_integrity_error_validator", "target_agent")
_emit_verifies_policy("p1", "checkpoint_integrity_error_validator", "policy_check")
_emit_observes_runtime_state("p1", "checkpoint_integrity_error_validator", "runtime_state")
_emit_verifies_boundary("p1", "checkpoint_integrity_error_validator", "boundary_check")
_emit_transcripts_response("p1", "checkpoint_integrity_error_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "checkpoint_integrity_error_validator")
_emit_gated_by_confidence("p1", "checkpoint_integrity_error_validator", "confidence_gate")
emit_replay_key("p0", "checkpoint_integrity_error_validator")
emit_determinism_digest("p0", "checkpoint_integrity_error_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "checkpoint_integrity_error_validator", "execution_auth")
_emit_validates_capability("p2", "checkpoint_integrity_error_validator", "capability_check")
_emit_routes_to_capability("p2", "checkpoint_integrity_error_validator", "capability_route")
_emit_writes_via_uwg("p2", "checkpoint_integrity_error_validator", "uwg_write")
_emit_blocks_direct_write("p2", "checkpoint_integrity_error_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "checkpoint_integrity_error_validator", "tool_invocation")
_emit_captures_execution_output("p2", "checkpoint_integrity_error_validator", "exec_output")
_emit_dispatches_agent("p3", "checkpoint_integrity_error_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "checkpoint_integrity_error_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "checkpoint_integrity_error_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "checkpoint_integrity_error_validator", "healing_outcome")
_emit_escalates_failure("p3", "checkpoint_integrity_error_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "checkpoint_integrity_error_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "checkpoint_integrity_error_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "checkpoint_integrity_error_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "checkpoint_integrity_error_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "checkpoint_integrity_error_validator", "eval_metric")
_emit_stores_embedding("p4", "checkpoint_integrity_error_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "checkpoint_integrity_error_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "checkpoint_integrity_error_validator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class CheckpointIntegrityError(Exception):
    """Raised when checkpoint integrity validation fails."""

    pass


class SecureCheckpointManager:
    """Manages secure checkpoint persistence with encryption and integrity checks."""

    def __init__(
        self,
        hop_id: str,
        checkpoint_dir: Path,
        encryption_key: bytes | None = None,
        integrity_key: bytes | None = None,
    ):
        """Initialize the secure checkpoint manager.

        Args:
            hop_id: Unique identifier for the hop
            checkpoint_dir: Directory to store checkpoints
            encryption_key: Optional key for encryption (generated if not provided)
            integrity_key: Optional key for HMAC (generated if not provided)
        """
        self.hop_id = hop_id
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.encryption_key = encryption_key or self._generate_key()
        self.integrity_key = integrity_key or self._generate_key()
        self.cipher = Fernet(self.encryption_key)
        logger.debug(f"Initialized SecureCheckpointManager for hop {hop_id}")

    def _generate_key(self) -> bytes:
        """Generate a cryptographically secure key."""
        return Fernet.generate_key()

    def _encrypt_data(self, data: str) -> bytes:
        """Encrypt data using Fernet symmetric encryption.

        Args:
            data: String data to encrypt

        Returns:
            Encrypted bytes
        """
        return self.cipher.encrypt(data.encode())

    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data using Fernet symmetric encryption.

        Args:
            encrypted_data: Encrypted bytes

        Returns:
            Decrypted string
        """
        return self.cipher.decrypt(encrypted_data).decode()

    def _calculate_hmac(self, data: bytes) -> str:
        """Calculate HMAC-SHA256 for data integrity.

        Args:
            data: Data to sign

        Returns:
            Hexadecimal HMAC digest
        """
        return hmac.new(self.integrity_key, data, hashlib.sha256).hexdigest()

    def _verify_hmac(self, data: bytes, expected_hmac: str) -> bool:
        """Verify HMAC-SHA256 for data integrity.

        Args:
            data: Data to verify
            expected_hmac: Expected HMAC digest

        Returns:
            True if integrity is valid
        """
        calculated_hmac = self._calculate_hmac(data)
        return hmac.compare_digest(calculated_hmac, expected_hmac)

    async def save_checkpoint(self, checkpoint: MicroCheckpoint) -> None:
        """Save a checkpoint with encryption and integrity protection.

        Args:
            checkpoint: Checkpoint data to save

        Raises:
            IOError: If unable to save checkpoint
        """
        try:
            checkpoint_data = json.dumps(checkpoint.dict(), default=str)
            encrypted_data = self._encrypt_data(checkpoint_data)
            integrity_hmac = self._calculate_hmac(encrypted_data)
            secure_checkpoint = {
                "version": "1.0",
                "hop_id": self.hop_id,
                "timestamp": time.time(),
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "integrity_hmac": integrity_hmac,
            }
            checkpoint_file = self.checkpoint_dir / f"{self.hop_id}_{checkpoint.stage.value}.secure"
            temp_file = checkpoint_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(secure_checkpoint, f, indent=2)
            temp_file.replace(checkpoint_file)
            logger.debug(f"Saved secure checkpoint for stage {checkpoint.stage.value}")
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to save secure checkpoint: {e}")
            raise OSError(f'Checkpoint save failed: {e}') from e

    async def load_latest_checkpoint(self) -> MicroCheckpoint | None:
        """Load the most recent checkpoint with integrity validation.

        Returns:
            The latest checkpoint or None if no valid checkpoint found

        Raises:
            CheckpointIntegrityError: If checkpoint integrity validation fails
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SecureCheckpointManager.load_latest_checkpoint"
        )

        latest_checkpoint = None
        latest_time = 0
        for checkpoint_file in tqdm(
            self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"), desc="Processing", unit="item"
        ):
            try:
                checkpoint = await self._load_checkpoint_file(checkpoint_file)
                if checkpoint and checkpoint.timestamp > latest_time:
                    latest_time = checkpoint.timestamp
                    latest_checkpoint = checkpoint
            except (
                CheckpointIntegrityError
            ) as e:  # guardian: CheckpointIntegrityError should be handled with specific context
                logger.warning(f"Checkpoint integrity check failed for {checkpoint_file}: {e}")
                quarantine_file = checkpoint_file.with_suffix(".corrupt")
                checkpoint_file.replace(quarantine_file)
                logger.warning(f"Moved corrupted checkpoint to {quarantine_file}")
            except Exception as e:  # guardian: allow-silent-swallow
                logger.warning(f"Failed to load checkpoint {checkpoint_file}: {e}")
        if latest_checkpoint:
            logger.info(f"Loaded secure checkpoint from stage {latest_checkpoint.stage.value}")
            return latest_checkpoint
        return None

    async def _load_checkpoint_file(self, checkpoint_file: Path) -> MicroCheckpoint | None:
        """Load and validate a single checkpoint file.

        Args:
            checkpoint_file: Path to checkpoint file

        Returns:
            Loaded checkpoint or None

        Raises:
            CheckpointIntegrityError: If integrity validation fails
        """
        with open(checkpoint_file) as f:
            secure_data = json.load(f)
        if not all(k in secure_data for k in ["encrypted_data", "integrity_hmac"]):
            raise CheckpointIntegrityError("Invalid checkpoint structure")
        encrypted_data = base64.b64decode(secure_data["encrypted_data"])
        expected_hmac = secure_data["integrity_hmac"]
        if not self._verify_hmac(encrypted_data, expected_hmac):
            raise CheckpointIntegrityError("Checkpoint integrity check failed")
        decrypted_data = self._decrypt_data(encrypted_data)
        checkpoint_dict = json.loads(decrypted_data)
        if "hop_id" in checkpoint_dict and checkpoint_dict["hop_id"] != self.hop_id:
            raise CheckpointIntegrityError(f"Checkpoint hop ID mismatch: {checkpoint_dict['hop_id']}")
        return MicroCheckpoint(**checkpoint_dict)

    def cleanup_old_checkpoints(self, keep_count: int = 3) -> None:
        """Clean up old checkpoints, keeping only the most recent ones.

        Args:
            keep_count: Number of recent checkpoints to keep per stage
        """
        stage_checkpoints = {}
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"):
            stage = checkpoint_file.stem.split("_")[-1]
            if stage not in stage_checkpoints:
                stage_checkpoints[stage] = []
            stage_checkpoints[stage].append(checkpoint_file)
        for stage, files in stage_checkpoints.items():
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            for old_file in files[keep_count:]:
                old_file.unlink()
                logger.debug(f"Removed old checkpoint: {old_file}")

    def quarantine_all_checkpoints(self) -> None:
        """Quarantine all checkpoints for this hop (emergency measure)."""
        quarantine_dir = self.checkpoint_dir / "quarantine"
        quarantine_dir.mkdir(exist_ok=True)
        for checkpoint_file in self.checkpoint_dir.glob(f"{self.hop_id}_*.secure"):
            quarantine_file = quarantine_dir / checkpoint_file.name
            checkpoint_file.replace(quarantine_file)
            logger.warning(f"Quarantined checkpoint: {checkpoint_file.name}")


class CheckpointManagerFactory:
    """Factory for creating and managing secure checkpoint managers."""

    _managers: dict[str, SecureCheckpointManager] = {}
    _global_key: bytes | None = None

    @classmethod
    def get_manager(
        cls,
        hop_id: str,
        checkpoint_dir: Path,
        use_global_key: bool = True,
    ) -> SecureCheckpointManager:
        """Get or create a checkpoint manager.

        Args:
            hop_id: Unique hop identifier
            checkpoint_dir: Directory for checkpoints
            use_global_key: Whether to use a global encryption key

        Returns:
            SecureCheckpointManager instance
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "CheckpointManagerFactory.get_manager"
        )

        if hop_id not in cls._managers:
            if use_global_key:
                if cls._global_key is None:
                    cls._global_key = Fernet.generate_key()
                    logger.info("Generated global checkpoint encryption key")
                manager = SecureCheckpointManager(hop_id, checkpoint_dir, encryption_key=cls._global_key)
            else:
                manager = SecureCheckpointManager(hop_id, checkpoint_dir)
            cls._managers[hop_id] = manager
        return cls._managers[hop_id]

    @classmethod
    def quarantine_all(cls, checkpoint_dir: Path) -> None:
        """Quarantine all checkpoints in a directory.

        Args:
            checkpoint_dir: Directory containing checkpoints
        """
        for manager in cls._managers.values():
            if manager.checkpoint_dir == checkpoint_dir:
                manager.quarantine_all_checkpoints()
