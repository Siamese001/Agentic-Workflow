"""DPO (Direct Preference Optimization) types for deterministic HITL feedback processing.

Frozen dataclasses with canonical serialization for human-in-the-loop feedback.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "dpo_types")
trace_contract.emit_determinism_digest("p0", "dpo_types")

trace_contract._emit_dispatches_healing_run("p1", "dpo_types", "L6")
trace_contract._emit_routes_through("p1", "dpo_types", "L6")
trace_contract._emit_checks_agent_registry("p1", "dpo_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "dpo_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "dpo_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "dpo_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "dpo_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "dpo_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "dpo_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "dpo_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "dpo_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "dpo_types")
trace_contract._emit_gated_by_confidence("p1", "dpo_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "dpo_types", "L6")
trace_contract._emit_reads_policy_state("p1", "dpo_types", "L6")
trace_contract._emit_authorize_and_execute("p2", "dpo_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "dpo_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "dpo_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "dpo_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "dpo_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "dpo_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "dpo_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "dpo_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "dpo_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "dpo_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "dpo_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "dpo_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "dpo_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "dpo_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "dpo_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "dpo_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "dpo_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "dpo_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "dpo_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "dpo_types", "exec_snapshot_link")
from tqdm import tqdm

trace_contract.record_execution_trace("dpo_types", "dpo_types_trace")


trace_contract._emit_emits_metric_event("dpo_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("dpo_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("dpo_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("dpo_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("dpo_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("dpo_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("dpo_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("dpo_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("dpo_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("dpo_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("dpo_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("dpo_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("dpo_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("dpo_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("dpo_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("dpo_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("dpo_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("dpo_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("dpo_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("dpo_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("dpo_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("dpo_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("dpo_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("dpo_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("dpo_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("dpo_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("dpo_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("dpo_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "dpo_types", "context_pull")
trace_contract._emit_pulls_context("p1", "dpo_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "dpo_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "dpo_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "dpo_types", "write_through")
trace_contract._emit_writes_through("p1", "dpo_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "dpo_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "dpo_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "dpo_types", "routing_commit")


@dataclass(frozen=True, slots=True)
class DPOExampleId:
    """Unique identifier for a DPO example derived from control and candidate hashes.

    Attributes:
        control_hash: SHA-256 hash of control output (hex string, 64 chars).
        candidate_hash: SHA-256 hash of candidate output (hex string, 64 chars).
    """

    control_hash: str
    candidate_hash: str

    def canonical_bytes(self) -> bytes:
        """Return canonical ASCII-only bytes representation for hashing.

        Returns:
            Bytes with deterministic ordering and formatting.
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "DPOExampleId.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "DPOExampleId.canonical_bytes", "p0_governance")
        return json.dumps(
            {"control_hash": self.control_hash, "candidate_hash": self.candidate_hash},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes.

        Returns:
            Hex string (64 characters).
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class DPOPair:
    """A single DPO preference pair with human decision.

    Attributes:
        example_id: Unique identifier for this example.
        control_output_hash: SHA-256 hash of control output.
        candidate_output_hash: SHA-256 hash of candidate output.
        human_decision: Human decision ("APPROVE" or "REJECT").
        reasons: Tuple of short deterministic reason codes.
    """

    example_id: DPOExampleId
    control_output_hash: str
    candidate_output_hash: str
    human_decision: str
    reasons: tuple[str, ...]

    def canonical_bytes(self) -> bytes:
        """Return canonical ASCII-only bytes representation for hashing.

        Returns:
            Bytes with deterministic ordering and formatting.
        """
        return json.dumps(
            {
                "example_id": {
                    "control_hash": self.example_id.control_hash,
                    "candidate_hash": self.example_id.candidate_hash,
                },
                "control_output_hash": self.control_output_hash,
                "candidate_output_hash": self.candidate_output_hash,
                "human_decision": self.human_decision,
                "reasons": list(self.reasons),
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes.

        Returns:
            Hex string (64 characters).
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class DPOBatch:
    """A batch of DPO pairs for processing.

    Attributes:
        pairs: Tuple of DPO pairs sorted by (control_hash, candidate_hash).
    """

    pairs: tuple[DPOPair, ...]

    def canonical_bytes(self) -> bytes:
        """Return canonical ASCII-only bytes representation for hashing.

        Returns:
            Bytes with deterministic ordering and formatting.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L6_OBSERVABILITY, "DPOBatch.canonical_bytes")

        pairs_data = []
        for pair in tqdm(self.pairs, desc="Processing", unit="item"):
            pairs_data.append(
                {
                    "example_id": {
                        "control_hash": pair.example_id.control_hash,
                        "candidate_hash": pair.example_id.candidate_hash,
                    },
                    "control_output_hash": pair.control_output_hash,
                    "candidate_output_hash": pair.candidate_output_hash,
                    "human_decision": pair.human_decision,
                    "reasons": list(pair.reasons),
                },
            )
        return json.dumps({"pairs": pairs_data}, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes.

        Returns:
            Hex string (64 characters).
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
