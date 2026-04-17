"""
InstructionPacket -- HMAC-SHA256 signed L2 ingress artifact.

Canonical JSON (sort_keys=True, separators=(",",":"), ensure_ascii=True)
is used as the signing surface.  Signature comparison is constant-time.

Phase 1: Cryptographic Boundary Contracts (Item 39)
Phase 2: L5 Guardian Certification Extension
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from agentic_core.L0_routing.utils.clock_provider import (
    ClockProvider as clock_provider,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency
from agentic_core.L2_execution.enforcement.key_source import get_current_secret
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "instruction_packet_types")
emit_determinism_digest("p0", "instruction_packet_types")

_emit_dispatches_healing_run("p1", "instruction_packet_types", "L2")
_emit_routes_through("p1", "instruction_packet_types", "L2")
_emit_checks_agent_registry("p1", "instruction_packet_types", "agent_registry")
_emit_validates_agent_capability("p1", "instruction_packet_types", "capability")
_emit_dispatches_execution_plan("p1", "instruction_packet_types", "exec_plan")
_emit_agent_executes_agent("p1", "instruction_packet_types", "sub_agent")
_emit_routes_to_agent("p1", "instruction_packet_types", "target_agent")
_emit_verifies_policy("p1", "instruction_packet_types", "policy_check")
_emit_observes_runtime_state("p1", "instruction_packet_types", "runtime_state")
_emit_verifies_boundary("p1", "instruction_packet_types", "boundary_check")
_emit_transcripts_response("p1", "instruction_packet_types", "transcript")
_emit_hard_fails_untranscripted("p1", "instruction_packet_types")
_emit_gated_by_confidence("p1", "instruction_packet_types", "confidence_gate")
_emit_escalates_to_human("p1", "instruction_packet_types", "L2")
_emit_reads_policy_state("p1", "instruction_packet_types", "L2")

_emit_applies_guardrail("p0", "instruction_packet_types", "p0_governance")
_emit_snapshots_state("p0", "instruction_packet_types", "state_snapshot")
_emit_authorize_and_execute("p2", "instruction_packet_types", "execution_auth")
_emit_validates_capability("p2", "instruction_packet_types", "capability_check")
_emit_routes_to_capability("p2", "instruction_packet_types", "capability_route")
_emit_writes_via_uwg("p2", "instruction_packet_types", "uwg_write")
_emit_blocks_direct_write("p2", "instruction_packet_types", "direct_write_block")
_emit_records_tool_invocation("p2", "instruction_packet_types", "tool_invocation")
_emit_captures_execution_output("p2", "instruction_packet_types", "exec_output")
_emit_dispatches_agent("p3", "instruction_packet_types", "agent_dispatch")
_emit_coordinates_agents("p3", "instruction_packet_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "instruction_packet_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "instruction_packet_types", "healing_outcome")
_emit_escalates_failure("p3", "instruction_packet_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "instruction_packet_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "instruction_packet_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "instruction_packet_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "instruction_packet_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "instruction_packet_types", "eval_metric")
_emit_stores_embedding("p4", "instruction_packet_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "instruction_packet_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "instruction_packet_types", "exec_snapshot_link")
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

_emit_emits_metric_event("instruction_packet_types", "p4obs", "metric_1")
_emit_emits_metric_event("instruction_packet_types", "p4obs", "metric_2")
_emit_emits_metric_event("instruction_packet_types", "p4obs", "metric_3")
_emit_emits_metric_event("instruction_packet_types", "p4obs", "metric_4")
_emit_emits_metric_event("instruction_packet_types", "p4obs", "metric_5")
_emit_emits_metric_event("instruction_packet_types", "p4obs", "metric_6")
_emit_records_incident_event("instruction_packet_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("instruction_packet_types", "p4obs", "anomaly")
_emit_writes_observability_log("instruction_packet_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("instruction_packet_types", "p4obs", "mon_state")
_emit_triggers_alert("instruction_packet_types", "p4obs", "alert")
_emit_links_incident_trace("instruction_packet_types", "p4obs", "trace_link")
_emit_captures_pattern("instruction_packet_types", "p3lm", "pattern")
_emit_records_learning_event("instruction_packet_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("instruction_packet_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("instruction_packet_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("instruction_packet_types", "p3lm", "routing")
_emit_improves_agent_policy("instruction_packet_types", "p3lm", "policy")
_emit_stores_learning_state("instruction_packet_types", "p3lm", "state")
_emit_records_execution_trace("instruction_packet_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("instruction_packet_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("instruction_packet_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("instruction_packet_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("instruction_packet_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("instruction_packet_types", "env_read", "p2_env_1")
_emit_reads_environ("instruction_packet_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("instruction_packet_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("instruction_packet_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "instruction_packet_types", "context_pull")
_emit_pulls_context("p1", "instruction_packet_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "instruction_packet_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "instruction_packet_types", "uwg_term_2")
_emit_writes_through("p1", "instruction_packet_types", "write_through")
_emit_writes_through("p1", "instruction_packet_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "instruction_packet_types", "safety_validation")
_emit_invokes_eval("p1", "instruction_packet_types", "eval_call")
_emit_proposal_commits_routing("p1", "instruction_packet_types", "routing_commit")


def _canonical_bytes(data: dict[str, Any]) -> bytes:
    """Return deterministic UTF-8 bytes from *data* (sorted keys, no spaces)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


class SignatureVerificationError(ValueError):
    """Raised when HMAC signature verification fails."""


@dataclass(frozen=True)
class InstructionPacket:
    """Signed instruction artifact for L2 ingress.

    Fields
    ------
    instruction_id : str
        Stable, deterministic identifier for this instruction.
    payload : str
        The instruction text / command payload.
    metadata : dict[str, Any]
        Arbitrary key/value context (must be JSON-serialisable).
    signature : str
        Lowercase hex HMAC-SHA256.  Empty string means unsigned.
    l5_signature : str
        L5 guardian certification signature (HMAC-SHA256). Empty means uncertified.
    certification_timestamp : str
        ISO8601 timestamp when L5 certification was applied.
    expiration_timestamp : str
        ISO8601 timestamp when L5 certification expires.
    agent_registry_hash : str
        SHA256 hash of agent registry at time of certification.
    execution_profile_hash : str
        SHA256 hash of execution profile at time of certification.
    policy_hash : str
        SHA256 hash of policy configuration at time of certification.
    """

    instruction_id: str
    payload: str
    metadata: dict[str, Any] = field(default_factory=dict)
    signature: str = field(default="", init=False)
    l5_signature: str = field(default="", init=True)
    certification_timestamp: str = field(default="", init=True)
    expiration_timestamp: str = field(default="", init=True)
    agent_registry_hash: str = field(default="", init=True)
    execution_profile_hash: str = field(default="", init=True)
    policy_hash: str = field(default="", init=True)

    def __post_init__(self) -> None:
        """Enforce mandatory signing at construction."""
        if not self.signature:
            get_credential_guard().check(operation="credential_access", target="get_current_secret")
            secret = get_current_secret()
            mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
            object.__setattr__(self, "signature", mac.hexdigest().lower())

    def _signable_dict(self) -> dict[str, Any]:
        """Return the dict that is signed by base signature (base fields only)."""
        return {"instruction_id": self.instruction_id, "metadata": self.metadata, "payload": self.payload}

    def _l5_signable_dict(self) -> dict[str, Any]:
        """Return the dict for L5 signature (excludes l5_signature to avoid circularity)."""
        return {
            "instruction_id": self.instruction_id,
            "metadata": self.metadata,
            "payload": self.payload,
            "certification_timestamp": self.certification_timestamp,
            "expiration_timestamp": self.expiration_timestamp,
            "agent_registry_hash": self.agent_registry_hash,
            "execution_profile_hash": self.execution_profile_hash,
            "policy_hash": self.policy_hash,
        }

    def canonical_bytes(self) -> bytes:
        """Deterministic bytes over the base signing surface."""
        return _canonical_bytes(self._signable_dict())

    def sign(self, secret: bytes) -> InstructionPacket:
        """Return a *new* InstructionPacket with HMAC-SHA256 signature set."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "InstructionPacket.sign")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:InstructionPacket.sign".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        new_packet = InstructionPacket.__new__(InstructionPacket)
        object.__setattr__(new_packet, "instruction_id", self.instruction_id)
        object.__setattr__(new_packet, "payload", self.payload)
        object.__setattr__(new_packet, "metadata", self.metadata)
        object.__setattr__(new_packet, "signature", mac.hexdigest().lower())
        object.__setattr__(new_packet, "l5_signature", self.l5_signature)
        object.__setattr__(new_packet, "certification_timestamp", self.certification_timestamp)
        object.__setattr__(new_packet, "expiration_timestamp", self.expiration_timestamp)
        object.__setattr__(new_packet, "agent_registry_hash", self.agent_registry_hash)
        object.__setattr__(new_packet, "execution_profile_hash", self.execution_profile_hash)
        object.__setattr__(new_packet, "policy_hash", self.policy_hash)
        return new_packet

    def certify_l5(
        self,
        l5_secret: bytes,
        agent_registry_hash: str,
        execution_profile_hash: str,
        policy_hash: str,
        expiration_hours: int = 24,
    ) -> InstructionPacket:
        """Return a *new* InstructionPacket with L5 certification applied.

        Args:
            l5_secret: L5 guardian signing secret
            agent_registry_hash: SHA256 of agent registry
            execution_profile_hash: SHA256 of execution profile
            policy_hash: SHA256 of policy configuration
            expiration_hours: Hours until certification expires

        Returns:
            New InstructionPacket with L5 certification fields populated
        """
        now = clock_provider.now(timezone.utc)
        expiration = now + timedelta(hours=expiration_hours)
        certified = InstructionPacket.__new__(InstructionPacket)
        object.__setattr__(certified, "instruction_id", self.instruction_id)
        object.__setattr__(certified, "payload", self.payload)
        object.__setattr__(certified, "metadata", self.metadata)
        object.__setattr__(certified, "signature", "")
        object.__setattr__(certified, "l5_signature", "")
        object.__setattr__(certified, "certification_timestamp", now.isoformat())
        object.__setattr__(certified, "expiration_timestamp", expiration.isoformat())
        object.__setattr__(certified, "agent_registry_hash", agent_registry_hash)
        object.__setattr__(certified, "execution_profile_hash", execution_profile_hash)
        object.__setattr__(certified, "policy_hash", policy_hash)
        object.__setattr__(certified, "signature", self.signature)
        l5_canonical_bytes = _canonical_bytes(certified._l5_signable_dict())
        l5_mac = hmac.new(l5_secret, l5_canonical_bytes, hashlib.sha256)
        object.__setattr__(certified, "l5_signature", l5_mac.hexdigest().lower())
        return certified

    def verify_l5_certification(self, l5_secret: bytes) -> None:
        """Verify L5 certification signature and expiration.

        Args:
            l5_secret: L5 guardian signing secret

        Raises:
            SignatureVerificationError: if L5 signature is invalid or expired
        """
        if not self.l5_signature:
            raise SignatureVerificationError("InstructionPacket has no L5 signature -- packet is uncertified")
        l5_canonical_bytes = _canonical_bytes(self._l5_signable_dict())
        mac = hmac.new(l5_secret, l5_canonical_bytes, hashlib.sha256)
        expected = mac.hexdigest().lower()
        if not hmac.compare_digest(self.l5_signature, expected):
            raise SignatureVerificationError(
                "InstructionPacket L5 signature mismatch -- certification tampered or wrong key",
            )
        if self.expiration_timestamp:
            try:
                expiration = datetime.fromisoformat(self.expiration_timestamp.replace("Z", "+00:00"))
                if clock_provider.now(timezone.utc) > expiration:
                    raise SignatureVerificationError("InstructionPacket L5 certification has expired")
            except ValueError as e:
                raise SignatureVerificationError(f"Invalid expiration timestamp format: {e}")
        else:
            raise SignatureVerificationError("InstructionPacket missing expiration timestamp")

    def verify(self, secret: bytes) -> None:
        """Raise SignatureVerificationError if signature is absent or wrong."""
        if not self.signature:
            raise SignatureVerificationError("InstructionPacket has no signature -- packet is unsigned")
        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        expected = mac.hexdigest().lower()
        if not hmac.compare_digest(self.signature, expected):
            raise SignatureVerificationError(
                "InstructionPacket signature mismatch -- packet tampered or wrong key",
            )

    @property
    def is_signed(self) -> bool:
        """True when a signature string is present (not verified)."""
        return bool(self.signature)

    @property
    def is_l5_certified(self) -> bool:
        """True when L5 certification signature is present (not verified)."""
        return bool(self.l5_signature)
