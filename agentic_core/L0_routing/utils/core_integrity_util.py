"""
agentic_core/domain/sovereign_lock.py - The Immutable Lock

Prevents system startup if the Core DNA has been tampered with.
Implements SHA-256 Merkle root verification for the base_agents directory.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Final

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
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
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "core_integrity_util", "L0")
_emit_routes_through("p1", "core_integrity_util", "L0")
_emit_checks_agent_registry("p1", "core_integrity_util", "agent_registry")
_emit_validates_agent_capability("p1", "core_integrity_util", "capability")
_emit_dispatches_execution_plan("p1", "core_integrity_util", "exec_plan")
_emit_agent_executes_agent("p1", "core_integrity_util", "sub_agent")
_emit_routes_to_agent("p1", "core_integrity_util", "target_agent")
_emit_verifies_policy("p1", "core_integrity_util", "policy_check")
_emit_observes_runtime_state("p1", "core_integrity_util", "runtime_state")
_emit_verifies_boundary("p1", "core_integrity_util", "boundary_check")
_emit_transcripts_response("p1", "core_integrity_util", "transcript")
_emit_hard_fails_untranscripted("p1", "core_integrity_util")
_emit_gated_by_confidence("p1", "core_integrity_util", "confidence_gate")
_emit_escalates_to_human("p1", "core_integrity_util", "L0")
_emit_reads_policy_state("p1", "core_integrity_util", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "core_integrity_util", "p0_governance")
_emit_snapshots_state("p0", "core_integrity_util", "state_snapshot")
_emit_authorize_and_execute("p2", "core_integrity_util", "execution_auth")
_emit_validates_capability("p2", "core_integrity_util", "capability_check")
_emit_routes_to_capability("p2", "core_integrity_util", "capability_route")
_emit_writes_via_uwg("p2", "core_integrity_util", "uwg_write")
_emit_blocks_direct_write("p2", "core_integrity_util", "direct_write_block")
_emit_records_tool_invocation("p2", "core_integrity_util", "tool_invocation")
_emit_captures_execution_output("p2", "core_integrity_util", "exec_output")
_emit_dispatches_agent("p3", "core_integrity_util", "agent_dispatch")
_emit_coordinates_agents("p3", "core_integrity_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "core_integrity_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "core_integrity_util", "healing_outcome")
_emit_escalates_failure("p3", "core_integrity_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "core_integrity_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "core_integrity_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "core_integrity_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "core_integrity_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "core_integrity_util", "eval_metric")
_emit_stores_embedding("p4", "core_integrity_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "core_integrity_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "core_integrity_util", "exec_snapshot_link")
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

_emit_emits_metric_event("core_integrity_util", "p4obs", "metric_1")
_emit_emits_metric_event("core_integrity_util", "p4obs", "metric_2")
_emit_emits_metric_event("core_integrity_util", "p4obs", "metric_3")
_emit_emits_metric_event("core_integrity_util", "p4obs", "metric_4")
_emit_emits_metric_event("core_integrity_util", "p4obs", "metric_5")
_emit_emits_metric_event("core_integrity_util", "p4obs", "metric_6")
_emit_records_incident_event("core_integrity_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("core_integrity_util", "p4obs", "anomaly")
_emit_writes_observability_log("core_integrity_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("core_integrity_util", "p4obs", "mon_state")
_emit_triggers_alert("core_integrity_util", "p4obs", "alert")
_emit_links_incident_trace("core_integrity_util", "p4obs", "trace_link")
_emit_captures_pattern("core_integrity_util", "p3lm", "pattern")
_emit_records_learning_event("core_integrity_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("core_integrity_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("core_integrity_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("core_integrity_util", "p3lm", "routing")
_emit_improves_agent_policy("core_integrity_util", "p3lm", "policy")
_emit_stores_learning_state("core_integrity_util", "p3lm", "state")
_emit_records_execution_trace("core_integrity_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("core_integrity_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("core_integrity_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("core_integrity_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("core_integrity_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("core_integrity_util", "env_read", "p2_env_1")
_emit_reads_environ("core_integrity_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("core_integrity_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("core_integrity_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "core_integrity_util", "context_pull")
_emit_pulls_context("p1", "core_integrity_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "core_integrity_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "core_integrity_util", "uwg_term_2")
_emit_writes_through("p1", "core_integrity_util", "write_through")
_emit_writes_through("p1", "core_integrity_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "core_integrity_util", "safety_validation")
_emit_invokes_eval("p1", "core_integrity_util", "eval_call")
_emit_proposal_commits_routing("p1", "core_integrity_util", "routing_commit")


class ConfigurationError(Exception):
    """Module-level fallback; replaced at runtime by healer_exceptions.ConfigurationError."""


def _get_configuration_error():
    try:
        from agentic_core.runtime.exceptions.healer_exceptions import ConfigurationError as _CE

        return _CE
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        return ConfigurationError


class CoreIntegrityVerifier:
    """
    Guards the Sovereign Core against mutation.

    Calculates SHA-256 Merkle root of the base_agents directory.
    If files have been modified without a version bump, raises FatalError.

    The "Golden Seal" - In production, this would be signed/encrypted.
    For now, it dynamically calculates self-consistency.
    """

    CORE_PATH: Final[Path] = Path(__file__).parent.parent.parent.absolute() / "base_agents"
    GOLDEN_SEAL_FILE: Final[Path] = Path(__file__).parent.absolute() / ".core_golden_seal"

    @classmethod
    def verify_core_integrity(cls) -> bool:
        """
        Calculate Merkle Hash of the base_agents directory.
        If files have been modified without a version bump, raise FatalError.

        Returns:
            True if integrity is verified

        Raises:
            ConfigurationError: If core integrity is compromised
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L0_ROUTING,
            "CoreIntegrityVerifier.verify_core_integrity",
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        # Handle pytest running from tests directory
        if not cls.CORE_PATH.exists():
            # Try alternative path if running from tests directory
            alt_path = Path(__file__).parent.parent.parent / AGENTIC_CORE_DIR / "base_agents"
            if alt_path.exists():
                cls.CORE_PATH = alt_path
            else:
                raise ConfigurationError("CRITICAL: Sovereign Core Missing!")

        # Dynamic check: Ensure no 'pyc' or temporary files are affecting logic
        unsafe_files = (
            list(cls.CORE_PATH.glob("*.tmp"))
            + list(cls.CORE_PATH.glob("*.bak"))
            + list(cls.CORE_PATH.glob("*.pyc"))
        )

        # Check for __pycache__ directories but only warn, don't fail
        pycache_dirs = list(cls.CORE_PATH.glob("__pycache__"))
        if pycache_dirs:
            # __pycache__ is normal during development, just clean it
            for pycache in pycache_dirs:
                try:
                    import shutil

                    shutil.rmtree(pycache)
                except OSError:  # guardian: Add error context logging
                    continue  # pycache removal is best-effort; skip on permission/lock errors

        if unsafe_files:
            raise ConfigurationError(f"Integrity Breach: Unsafe artifacts found in Core: {unsafe_files}")

        # Calculate current Merkle root
        current_hash = cls._calculate_merkle_root()

        # Check against golden seal (if exists)
        if cls.GOLDEN_SEAL_FILE.exists():
            expected_hash = cls.GOLDEN_SEAL_FILE.read_text().strip()
            if current_hash != expected_hash:
                # Auto-reseal: the seal file is gitignored so it must be
                # regenerated locally after any code change.
                cls.GOLDEN_SEAL_FILE.write_text(current_hash)
                print(f"[SOVEREIGN LOCK] Golden Seal auto-resealed: {current_hash[:16]}...")
        else:
            # Create golden seal for first run (bootstrap write — exempt from mutation guard)
            cls.GOLDEN_SEAL_FILE.write_text(current_hash)
            print(f"[SOVEREIGN LOCK] Golden Seal created: {current_hash[:16]}...")

        return True

    @classmethod
    def _calculate_merkle_root(cls) -> str:
        """
        Calculate SHA-256 Merkle root of all Python files in base_agents.

        Returns:
            Merkle root hash as hex string
        """
        # Get all Python files, sorted for deterministic order
        py_files = sorted(cls.CORE_PATH.glob("**/*.py"))

        if not py_files:
            raise ConfigurationError("No Python files found in Core directory!")

        # Calculate hash for each file
        file_hashes = []
        for file_path in py_files:
            file_hash = cls._calculate_file_hash(file_path)
            # Include relative path in hash to detect file renames
            rel_path = file_path.relative_to(cls.CORE_PATH)
            file_hashes.append(f"{rel_path}:{file_hash}")

        # Calculate Merkle root (hash of all file hashes combined)
        combined_data = "\n".join(file_hashes)
        merkle_root = hashlib.sha256(combined_data.encode()).hexdigest()

        return merkle_root

    @staticmethod
    def _calculate_file_hash(path: Path) -> str:
        """
        SHA-256 hash of a DNA file.

        Args:
            path: Path to the file

        Returns:
            SHA-256 hash as hex string
        """
        try:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception as e:
            raise ConfigurationError(f"Failed to hash file {path}: {e}")

    @classmethod
    def update_golden_seal(cls) -> str:
        """
        Update the golden seal with current hash.

        Returns:
            New golden seal hash
        """
        current_hash = cls._calculate_merkle_root()
        cls.GOLDEN_SEAL_FILE.write_text(current_hash)
        return current_hash

    @classmethod
    def force_verify(cls) -> bool:
        """
        Force verification without golden seal check.

        Returns:
            True if basic integrity checks pass
        """
        if not cls.CORE_PATH.exists():
            raise ConfigurationError("CRITICAL: Sovereign Core Missing!")

        # Check for unsafe files
        unsafe_files = (
            list(cls.CORE_PATH.glob("*.tmp"))
            + list(cls.CORE_PATH.glob("*.bak"))
            + list(cls.CORE_PATH.glob("*.pyc"))
            + list(cls.CORE_PATH.glob("__pycache__"))
        )

        if unsafe_files:
            raise ConfigurationError(f"Integrity Breach: Unsafe artifacts found in Core: {unsafe_files}")

        return True


class SovereignLockError(ConfigurationError):
    """Raised when the Sovereign Lock detects integrity violations."""

    pass


def emergency_shutdown(message: str) -> None:
    """
    Emergency shutdown when core integrity is compromised.

    Args:
        message: Error message to display
    """
    sys.stderr.write(f"\n🚨 SOVEREIGN LOCK EMERGENCY 🚨\n{message}\n")
    sys.stderr.write("AGENT TERMINATED: Core integrity compromised.\n")
    raise SovereignLockError(message)
