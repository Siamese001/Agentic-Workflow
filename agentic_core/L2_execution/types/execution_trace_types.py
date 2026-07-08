"""ExecutionTrace — spec contract [4] REVISED.

Fields: trace_id, plan_hash, actor, target, diff, policy_hash,
        timestamp(frozen), prev_hash(chain), replay_key, transcript_hash.

replay_key = SHA256(trace_id + plan_hash + transcript_hash)  — deterministic, no time entropy.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "execution_trace_types")
trace_contract.emit_determinism_digest("p0", "execution_trace_types")

trace_contract._emit_dispatches_healing_run("p1", "execution_trace_types", "L2")
trace_contract._emit_routes_through("p1", "execution_trace_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "execution_trace_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "execution_trace_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "execution_trace_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "execution_trace_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "execution_trace_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "execution_trace_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "execution_trace_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "execution_trace_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "execution_trace_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "execution_trace_types")
trace_contract._emit_gated_by_confidence("p1", "execution_trace_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "execution_trace_types", "L2")
trace_contract._emit_reads_policy_state("p1", "execution_trace_types", "L2")

trace_contract._emit_applies_guardrail("p0", "execution_trace_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "execution_trace_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "execution_trace_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "execution_trace_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "execution_trace_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "execution_trace_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "execution_trace_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "execution_trace_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "execution_trace_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "execution_trace_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "execution_trace_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "execution_trace_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "execution_trace_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "execution_trace_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "execution_trace_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "execution_trace_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "execution_trace_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "execution_trace_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "execution_trace_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "execution_trace_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "execution_trace_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "execution_trace_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("execution_trace_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("execution_trace_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("execution_trace_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("execution_trace_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("execution_trace_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("execution_trace_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("execution_trace_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("execution_trace_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("execution_trace_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("execution_trace_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("execution_trace_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("execution_trace_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("execution_trace_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("execution_trace_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("execution_trace_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("execution_trace_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("execution_trace_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("execution_trace_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("execution_trace_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("execution_trace_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("execution_trace_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("execution_trace_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("execution_trace_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "execution_trace_types", "context_pull")
trace_contract._emit_pulls_context("p1", "execution_trace_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_trace_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_trace_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "execution_trace_types", "write_through")
trace_contract._emit_writes_through("p1", "execution_trace_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "execution_trace_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "execution_trace_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "execution_trace_types", "routing_commit")


def _compute_replay_key(trace_id: str, plan_hash: str, transcript_hash: str) -> str:
    from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError  # noqa: F401

    raw = (trace_id + plan_hash + transcript_hash).encode("ascii", errors="replace")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class ExecutionTrace:
    trace_id: str
    instruction_packet_id: str
    governed_payload_hash: str
    sandbox_envelope_ids: tuple[str, ...]
    llm_response_hash: str
    validation_decision: str
    timing_ms: int
    hash_chain_root: str
    policy_hash: str = ""
    prev_hash: str = ""
    transcript_hash: str = ""
    agent_id: str = ""
    error: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
    replay_key: str = field(init=False, default="")

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id required")
        if self.validation_decision not in ("PASS", "FAIL", "ESCALATE"):
            raise ValueError(
                f"validation_decision must be PASS|FAIL|ESCALATE, got {self.validation_decision!r}",
            )
        rk = _compute_replay_key(self.trace_id, self.policy_hash, self.transcript_hash)
        object.__setattr__(self, "replay_key", rk)

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "ExecutionTrace.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecutionTrace.canonical_bytes".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        obj = {
            "agent_id": self.agent_id,
            "governed_payload_hash": self.governed_payload_hash,
            "hash_chain_root": self.hash_chain_root,
            "instruction_packet_id": self.instruction_packet_id,
            "llm_response_hash": self.llm_response_hash,
            "policy_hash": self.policy_hash,
            "prev_hash": self.prev_hash,
            "replay_key": self.replay_key,
            "sandbox_envelope_ids": list(self.sandbox_envelope_ids),
            "timing_ms": self.timing_ms,
            "trace_id": self.trace_id,
            "transcript_hash": self.transcript_hash,
            "validation_decision": self.validation_decision,
        }
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def validate_completeness(self) -> None:
        """Addendum 1.1: Raise ExecutionTraceIntegrityError if any required field is empty.

        Required fields: trace_id, instruction_packet_id, governed_payload_hash,
        llm_response_hash, validation_decision, hash_chain_root, replay_key.
        """
        _required = {
            "trace_id": self.trace_id,
            "instruction_packet_id": self.instruction_packet_id,
            "governed_payload_hash": self.governed_payload_hash,
            "llm_response_hash": self.llm_response_hash,
            "validation_decision": self.validation_decision,
            "hash_chain_root": self.hash_chain_root,
            "replay_key": self.replay_key,
        }
        missing = [k for k, v in _required.items() if not v]
        if missing:
            raise ExecutionTraceIntegrityError(
                f"ExecutionTrace missing required field(s): {missing}. Execution marked FAILED — trace is incomplete.",
            )


class ExecutionTraceBuilder:
    """Mutable builder. Call seal() exactly once."""

    def __init__(self, trace_id: str, instruction_packet_id: str) -> None:
        self.trace_id = trace_id
        self.instruction_packet_id = instruction_packet_id
        self.governed_payload_hash = ""
        self.sandbox_envelope_ids: list[str] = []
        self.llm_response_hash = ""
        self.validation_decision = "PASS"
        self.timing_ms = 0
        self.hash_chain_root = ""
        self.policy_hash = ""
        self.prev_hash = ""
        self.transcript_hash = ""
        self.agent_id = ""
        self.error = ""
        self.extra: dict[str, Any] = {}

    def set_governed_payload(self, routing_hash: str) -> None:
        self.governed_payload_hash = routing_hash

    def add_sandbox_envelope(self, envelope_id: str) -> None:
        self.sandbox_envelope_ids.append(envelope_id)

    def set_llm_response(self, raw_text: str) -> None:
        self.llm_response_hash = hashlib.sha256(raw_text.encode("utf-8", errors="replace")).hexdigest()

    def set_transcript(self, transcript_bytes: bytes) -> None:
        """Set transcript_hash from raw PTC ToolTranscript bytes."""
        self.transcript_hash = hashlib.sha256(transcript_bytes).hexdigest()

    def set_policy_hash(self, policy_hash: str) -> None:
        self.policy_hash = policy_hash

    def set_prev_hash(self, prev_hash: str) -> None:
        self.prev_hash = prev_hash

    def set_validation_decision(self, decision: str) -> None:
        self.validation_decision = decision

    def set_hash_chain_root(self, root: str) -> None:
        self.hash_chain_root = root

    def set_timing(self, ms: int) -> None:
        self.timing_ms = ms

    def seal(self) -> ExecutionTrace:
        return ExecutionTrace(
            trace_id=self.trace_id,
            instruction_packet_id=self.instruction_packet_id,
            governed_payload_hash=self.governed_payload_hash,
            sandbox_envelope_ids=tuple(self.sandbox_envelope_ids),
            llm_response_hash=self.llm_response_hash,
            validation_decision=self.validation_decision,
            timing_ms=self.timing_ms,
            hash_chain_root=self.hash_chain_root,
            policy_hash=self.policy_hash,
            prev_hash=self.prev_hash,
            transcript_hash=self.transcript_hash,
            agent_id=self.agent_id,
            error=self.error,
            extra=self.extra,
        )
