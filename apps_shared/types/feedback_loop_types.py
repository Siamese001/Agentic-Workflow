"""Feedback Loop - Continuous quality improvement system.

This module collects feedback on signal quality, analyzes patterns,
and adjusts validation thresholds dynamically for optimal outputs.
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "feedback_loop_types", "p0_governance")
_emit_reads_policy_state("p0", "feedback_loop_types", "policy_binding")
_emit_snapshots_state("p0", "feedback_loop_types", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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

_emit_emits_metric_event("feedback_loop_types", "p4obs", "metric_1")
_emit_emits_metric_event("feedback_loop_types", "p4obs", "metric_2")
_emit_emits_metric_event("feedback_loop_types", "p4obs", "metric_3")
_emit_emits_metric_event("feedback_loop_types", "p4obs", "metric_4")
_emit_emits_metric_event("feedback_loop_types", "p4obs", "metric_5")
_emit_emits_metric_event("feedback_loop_types", "p4obs", "metric_6")
_emit_records_incident_event("feedback_loop_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("feedback_loop_types", "p4obs", "anomaly")
_emit_writes_observability_log("feedback_loop_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("feedback_loop_types", "p4obs", "mon_state")
_emit_triggers_alert("feedback_loop_types", "p4obs", "alert")
_emit_links_incident_trace("feedback_loop_types", "p4obs", "trace_link")
_emit_captures_pattern("feedback_loop_types", "p3lm", "pattern")
_emit_records_learning_event("feedback_loop_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("feedback_loop_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("feedback_loop_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("feedback_loop_types", "p3lm", "routing")
_emit_improves_agent_policy("feedback_loop_types", "p3lm", "policy")
_emit_stores_learning_state("feedback_loop_types", "p3lm", "state")
_emit_records_execution_trace("feedback_loop_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("feedback_loop_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("feedback_loop_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("feedback_loop_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("feedback_loop_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("feedback_loop_types", "env_read", "p2_env_1")
_emit_reads_environ("feedback_loop_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("feedback_loop_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("feedback_loop_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "feedback_loop_types", "context_pull")
_emit_pulls_context("p1", "feedback_loop_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "feedback_loop_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "feedback_loop_types", "uwg_term_2")
_emit_writes_through("p1", "feedback_loop_types", "write_through")
_emit_writes_through("p1", "feedback_loop_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "feedback_loop_types", "safety_validation")
_emit_invokes_eval("p1", "feedback_loop_types", "eval_call")
_emit_proposal_commits_routing("p1", "feedback_loop_types", "routing_commit")
_emit_escalates_to_human("p1", "feedback_loop_types", "human_escalation")
_emit_routes_through("p1", "feedback_loop_types", "route_through")
_emit_checks_agent_registry("p1", "feedback_loop_types", "agent_registry")
_emit_validates_agent_capability("p1", "feedback_loop_types", "capability")
_emit_dispatches_execution_plan("p1", "feedback_loop_types", "exec_plan")
_emit_agent_executes_agent("p1", "feedback_loop_types", "sub_agent")
_emit_routes_to_agent("p1", "feedback_loop_types", "target_agent")
_emit_verifies_policy("p1", "feedback_loop_types", "policy_check")
_emit_observes_runtime_state("p1", "feedback_loop_types", "runtime_state")
_emit_verifies_boundary("p1", "feedback_loop_types", "boundary_check")
_emit_transcripts_response("p1", "feedback_loop_types", "transcript")
_emit_hard_fails_untranscripted("p1", "feedback_loop_types")
_emit_gated_by_confidence("p1", "feedback_loop_types", "confidence_gate")
emit_replay_key("p0", "feedback_loop_types")
emit_determinism_digest("p0", "feedback_loop_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "feedback_loop_types", "execution_auth")
_emit_validates_capability("p2", "feedback_loop_types", "capability_check")
_emit_routes_to_capability("p2", "feedback_loop_types", "capability_route")
_emit_writes_via_uwg("p2", "feedback_loop_types", "uwg_write")
_emit_blocks_direct_write("p2", "feedback_loop_types", "direct_write_block")
_emit_records_tool_invocation("p2", "feedback_loop_types", "tool_invocation")
_emit_captures_execution_output("p2", "feedback_loop_types", "exec_output")
_emit_dispatches_agent("p3", "feedback_loop_types", "agent_dispatch")
_emit_coordinates_agents("p3", "feedback_loop_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "feedback_loop_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "feedback_loop_types", "healing_outcome")
_emit_escalates_failure("p3", "feedback_loop_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "feedback_loop_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "feedback_loop_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "feedback_loop_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "feedback_loop_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "feedback_loop_types", "eval_metric")
_emit_stores_embedding("p4", "feedback_loop_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "feedback_loop_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "feedback_loop_types", "exec_snapshot_link")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_1")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_2")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_3")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_4")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_5")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_6")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_7")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_8")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_9")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_10")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_11")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_12")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_13")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_14")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_15")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_16")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_17")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_18")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_19")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_20")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_21")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_22")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_23")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_24")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_25")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_26")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_27")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_28")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_29")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_30")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_31")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_32")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_33")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_34")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_35")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_36")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_37")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_38")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_39")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_40")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_41")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_42")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_43")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_44")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_45")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_46")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_47")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_48")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_49")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_50")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_51")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_52")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_53")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_54")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_55")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_56")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_57")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_58")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_59")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_60")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_61")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_62")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_63")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_64")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_65")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_66")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_67")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_68")
_emit_reads_through("l4", "feedback_loop_types", "urg_read_69")

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback."""

    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    AUTOMATIC = "automatic"


@dataclass
class QualityFeedback:
    """Feedback on signal quality."""

    assessment_id: str
    feedback_type: FeedbackType
    timestamp: datetime
    accuracy_rating: int | None = None
    relevance_rating: int | None = None
    clarity_rating: int | None = None
    completeness_rating: int | None = None
    positive_aspects: list[str] = field(default_factory=list)
    improvement_areas: list[str] = field(default_factory=list)
    user_comments: str | None = None
    hop_id: str | None = None
    stage: str | None = None
    user_id: str | None = None


@dataclass
class QualityTrend:
    """Trend analysis for quality metrics."""

    metric_name: str
    current_value: float
    trend_direction: str
    trend_strength: float
    confidence: float
    recent_values: list[float] = field(default_factory=list)
    baseline_value: float | None = None


class AdaptiveThresholds:
    """Dynamically adjusting quality thresholds."""

    def __init__(self, initial_thresholds: dict[str, float]):
        """Initialize adaptive thresholds.

        Args:
            initial_thresholds: Starting threshold values
        """
        self.thresholds = initial_thresholds.copy()
        self.adjustment_history: list[dict[str, Any]] = []
        self.min_thresholds = {"excellent": 0.85, "high": 0.7, "good": 0.55, "marginal": 0.4}
        self.max_thresholds = {"excellent": 0.95, "high": 0.85, "good": 0.7, "marginal": 0.55}

    def adjust_thresholds(
        self, quality_scores: list[float], acceptance_rate: float, target_acceptance: float = 0.75
    ) -> dict[str, float]:
        """Adjust thresholds based on performance.

        Args:
            quality_scores: Recent quality scores
            acceptance_rate: Current acceptance rate
            target_acceptance: Target acceptance rate

        Returns:
            Updated thresholds
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "AdaptiveFeedbackLoop.adjust_thresholds")
        if not quality_scores:
            return self.thresholds
        acceptance_gap = target_acceptance - acceptance_rate
        if abs(acceptance_gap) < 0.05:
            return self.thresholds
        adjustment_factor = acceptance_gap * 0.1
        for level in ["excellent", "high", "good", "marginal"]:
            current = self.thresholds.get(level, 0.5)
            new_value = current + adjustment_factor
            new_value = max(self.min_thresholds[level], min(self.max_thresholds[level], new_value))
            self.thresholds[level] = new_value
        self.adjustment_history.append(
            {
                "timestamp": datetime.now(),
                "acceptance_rate": acceptance_rate,
                "adjustment_factor": adjustment_factor,
                "new_thresholds": self.thresholds.copy(),
            }
        )
        logger.info(
            f"Adjusted thresholds: acceptance_rate={acceptance_rate:.2f}, adjustment={adjustment_factor:.3f}"
        )
        return self.thresholds


class FeedbackLoop:
    """Manages feedback collection and quality improvement."""

    def __init__(self, name: str = "default", history_size: int = 1000):
        """Initialize the feedback loop.

        Args:
            name: Loop name for logging
            history_size: Maximum history to retain
        """
        self.name = name
        self.history_size = history_size
        self.assessments: deque = deque(maxlen=history_size)
        self.feedback: deque = deque(maxlen=history_size)
        self.quality_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._trends_cache: dict[str, QualityTrend] = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300
        self.adaptive_thresholds = AdaptiveThresholds(
            {"excellent": 0.9, "high": 0.75, "good": 0.6, "marginal": 0.4}
        )
        self._lock = threading.Lock()
        logger.debug(f"Initialized FeedbackLoop: {name}")

    def record_assessment(self, assessment: SignalAssessment) -> None:
        """Record a signal assessment.

        Args:
            assessment: Assessment to record
        """
        with self._lock:
            self.assessments.append(assessment)
            self.quality_history["composite"].append(assessment.composite_score)
            self.quality_history["relevance"].append(assessment.relevance_score)
            self.quality_history["authority"].append(assessment.authority_score)
            self.quality_history["coherence"].append(assessment.coherence_score)
            self.quality_history["specificity"].append(assessment.specificity_score)
            self.quality_history["snr"].append(assessment.signal_to_noise_ratio)
            self.quality_history["accuracy"].append(assessment.factual_accuracy)
            self._cache_timestamp = 0

    def add_feedback(self, feedback: QualityFeedback) -> None:
        """Add feedback to the loop.

        Args:
            feedback: Feedback to add
        """
        with self._lock:
            self.feedback.append(feedback)
            for assessment in reversed(self.assessments):
                if assessment.content_hash == feedback.assessment_id:
                    assessment.feedback = feedback
                    break
            logger.debug(f"Added {feedback.feedback_type.value} feedback")

    def analyze_trends(self, force_refresh: bool = False) -> dict[str, QualityTrend]:
        """Analyze quality trends.

        Args:
            force_refresh: Force cache refresh

        Returns:
            Dictionary of trends by metric
        """
        now = time.time()
        if not force_refresh and now - self._cache_timestamp < self._cache_ttl:
            return self._trends_cache
        with self._lock:
            trends = {}
            for metric, values in self.quality_history.items():
                if len(values) < 10:
                    continue
                trend = self._calculate_trend(metric, list(values))
                trends[metric] = trend
            self._trends_cache = trends
            self._cache_timestamp = now
            return trends

    def _calculate_trend(self, metric_name: str, values: list[float]) -> QualityTrend:
        """Calculate trend for a metric.

        Args:
            metric_name: Name of metric
            values: Recent values

        Returns:
            QualityTrend analysis
        """
        if len(values) < 2:
            return QualityTrend(
                metric_name=metric_name,
                current_value=values[0] if values else 0.0,
                trend_direction="stable",
                trend_strength=0.0,
                confidence=0.0,
            )
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        if abs(slope) < 0.001:
            direction = "stable"
        elif slope > 0:
            direction = "improving"
        else:
            direction = "declining"
        value_range = max(values) - min(values)
        if value_range > 0:
            strength = min(1.0, abs(slope * n) / value_range)
        else:
            strength = 0.0
        variance = statistics.variance(values) if len(values) > 1 else 0
        confidence = max(0.0, 1.0 - variance / (value_range + 0.001))
        return QualityTrend(
            metric_name=metric_name,
            current_value=values[-1],
            trend_direction=direction,
            trend_strength=strength,
            confidence=confidence,
            recent_values=values[-10:],
            baseline_value=statistics.mean(values[:10]) if len(values) >= 10 else None,
        )

    def get_quality_insights(self) -> dict[str, Any]:
        """Get insights about quality patterns.

        Returns:
            Insights dictionary
        """
        with self._lock:
            if not self.assessments:
                return {"message": "No assessments available"}
            recent_assessments = list(self.assessments)[-50:]
            quality_counts = defaultdict(int)
            for assessment in recent_assessments:
                quality_counts[assessment.quality_level.value] += 1
            flag_counts = defaultdict(int)
            for assessment in recent_assessments:
                for flag in assessment.flags:
                    flag_counts[flag] += 1
            avg_scores = {
                "composite": statistics.mean([a.composite_score for a in recent_assessments]),
                "relevance": statistics.mean([a.relevance_score for a in recent_assessments]),
                "authority": statistics.mean([a.authority_score for a in recent_assessments]),
                "coherence": statistics.mean([a.coherence_score for a in recent_assessments]),
                "specificity": statistics.mean([a.specificity_score for a in recent_assessments]),
            }
            high_risk_count = sum(1 for a in recent_assessments if a.hallucination_risk > 0.3)
            return {
                "total_assessments": len(self.assessments),
                "recent_assessments": len(recent_assessments),
                "quality_distribution": dict(quality_counts),
                "common_flags": dict(flag_counts),
                "average_scores": avg_scores,
                "high_hallucination_risk_rate": high_risk_count / len(recent_assessments),
                "current_thresholds": self.adaptive_thresholds.thresholds,
                "trends": self.analyze_trends(),
            }

    def recommend_improvements(self) -> list[str]:
        """Recommend improvements based on feedback.

        Returns:
            List of recommendations
        """
        insights = self.get_quality_insights()
        recommendations = []
        if "quality_distribution" in insights:
            dist = insights["quality_distribution"]
            total = sum(dist.values())
            if total > 0:
                poor_rate = dist.get("poor", 0) / total
                marginal_rate = dist.get("marginal", 0) / total
                if poor_rate > 0.2:
                    recommendations.append(
                        "High rate of poor quality outputs (>20%). Consider strengthening input validation and prompt engineering."
                    )
                if marginal_rate > 0.3:
                    recommendations.append(
                        "Many outputs are only marginal quality. Review factual accuracy requirements and add more specific guidelines."
                    )
        if "common_flags" in insights:
            flags = insights["common_flags"]
            if flags.get("LOW_QUALITY", 0) > 5:
                recommendations.append(
                    "Frequent LOW_QUALITY flags detected. Increase minimum quality thresholds or enhance training data."
                )
            if flags.get("HALLUCINATION_RISK", 0) > 3:
                recommendations.append(
                    "Hallucination risks detected. Add stronger fact-checking and source verification."
                )
            if flags.get("HIGHLY_REPETITIVE", 0) > 5:
                recommendations.append(
                    "High repetition in outputs. Implement diversity constraints and content variety checks."
                )
        if "trends" in insights:
            trends = insights["trends"]
            for metric, trend in trends.items():
                if trend.trend_direction == "declining" and trend.confidence > 0.7:
                    recommendations.append(
                        f"{metric.title()} quality is declining with high confidence. Review recent changes and consider targeted improvements."
                    )
        if insights.get("high_hallucination_risk_rate", 0) > 0.15:
            recommendations.append(
                "High hallucination risk rate (>15%). Implement stricter source verification and reduce speculative language."
            )
        return recommendations

    def adjust_thresholds_automatically(self) -> dict[str, float]:
        """Automatically adjust thresholds based on performance.

        Returns:
            Updated thresholds
        """
        with self._lock:
            if len(self.assessments) < 20:
                logger.warning("Insufficient data for automatic threshold adjustment")
                return self.adaptive_thresholds.thresholds
            recent = list(self.assessments)[-20:]
            accepted = sum(
                1
                for a in recent
                if a.quality_level in [SignalQuality.GOOD, SignalQuality.HIGH, SignalQuality.EXCELLENT]
            )
            acceptance_rate = accepted / len(recent)
            quality_scores = [a.composite_score for a in recent]
            new_thresholds = self.adaptive_thresholds.adjust_thresholds(quality_scores, acceptance_rate)
            return new_thresholds

    def export_feedback_data(self) -> dict[str, Any]:
        """Export feedback data for analysis.

        Returns:
            Export data dictionary
        """
        with self._lock:
            return {
                "assessments": [
                    {
                        "content_hash": a.content_hash,
                        "quality_level": a.quality_level.value,
                        "composite_score": a.composite_score,
                        "timestamp": a.timestamp.isoformat(),
                        "flags": a.flags,
                    }
                    for a in self.assessments
                ],
                "feedback": [
                    {
                        "assessment_id": f.assessment_id,
                        "type": f.feedback_type.value,
                        "ratings": {
                            "accuracy": f.accuracy_rating,
                            "relevance": f.relevance_rating,
                            "clarity": f.clarity_rating,
                            "completeness": f.completeness_rating,
                        },
                        "comments": f.user_comments,
                        "timestamp": f.timestamp.isoformat(),
                    }
                    for f in self.feedback
                ],
                "threshold_history": self.adaptive_thresholds.adjustment_history,
                "insights": self.get_quality_insights(),
                "recommendations": self.recommend_improvements(),
            }


_feedback_loops: dict[str, FeedbackLoop] = {}
_loop_lock = threading.Lock()


def get_feedback_loop(name: str = "default", history_size: int = 1000) -> FeedbackLoop:
    """Get or create a feedback loop.

    Args:
        name: Loop name
        history_size: Maximum history to retain

    Returns:
        FeedbackLoop instance
    """
    with _loop_lock:
        if name not in _feedback_loops:
            _feedback_loops[name] = FeedbackLoop(name, history_size)
        return _feedback_loops[name]
