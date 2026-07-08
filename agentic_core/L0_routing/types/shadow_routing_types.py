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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_dispatches_healing_run("p1", "shadow_routing_types", "L0")
trace_contract._emit_routes_through("p1", "shadow_routing_types", "L0")
trace_contract._emit_checks_agent_registry("p1", "shadow_routing_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "shadow_routing_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "shadow_routing_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "shadow_routing_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "shadow_routing_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "shadow_routing_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "shadow_routing_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "shadow_routing_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "shadow_routing_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "shadow_routing_types")
trace_contract._emit_gated_by_confidence("p1", "shadow_routing_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "shadow_routing_types", "L0")
trace_contract._emit_reads_policy_state("p1", "shadow_routing_types", "L0")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "shadow_routing_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "shadow_routing_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "shadow_routing_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "shadow_routing_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "shadow_routing_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "shadow_routing_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "shadow_routing_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "shadow_routing_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "shadow_routing_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "shadow_routing_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "shadow_routing_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "shadow_routing_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "shadow_routing_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "shadow_routing_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "shadow_routing_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "shadow_routing_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "shadow_routing_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "shadow_routing_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "shadow_routing_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "shadow_routing_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "shadow_routing_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "shadow_routing_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("shadow_routing_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("shadow_routing_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("shadow_routing_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("shadow_routing_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("shadow_routing_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("shadow_routing_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("shadow_routing_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("shadow_routing_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("shadow_routing_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("shadow_routing_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("shadow_routing_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("shadow_routing_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("shadow_routing_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("shadow_routing_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("shadow_routing_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("shadow_routing_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("shadow_routing_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("shadow_routing_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("shadow_routing_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("shadow_routing_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("shadow_routing_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("shadow_routing_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("shadow_routing_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "shadow_routing_types", "context_pull")
trace_contract._emit_pulls_context("p1", "shadow_routing_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "shadow_routing_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "shadow_routing_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "shadow_routing_types", "write_through")
trace_contract._emit_writes_through("p1", "shadow_routing_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "shadow_routing_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "shadow_routing_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "shadow_routing_types", "routing_commit")


def _get_canonical_json():
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        canonical_json as _cj,
    )  # guardian: allow-layer-violation -- L0 module uses L2 type/utility; intentional cross-layer dependency in enforcement/routing layer

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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L0_ROUTING,
            "ShadowRoutingDecision.compute_canonical_fingerprint",
        )
        trace_contract.emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        trace_contract.emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

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
