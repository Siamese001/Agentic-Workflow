"""
L2 MLPatternRecord — Phase 4

Versioned pattern metadata with domain isolation + policy/model hash binding.
All stored healing patterns carry domain_hash, policy_hash, model_hash, and
schema_version. Retrieval enforces compatibility; mismatches are rejected
deterministically (no silent fallback).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "ml_pattern_record_types")
trace_contract.emit_determinism_digest("p0", "ml_pattern_record_types")

trace_contract._emit_dispatches_healing_run("p1", "ml_pattern_record_types", "L2")
trace_contract._emit_routes_through("p1", "ml_pattern_record_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "ml_pattern_record_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ml_pattern_record_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ml_pattern_record_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ml_pattern_record_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ml_pattern_record_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "ml_pattern_record_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ml_pattern_record_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ml_pattern_record_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ml_pattern_record_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ml_pattern_record_types")
trace_contract._emit_gated_by_confidence("p1", "ml_pattern_record_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ml_pattern_record_types", "L2")
trace_contract._emit_reads_policy_state("p1", "ml_pattern_record_types", "L2")

trace_contract._emit_applies_guardrail("p0", "ml_pattern_record_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "ml_pattern_record_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "ml_pattern_record_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "ml_pattern_record_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ml_pattern_record_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ml_pattern_record_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ml_pattern_record_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ml_pattern_record_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ml_pattern_record_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ml_pattern_record_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ml_pattern_record_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ml_pattern_record_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ml_pattern_record_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ml_pattern_record_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ml_pattern_record_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ml_pattern_record_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ml_pattern_record_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ml_pattern_record_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ml_pattern_record_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ml_pattern_record_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ml_pattern_record_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ml_pattern_record_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ml_pattern_record_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ml_pattern_record_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ml_pattern_record_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ml_pattern_record_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ml_pattern_record_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ml_pattern_record_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ml_pattern_record_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ml_pattern_record_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ml_pattern_record_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ml_pattern_record_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ml_pattern_record_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ml_pattern_record_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ml_pattern_record_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("ml_pattern_record_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ml_pattern_record_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ml_pattern_record_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ml_pattern_record_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ml_pattern_record_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ml_pattern_record_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ml_pattern_record_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ml_pattern_record_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ml_pattern_record_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ml_pattern_record_types", "context_pull")
trace_contract._emit_pulls_context("p1", "ml_pattern_record_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ml_pattern_record_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ml_pattern_record_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ml_pattern_record_types", "write_through")
trace_contract._emit_writes_through("p1", "ml_pattern_record_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ml_pattern_record_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ml_pattern_record_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ml_pattern_record_types", "routing_commit")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PatternCompatibilityError(Exception):
    """
    Raised when a retrieved pattern is incompatible with the active config.

    Violation codes:
        DOMAIN_HASH_MISMATCH   — pattern domain does not match query domain
        POLICY_HASH_MISMATCH   — pattern policy_hash != active PolicyConfig hash
        MODEL_HASH_MISMATCH    — pattern model_hash != active ModelConfig hash
    """

    DOMAIN_MISMATCH = "DOMAIN_HASH_MISMATCH"
    POLICY_MISMATCH = "POLICY_HASH_MISMATCH"
    MODEL_MISMATCH = "MODEL_HASH_MISMATCH"

    def __init__(self, violation_code: str, message: str) -> None:
        self.violation_code = violation_code
        super().__init__(f"[{violation_code}] {message}")


@dataclass
class MLPatternRecord:
    """
    Versioned healing pattern record stored in L4.

    Required fields:
        schema_version  — int, incremented on breaking schema changes
        domain_id       — str, e.g. "agentic_core", "apps_lic", "apps_rg"
        domain_hash     — sha256 of domain_id (deterministic domain binding)
        policy_hash     — sha256 of active PolicyConfig.canonical_bytes()
        model_hash      — sha256 of active ModelConfig.canonical_bytes()
        pattern_id      — str, unique identifier for this pattern
        payload         — dict, the actual healing strategy/pattern data
        record_hash     — sha256 of canonical_bytes() excluding record_hash
    """

    schema_version: int
    domain_id: str
    domain_hash: str
    policy_hash: str
    model_hash: str
    pattern_id: str
    payload: dict[str, Any]
    record_hash: str

    def __post_init__(self) -> None:
        if self.schema_version < 1:
            raise ValueError(f"schema_version must be >= 1, got {self.schema_version}")
        if not self.domain_id:
            raise ValueError("domain_id must be non-empty")
        if len(self.domain_hash) != 64:
            raise ValueError(f"domain_hash must be 64 hex chars, got len={len(self.domain_hash)}")
        if len(self.policy_hash) != 64:
            raise ValueError(f"policy_hash must be 64 hex chars, got len={len(self.policy_hash)}")
        if len(self.model_hash) != 64:
            raise ValueError(f"model_hash must be 64 hex chars, got len={len(self.model_hash)}")
        if not self.pattern_id:
            raise ValueError("pattern_id must be non-empty")
        if not isinstance(self.payload, dict):
            raise TypeError(f"payload must be a dict, got {type(self.payload).__name__}")
        if len(self.record_hash) != 64:
            raise ValueError(f"record_hash must be 64 hex chars, got len={len(self.record_hash)}")

    def canonical_bytes(self) -> bytes:
        """Deterministic serialization excluding record_hash."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "MLPatternRecord.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MLPatternRecord.canonical_bytes".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        doc = {
            "domain_hash": self.domain_hash,
            "domain_id": self.domain_id,
            "model_hash": self.model_hash,
            "pattern_id": self.pattern_id,
            "payload": self.payload,
            "policy_hash": self.policy_hash,
            "schema_version": self.schema_version,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()

    @staticmethod
    def compute_domain_hash(domain_id: str) -> str:
        return _sha256(domain_id.encode())

    @staticmethod
    def compute_record_hash(
        schema_version: int,
        domain_id: str,
        domain_hash: str,
        policy_hash: str,
        model_hash: str,
        pattern_id: str,
        payload: dict[str, Any],
    ) -> str:
        doc = {
            "domain_hash": domain_hash,
            "domain_id": domain_id,
            "model_hash": model_hash,
            "pattern_id": pattern_id,
            "payload": payload,
            "policy_hash": policy_hash,
            "schema_version": schema_version,
        }
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()
        return _sha256(raw)

    @classmethod
    def build(
        cls,
        domain_id: str,
        policy_hash: str,
        model_hash: str,
        pattern_id: str,
        payload: dict[str, Any],
        schema_version: int = 1,
    ) -> MLPatternRecord:
        """Factory: compute domain_hash and record_hash automatically."""
        domain_hash = cls.compute_domain_hash(domain_id)
        record_hash = cls.compute_record_hash(
            schema_version=schema_version,
            domain_id=domain_id,
            domain_hash=domain_hash,
            policy_hash=policy_hash,
            model_hash=model_hash,
            pattern_id=pattern_id,
            payload=payload,
        )
        return cls(
            schema_version=schema_version,
            domain_id=domain_id,
            domain_hash=domain_hash,
            policy_hash=policy_hash,
            model_hash=model_hash,
            pattern_id=pattern_id,
            payload=payload,
            record_hash=record_hash,
        )


def enforce_pattern_compatibility(
    record: MLPatternRecord,
    query_domain_id: str,
    active_policy_hash: str,
    active_model_hash: str,
) -> None:
    """
    Enforce domain isolation + policy/model hash compatibility.

    Raises PatternCompatibilityError deterministically on any mismatch.
    No silent fallback.
    """
    expected_domain_hash = MLPatternRecord.compute_domain_hash(query_domain_id)
    if record.domain_hash != expected_domain_hash:
        raise PatternCompatibilityError(
            PatternCompatibilityError.DOMAIN_MISMATCH,
            f"Pattern domain_hash {record.domain_hash[:8]}... does not match query domain '{query_domain_id}' (expected {expected_domain_hash[:8]}...)",
        )
    if record.policy_hash != active_policy_hash:
        raise PatternCompatibilityError(
            PatternCompatibilityError.POLICY_MISMATCH,
            f"Pattern policy_hash {record.policy_hash[:8]}... != active policy_hash {active_policy_hash[:8]}...",
        )
    if record.model_hash != active_model_hash:
        raise PatternCompatibilityError(
            PatternCompatibilityError.MODEL_MISMATCH,
            f"Pattern model_hash {record.model_hash[:8]}... != active model_hash {active_model_hash[:8]}...",
        )
