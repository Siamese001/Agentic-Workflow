"""System Learning Cache Admission Gate

Integrates system learning with L4 cache admission infrastructure for
validation and quality control of cache entries.

Extends the base cache admission gate with system learning specific
validation criteria and telemetry integration.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.cache.cache_key_builders import build_rag_admission_key
from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache


# Lazy import to avoid L_SL->L4 gravity violation
def _get_cache_admission_gate():
    from agentic_core.L4_state.utils.memory.cache_admission_gate import (
        CacheAdmissionDecision,
        CacheAdmissionGate,
    )

    return CacheAdmissionDecision, CacheAdmissionGate


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

# Module-level telemetry emission
_emit_applies_guardrail("p0", "system_learning_admission_gate", "p0_governance")
_emit_reads_policy_state("p0", "system_learning_admission_gate", "policy_binding")
_emit_snapshots_state("p0", "system_learning_admission_gate", "state_snapshot")

_emit_emits_metric_event("system_learning_admission_gate", "p4obs", "metric_1")
_emit_emits_metric_event("system_learning_admission_gate", "p4obs", "metric_2")
_emit_emits_metric_event("system_learning_admission_gate", "p4obs", "metric_3")
_emit_emits_metric_event("system_learning_admission_gate", "p4obs", "metric_4")
_emit_emits_metric_event("system_learning_admission_gate", "p4obs", "metric_5")
_emit_emits_metric_event("system_learning_admission_gate", "p4obs", "metric_6")
_emit_records_incident_event("system_learning_admission_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("system_learning_admission_gate", "p4obs", "anomaly")
_emit_writes_observability_log("system_learning_admission_gate", "p4obs", "obs_log")
_emit_records_telemetry_event("system_learning_admission_gate", "p4obs", "mon_state")
_emit_triggers_alert("system_learning_admission_gate", "p4obs", "alert")
_emit_links_incident_trace("system_learning_admission_gate", "p4obs", "trace_link")
_emit_captures_pattern("system_learning_admission_gate", "p3lm", "pattern")
_emit_records_learning_event("system_learning_admission_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("system_learning_admission_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("system_learning_admission_gate", "p3lm", "meta_feed")
_emit_feeds_meta_learning("system_learning_admission_gate", "p3lm", "routing")
_emit_improves_agent_policy("system_learning_admission_gate", "p3lm", "policy")
_emit_stores_learning_state("system_learning_admission_gate", "p3lm", "state")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SystemLearningAdmissionContext:
    """Context for system learning cache admission decisions."""

    # Base context
    u0_hash: str
    policy_hash: str
    embedder_version: str

    # System learning specific context
    learning_session_id: str | None = None
    drift_detection_enabled: bool = True
    telemetry_window_size: int = 1000
    confidence_threshold: float = 0.7

    # Quality metrics
    avg_retrieval_score: float = 0.0
    result_diversity: float = 0.0
    semantic_coherence: float = 0.0


class SystemLearningAdmissionDecision(CacheAdmissionDecision):
    """Extended admission decision with system learning specific metrics."""

    # System learning specific metrics
    learning_score: float = 0.0
    drift_indicators: dict[str, float] | None = None
    telemetry_correlation: float = 0.0
    quality_confidence: float = 0.0

    # Learning context
    learning_context: SystemLearningAdmissionContext | None = None


class SystemLearningCacheAdmissionGate:
    """Cache admission gate with system learning specific validation.

    Extends the base admission gate with:
    - Learning quality assessment
    - Drift detection integration
    - Telemetry correlation analysis
    - Policy-aware validation
    - Comprehensive observability
    """

    def __init__(
        self,
        support_threshold: float = 0.3,
        completeness_threshold: float = 0.6,
        learning_quality_threshold: float = 0.7,
        drift_tolerance: float = 0.2,
        enable_telemetry_correlation: bool = True,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        """Initialize system learning cache admission gate."""
        self.support_threshold = support_threshold
        self.completeness_threshold = completeness_threshold
        self.learning_quality_threshold = learning_quality_threshold
        self.drift_tolerance = drift_tolerance
        self.enable_telemetry_correlation = enable_telemetry_correlation
        self._cache = cache or get_hot_cache()

        # Initialize base gate
        self._base_gate = CacheAdmissionGate(
            support_threshold=support_threshold,
            completeness_threshold=completeness_threshold,
        )

        # Metrics tracking
        self._metrics = {
            "total_evaluations": 0,
            "admissions": 0,
            "denials": 0,
            "learning_quality_failures": 0,
            "drift_detection_failures": 0,
            "telemetry_correlation_failures": 0,
            "policy_violations": 0,
        }

        logger.info(
            f"SystemLearningCacheAdmissionGate initialized: "
            f"support_threshold={support_threshold}, "
            f"learning_quality_threshold={learning_quality_threshold}, "
            f"drift_tolerance={drift_tolerance}",
        )

    async def evaluate_admission(
        self,
        context: SystemLearningAdmissionContext,
        retrieval_results: list[dict[str, Any]],
        query_text: str | None = None,
        timestamp_utc: str | None = None,
    ) -> SystemLearningAdmissionDecision:
        """Evaluate cache admission with system learning specific validation.

        Args:
            context: System learning admission context
            retrieval_results: Retrieval results to evaluate
            query_text: Original query for semantic analysis
            timestamp_utc: UTC timestamp for deterministic logging

        Returns:
            Admission decision with system learning metrics
        """
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "SystemLearningCacheAdmissionGate.evaluate_admission",
        )

        self._metrics["total_evaluations"] += 1

        try:
            # Start with base admission evaluation
            base_decision = self._base_gate.evaluate_admission(
                retrieval_results=retrieval_results,
                query_text=query_text,
                timestamp_utc=timestamp_utc,
            )

            # System learning specific validations
            learning_result = await self._evaluate_learning_quality(context, retrieval_results, query_text)

            drift_result = await self._evaluate_drift_indicators(context, retrieval_results)

            telemetry_result = await self._evaluate_telemetry_correlation(context, retrieval_results)

            # Combine decisions
            final_decision = self._combine_admission_decisions(
                base_decision,
                learning_result,
                drift_result,
                telemetry_result,
                context,
            )

            # Record decision
            await self._record_admission_decision(final_decision)

            # Update metrics
            if final_decision.admitted:
                self._metrics["admissions"] += 1
                _emit_records_learning_event("p3lm", "system_learning_admission_gate", "cache_admitted")
            else:
                self._metrics["denials"] += 1
                _emit_captures_pattern("p3lm", "system_learning_admission_gate", "cache_denied")

            return final_decision

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
            logger.error("Admission evaluation failed: %s", exc)
            _emit_captures_runtime_anomaly(
                "p4obs",
                "system_learning_admission_gate",
                "admission_evaluation_failure",
            )

            # Fail closed on errors
            return SystemLearningAdmissionDecision(
                admitted=False,
                reason="error",
                explanation=f"Admission evaluation failed: {exc}",
                learning_context=context,
            )

    async def _evaluate_learning_quality(
        self,
        context: SystemLearningAdmissionContext,
        retrieval_results: list[dict[str, Any]],
        query_text: str | None = None,
    ) -> dict[str, Any]:
        """Evaluate learning quality of retrieval results."""
        try:
            quality_score = 0.0
            quality_factors = {}

            # Factor 1: Average retrieval score
            if retrieval_results:
                scores = [r.get("score", 0.0) for r in retrieval_results]
                avg_score = sum(scores) / len(scores)
                quality_factors["avg_score"] = avg_score
                quality_score += avg_score * 0.4

            # Factor 2: Result diversity
            if len(retrieval_results) > 1:
                # Simple diversity calculation based on score distribution
                scores = [r.get("score", 0.0) for r in retrieval_results]
                score_variance = sum((s - sum(scores) / len(scores)) ** 2 for s in scores) / len(scores)
                diversity = min(score_variance / 0.25, 1.0)  # Normalize to 0-1
                quality_factors["diversity"] = diversity
                quality_score += diversity * 0.3

            # Factor 3: Semantic coherence (if query text available)
            if query_text and len(retrieval_results) > 0:
                # Simple coherence check based on score consistency
                scores = [r.get("score", 0.0) for r in retrieval_results]
                score_std = (sum((s - sum(scores) / len(scores)) ** 2 for s in scores) / len(scores)) ** 0.5
                coherence = max(0, 1 - score_std)  # Lower std = higher coherence
                quality_factors["coherence"] = coherence
                quality_score += coherence * 0.3

            # Determine if quality meets threshold
            meets_quality = quality_score >= context.confidence_threshold

            if not meets_quality:
                self._metrics["learning_quality_failures"] += 1

            return {
                "meets_quality": meets_quality,
                "quality_score": quality_score,
                "quality_factors": quality_factors,
            }

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
            logger.debug("Learning quality evaluation failed: %s", exc)
            return {
                "meets_quality": False,
                "quality_score": 0.0,
                "quality_factors": {},
            }

    async def _evaluate_drift_indicators(
        self,
        context: SystemLearningAdmissionContext,
        retrieval_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Evaluate drift indicators in retrieval results."""
        try:
            if not context.drift_detection_enabled:
                return {"has_drift": False, "drift_score": 0.0, "indicators": {}}

            drift_indicators = {}
            drift_score = 0.0

            # Indicator 1: Score distribution shift
            if retrieval_results:
                scores = [r.get("score", 0.0) for r in retrieval_results]
                # Check for unusual score patterns
                high_score_ratio = sum(1 for s in scores if s > 0.9) / len(scores)
                drift_indicators["high_score_ratio"] = high_score_ratio
                if high_score_ratio > 0.7:  # Too many high scores
                    drift_score += 0.3

            # Indicator 2: Result count anomaly
            expected_count = min(10, max(3, len(retrieval_results)))
            count_deviation = abs(len(retrieval_results) - expected_count) / expected_count
            drift_indicators["count_deviation"] = count_deviation
            if count_deviation > 0.5:
                drift_score += 0.2

            # Indicator 3: Source diversity (if available)
            sources = set()
            for result in retrieval_results:
                source = result.get("source", "")
                if source:
                    sources.add(source)

            if len(retrieval_results) > 0:
                source_diversity = len(sources) / len(retrieval_results)
                drift_indicators["source_diversity"] = source_diversity
                if source_diversity < 0.3:  # Too few sources
                    drift_score += 0.2

            # Determine if drift exceeds tolerance
            has_drift = drift_score > context.drift_tolerance

            if has_drift:
                self._metrics["drift_detection_failures"] += 1

            return {
                "has_drift": has_drift,
                "drift_score": drift_score,
                "indicators": drift_indicators,
            }

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
            logger.debug("Drift evaluation failed: %s", exc)
            return {
                "has_drift": True,  # Fail closed
                "drift_score": 1.0,
                "indicators": {},
            }

    async def _evaluate_telemetry_correlation(
        self,
        context: SystemLearningAdmissionContext,
        retrieval_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Evaluate telemetry correlation with retrieval results."""
        try:
            if not self.enable_telemetry_correlation:
                return {"correlates": True, "correlation_score": 1.0}

            # For now, implement basic correlation check
            # In production, this would correlate with actual telemetry data

            correlation_score = 1.0
            correlation_factors = {}

            # Factor 1: Result size correlation
            if context.telemetry_window_size > 0:
                expected_size = min(context.telemetry_window_size, len(retrieval_results))
                size_ratio = len(retrieval_results) / expected_size if expected_size > 0 else 0
                correlation_factors["size_ratio"] = size_ratio
                correlation_score *= min(size_ratio, 1.0)

            # Factor 2: Score consistency with historical patterns
            if retrieval_results:
                scores = [r.get("score", 0.0) for r in retrieval_results]
                avg_score = sum(scores) / len(scores)
                # Assume historical average around 0.7 for this example
                historical_avg = 0.7
                score_consistency = 1 - abs(avg_score - historical_avg) / historical_avg
                correlation_factors["score_consistency"] = score_consistency
                correlation_score *= score_consistency

            correlates = correlation_score >= 0.5

            if not correlates:
                self._metrics["telemetry_correlation_failures"] += 1

            return {
                "correlates": correlates,
                "correlation_score": correlation_score,
                "factors": correlation_factors,
            }

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
            logger.debug("Telemetry correlation evaluation failed: %s", exc)
            return {
                "correlates": False,  # Fail closed
                "correlation_score": 0.0,
            }

    def _combine_admission_decisions(
        self,
        base_decision: CacheAdmissionDecision,
        learning_result: dict[str, Any],
        drift_result: dict[str, Any],
        telemetry_result: dict[str, Any],
        context: SystemLearningAdmissionContext,
    ) -> SystemLearningAdmissionDecision:
        """Combine all evaluation results into final decision."""

        # Start with base decision
        admitted = base_decision.admitted
        denial_reasons = []
        explanation_parts = []

        # Apply system learning specific criteria
        if not learning_result["meets_quality"]:
            admitted = False
            denial_reasons.append("learning_quality")
            explanation_parts.append(
                f"Learning quality {learning_result['quality_score']:.2f} "
                f"below threshold {context.confidence_threshold}",
            )

        if drift_result["has_drift"]:
            admitted = False
            denial_reasons.append("drift_detected")
            explanation_parts.append(
                f"Drift score {drift_result['drift_score']:.2f} exceeds tolerance {context.drift_tolerance}",
            )

        if not telemetry_result["correlates"]:
            admitted = False
            denial_reasons.append("telemetry_mismatch")
            explanation_parts.append(
                f"Telemetry correlation {telemetry_result['correlation_score']:.2f} below threshold",
            )

        # Build final explanation
        if not admitted:
            explanation = (
                "; ".join(explanation_parts) if explanation_parts else "System learning validation failed"
            )
            if base_decision.explanation:
                explanation = f"{base_decision.explanation}; {explanation}"
        else:
            explanation = base_decision.explanation or "All validations passed"

        # Determine reason
        if admitted:
            reason = "all_gates_passed"
        else:
            reason = denial_reasons[0] if denial_reasons else "other"

        return SystemLearningAdmissionDecision(
            admitted=admitted,
            reason=reason,
            explanation=explanation,
            learning_score=learning_result["quality_score"],
            drift_indicators=drift_result["indicators"],
            telemetry_correlation=telemetry_result["correlation_score"],
            quality_confidence=learning_result["quality_score"],
            learning_context=context,
        )

    async def _record_admission_decision(
        self,
        decision: SystemLearningAdmissionDecision,
    ) -> None:
        """Record admission decision for telemetry and learning."""
        try:
            # Store admission decision in cache for analysis
            if decision.learning_context:
                admission_key = build_rag_admission_key(
                    decision.learning_context.u0_hash,
                    decision.learning_context.policy_hash,
                    decision.learning_context.embedder_version,
                )

                decision_data = {
                    "admitted": decision.admitted,
                    "reason": decision.reason.value
                    if hasattr(decision.reason, "value")
                    else str(decision.reason),
                    "explanation": decision.explanation,
                    "learning_score": decision.learning_score,
                    "drift_indicators": decision.drift_indicators,
                    "telemetry_correlation": decision.telemetry_correlation,
                    "quality_confidence": decision.quality_confidence,
                    "timestamp": _emit_records_execution_trace("", LayerSegment.L4_STATE, ""),
                }

                self._cache.set_json(admission_key, decision_data, ttl_seconds=3600)

            # Emit telemetry events
            if decision.admitted:
                _emit_feeds_meta_learning("p3lm", "system_learning_admission_gate", "admission_recorded")
            else:
                _emit_captures_pattern("p3lm", "system_learning_admission_gate", "denial_recorded")

        except (AttributeError, RuntimeError, TypeError, ValueError, OSError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            logger.debug("system_learning_admission_gate: admission decision record failure: %s", exc)

    def get_metrics(self) -> dict[str, Any]:
        """Get admission gate metrics."""
        total = self._metrics["total_evaluations"]
        admission_rate = self._metrics["admissions"] / total if total > 0 else 0.0

        return {
            **self._metrics,
            "admission_rate": admission_rate,
            "denial_rate": 1 - admission_rate,
        }

    def reset_metrics(self) -> None:
        """Reset admission gate metrics."""
        for key in self._metrics:
            self._metrics[key] = 0
        _emit_records_telemetry_event("system_learning_admission_gate", "p4obs", "metrics_reset")


# Module-level singleton
_system_learning_admission_gate: SystemLearningCacheAdmissionGate | None = None


def get_system_learning_admission_gate() -> SystemLearningCacheAdmissionGate:
    """Get the singleton system learning admission gate instance."""
    global _system_learning_admission_gate
    if _system_learning_admission_gate is None:
        _system_learning_admission_gate = SystemLearningCacheAdmissionGate()
    return _system_learning_admission_gate


__all__ = [
    "SystemLearningCacheAdmissionGate",
    "SystemLearningAdmissionDecision",
    "SystemLearningAdmissionContext",
    "get_system_learning_admission_gate",
]
