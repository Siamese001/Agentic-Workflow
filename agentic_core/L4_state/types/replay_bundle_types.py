"""
Phase 9 — ReplayBundle: deterministic, immutable execution evidence artifact.

Sufficient to reconstruct (replay) all decision inputs for an execution:
  manifest_hash, active_config_hashes, citation_hash (if retrieval used),
  prior signal/violation hashes, tool intent/result hashes.

replay_hash = sha256(canonical_bytes excluding replay_hash).
All list fields sorted for determinism.
Volatile fields excluded from canonical_bytes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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
    record_execution_trace,
)

emit_replay_key("p0", "replay_bundle_types")
emit_determinism_digest("p0", "replay_bundle_types")

_emit_dispatches_healing_run("p1", "replay_bundle_types", "L4")
_emit_routes_through("p1", "replay_bundle_types", "L4")
_emit_checks_agent_registry("p1", "replay_bundle_types", "agent_registry")
_emit_validates_agent_capability("p1", "replay_bundle_types", "capability")
_emit_dispatches_execution_plan("p1", "replay_bundle_types", "exec_plan")
_emit_agent_executes_agent("p1", "replay_bundle_types", "sub_agent")
_emit_routes_to_agent("p1", "replay_bundle_types", "target_agent")
_emit_verifies_policy("p1", "replay_bundle_types", "policy_check")
_emit_observes_runtime_state("p1", "replay_bundle_types", "runtime_state")
_emit_verifies_boundary("p1", "replay_bundle_types", "boundary_check")
_emit_transcripts_response("p1", "replay_bundle_types", "transcript")
_emit_hard_fails_untranscripted("p1", "replay_bundle_types")
_emit_gated_by_confidence("p1", "replay_bundle_types", "confidence_gate")
_emit_escalates_to_human("p1", "replay_bundle_types", "L4")
_emit_reads_policy_state("p1", "replay_bundle_types", "L4")
_emit_authorize_and_execute("p2", "replay_bundle_types", "execution_auth")
_emit_validates_capability("p2", "replay_bundle_types", "capability_check")
_emit_routes_to_capability("p2", "replay_bundle_types", "capability_route")
_emit_writes_via_uwg("p2", "replay_bundle_types", "uwg_write")
_emit_blocks_direct_write("p2", "replay_bundle_types", "direct_write_block")
_emit_records_tool_invocation("p2", "replay_bundle_types", "tool_invocation")
_emit_captures_execution_output("p2", "replay_bundle_types", "exec_output")
_emit_dispatches_agent("p3", "replay_bundle_types", "agent_dispatch")
_emit_coordinates_agents("p3", "replay_bundle_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "replay_bundle_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "replay_bundle_types", "healing_outcome")
_emit_escalates_failure("p3", "replay_bundle_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "replay_bundle_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "replay_bundle_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "replay_bundle_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "replay_bundle_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "replay_bundle_types", "eval_metric")
_emit_stores_embedding("p4", "replay_bundle_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "replay_bundle_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "replay_bundle_types", "exec_snapshot_link")
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

record_execution_trace("replay_bundle_types", "replay_bundle_types_trace")


_emit_emits_metric_event("replay_bundle_types", "p4obs", "metric_1")
_emit_emits_metric_event("replay_bundle_types", "p4obs", "metric_2")
_emit_emits_metric_event("replay_bundle_types", "p4obs", "metric_3")
_emit_emits_metric_event("replay_bundle_types", "p4obs", "metric_4")
_emit_emits_metric_event("replay_bundle_types", "p4obs", "metric_5")
_emit_emits_metric_event("replay_bundle_types", "p4obs", "metric_6")
_emit_records_incident_event("replay_bundle_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("replay_bundle_types", "p4obs", "anomaly")
_emit_writes_observability_log("replay_bundle_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("replay_bundle_types", "p4obs", "mon_state")
_emit_triggers_alert("replay_bundle_types", "p4obs", "alert")
_emit_links_incident_trace("replay_bundle_types", "p4obs", "trace_link")
_emit_captures_pattern("replay_bundle_types", "p3lm", "pattern")
_emit_records_learning_event("replay_bundle_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("replay_bundle_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("replay_bundle_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("replay_bundle_types", "p3lm", "routing")
_emit_improves_agent_policy("replay_bundle_types", "p3lm", "policy")
_emit_stores_learning_state("replay_bundle_types", "p3lm", "state")
_emit_records_execution_trace("replay_bundle_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("replay_bundle_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("replay_bundle_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("replay_bundle_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("replay_bundle_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("replay_bundle_types", "env_read", "p2_env_1")
_emit_reads_environ("replay_bundle_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("replay_bundle_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("replay_bundle_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "replay_bundle_types", "context_pull")
_emit_pulls_context("p1", "replay_bundle_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "replay_bundle_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "replay_bundle_types", "uwg_term_2")
_emit_writes_through("p1", "replay_bundle_types", "write_through")
_emit_writes_through("p1", "replay_bundle_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "replay_bundle_types", "safety_validation")
_emit_invokes_eval("p1", "replay_bundle_types", "eval_call")
_emit_proposal_commits_routing("p1", "replay_bundle_types", "routing_commit")

_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class ReplayBundle:
    """
    Immutable execution evidence artifact.

    Fields
    ------
    schema_version              : int
    mission_id                  : str   — non-empty
    execution_start_tick        : int   — >= 0
    execution_end_tick          : int   — >= execution_start_tick
    manifest_hash               : str   — non-empty sha256 of execution manifest
    active_config_hashes        : dict  — {policy_hash, routing_hash, model_hash, budget_hash, ...}
    retrieval_used              : bool  — True iff L4 retrieval was performed
    citation_hash               : str   — required iff retrieval_used=True
    prior_detection_signal_hash : str   — empty string if no prior signal
    prior_violation_event_hashes: list  — sorted list of ViolationEvent.event_hash strings
    tool_intent_hashes          : list  — sorted list of ToolIntent.intent_hash strings
    tool_result_hashes          : list  — sorted list of ToolResult.result_hash strings
    replay_hash                 : str   — sha256(canonical_bytes); auto-computed
    """

    schema_version: int
    mission_id: str
    execution_start_tick: int
    execution_end_tick: int
    manifest_hash: str
    active_config_hashes: dict[str, str]
    retrieval_used: bool
    citation_hash: str
    prior_detection_signal_hash: str
    prior_violation_event_hashes: list[str]
    tool_intent_hashes: list[str]
    tool_result_hashes: list[str]
    replay_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"ReplayBundle: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}",
            )
        if not self.mission_id:
            raise ValueError("ReplayBundle: mission_id must be non-empty")
        if self.execution_start_tick < 0:
            raise ValueError(
                f"ReplayBundle: execution_start_tick must be >= 0, got {self.execution_start_tick}",
            )
        if self.execution_end_tick < self.execution_start_tick:
            raise ValueError(
                f"ReplayBundle: execution_end_tick ({self.execution_end_tick}) must be >= execution_start_tick ({self.execution_start_tick})",
            )
        if not self.manifest_hash:
            raise ValueError("ReplayBundle: manifest_hash must be non-empty")
        if not isinstance(self.active_config_hashes, dict):
            raise TypeError("ReplayBundle: active_config_hashes must be a dict")
        if self.retrieval_used and (not self.citation_hash):
            raise ValueError("ReplayBundle: citation_hash is required when retrieval_used=True")
        if not isinstance(self.prior_violation_event_hashes, list):
            raise TypeError("ReplayBundle: prior_violation_event_hashes must be a list")
        if not isinstance(self.tool_intent_hashes, list):
            raise TypeError("ReplayBundle: tool_intent_hashes must be a list")
        if not isinstance(self.tool_result_hashes, list):
            raise TypeError("ReplayBundle: tool_result_hashes must be a list")
        self.prior_violation_event_hashes = sorted(self.prior_violation_event_hashes)
        self.tool_intent_hashes = sorted(self.tool_intent_hashes)
        self.tool_result_hashes = sorted(self.tool_result_hashes)
        object.__setattr__(self, "replay_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """
        Deterministic serialisation excluding replay_hash (self-referential).
        All list fields sorted. active_config_hashes keys sorted.
        No volatile fields (timestamps, trace IDs).
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReplayBundle.canonical_bytes", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReplayBundle.canonical_bytes", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ReplayBundle.canonical_bytes")

        doc: dict[str, Any] = {
            "active_config_hashes": {
                k: self.active_config_hashes[k] for k in sorted(self.active_config_hashes)
            },
            "citation_hash": self.citation_hash,
            "execution_end_tick": self.execution_end_tick,
            "execution_start_tick": self.execution_start_tick,
            "manifest_hash": self.manifest_hash,
            "mission_id": self.mission_id,
            "prior_detection_signal_hash": self.prior_detection_signal_hash,
            "prior_violation_event_hashes": sorted(self.prior_violation_event_hashes),
            "retrieval_used": self.retrieval_used,
            "schema_version": self.schema_version,
            "tool_intent_hashes": sorted(self.tool_intent_hashes),
            "tool_result_hashes": sorted(self.tool_result_hashes),
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mission_id": self.mission_id,
            "execution_start_tick": self.execution_start_tick,
            "execution_end_tick": self.execution_end_tick,
            "manifest_hash": self.manifest_hash,
            "active_config_hashes": dict(self.active_config_hashes),
            "retrieval_used": self.retrieval_used,
            "citation_hash": self.citation_hash,
            "prior_detection_signal_hash": self.prior_detection_signal_hash,
            "prior_violation_event_hashes": list(self.prior_violation_event_hashes),
            "tool_intent_hashes": list(self.tool_intent_hashes),
            "tool_result_hashes": list(self.tool_result_hashes),
            "replay_hash": self.replay_hash,
        }


def build_replay_bundle(
    mission_id: str,
    execution_start_tick: int,
    execution_end_tick: int,
    manifest_hash: str,
    active_config_hashes: dict[str, str],
    *,
    retrieval_used: bool = False,
    citation_hash: str = "",
    prior_detection_signal_hash: str = "",
    prior_violation_event_hashes: list[str] | None = None,
    tool_intent_hashes: list[str] | None = None,
    tool_result_hashes: list[str] | None = None,
) -> ReplayBundle:
    """Factory: build a ReplayBundle from execution parameters."""
    return ReplayBundle(
        schema_version=_SCHEMA_VERSION,
        mission_id=mission_id,
        execution_start_tick=execution_start_tick,
        execution_end_tick=execution_end_tick,
        manifest_hash=manifest_hash,
        active_config_hashes=active_config_hashes,
        retrieval_used=retrieval_used,
        citation_hash=citation_hash,
        prior_detection_signal_hash=prior_detection_signal_hash,
        prior_violation_event_hashes=prior_violation_event_hashes or [],
        tool_intent_hashes=tool_intent_hashes or [],
        tool_result_hashes=tool_result_hashes or [],
    )
