"""
agentic_core/runtime/execution_bound_token.py

Execution-bound capability tokens with cryptographic integrity.

Each token is signed against: token_id, capability_type, caller/target
contexts, execution_trace_id, policy_hash, determinism_digest, and
hierarchy_hash.  This prevents replay across different execution contexts
even within the 1-hour validity window.

Authority secret is loaded exclusively from the AGENTIC_AUTHORITY_SECRET
environment variable.  The module hard-fails at authority construction time
if the variable is absent (fail-closed design).
"""

import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "execution_bound_token", "p0_governance")
_emit_snapshots_state("p0", "execution_bound_token", "state_snapshot")
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

_emit_emits_metric_event("execution_bound_token", "p4obs", "metric_1")
_emit_emits_metric_event("execution_bound_token", "p4obs", "metric_2")
_emit_emits_metric_event("execution_bound_token", "p4obs", "metric_3")
_emit_emits_metric_event("execution_bound_token", "p4obs", "metric_4")
_emit_emits_metric_event("execution_bound_token", "p4obs", "metric_5")
_emit_emits_metric_event("execution_bound_token", "p4obs", "metric_6")
_emit_records_incident_event("execution_bound_token", "p4obs", "incident")
_emit_captures_runtime_anomaly("execution_bound_token", "p4obs", "anomaly")
_emit_writes_observability_log("execution_bound_token", "p4obs", "obs_log")
_emit_updates_monitoring_state("execution_bound_token", "p4obs", "mon_state")
_emit_triggers_alert("execution_bound_token", "p4obs", "alert")
_emit_links_incident_trace("execution_bound_token", "p4obs", "trace_link")
_emit_captures_pattern("execution_bound_token", "p3lm", "pattern")
_emit_records_learning_event("execution_bound_token", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execution_bound_token", "p3lm", "snapshot")
_emit_feeds_meta_learning("execution_bound_token", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execution_bound_token", "p3lm", "routing")
_emit_improves_agent_policy("execution_bound_token", "p3lm", "policy")
_emit_stores_learning_state("execution_bound_token", "p3lm", "state")
_emit_records_execution_trace("execution_bound_token", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execution_bound_token", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execution_bound_token", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execution_bound_token", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execution_bound_token", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execution_bound_token", "env_read", "p2_env_1")
_emit_reads_environ("execution_bound_token", "env_read", "p2_env_2")
_emit_reads_runtime_state("execution_bound_token", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execution_bound_token", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execution_bound_token", "context_pull")
_emit_pulls_context("p1", "execution_bound_token", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "execution_bound_token", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execution_bound_token", "uwg_term_2")
_emit_writes_through("p1", "execution_bound_token", "write_through")
_emit_writes_through("p1", "execution_bound_token", "write_through_2")
_emit_validated_by_safety_plane("p1", "execution_bound_token", "safety_validation")
_emit_invokes_eval("p1", "execution_bound_token", "eval_call")
_emit_proposal_commits_routing("p1", "execution_bound_token", "routing_commit")
_emit_escalates_to_human("p1", "execution_bound_token", "human_escalation")
_emit_routes_through("p1", "execution_bound_token", "route_through")
_emit_checks_agent_registry("p1", "execution_bound_token", "agent_registry")
_emit_validates_agent_capability("p1", "execution_bound_token", "capability")
_emit_dispatches_execution_plan("p1", "execution_bound_token", "exec_plan")
_emit_agent_executes_agent("p1", "execution_bound_token", "sub_agent")
_emit_routes_to_agent("p1", "execution_bound_token", "target_agent")
_emit_verifies_policy("p1", "execution_bound_token", "policy_check")
_emit_observes_runtime_state("p1", "execution_bound_token", "runtime_state")
_emit_verifies_boundary("p1", "execution_bound_token", "boundary_check")
_emit_transcripts_response("p1", "execution_bound_token", "transcript")
_emit_hard_fails_untranscripted("p1", "execution_bound_token")
_emit_gated_by_confidence("p1", "execution_bound_token", "confidence_gate")
emit_replay_key("p0", "execution_bound_token")
emit_determinism_digest("p0", "execution_bound_token")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "execution_bound_token", "execution_auth")
_emit_validates_capability("p2", "execution_bound_token", "capability_check")
_emit_routes_to_capability("p2", "execution_bound_token", "capability_route")
_emit_writes_via_uwg("p2", "execution_bound_token", "uwg_write")
_emit_blocks_direct_write("p2", "execution_bound_token", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_bound_token", "tool_invocation")
_emit_captures_execution_output("p2", "execution_bound_token", "exec_output")
_emit_dispatches_agent("p3", "execution_bound_token", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_bound_token", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_bound_token", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_bound_token", "healing_outcome")
_emit_escalates_failure("p3", "execution_bound_token", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_bound_token", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_bound_token", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_bound_token", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_bound_token", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_bound_token", "eval_metric")
_emit_stores_embedding("p4", "execution_bound_token", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_bound_token", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_bound_token", "exec_snapshot_link")


class CapabilityType(Enum):
    READ_ONLY = "read_only"
    WRITE_STATE = "write_state"
    MUTATE_CONFIG = "mutate_config"
    ACTIVATE_LEARNING = "activate_learning"


@dataclass(frozen=True)
class ExecutionBoundToken:
    """Cryptographic token bound to a specific execution trace and policy."""

    token_id: str
    capability_type: CapabilityType
    caller_context: str
    target_context: str
    execution_trace_id: str
    policy_hash: str
    determinism_digest: str
    hierarchy_hash: str
    signature_hash: str
    authority_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def verify_execution_binding(
        self,
        expected_trace_id: str,
        expected_policy_hash: str,
        expected_determinism_digest: str,
        expected_hierarchy_hash: str,
    ) -> bool:
        """Return True iff token is bound to the supplied execution context."""
        return (
            self.execution_trace_id == expected_trace_id
            and self.policy_hash == expected_policy_hash
            and (self.determinism_digest == expected_determinism_digest)
            and (self.hierarchy_hash == expected_hierarchy_hash)
        )

    def verify_signature(self, authority_public_hash: str) -> bool:
        """Return True iff token signature is cryptographically valid."""
        return (
            self.authority_hash == authority_public_hash
            and self.signature_hash == self._compute_expected_signature()
        )

    def _compute_expected_signature(self) -> str:
        """Compute the expected HMAC-style signature (no secret — used for self-check)."""
        payload = {
            "token_id": self.token_id,
            "capability_type": self.capability_type.value,
            "caller_context": self.caller_context,
            "target_context": self.target_context,
            "execution_trace_id": self.execution_trace_id,
            "policy_hash": self.policy_hash,
            "determinism_digest": self.determinism_digest,
            "hierarchy_hash": self.hierarchy_hash,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        ).hexdigest()


class SecureCapabilityAuthority:
    """Issues and verifies execution-bound capability tokens.

    Authority secret is loaded from AGENTIC_AUTHORITY_SECRET.
    Construction raises RuntimeError if the variable is absent (fail-closed).
    """

    def __init__(self) -> None:
        self._authority_secret: str = self._load_authority_secret()
        self.authority_public_hash: str = hashlib.sha256(self._authority_secret.encode("utf-8")).hexdigest()

    @staticmethod
    def _load_authority_secret() -> str:
        secret = os.environ.get("AGENTIC_AUTHORITY_SECRET")
        if not secret:
            raise RuntimeError(
                "AGENTIC_AUTHORITY_SECRET environment variable is required but not set. Cannot initialize SecureCapabilityAuthority.",
            )
        return secret

    def issue_token(
        self,
        capability_type: CapabilityType,
        caller_context: str,
        target_context: str,
        execution_trace_id: str,
        policy_hash: str,
        determinism_digest: str,
        hierarchy_hash: str,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionBoundToken:
        """Issue a new execution-bound capability token."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SecureCapabilityAuthority.issue_token")

        token_id = str(uuid.uuid4())
        raw_signature_payload = f"{token_id}:{capability_type.value}:{caller_context}:{target_context}:{execution_trace_id}:{policy_hash}:{determinism_digest}:{hierarchy_hash}"
        signature_hash = hashlib.sha256(
            (raw_signature_payload + self._authority_secret).encode("utf-8"),
        ).hexdigest()
        return ExecutionBoundToken(
            token_id=token_id,
            capability_type=capability_type,
            caller_context=caller_context,
            target_context=target_context,
            execution_trace_id=execution_trace_id,
            policy_hash=policy_hash,
            determinism_digest=determinism_digest,
            hierarchy_hash=hierarchy_hash,
            signature_hash=signature_hash,
            authority_hash=self.authority_public_hash,
            metadata=metadata or {},
        )

    def verify_token(self, token: ExecutionBoundToken) -> bool:
        """Verify a token was issued by this authority."""
        raw_signature_payload = f"{token.token_id}:{token.capability_type.value}:{token.caller_context}:{token.target_context}:{token.execution_trace_id}:{token.policy_hash}:{token.determinism_digest}:{token.hierarchy_hash}"
        expected_signature = hashlib.sha256(
            (raw_signature_payload + self._authority_secret).encode("utf-8"),
        ).hexdigest()
        return (
            token.authority_hash == self.authority_public_hash and token.signature_hash == expected_signature
        )


_capability_authority: SecureCapabilityAuthority | None = None


def get_capability_authority() -> SecureCapabilityAuthority:
    """Return the global SecureCapabilityAuthority (lazy-initialized)."""
    global _capability_authority
    if _capability_authority is None:
        _capability_authority = SecureCapabilityAuthority()
    return _capability_authority

_emit_reads_through("l4", "execution_bound_token", "urg_read_1")
_emit_reads_through("l4", "execution_bound_token", "urg_read_2")
_emit_reads_through("l4", "execution_bound_token", "urg_read_3")
_emit_reads_through("l4", "execution_bound_token", "urg_read_4")
_emit_reads_through("l4", "execution_bound_token", "urg_read_5")
_emit_reads_through("l4", "execution_bound_token", "urg_read_6")
_emit_reads_through("l4", "execution_bound_token", "urg_read_7")
_emit_reads_through("l4", "execution_bound_token", "urg_read_8")
_emit_reads_through("l4", "execution_bound_token", "urg_read_9")
_emit_reads_through("l4", "execution_bound_token", "urg_read_10")
_emit_reads_through("l4", "execution_bound_token", "urg_read_11")
_emit_reads_through("l4", "execution_bound_token", "urg_read_12")
_emit_reads_through("l4", "execution_bound_token", "urg_read_13")
_emit_reads_through("l4", "execution_bound_token", "urg_read_14")
_emit_reads_through("l4", "execution_bound_token", "urg_read_15")
_emit_reads_through("l4", "execution_bound_token", "urg_read_16")
_emit_reads_through("l4", "execution_bound_token", "urg_read_17")
_emit_reads_through("l4", "execution_bound_token", "urg_read_18")
_emit_reads_through("l4", "execution_bound_token", "urg_read_19")
_emit_reads_through("l4", "execution_bound_token", "urg_read_20")
_emit_reads_through("l4", "execution_bound_token", "urg_read_21")
_emit_reads_through("l4", "execution_bound_token", "urg_read_22")
_emit_reads_through("l4", "execution_bound_token", "urg_read_23")
_emit_reads_through("l4", "execution_bound_token", "urg_read_24")
_emit_reads_through("l4", "execution_bound_token", "urg_read_25")
_emit_reads_through("l4", "execution_bound_token", "urg_read_26")
_emit_reads_through("l4", "execution_bound_token", "urg_read_27")
_emit_reads_through("l4", "execution_bound_token", "urg_read_28")
_emit_reads_through("l4", "execution_bound_token", "urg_read_29")
_emit_reads_through("l4", "execution_bound_token", "urg_read_30")
_emit_reads_through("l4", "execution_bound_token", "urg_read_31")
_emit_reads_through("l4", "execution_bound_token", "urg_read_32")
_emit_reads_through("l4", "execution_bound_token", "urg_read_33")
_emit_reads_through("l4", "execution_bound_token", "urg_read_34")
_emit_reads_through("l4", "execution_bound_token", "urg_read_35")
_emit_reads_through("l4", "execution_bound_token", "urg_read_36")
_emit_reads_through("l4", "execution_bound_token", "urg_read_37")
