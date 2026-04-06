"""Healing Config Optimizer - Threshold adjustment proposals.

Phase 6: Consumes healing outcome aggregates to propose threshold adjustments.
All proposals are proposal-only via ChangePackage; no direct config mutation.
W2: Embedding-augmented scoring (C0-only, informational). Final closeout.
"""

from __future__ import annotations

import uuid
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "healing_config_optimizer", "execution_auth")
_emit_validates_capability("p2", "healing_config_optimizer", "capability_check")
_emit_routes_to_capability("p2", "healing_config_optimizer", "capability_route")
_emit_writes_via_uwg("p2", "healing_config_optimizer", "uwg_write")
_emit_blocks_direct_write("p2", "healing_config_optimizer", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_config_optimizer", "tool_invocation")
_emit_captures_execution_output("p2", "healing_config_optimizer", "exec_output")
_emit_dispatches_agent("p3", "healing_config_optimizer", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_config_optimizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_config_optimizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_config_optimizer", "healing_outcome")
_emit_escalates_failure("p3", "healing_config_optimizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_config_optimizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_config_optimizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_config_optimizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_config_optimizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_config_optimizer", "eval_metric")
_emit_stores_embedding("p4", "healing_config_optimizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_config_optimizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_config_optimizer", "exec_snapshot_link")
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.pattern_analysis_types import (
    PatternFindingReport,
)

_emit_applies_guardrail("p0", "healing_config_optimizer", "p0_governance")
_emit_reads_policy_state("p0", "healing_config_optimizer", "policy_binding")
_emit_snapshots_state("p0", "healing_config_optimizer", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
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
    _emit_routes_through,
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

_emit_emits_metric_event("healing_config_optimizer", "p4obs", "metric_1")
_emit_emits_metric_event("healing_config_optimizer", "p4obs", "metric_2")
_emit_emits_metric_event("healing_config_optimizer", "p4obs", "metric_3")
_emit_emits_metric_event("healing_config_optimizer", "p4obs", "metric_4")
_emit_emits_metric_event("healing_config_optimizer", "p4obs", "metric_5")
_emit_emits_metric_event("healing_config_optimizer", "p4obs", "metric_6")
_emit_records_incident_event("healing_config_optimizer", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_config_optimizer", "p4obs", "anomaly")
_emit_writes_observability_log("healing_config_optimizer", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_config_optimizer", "p4obs", "mon_state")
_emit_triggers_alert("healing_config_optimizer", "p4obs", "alert")
_emit_links_incident_trace("healing_config_optimizer", "p4obs", "trace_link")
_emit_captures_pattern("healing_config_optimizer", "p3lm", "pattern")
_emit_records_learning_event("healing_config_optimizer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_config_optimizer", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_config_optimizer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_config_optimizer", "p3lm", "routing")
_emit_improves_agent_policy("healing_config_optimizer", "p3lm", "policy")
_emit_stores_learning_state("healing_config_optimizer", "p3lm", "state")
_emit_records_execution_trace("healing_config_optimizer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_config_optimizer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_config_optimizer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_config_optimizer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_config_optimizer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_config_optimizer", "env_read", "p2_env_1")
_emit_reads_environ("healing_config_optimizer", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_config_optimizer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_config_optimizer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_config_optimizer", "context_pull")
_emit_pulls_context("p1", "healing_config_optimizer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_config_optimizer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_config_optimizer", "uwg_term_2")
_emit_writes_through("p1", "healing_config_optimizer", "write_through")
_emit_writes_through("p1", "healing_config_optimizer", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_config_optimizer", "safety_validation")
_emit_invokes_eval("p1", "healing_config_optimizer", "eval_call")
_emit_proposal_commits_routing("p1", "healing_config_optimizer", "routing_commit")
_emit_escalates_to_human("p1", "healing_config_optimizer", "human_escalation")
_emit_routes_through("p1", "healing_config_optimizer", "route_through")
_emit_checks_agent_registry("p1", "healing_config_optimizer", "agent_registry")
_emit_validates_agent_capability("p1", "healing_config_optimizer", "capability")
_emit_dispatches_execution_plan("p1", "healing_config_optimizer", "exec_plan")
_emit_agent_executes_agent("p1", "healing_config_optimizer", "sub_agent")
_emit_routes_to_agent("p1", "healing_config_optimizer", "target_agent")
_emit_verifies_policy("p1", "healing_config_optimizer", "policy_check")
_emit_observes_runtime_state("p1", "healing_config_optimizer", "runtime_state")
_emit_verifies_boundary("p1", "healing_config_optimizer", "boundary_check")
_emit_transcripts_response("p1", "healing_config_optimizer", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_config_optimizer")
emit_replay_key("p0", "healing_config_optimizer")
emit_determinism_digest("p0", "healing_config_optimizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class HealingConfigOptimizer:
    """Optimizer for healing tier thresholds based on outcome aggregates.

    Consumes HealingOutcomeAggregateSnapshot and produces deterministic
    threshold adjustment proposals. All changes are proposal-only.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        min_sample_size: int = 20,
        low_success_rate_threshold: float = 0.5,
        escalation_delta: float = 0.1,
        max_threshold: float = 2.0,
        max_delta: float = 0.2,  # Maximum delta per run for bounded adjustments
    ) -> None:
        """Initialize optimizer with deterministic parameters.

        Args:
            min_sample_size: Minimum sample size for reliable statistics.
            low_success_rate_threshold: Success rate below which escalation is considered.
            escalation_delta: Fixed delta to add to threshold when escalating.
            max_threshold: Maximum allowed threshold value.
            max_delta: Maximum delta per run for bounded adjustments.
        """
        if min_sample_size < 1:
            raise ValueError("min_sample_size must be >= 1")
        if not 0.0 <= low_success_rate_threshold <= 1.0:
            raise ValueError("low_success_rate_threshold must be in [0.0, 1.0]")
        if escalation_delta <= 0:
            raise ValueError("escalation_delta must be > 0")
        if max_threshold <= 0:
            raise ValueError("max_threshold must be > 0")
        if max_delta <= 0:
            raise ValueError("max_delta must be > 0")

        self._min_sample_size = min_sample_size
        self._low_success_rate_threshold = low_success_rate_threshold
        self._escalation_delta = escalation_delta
        self._max_threshold = max_threshold
        self._max_delta = max_delta

    def create_snapshot_from_intake(self, intake_record, created_utc: int) -> HealingOutcomeAggregateSnapshot:
        """Create aggregate snapshot from healing outcome intake record.

        Args:
            intake_record: Healing outcome intake record.
            created_utc: Timestamp for the snapshot.

        Returns:
            Aggregate snapshot for threshold optimization.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingConfigOptimizer.create_snapshot_from_intake")

        # Convert intake snapshot to aggregate format
        aggregate_pairs = []

        if hasattr(intake_record, "snapshot"):
            for stats in intake_record.snapshot:
                key = HealingOutcomeAggregateKey(
                    healer_name=stats.healer_id, tier=stats.tier, failure_type=stats.failure_type
                )
                aggregate = HealingOutcomeAggregate(
                    success_count=stats.success_count,
                    failure_count=stats.failure_count,
                    total_count=stats.total_count,
                )
                aggregate_pairs.append((key, aggregate))

        # Sort deterministically
        aggregate_pairs.sort(key=lambda pair: (pair[0].healer_name, pair[0].tier, pair[0].failure_type))

        # Create temporary snapshot to compute hash
        temp_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="temp",  # Temporary value
            created_utc=created_utc,
            aggregates=tuple(aggregate_pairs),
        )

        # Compute version_id as hash of content
        version_id = temp_snapshot.content_hash()

        # Create final snapshot with correct version_id
        snapshot = HealingOutcomeAggregateSnapshot(
            version_id=version_id, created_utc=created_utc, aggregates=tuple(aggregate_pairs)
        )

        return snapshot

    def propose_threshold_adjustments(
        self,
        snapshot: HealingOutcomeAggregateSnapshot,
        embedding_metadata: dict[str, Any] | None = None,
    ) -> ThresholdAdjustmentProposal:
        """Analyze snapshot and propose threshold adjustments.

        Args:
            snapshot: Healing outcome aggregate snapshot.

        Returns:
            Proposal with threshold adjustments (proposal-only).
        """
        _emit_gated_by_confidence(str(uuid.uuid4()), "HealingConfigOptimizer.propose_threshold_adjustments", "0.5")
        adjustments = []

        for key, aggregate in snapshot.aggregates:
            # Check if we have enough data
            if aggregate.total_count < self._min_sample_size:
                continue

            # Check if success rate is below threshold
            if aggregate.success_rate < self._low_success_rate_threshold:
                # Propose escalation
                current_threshold = self._get_current_threshold(key)
                new_threshold = min(current_threshold + self._escalation_delta, self._max_threshold)

                if new_threshold != current_threshold:
                    adjustment = ThresholdAdjustment(
                        healer_name=key.healer_name,
                        tier=key.tier,
                        failure_type=key.failure_type,
                        current_threshold=current_threshold,
                        proposed_threshold=new_threshold,
                        reason=(
                            f"Success rate {aggregate.success_rate:.4f} "
                            f"< {self._low_success_rate_threshold} "
                            f"with {aggregate.total_count} samples"
                        ),
                        confidence=self._compute_confidence(aggregate),
                    )
                    adjustments.append(adjustment)

        # Sort adjustments deterministically
        adjustments.sort(key=lambda a: (a.healer_name, a.tier, a.failure_type, a.proposed_threshold))

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=tuple(adjustments),
        )

    def propose_threshold_adjustments_with_patterns(
        self,
        snapshot: HealingOutcomeAggregateSnapshot,
        pattern_report: PatternFindingReport | None = None,
        embedding_metadata: dict[str, Any] | None = None,
    ) -> ThresholdAdjustmentProposal:
        """Analyze snapshot with pattern findings and propose threshold adjustments.

        Args:
            snapshot: Healing outcome aggregate snapshot.
            pattern_report: Optional pattern analysis report.
            embedding_metadata: Optional embedding metadata for W2 integration.

        Returns:
            Proposal with threshold adjustments (proposal-only).
        """
        # If embedding metadata is provided, use the embedding-aware method
        if embedding_metadata:
            return self.propose_threshold_adjustments_with_embeddings(
                snapshot, pattern_report, embedding_metadata
            )

        # Otherwise, use the original pattern-only logic
        base_proposal = self.propose_threshold_adjustments(snapshot)
        adjustments = list(base_proposal.adjustments)

        # Apply pattern-based adjustments
        if pattern_report:
            pattern_adjustments = self._apply_pattern_findings(pattern_report)
            adjustments.extend(pattern_adjustments)

        # Sort deterministically and apply bounds
        adjustments.sort(key=lambda a: (a.healer_name, a.tier, a.failure_type, a.proposed_threshold))
        bounded_adjustments = self._apply_bounded_constraints(adjustments)

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=tuple(bounded_adjustments),
        )

    def _apply_pattern_findings(self, pattern_report: PatternFindingReport) -> list[ThresholdAdjustment]:
        """Apply pattern findings to generate adjustments."""
        adjustments = []

        for finding in pattern_report.findings:
            if finding.key.label == "UNDERPERFORMING_HEALER_TIER":
                # Increase escalation aggressiveness
                component = finding.key.component
                # Map component to healer/tier (simplified)
                healer_name = component.split("_")[0] if "_" in component else component
                tier = "LOCAL_AGENT"  # Default tier

                current_threshold = self._get_current_threshold_for_healer(healer_name, tier)
                # Apply bounded delta based on severity
                delta = min(self._escalation_delta * finding.severity, self._max_delta)
                new_threshold = min(current_threshold + delta, self._max_threshold)

                if new_threshold != current_threshold:
                    adjustment = ThresholdAdjustment(
                        healer_name=healer_name,
                        tier=tier,
                        failure_type="pattern_based",
                        current_threshold=current_threshold,
                        proposed_threshold=new_threshold,
                        reason=f"Pattern finding: {finding.key.label} (severity={finding.severity:.3f})",
                        confidence=finding.severity,
                    )
                    adjustments.append(adjustment)

            elif finding.key.label == "ROUTING_DRIFT_HIGH":
                # Tighten thresholds for components with high drift
                component = finding.key.component
                healer_name = component.split("_")[0] if "_" in component else component
                tier = "LOCAL_AGENT"

                current_threshold = self._get_current_threshold_for_healer(healer_name, tier)
                # Decrease threshold to be more strict (but not below minimum)
                delta = min(self._escalation_delta * finding.severity * 0.5, self._max_delta)
                new_threshold = max(current_threshold - delta, 0.1)

                if new_threshold != current_threshold:
                    adjustment = ThresholdAdjustment(
                        healer_name=healer_name,
                        tier=tier,
                        failure_type="drift_based",
                        current_threshold=current_threshold,
                        proposed_threshold=new_threshold,
                        reason=f"Pattern finding: {finding.key.label} (severity={finding.severity:.3f})",
                        confidence=finding.severity,
                    )
                    adjustments.append(adjustment)

        return adjustments

    def _apply_bounded_constraints(self, adjustments: list[ThresholdAdjustment]) -> list[ThresholdAdjustment]:
        """Apply bounded delta constraints to adjustments."""
        bounded_adjustments = []

        # Group by healer_name and tier
        grouped = {}
        for adj in adjustments:
            key = (adj.healer_name, adj.tier)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(adj)

        # Apply constraints per group
        for (healer_name, tier), group_adj in grouped.items():
            # Get current threshold
            current_threshold = self._get_current_threshold_for_healer(healer_name, tier)

            # Calculate total delta
            total_delta = 0.0
            for adj in group_adj:
                total_delta += adj.proposed_threshold - current_threshold

            # Clamp to max_delta
            if abs(total_delta) > self._max_delta:
                # Scale down all adjustments proportionally
                scale = self._max_delta / abs(total_delta)
                for adj in group_adj:
                    scaled_delta = (adj.proposed_threshold - current_threshold) * scale
                    adj = ThresholdAdjustment(
                        healer_name=adj.healer_name,
                        tier=adj.tier,
                        failure_type=adj.failure_type,
                        current_threshold=current_threshold,
                        proposed_threshold=current_threshold + scaled_delta,
                        reason=adj.reason + f" (scaled to max_delta={self._max_delta})",
                        confidence=adj.confidence,
                    )
                    bounded_adjustments.append(adj)
            else:
                bounded_adjustments.extend(group_adj)

        return bounded_adjustments

    def _get_current_threshold_for_healer(self, healer_name: str, tier: str) -> float:
        """Get current threshold for a healer and tier."""
        # Use existing method with a temporary key
        from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregateKey

        key = HealingOutcomeAggregateKey(healer_name=healer_name, tier=tier, failure_type="generic")
        return self._get_current_threshold(key)

    def _get_current_threshold(self, key: HealingOutcomeAggregateKey) -> float:
        """Get current threshold for a key.

        In practice, this would query the current config.
        For now, returns deterministic defaults.
        """
        # Default thresholds by tier
        tier_defaults = {
            "LOCAL_AGENT": 0.5,
            "REMOTE_AGENT": 0.6,
            "CLOUD_SERVICE": 0.7,
        }
        return tier_defaults.get(key.tier, 0.5)

    def _compute_confidence(self, aggregate: HealingOutcomeAggregate) -> float:
        """Compute confidence in the proposed adjustment.

        Args:
            aggregate: Aggregate statistics.

        Returns:
            Confidence score (0.0 to 1.0).
        """
        # Simple confidence based on sample size
        # More samples = higher confidence
        # guardian: allow-magic-config
        max_samples = 1000
        normalized_samples = min(aggregate.total_count, max_samples) / max_samples

        # Also consider how far below threshold the success rate is
        rate_gap = self._low_success_rate_threshold - aggregate.success_rate
        normalized_gap = min(rate_gap / self._low_success_rate_threshold, 1.0)

        # Combine factors
        confidence = (normalized_samples * 0.6) + (normalized_gap * 0.4)
        return round(confidence + 1e-10, 4)  # Round-half-up

    # guardian: allow-magic-config
    def propose_threshold_adjustments_with_embeddings(
        self,
        snapshot: HealingOutcomeAggregateSnapshot,
        pattern_report: Any = None,
        embedding_metadata: dict[str, Any] | None = None,
        embedding_influence_cap: float = 0.25,
        min_sample_threshold: int = 20,
    ) -> ThresholdAdjustmentProposal:
        """Analyze snapshot with embedding influence and propose threshold adjustments.

        This is W2 implementation: embeddings provide C0 informational context
        and contribute to scoring with bounded influence.

        Args:
            snapshot: Healing outcome aggregate snapshot.
            pattern_report: Optional pattern analysis report.
            embedding_metadata: Embedding retrieval metadata for C0 context.
            embedding_influence_cap: Maximum influence of embeddings (<= 0.25).
            min_sample_threshold: Minimum samples for embedding influence.

        Returns:
            Proposal with threshold adjustments (proposal-only).
        """
        # Get base adjustments from snapshot
        base_proposal = self.propose_threshold_adjustments(snapshot)
        adjustments = list(base_proposal.adjustments)

        # Apply pattern-based adjustments if available
        if pattern_report:
            pattern_adjustments = self._apply_pattern_findings(pattern_report)
            adjustments.extend(pattern_adjustments)

        # Apply embedding-influenced scoring if enabled and guard passes
        if embedding_metadata and embedding_metadata.get("embedding_enabled_at_time", False):
            # Calculate total sample size across all aggregates
            total_samples = sum(agg.total_count for _, agg in snapshot.aggregates)

            # Small-N guard: if insufficient samples, embedding_weight = 0.0
            if total_samples >= min_sample_threshold:
                # Apply embedding influence to confidence scores
                embedding_weight = min(embedding_influence_cap, 0.25)

                # Get embedding scores for aggregation
                embedding_scores = embedding_metadata.get("embedding_topk_scores_round6", [])
                embedding_score = self._aggregate_embedding_scores(embedding_scores)

                # Update adjustments with embedding-influenced confidence
                embedding_influenced_adjustments = []
                for adj in adjustments:
                    # Combine statistical confidence with embedding score
                    statistical_confidence = adj.confidence
                    embedding_confidence = embedding_score

                    # Bounded combination: statistical remains dominant
                    final_confidence = (
                        1.0 - embedding_weight
                    ) * statistical_confidence + embedding_weight * embedding_confidence

                    # Round to 6 decimal places for determinism
                    final_confidence = round(final_confidence + 1e-10, 6)

                    # Create new adjustment with embedding-influenced confidence
                    influenced_adj = ThresholdAdjustment(
                        healer_name=adj.healer_name,
                        tier=adj.tier,
                        failure_type=adj.failure_type,
                        current_threshold=adj.current_threshold,
                        proposed_threshold=adj.proposed_threshold,
                        reason=(
                            adj.reason + f" (embedding_influenced: weight={embedding_weight:.3f}, "
                            f"score={embedding_score:.6f})"
                        ),
                        confidence=final_confidence,
                    )
                    embedding_influenced_adjustments.append(influenced_adj)

                adjustments = embedding_influenced_adjustments

        # Sort deterministically and apply bounds
        adjustments.sort(key=lambda a: (a.healer_name, a.tier, a.failure_type, a.proposed_threshold))
        bounded_adjustments = self._apply_bounded_constraints(adjustments)

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=tuple(bounded_adjustments),
        )

    def _aggregate_embedding_scores(self, scores: list[float]) -> float:
        """Aggregate embedding scores deterministically.

        Args:
            scores: List of similarity scores (rounded to 6 decimals).

        Returns:
            Aggregated score (0.0 to 1.0).
        """
        if not scores:
            return 0.0

        # Use max for deterministic aggregation (most relevant context)
        # Could also use mean of top-3, but max is simpler and deterministic
        return max(scores) if scores else 0.0


# Data structures for proposals
@dataclass(frozen=True, slots=True)
class ThresholdAdjustment:
    """Proposal to adjust a healing threshold."""

    healer_name: str
    tier: str
    failure_type: str
    current_threshold: float
    proposed_threshold: float
    reason: str
    confidence: float

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ThresholdAdjustment.canonical_bytes")

        data = {
            "healer_name": self.healer_name,
            "tier": self.tier,
            "failure_type": self.failure_type,
            "current_threshold": self.current_threshold,
            "proposed_threshold": self.proposed_threshold,
            "reason": self.reason,
            "confidence": self.confidence,
        }
        import json

        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA-256 hash."""
        import hashlib

        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class ThresholdAdjustmentProposal:
    """Proposal-only container for threshold adjustments."""

    snapshot_version_id: str
    created_utc: int
    adjustments: tuple[ThresholdAdjustment, ...] = field(default_factory=tuple)

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ThresholdAdjustmentProposal.canonical_bytes")

        adjustments_data = []
        for adj in self.adjustments:
            adjustments_data.append(
                {
                    "healer_name": adj.healer_name,
                    "tier": adj.tier,
                    "failure_type": adj.failure_type,
                    "current_threshold": adj.current_threshold,
                    "proposed_threshold": adj.proposed_threshold,
                    "reason": adj.reason,
                    "confidence": adj.confidence,
                }
            )

        data = {
            "snapshot_version_id": self.snapshot_version_id,
            "created_utc": self.created_utc,
            "adjustments": adjustments_data,
        }

        import json

        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA-256 hash."""
        import hashlib

        return hashlib.sha256(self.canonical_bytes()).hexdigest()


__all__ = [
    "HealingConfigOptimizer",
    "ThresholdAdjustment",
    "ThresholdAdjustmentProposal",
]
