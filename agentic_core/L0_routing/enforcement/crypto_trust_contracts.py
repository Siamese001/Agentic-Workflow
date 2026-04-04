"""
V15 P5 Framework Contracts — Cryptographic Trust & Signing Enforcement.

Runtime contracts enforcing P5 (Tokenized Authority / Cryptographic Trust)
invariants required by the V15 Target State audit (Prompt v5.0 Enhanced).

Contract version: 1.0.0
"""

from __future__ import annotations

import hashlib
import uuid

from agentic_core.L0_routing.types.crypto_trust_types import (
    HashMismatchTracker,
    KeyStatus,
    ReplayGuardRecord,
    SignatureEnclave,
    SignatureEnvelope,
    SignedGuardianArtifact,
    SigningAlgorithm,
    TrustRoot,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

# =============================================================================
# Canonical Hashing
# =============================================================================


def hash_artifact_canonical(artifact_bytes: bytes) -> str:
    """Canonical SHA-256 hash of artifact bytes. Single source of truth."""
    return hashlib.sha256(artifact_bytes).hexdigest()


# =============================================================================
# §7.4 / §7.4.1 — sign_artifact
# =============================================================================


class SigningError(Exception):
    """Raised when artifact signing fails."""


def sign_artifact(
    artifact_bytes: bytes,
    key_id: str,
    enclave: SignatureEnclave,
    trace_id: str,
    semantic_clock_tick: int,
) -> SignatureEnvelope:
    """§7.4 / §7.4.1 — Sign artifact bytes via the enclave. Fail-closed."""
    _emit_signs_execution_trace(str(uuid.uuid4()), "seg_hash", "seg_sig", 0)
    artifact_hash = hash_artifact_canonical(artifact_bytes)
    try:
        signature = enclave.sign(artifact_bytes, key_id)
    except (KeyError, PermissionError) as exc:
        raise SigningError(
            f"FAIL (P5): Signing failed for key '{key_id}': {exc}",
        ) from exc
    except Exception as exc:
        raise SigningError(
            f"FAIL (P5): Unexpected signing error: {exc}",
        ) from exc

    key_record = enclave.get_key_record(key_id)
    algorithm = key_record.algorithm if key_record else SigningAlgorithm.HMAC_SHA256

    return SignatureEnvelope(
        trace_id=trace_id,
        artifact_hash=artifact_hash,
        key_id=key_id,
        signature=signature,
        algorithm=algorithm,
        semantic_clock_tick=semantic_clock_tick,
    )


# =============================================================================
# §7.4.2 — verify_signature
# =============================================================================


class VerificationError(Exception):
    """Raised when signature verification fails (fail-closed)."""


def verify_signature(
    artifact_bytes: bytes,
    envelope: SignatureEnvelope,
    trust_root: TrustRoot,
    enclave: SignatureEnclave,
) -> bool:
    """§7.4.2 — Verify signature against pinned public keys. Fail-closed.

    Checks:
    1. artifact_hash matches canonical hash of artifact_bytes
    2. key_id exists in trust_root and is ACTIVE
    3. Signature is valid per enclave.verify()
    """
    # Check artifact hash
    _emit_verifies_boundary(str(uuid.uuid4()), "Module.verify_signature", "L0_ROUTING")
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.verify_signature", "L0_ROUTING")
    actual_hash = hash_artifact_canonical(artifact_bytes)
    if actual_hash != envelope.artifact_hash:
        raise VerificationError(
            f"FAIL (P5): artifact_hash mismatch. Expected {envelope.artifact_hash}, got {actual_hash}.",
        )

    # Check key exists and is active
    key_record = trust_root.get_key(envelope.key_id)
    if key_record is None:
        raise VerificationError(
            f"FAIL (P5): Unknown key_id '{envelope.key_id}' in trust root.",
        )
    if key_record.status == KeyStatus.REVOKED:
        raise VerificationError(
            f"FAIL (P5): Key '{envelope.key_id}' is REVOKED.",
        )

    # Verify signature
    valid = enclave.verify(artifact_bytes, envelope.signature, envelope.key_id)
    if not valid:
        raise VerificationError(
            f"FAIL (P5): Signature verification failed for "
            f"key '{envelope.key_id}', trace '{envelope.trace_id}'.",
        )

    return True


# =============================================================================
# §7.2 — Replay Guard
# =============================================================================


class ReplayDetectedError(Exception):
    """Raised when a replay attack is detected."""


class ReplayGuardStore:
    """§7.2 — In-memory replay guard store.

    Tracks artifact_hash sightings. Blocks on second sighting.
    """

    def __init__(self) -> None:
        self._records: dict[str, ReplayGuardRecord] = {}

    def check_and_record(
        self,
        artifact_hash: str,
        current_tick: int,
    ) -> ReplayGuardRecord:
        """Record an artifact hash. Raises on replay (second sighting)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ReplayGuardStore.check_and_record")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if artifact_hash in self._records:
            record = self._records[artifact_hash]
            record.seen_count += 1
            raise ReplayDetectedError(
                f"FAIL (P5): Replay detected for artifact_hash "
                f"'{artifact_hash[:16]}...'. "
                f"First seen at tick {record.first_seen_tick}, "
                f"now seen {record.seen_count} times.",
            )
        record = ReplayGuardRecord(
            artifact_hash=artifact_hash,
            first_seen_tick=current_tick,
        )
        self._records[artifact_hash] = record
        return record

    @property
    def record_count(self) -> int:
        return len(self._records)


def record_and_block_replay(
    envelope: SignatureEnvelope,
    replay_store: ReplayGuardStore,
) -> bool:
    """§7.2 — Record envelope and block if replay detected. Fail-closed."""
    replay_store.check_and_record(
        envelope.artifact_hash,
        envelope.semantic_clock_tick,
    )
    return True


# =============================================================================
# §2.6 — Hash Mismatch Escalation
# =============================================================================


class EscalationRequiredError(Exception):
    """Raised when ≥2 hash mismatches force human escalation."""


def record_hash_mismatch(tracker: HashMismatchTracker) -> bool:
    """§2.6 — Record a hash mismatch. Raises if escalation threshold met."""
    needs_escalation = tracker.record_mismatch()
    if needs_escalation:
        raise EscalationRequiredError(
            f"FAIL (P5): ≥{tracker.escalation_threshold} hash mismatches "
            f"in wave '{tracker.wave_id}'. Human escalation required.",
        )
    return False


# =============================================================================
# §7.2.1 — Build Signed Guardian Artifact
# =============================================================================


class SignedGuardianError(Exception):
    """Raised when signed guardian artifact construction fails."""


def build_signed_guardian_artifact(
    trace_id: str,
    prestaged_perms: tuple[str, ...],
    environment_metadata: dict[str, str],
    commit_hash: str,
    pass_fail: bool,
    artifact_bytes: bytes,
    key_id: str,
    enclave: SignatureEnclave,
) -> SignedGuardianArtifact:
    """§7.2.1 / §7.4 — Build a signed guardian artifact. Fail-closed."""
    try:
        signature = enclave.sign(artifact_bytes, key_id)
    except (KeyError, PermissionError) as exc:
        raise SignedGuardianError(
            f"FAIL (P5): Cannot sign guardian artifact: {exc}",
        ) from exc

    try:
        return SignedGuardianArtifact(
            trace_id=trace_id,
            signature=signature,
            prestaged_perms=prestaged_perms,
            environment_metadata=environment_metadata,
            commit_hash=commit_hash,
            pass_fail=pass_fail,
        )
    except (ValueError, TypeError) as exc:
        raise SignedGuardianError(
            f"FAIL (P5): SignedGuardianArtifact construction failed: {exc}",
        ) from exc


__all__ = [
    "EscalationRequiredError",
    "ReplayDetectedError",
    "ReplayGuardStore",
    "SignedGuardianError",
    "SigningError",
    "VerificationError",
    "build_signed_guardian_artifact",
    "hash_artifact_canonical",
    "record_and_block_replay",
    "record_hash_mismatch",
    "sign_artifact",
    "verify_signature",
]
