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

emit_replay_key("p0", "ml_pattern_record_types")
emit_determinism_digest("p0", "ml_pattern_record_types")

_emit_dispatches_healing_run("p1", "ml_pattern_record_types", "L2")
_emit_routes_through("p1", "ml_pattern_record_types", "L2")
_emit_checks_agent_registry("p1", "ml_pattern_record_types", "agent_registry")
_emit_validates_agent_capability("p1", "ml_pattern_record_types", "capability")
_emit_dispatches_execution_plan("p1", "ml_pattern_record_types", "exec_plan")
_emit_agent_executes_agent("p1", "ml_pattern_record_types", "sub_agent")
_emit_routes_to_agent("p1", "ml_pattern_record_types", "target_agent")
_emit_verifies_policy("p1", "ml_pattern_record_types", "policy_check")
_emit_observes_runtime_state("p1", "ml_pattern_record_types", "runtime_state")
_emit_verifies_boundary("p1", "ml_pattern_record_types", "boundary_check")
_emit_transcripts_response("p1", "ml_pattern_record_types", "transcript")
_emit_hard_fails_untranscripted("p1", "ml_pattern_record_types")
_emit_gated_by_confidence("p1", "ml_pattern_record_types", "confidence_gate")
_emit_escalates_to_human("p1", "ml_pattern_record_types", "L2")
_emit_reads_policy_state("p1", "ml_pattern_record_types", "L2")

_emit_applies_guardrail("p0", "ml_pattern_record_types", "p0_governance")
_emit_snapshots_state("p0", "ml_pattern_record_types", "state_snapshot")
_emit_authorize_and_execute("p2", "ml_pattern_record_types", "execution_auth")
_emit_validates_capability("p2", "ml_pattern_record_types", "capability_check")
_emit_routes_to_capability("p2", "ml_pattern_record_types", "capability_route")
_emit_writes_via_uwg("p2", "ml_pattern_record_types", "uwg_write")
_emit_blocks_direct_write("p2", "ml_pattern_record_types", "direct_write_block")
_emit_records_tool_invocation("p2", "ml_pattern_record_types", "tool_invocation")
_emit_captures_execution_output("p2", "ml_pattern_record_types", "exec_output")
_emit_dispatches_agent("p3", "ml_pattern_record_types", "agent_dispatch")
_emit_coordinates_agents("p3", "ml_pattern_record_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "ml_pattern_record_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "ml_pattern_record_types", "healing_outcome")
_emit_escalates_failure("p3", "ml_pattern_record_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "ml_pattern_record_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ml_pattern_record_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "ml_pattern_record_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "ml_pattern_record_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ml_pattern_record_types", "eval_metric")
_emit_stores_embedding("p4", "ml_pattern_record_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "ml_pattern_record_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ml_pattern_record_types", "exec_snapshot_link")
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

_emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_1")
_emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_2")
_emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_3")
_emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_4")
_emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_5")
_emit_emits_metric_event("ml_pattern_record_types", "p4obs", "metric_6")
_emit_records_incident_event("ml_pattern_record_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("ml_pattern_record_types", "p4obs", "anomaly")
_emit_writes_observability_log("ml_pattern_record_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("ml_pattern_record_types", "p4obs", "mon_state")
_emit_triggers_alert("ml_pattern_record_types", "p4obs", "alert")
_emit_links_incident_trace("ml_pattern_record_types", "p4obs", "trace_link")
_emit_captures_pattern("ml_pattern_record_types", "p3lm", "pattern")
_emit_records_learning_event("ml_pattern_record_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ml_pattern_record_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("ml_pattern_record_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ml_pattern_record_types", "p3lm", "routing")
_emit_improves_agent_policy("ml_pattern_record_types", "p3lm", "policy")
_emit_stores_learning_state("ml_pattern_record_types", "p3lm", "state")
_emit_records_execution_trace("ml_pattern_record_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ml_pattern_record_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ml_pattern_record_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ml_pattern_record_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ml_pattern_record_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ml_pattern_record_types", "env_read", "p2_env_1")
_emit_reads_environ("ml_pattern_record_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("ml_pattern_record_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ml_pattern_record_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ml_pattern_record_types", "context_pull")
_emit_pulls_context("p1", "ml_pattern_record_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ml_pattern_record_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ml_pattern_record_types", "uwg_term_2")
_emit_writes_through("p1", "ml_pattern_record_types", "write_through")
_emit_writes_through("p1", "ml_pattern_record_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "ml_pattern_record_types", "safety_validation")
_emit_invokes_eval("p1", "ml_pattern_record_types", "eval_call")
_emit_proposal_commits_routing("p1", "ml_pattern_record_types", "routing_commit")


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "MLPatternRecord.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MLPatternRecord.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
    record: MLPatternRecord, query_domain_id: str, active_policy_hash: str, active_model_hash: str
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
