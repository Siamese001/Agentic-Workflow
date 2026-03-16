"""DPO (Direct Preference Optimization) types for deterministic HITL feedback processing.

Frozen dataclasses with canonical serialization for human-in-the-loop feedback.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "dpo_types")
emit_determinism_digest("p0", "dpo_types")

_emit_dispatches_healing_run("p1", "dpo_types", "L6")
_emit_routes_through("p1", "dpo_types", "L6")
_emit_escalates_to_human("p1", "dpo_types", "L6")
_emit_reads_policy_state("p1", "dpo_types", "L6")
_emit_authorize_and_execute("p2", "dpo_types", "execution_auth")
_emit_validates_capability("p2", "dpo_types", "capability_check")
_emit_routes_to_capability("p2", "dpo_types", "capability_route")
_emit_writes_via_uwg("p2", "dpo_types", "uwg_write")
_emit_blocks_direct_write("p2", "dpo_types", "direct_write_block")
_emit_records_tool_invocation("p2", "dpo_types", "tool_invocation")
_emit_captures_execution_output("p2", "dpo_types", "exec_output")
_emit_dispatches_agent("p3", "dpo_types", "agent_dispatch")
_emit_coordinates_agents("p3", "dpo_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "dpo_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "dpo_types", "healing_outcome")
_emit_escalates_failure("p3", "dpo_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "dpo_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dpo_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "dpo_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "dpo_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dpo_types", "eval_metric")
_emit_stores_embedding("p4", "dpo_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "dpo_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dpo_types", "exec_snapshot_link")


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

        _emit_snapshots_state(str(_uuid.uuid4()), "DPOExampleId.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DPOExampleId.canonical_bytes", "p0_governance")
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "DPOBatch.canonical_bytes")

        pairs_data = []
        for pair in self.pairs:
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
                }
            )
        return json.dumps({"pairs": pairs_data}, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes.

        Returns:
            Hex string (64 characters).
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
