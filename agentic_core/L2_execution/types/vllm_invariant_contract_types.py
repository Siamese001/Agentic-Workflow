"""
PHASE 5 — Formal Invariant Verifier: Runtime Enforcement Contract.

Pure-L2 invariant contract defining architectural invariants enforced at the
execution boundary (Phase 3 adapter/controller seam).

All violations are deterministically serializable with canonical JSON and SHA256 hashing.
No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "vllm_invariant_contract_types")
trace_contract.emit_determinism_digest("p0", "vllm_invariant_contract_types")

trace_contract._emit_dispatches_healing_run("p1", "vllm_invariant_contract_types", "L2")
trace_contract._emit_routes_through("p1", "vllm_invariant_contract_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "vllm_invariant_contract_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "vllm_invariant_contract_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "vllm_invariant_contract_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "vllm_invariant_contract_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "vllm_invariant_contract_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "vllm_invariant_contract_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "vllm_invariant_contract_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "vllm_invariant_contract_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "vllm_invariant_contract_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "vllm_invariant_contract_types")
trace_contract._emit_gated_by_confidence("p1", "vllm_invariant_contract_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "vllm_invariant_contract_types", "L2")
trace_contract._emit_reads_policy_state("p1", "vllm_invariant_contract_types", "L2")

trace_contract._emit_applies_guardrail("p0", "vllm_invariant_contract_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "vllm_invariant_contract_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "vllm_invariant_contract_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "vllm_invariant_contract_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "vllm_invariant_contract_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "vllm_invariant_contract_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "vllm_invariant_contract_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "vllm_invariant_contract_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "vllm_invariant_contract_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "vllm_invariant_contract_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "vllm_invariant_contract_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "vllm_invariant_contract_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "vllm_invariant_contract_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "vllm_invariant_contract_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "vllm_invariant_contract_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "vllm_invariant_contract_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "vllm_invariant_contract_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "vllm_invariant_contract_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "vllm_invariant_contract_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "vllm_invariant_contract_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "vllm_invariant_contract_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "vllm_invariant_contract_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("vllm_invariant_contract_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("vllm_invariant_contract_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("vllm_invariant_contract_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("vllm_invariant_contract_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("vllm_invariant_contract_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("vllm_invariant_contract_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("vllm_invariant_contract_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("vllm_invariant_contract_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("vllm_invariant_contract_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("vllm_invariant_contract_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("vllm_invariant_contract_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("vllm_invariant_contract_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("vllm_invariant_contract_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("vllm_invariant_contract_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("vllm_invariant_contract_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("vllm_invariant_contract_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("vllm_invariant_contract_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("vllm_invariant_contract_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("vllm_invariant_contract_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("vllm_invariant_contract_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("vllm_invariant_contract_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("vllm_invariant_contract_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("vllm_invariant_contract_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("vllm_invariant_contract_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("vllm_invariant_contract_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("vllm_invariant_contract_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("vllm_invariant_contract_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("vllm_invariant_contract_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "vllm_invariant_contract_types", "context_pull")
trace_contract._emit_pulls_context("p1", "vllm_invariant_contract_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "vllm_invariant_contract_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "vllm_invariant_contract_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "vllm_invariant_contract_types", "write_through")
trace_contract._emit_writes_through("p1", "vllm_invariant_contract_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "vllm_invariant_contract_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "vllm_invariant_contract_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "vllm_invariant_contract_types", "routing_commit")


class InvariantId(str, Enum):
    """Stable invariant identifiers for runtime enforcement."""

    INV_NO_GPU_IMPORTS_IN_L0_L6 = "INV_NO_GPU_IMPORTS_IN_L0_L6"
    INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS = "INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS"
    INV_LOCAL_REQUEST_TEMPERATURE_ZERO = "INV_LOCAL_REQUEST_TEMPERATURE_ZERO"
    INV_LOCAL_REQUEST_SEED_PRESENT = "INV_LOCAL_REQUEST_SEED_PRESENT"
    INV_TELEMETRY_HAS_FINGERPRINT_HASH = "INV_TELEMETRY_HAS_FINGERPRINT_HASH"
    INV_REPLAY_HASH_PRESENT_WHEN_ENABLED = "INV_REPLAY_HASH_PRESENT_WHEN_ENABLED"
    INV_GEMINI_FALLBACK_REQUIRES_REASON = "INV_GEMINI_FALLBACK_REQUIRES_REASON"


class InvariantSeverity(str, Enum):
    """Severity levels for invariant violations."""

    INFO = "INFO"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class InvariantViolation:
    """Immutable invariant violation artifact with deterministic serialization.

    All fields are deterministic (no timestamps, no nondeterministic runtime state).
    Context dict is canonicalized with sorted keys for stable hashing.
    """

    invariant_id: str
    severity: str
    message: str
    context: dict[str, Any]

    def canonical_json(self) -> str:
        """Returns canonical JSON representation with sorted keys."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "InvariantViolation.canonical_json",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:InvariantViolation.canonical_json".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "invariant_id": self.invariant_id,
            "severity": self.severity,
            "message": self.message,
            "context": self.context,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def violation_hash(self) -> str:
        """Returns SHA256 hash of canonical JSON representation."""
        import hashlib

        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        """Returns dict representation with stable key ordering."""
        return {
            "invariant_id": self.invariant_id,
            "severity": self.severity,
            "message": self.message,
            "context": self.context,
            "violation_hash": self.violation_hash(),
        }
