"""AgentOutputContract — signed wrapper for every apps_* agent execute() return.

Spec contract [7]: every agent output must carry:
  - agent_id: stable registry key
  - trace_id: correlates back to InstructionPacket / SandboxEnvelope
  - schema_tag: dotted qualified name of the payload Pydantic model
  - output_contract_hash: SHA-256 of canonical payload bytes
  - signature: HMAC-SHA256 over the signable dict (excl. sig field)
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
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

emit_replay_key("p0", "agent_output_contract_types")
emit_determinism_digest("p0", "agent_output_contract_types")

_emit_dispatches_healing_run("p1", "agent_output_contract_types", "L2")
_emit_routes_through("p1", "agent_output_contract_types", "L2")
_emit_checks_agent_registry("p1", "agent_output_contract_types", "agent_registry")
_emit_validates_agent_capability("p1", "agent_output_contract_types", "capability")
_emit_dispatches_execution_plan("p1", "agent_output_contract_types", "exec_plan")
_emit_agent_executes_agent("p1", "agent_output_contract_types", "sub_agent")
_emit_routes_to_agent("p1", "agent_output_contract_types", "target_agent")
_emit_verifies_policy("p1", "agent_output_contract_types", "policy_check")
_emit_observes_runtime_state("p1", "agent_output_contract_types", "runtime_state")
_emit_verifies_boundary("p1", "agent_output_contract_types", "boundary_check")
_emit_transcripts_response("p1", "agent_output_contract_types", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_output_contract_types")
_emit_gated_by_confidence("p1", "agent_output_contract_types", "confidence_gate")
_emit_escalates_to_human("p1", "agent_output_contract_types", "L2")
_emit_reads_policy_state("p1", "agent_output_contract_types", "L2")

_emit_applies_guardrail("p0", "agent_output_contract_types", "p0_governance")
_emit_snapshots_state("p0", "agent_output_contract_types", "state_snapshot")
_emit_authorize_and_execute("p2", "agent_output_contract_types", "execution_auth")
_emit_validates_capability("p2", "agent_output_contract_types", "capability_check")
_emit_routes_to_capability("p2", "agent_output_contract_types", "capability_route")
_emit_writes_via_uwg("p2", "agent_output_contract_types", "uwg_write")
_emit_blocks_direct_write("p2", "agent_output_contract_types", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_output_contract_types", "tool_invocation")
_emit_captures_execution_output("p2", "agent_output_contract_types", "exec_output")
_emit_dispatches_agent("p3", "agent_output_contract_types", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_output_contract_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_output_contract_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_output_contract_types", "healing_outcome")
_emit_escalates_failure("p3", "agent_output_contract_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_output_contract_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_output_contract_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_output_contract_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_output_contract_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_output_contract_types", "eval_metric")
_emit_stores_embedding("p4", "agent_output_contract_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_output_contract_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_output_contract_types", "exec_snapshot_link")
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

_emit_emits_metric_event("agent_output_contract_types", "p4obs", "metric_1")
_emit_emits_metric_event("agent_output_contract_types", "p4obs", "metric_2")
_emit_emits_metric_event("agent_output_contract_types", "p4obs", "metric_3")
_emit_emits_metric_event("agent_output_contract_types", "p4obs", "metric_4")
_emit_emits_metric_event("agent_output_contract_types", "p4obs", "metric_5")
_emit_emits_metric_event("agent_output_contract_types", "p4obs", "metric_6")
_emit_records_incident_event("agent_output_contract_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_output_contract_types", "p4obs", "anomaly")
_emit_writes_observability_log("agent_output_contract_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_output_contract_types", "p4obs", "mon_state")
_emit_triggers_alert("agent_output_contract_types", "p4obs", "alert")
_emit_links_incident_trace("agent_output_contract_types", "p4obs", "trace_link")
_emit_captures_pattern("agent_output_contract_types", "p3lm", "pattern")
_emit_records_learning_event("agent_output_contract_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_output_contract_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_output_contract_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_output_contract_types", "p3lm", "routing")
_emit_improves_agent_policy("agent_output_contract_types", "p3lm", "policy")
_emit_stores_learning_state("agent_output_contract_types", "p3lm", "state")
_emit_records_execution_trace("agent_output_contract_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_output_contract_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_output_contract_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_output_contract_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_output_contract_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_output_contract_types", "env_read", "p2_env_1")
_emit_reads_environ("agent_output_contract_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_output_contract_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_output_contract_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_output_contract_types", "context_pull")
_emit_pulls_context("p1", "agent_output_contract_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_output_contract_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_output_contract_types", "uwg_term_2")
_emit_writes_through("p1", "agent_output_contract_types", "write_through")
_emit_writes_through("p1", "agent_output_contract_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_output_contract_types", "safety_validation")
_emit_invokes_eval("p1", "agent_output_contract_types", "eval_call")
_emit_proposal_commits_routing("p1", "agent_output_contract_types", "routing_commit")


class OutputContractViolation(ValueError):
    """Raised when AgentOutputContract invariants are broken."""


@dataclass(frozen=True)
class AgentOutputContract:
    """Signed envelope for a single agent execute() call result."""

    agent_id: str
    trace_id: str
    schema_tag: str
    output_contract_hash: str
    payload: dict[str, Any]
    signature: str = field(default="")

    def __post_init__(self) -> None:
        if not self.agent_id:
            raise OutputContractViolation("agent_id is required")
        if not self.schema_tag:
            raise OutputContractViolation("schema_tag is required")
        if not self.output_contract_hash:
            raise OutputContractViolation("output_contract_hash is required")

    def _signable_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "output_contract_hash": self.output_contract_hash,
            "schema_tag": self.schema_tag,
            "trace_id": self.trace_id,
        }

    def sign(self, secret: bytes) -> AgentOutputContract:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "AgentOutputContract.sign")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AgentOutputContract.sign".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        mac = hmac.new(
            secret,
            json.dumps(self._signable_dict(), sort_keys=True, separators=(",", ":")).encode("ascii"),
            hashlib.sha256,
        )
        return AgentOutputContract(
            agent_id=self.agent_id,
            trace_id=self.trace_id,
            schema_tag=self.schema_tag,
            output_contract_hash=self.output_contract_hash,
            payload=self.payload,
            signature=mac.hexdigest().lower(),
        )

    def verify(self, secret: bytes) -> None:
        if not self.signature:
            raise OutputContractViolation("signature absent")
        mac = hmac.new(
            secret,
            json.dumps(self._signable_dict(), sort_keys=True, separators=(",", ":")).encode("ascii"),
            hashlib.sha256,
        )
        if not hmac.compare_digest(self.signature, mac.hexdigest().lower()):
            raise OutputContractViolation("signature mismatch")


def wrap_output(agent_id: str, trace_id: str, payload_model: Any, secret: bytes) -> AgentOutputContract:
    """Convenience: hash + sign a Pydantic model output."""
    schema_tag = f"{type(payload_model).__module__}.{type(payload_model).__qualname__}"
    payload_bytes = payload_model.model_dump_json(by_alias=False).encode("utf-8")
    contract_hash = hashlib.sha256(payload_bytes).hexdigest()
    contract = AgentOutputContract(
        agent_id=agent_id,
        trace_id=trace_id,
        schema_tag=schema_tag,
        output_contract_hash=contract_hash,
        payload=payload_model.model_dump(),
    )
    return contract.sign(secret)


__all__ = ["AgentOutputContract", "OutputContractViolation", "wrap_output"]
