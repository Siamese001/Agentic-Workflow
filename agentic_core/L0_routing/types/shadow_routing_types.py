"""
Phase 9: Shadow Router Types - Non-invasive routing drift detection.

Types for shadow routing decisions that observe L0 routing without affecting
live traffic. All shadow outputs are read-only side-channels.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L0_routing.types.routing_artifact_types import RoutePath
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "shadow_routing_types", "L0")
_emit_routes_through("p1", "shadow_routing_types", "L0")
_emit_checks_agent_registry("p1", "shadow_routing_types", "agent_registry")
_emit_validates_agent_capability("p1", "shadow_routing_types", "capability")
_emit_dispatches_execution_plan("p1", "shadow_routing_types", "exec_plan")
_emit_agent_executes_agent("p1", "shadow_routing_types", "sub_agent")
_emit_routes_to_agent("p1", "shadow_routing_types", "target_agent")
_emit_verifies_policy("p1", "shadow_routing_types", "policy_check")
_emit_observes_runtime_state("p1", "shadow_routing_types", "runtime_state")
_emit_verifies_boundary("p1", "shadow_routing_types", "boundary_check")
_emit_transcripts_response("p1", "shadow_routing_types", "transcript")
_emit_hard_fails_untranscripted("p1", "shadow_routing_types")
_emit_gated_by_confidence("p1", "shadow_routing_types", "confidence_gate")
_emit_escalates_to_human("p1", "shadow_routing_types", "L0")
_emit_reads_policy_state("p1", "shadow_routing_types", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "shadow_routing_types", "p0_governance")
_emit_snapshots_state("p0", "shadow_routing_types", "state_snapshot")
_emit_authorize_and_execute("p2", "shadow_routing_types", "execution_auth")
_emit_validates_capability("p2", "shadow_routing_types", "capability_check")
_emit_routes_to_capability("p2", "shadow_routing_types", "capability_route")
_emit_writes_via_uwg("p2", "shadow_routing_types", "uwg_write")
_emit_blocks_direct_write("p2", "shadow_routing_types", "direct_write_block")
_emit_records_tool_invocation("p2", "shadow_routing_types", "tool_invocation")
_emit_captures_execution_output("p2", "shadow_routing_types", "exec_output")
_emit_dispatches_agent("p3", "shadow_routing_types", "agent_dispatch")
_emit_coordinates_agents("p3", "shadow_routing_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "shadow_routing_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "shadow_routing_types", "healing_outcome")
_emit_escalates_failure("p3", "shadow_routing_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "shadow_routing_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "shadow_routing_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "shadow_routing_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "shadow_routing_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "shadow_routing_types", "eval_metric")
_emit_stores_embedding("p4", "shadow_routing_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "shadow_routing_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "shadow_routing_types", "exec_snapshot_link")
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

_emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_1")
_emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_2")
_emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_3")
_emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_4")
_emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_5")
_emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_6")
_emit_records_incident_event("shadow_routing_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("shadow_routing_types", "p4obs", "anomaly")
_emit_writes_observability_log("shadow_routing_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("shadow_routing_types", "p4obs", "mon_state")
_emit_triggers_alert("shadow_routing_types", "p4obs", "alert")
_emit_links_incident_trace("shadow_routing_types", "p4obs", "trace_link")
_emit_captures_pattern("shadow_routing_types", "p3lm", "pattern")
_emit_records_learning_event("shadow_routing_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("shadow_routing_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("shadow_routing_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("shadow_routing_types", "p3lm", "routing")
_emit_improves_agent_policy("shadow_routing_types", "p3lm", "policy")
_emit_stores_learning_state("shadow_routing_types", "p3lm", "state")
_emit_records_execution_trace("shadow_routing_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("shadow_routing_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("shadow_routing_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("shadow_routing_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("shadow_routing_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("shadow_routing_types", "env_read", "p2_env_1")
_emit_reads_environ("shadow_routing_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("shadow_routing_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("shadow_routing_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "shadow_routing_types", "context_pull")
_emit_pulls_context("p1", "shadow_routing_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "shadow_routing_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "shadow_routing_types", "uwg_term_2")
_emit_writes_through("p1", "shadow_routing_types", "write_through")
_emit_writes_through("p1", "shadow_routing_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "shadow_routing_types", "safety_validation")
_emit_invokes_eval("p1", "shadow_routing_types", "eval_call")
_emit_proposal_commits_routing("p1", "shadow_routing_types", "routing_commit")


def _get_canonical_json():
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import canonical_json as _cj

    return _cj


canonical_json = _get_canonical_json()


class ShadowRoutingRationale(str, Enum):
    """Shadow routing rationale - independent of live routing rationale."""

    ALIGN_WITH_LIVE = "align_with_live"
    ALTERNATE_PATH_SUGGESTED = "alternate_path_suggested"
    RISK_MITIGATION = "risk_mitigation"
    POLICY_OPTIMIZATION = "policy_optimization"
    FEATURE_DRIFT_DETECTED = "feature_drift_detected"


@dataclass(frozen=True)
class ShadowRoutingDecision:
    """Non-invasive shadow routing decision with drift detection.

    This artifact is produced after the actual routing decision is made
    and cannot affect the live route. It serves as a side-channel for
    detecting routing drift and providing shadow suggestions.
    """

    trace_id: str
    observed_route: RoutePath
    shadow_route: RoutePath
    drift_score: float
    feature_fingerprint: str
    timestamp: str
    shadow_rationale: ShadowRoutingRationale
    model_version: str = "shadow-router-v1.0"
    ruleset_version: str = "phase9-initial"
    semantic_clock: SemanticClockSnapshot | None = None
    feature_snapshot: dict[str, Any] | None = field(default=None, repr=False)

    def compute_canonical_fingerprint(self, features: dict[str, Any]) -> str:
        """Compute deterministic 64-hex fingerprint from routing features.

        Args:
            features: Dictionary of routing features used for classification

        Returns:
            64-character lowercase hex SHA256 digest
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ShadowRoutingDecision.compute_canonical_fingerprint",
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        canonical_features = canonical_json(features)
        return hashlib.sha256(canonical_features.encode("utf-8")).hexdigest()

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for hashing/storage.

        Returns:
            Canonical JSON string representation
        """
        canonical_dict = {
            "trace_id": self.trace_id,
            "observed_route": self.observed_route.value,
            "shadow_route": self.shadow_route.value,
            "drift_score": self.drift_score,
            "feature_fingerprint": self.feature_fingerprint,
            "model_version": self.model_version,
            "ruleset_version": self.ruleset_version,
            "shadow_rationale": self.shadow_rationale.value,
        }
        if self.semantic_clock is not None:
            canonical_dict["semantic_clock"] = self.semantic_clock.to_dict()
        return canonical_json(canonical_dict)


@dataclass(frozen=True)
class ShadowRoutingTelemetry:
    """Telemetry artifact for shadow routing observations.

    Emitted to L6 observability bus and optionally stored in L4.
    """

    trace_id: str
    shadow_decision: ShadowRoutingDecision
    emitted_at: str

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for storage/transmission."""
        return canonical_json(
            {
                "trace_id": self.trace_id,
                "shadow_decision": json.loads(self.shadow_decision.to_canonical_json()),
                "emitted_at": self.emitted_at,
            },
        )
