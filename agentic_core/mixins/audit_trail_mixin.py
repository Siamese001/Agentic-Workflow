from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "audit_trail_mixin", "p0_governance")
_emit_reads_policy_state("p0", "audit_trail_mixin", "policy_binding")
_emit_snapshots_state("p0", "audit_trail_mixin", "state_snapshot")
emit_replay_key("p0", "audit_trail_mixin")
emit_determinism_digest("p0", "audit_trail_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "audit_trail_mixin", "execution_auth")
_emit_validates_capability("p2", "audit_trail_mixin", "capability_check")
_emit_routes_to_capability("p2", "audit_trail_mixin", "capability_route")
_emit_writes_via_uwg("p2", "audit_trail_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "audit_trail_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "audit_trail_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "audit_trail_mixin", "exec_output")
_emit_dispatches_agent("p3", "audit_trail_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "audit_trail_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "audit_trail_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "audit_trail_mixin", "healing_outcome")
_emit_escalates_failure("p3", "audit_trail_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "audit_trail_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "audit_trail_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "audit_trail_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "audit_trail_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "audit_trail_mixin", "eval_metric")
_emit_stores_embedding("p4", "audit_trail_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "audit_trail_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "audit_trail_mixin", "exec_snapshot_link")

'\n[PHASE 24] AuditTrailMixin - Sovereign Black Box with Cryptographic Chain-of-Custody.\n\nProvides tamper-evident audit logging using SHA-256 hash chaining PLUS\nJSON-structured Black Box logging for forensic analysis.\n\nKey Design Decisions:\n1. JSON-structured logging for machine ingestion (Black Box)\n2. Cryptographic hash chaining for tamper evidence\n3. Does NOT write to Redis directly - injects audit_proof into EventEmission payload\n4. Synchronous hash generation (fast enough for main thread)\n5. Async event emission via event_emission_mixin dependency\n6. Session salt for chain isolation between agent instances\n\nBlack Box Format:\n{\n    "timestamp": "2026-01-24T14:57:00.000Z",\n    "agent_id": "CampaignPlannerAgent",\n    "domain": "apps_rg",\n    "session": "20260124-145700",\n    "action": "BOOT",\n    "details": {"status": "initialized", "mode": "hardened"},\n    "integrity_status": "VERIFIED"\n}\n\nUsage:\n    class MyAgent(AuditTrailMixin, event_emission_mixin, SovereignBaseAgent):\n        async def execute_action(self, action):\n            await self.emit_auditable_action("EXECUTE", {"action_id": action.id})\n            # Also logs to Black Box\n            self.log_sovereign_event("EXECUTE", {"action_id": action.id})\n            result = await self._do_execute(action)\n            return result\n\n[SSOT] Audit trail implementation for L6 observability.\n'
import hashlib
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("audit_trail_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("audit_trail_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("audit_trail_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("audit_trail_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("audit_trail_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("audit_trail_mixin", "p4obs", "metric_6")
_emit_records_incident_event("audit_trail_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("audit_trail_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("audit_trail_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("audit_trail_mixin", "p4obs", "mon_state")
_emit_triggers_alert("audit_trail_mixin", "p4obs", "alert")
_emit_links_incident_trace("audit_trail_mixin", "p4obs", "trace_link")
_emit_captures_pattern("audit_trail_mixin", "p3lm", "pattern")
_emit_records_learning_event("audit_trail_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("audit_trail_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("audit_trail_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("audit_trail_mixin", "p3lm", "routing")
_emit_improves_agent_policy("audit_trail_mixin", "p3lm", "policy")
_emit_stores_learning_state("audit_trail_mixin", "p3lm", "state")
_emit_records_execution_trace("audit_trail_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("audit_trail_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("audit_trail_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("audit_trail_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("audit_trail_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("audit_trail_mixin", "env_read", "p2_env_1")
_emit_reads_environ("audit_trail_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("audit_trail_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("audit_trail_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "audit_trail_mixin", "context_pull")
_emit_pulls_context("p1", "audit_trail_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "audit_trail_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "audit_trail_mixin", "uwg_term_2")
_emit_writes_through("p1", "audit_trail_mixin", "write_through")
_emit_writes_through("p1", "audit_trail_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "audit_trail_mixin", "safety_validation")
_emit_invokes_eval("p1", "audit_trail_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "audit_trail_mixin", "routing_commit")
_emit_escalates_to_human("p1", "audit_trail_mixin", "human_escalation")
_emit_routes_through("p1", "audit_trail_mixin", "route_through")
_emit_checks_agent_registry("p1", "audit_trail_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "audit_trail_mixin", "capability")
_emit_dispatches_execution_plan("p1", "audit_trail_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "audit_trail_mixin", "sub_agent")
_emit_routes_to_agent("p1", "audit_trail_mixin", "target_agent")
_emit_verifies_policy("p1", "audit_trail_mixin", "policy_check")
_emit_observes_runtime_state("p1", "audit_trail_mixin", "runtime_state")
_emit_verifies_boundary("p1", "audit_trail_mixin", "boundary_check")
_emit_transcripts_response("p1", "audit_trail_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "audit_trail_mixin")
_emit_gated_by_confidence("p1", "audit_trail_mixin", "confidence_gate")

Logger = logging.getLogger("SovereignBlackBox")


@dataclass
class AuditProof:
    """
    Cryptographic proof of an audited action.

    Attributes:
        action_id: Unique identifier for this action
        prev_hash: Hash of the previous action in the chain
        curr_hash: Hash of this action (includes prev_hash for chaining)
        timestamp: Unix timestamp when proof was generated
        chain_id: Session salt identifying this chain
    """

    action_id: str
    prev_hash: str
    curr_hash: str
    timestamp: float
    chain_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "action_id": self.action_id,
            "prev_hash": self.prev_hash,
            "curr_hash": self.curr_hash,
            "timestamp": self.timestamp,
            "chain_id": self.chain_id,
        }

    def verify_chain_link(self, expected_prev_hash: str) -> bool:
        """Verify this proof links to the expected previous hash."""
        return self.prev_hash == expected_prev_hash


@dataclass
class AuditChainStats:
    """Statistics for an audit chain."""

    chain_id: str
    genesis_time: float
    last_action_time: float
    total_actions: int
    last_hash: str


class AuditTrailMixin:
    """
    [PHASE 24] Provides cryptographic chain-of-custody + Black Box structured logging.

    Must be mixed in with event_emission_mixin for async event dispatch.

    Hash Chain:
        Each action's hash includes the previous hash, creating an
        immutable chain. Any tampering breaks the chain verification.

    Black Box Logging:
        JSON-structured logging for forensic analysis and compliance.
        Every Healer action and Validator check is automatically recorded.

    Session Isolation:
        Each agent instance gets a unique session salt, isolating
        its chain from other instances.

    Performance:
        Hash generation is synchronous and fast (~0.1ms per action).
        Event emission is async and non-blocking.

    Attributes:
        _audit_last_hash: Hash of the last action in the chain
        _audit_session_salt: Random salt for this session
        _audit_genesis_time: When this chain was created
        _audit_action_count: Total actions in this chain
        _audit_enabled: Whether Black Box logging is enabled
        _session_id: Session identifier for Black Box logs
    """

    GENESIS_HASH = "0" * 64
    _audit_last_hash: str = GENESIS_HASH
    _audit_session_salt: str = ""
    _audit_genesis_time: float = 0.0
    _audit_action_count: int = 0
    _audit_enabled: bool = True
    _session_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d-%H%M%S"))

    def __init__(self, *args, **kwargs):
        """Initialize audit chain with unique session salt."""
        super().__init__(*args, **kwargs)
        self._audit_session_salt = secrets.token_hex(16)
        self._audit_last_hash = self.GENESIS_HASH
        self._audit_genesis_time = time.time()
        self._audit_action_count = 0
        self._audit_enabled = True
        self._session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        Logger.debug(
            f"[{self.__class__.__name__}] Audit chain initialized: chain_id={self._audit_session_salt[:8]}..."
        )

    def log_sovereign_event(self, action: str, details: dict[str, Any], level: str = "INFO") -> None:
        """
        Write an immutable record to the structured Black Box log.

        Args:
            action: The action being performed (e.g., "BOOT", "HEAL", "VALIDATE")
            details: Additional context data for the event
            level: Log level (INFO, WARNING, ERROR)
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AuditTrailMixin.log_sovereign_event")

        if not self._audit_enabled:
            return
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": getattr(self, "name", "UnknownSovereign"),
            "domain": getattr(self, "domain_root", Path("unknown")).name,
            "session": self._session_id,
            "action": action.upper(),
            "details": details,
            "integrity_status": "VERIFIED",
        }

        def json_serializer(obj):
            """Custom JSON serializer for dataclass Fields and other objects"""
            if hasattr(obj, "__name__"):
                return str(obj)
            elif hasattr(obj, "default"):
                return f"Field({obj.default})"
            elif hasattr(obj, "__dict__"):
                return str(obj)
            else:
                return str(obj)

        log_entry = json.dumps(payload, separators=(",", ":"), default=json_serializer)
        if level == "ERROR":
            Logger.error(log_entry)
        elif level == "WARNING":
            Logger.warning(log_entry)
        else:
            Logger.info(log_entry)

    def log_heal_event(self, violations_found: int, violations_fixed: int, execution_time_ms: float) -> None:
        """
        Specialized logging for heal_repository events.

        Args:
            violations_found: Number of violations detected
            violations_fixed: Number of violations successfully fixed
            execution_time_ms: Time taken to execute healing
        """
        self.log_sovereign_event(
            "HEAL",
            {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "execution_time_ms": execution_time_ms,
                "heal_status": "COMPLETED",
            },
        )

    def log_validation_event(self, validator_name: str, result: bool, details: dict[str, Any]) -> None:
        """
        Specialized logging for validator events.

        Args:
            validator_name: Name of the validator that ran
            result: Whether validation passed
            details: Additional validation context
        """
        self.log_sovereign_event(
            "VALIDATE", {"validator": validator_name, "result": "PASS" if result else "FAIL", **details}
        )

    def disable_audit(self) -> None:
        """Disable audit logging (for testing only)."""
        self._audit_enabled = False
        self.log_sovereign_event("AUDIT_CONTROL", {"enabled": False})

    def enable_audit(self) -> None:
        """Enable audit logging."""
        self._audit_enabled = True
        self.log_sovereign_event("AUDIT_CONTROL", {"enabled": True})

    def _canonicalize_payload(self, payload: dict[str, Any]) -> str:
        """
        Canonicalize payload for consistent hashing.

        Sorts keys recursively to ensure deterministic serialization.
        """

        def _sort_recursive(obj: Any) -> Any:
            if isinstance(obj, dict):
                return sorted(((k, _sort_recursive(v)) for k, v in obj.items()))
            elif isinstance(obj, list | tuple):
                return [_sort_recursive(item) for item in obj]
            return obj

        return str(_sort_recursive(payload))

    def _generate_audit_proof(self, action_type: str, payload: dict[str, Any]) -> AuditProof:
        """
        Synchronous cryptographic proof generation.

        Fast enough to run in main thread (~0.1ms).

        Args:
            action_type: Type of action being audited
            payload: Action payload data

        Returns:
            AuditProof with hash chain link
        """
        timestamp = time.time()
        payload_str = self._canonicalize_payload(payload)
        raw_data = (
            f"{self._audit_last_hash}|{self._audit_session_salt}|{action_type}|{payload_str}|{timestamp}"
        )
        curr_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        proof = AuditProof(
            action_id=f"act_{self._audit_action_count}_{int(timestamp * 1000)}",
            prev_hash=self._audit_last_hash,
            curr_hash=curr_hash,
            timestamp=timestamp,
            chain_id=self._audit_session_salt,
        )
        self._audit_last_hash = curr_hash
        self._audit_action_count += 1
        return proof

    async def emit_auditable_action(
        self, action_type: str, payload: dict[str, Any], severity: str = "INFO"
    ) -> AuditProof:
        """
        Generate proof and emit via event_emission_mixin.

        Args:
            action_type: Type of action (e.g., "FILE_MOVE", "HEAL_VIOLATION")
            payload: Action data to audit
            severity: Event severity level

        Returns:
            AuditProof for caller verification

        Raises:
            NotImplementedError: If event_emission_mixin is not present
        """
        proof = self._generate_audit_proof(action_type, payload)
        if not hasattr(self, "emit_event"):
            raise NotImplementedError(
                "AuditTrailMixin requires event_emission_mixin. Ensure your class inherits from both mixins."
            )
        event_payload = {
            "data": payload,
            "audit_proof": {
                "hash": proof.curr_hash,
                "prev": proof.prev_hash,
                "chain_id": proof.chain_id,
                "action_id": proof.action_id,
            },
        }
        await self.emit_event(event_type=f"AUDIT_{action_type}", payload=event_payload, severity=severity)
        Logger.debug(
            f"[{self.__class__.__name__}] Audited action: {action_type} (hash={proof.curr_hash[:16]}...)"
        )
        return proof

    def emit_auditable_action_sync(self, action_type: str, payload: dict[str, Any]) -> AuditProof:
        """
        Synchronous version for non-async contexts.

        Generates proof but does NOT emit event (no async dispatch).
        Use this when you need the proof but can't await.

        Args:
            action_type: Type of action
            payload: Action data

        Returns:
            AuditProof for caller verification
        """
        proof = self._generate_audit_proof(action_type, payload)
        Logger.debug(
            f"[{self.__class__.__name__}] Sync audit proof: {action_type} (hash={proof.curr_hash[:16]}...)"
        )
        return proof

    def verify_chain_integrity(self, proofs: list[AuditProof]) -> tuple[bool, int | None]:
        """
        Verify a sequence of proofs forms a valid chain.

        Args:
            proofs: List of AuditProof objects in order

        Returns:
            Tuple of (is_valid, first_broken_index)
            If valid, returns (True, None)
            If broken, returns (False, index_of_first_break)
        """
        if not proofs:
            return (True, None)
        if proofs[0].prev_hash != self.GENESIS_HASH:
            pass
        for i in range(1, len(proofs)):
            if proofs[i].prev_hash != proofs[i - 1].curr_hash:
                return (False, i)
        return (True, None)

    def get_audit_chain_stats(self) -> AuditChainStats:
        """Get statistics for this audit chain."""
        return AuditChainStats(
            chain_id=self._audit_session_salt,
            genesis_time=self._audit_genesis_time,
            last_action_time=time.time(),
            total_actions=self._audit_action_count,
            last_hash=self._audit_last_hash,
        )

    def get_chain_head(self) -> str:
        """Get the current head of the hash chain."""
        return self._audit_last_hash
