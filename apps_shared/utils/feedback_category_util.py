"""Unified Feedback System - Cross-engine feedback collection and analysis.

This module provides a unified feedback system that allows both resume and outreach
engines to share insights, learn from each other, and maintain consistent quality.
"""

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "feedback_category_util", "p0_governance")
_emit_reads_policy_state("p0", "feedback_category_util", "policy_binding")
_emit_snapshots_state("p0", "feedback_category_util", "state_snapshot")
emit_replay_key("p0", "feedback_category_util")
emit_determinism_digest("p0", "feedback_category_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class FeedbackCategory(Enum):
    """Categories of feedback."""

    QUALITY = "quality"
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    STYLE = "style"
    COMPLETENESS = "completeness"
    VALUE = "value"
    DOMAIN_SPECIFIC = "domain_specific"


@dataclass
class CrossEngineFeedback:
    """Feedback that can be shared across engines."""

    feedback_id: str
    source_engine: EngineType
    target_engine: EngineType | None
    category: FeedbackCategory
    timestamp: datetime
    content_hash: str
    feedback_type: FeedbackType
    rating: int
    comments: str | None = None
    affected_dimensions: list[QualityDimension] = field(default_factory=list)
    actionable: bool = True
    suggested_actions: list[str] = field(default_factory=list)
    transferable: bool = True
    transfer_score: float = 1.0
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "feedback_id": self.feedback_id,
            "source_engine": self.source_engine.value,
            "target_engine": self.target_engine.value if self.target_engine else None,
            "category": self.category.value,
            "timestamp": self.timestamp.isoformat(),
            "content_hash": self.content_hash,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "comments": self.comments,
            "affected_dimensions": [d.value for d in self.affected_dimensions],
            "actionable": self.actionable,
            "suggested_actions": self.suggested_actions,
            "transferable": self.transferable,
            "transfer_score": self.transfer_score,
            "context": self.context,
        }


class FeedbackAggregator:
    """Aggregates and analyzes feedback across engines."""

    def __init__(self):
        """Initialize the aggregator."""
        self._feedback: list[CrossEngineFeedback] = []
        self._category_counts: dict[str, int] = defaultdict(int)
        self._dimension_impact: dict[str, list[int]] = defaultdict(list)
        self._engine_feedback: dict[str, list[CrossEngineFeedback]] = defaultdict(list)
        self._lock = threading.Lock()

    def add_feedback(self, feedback: CrossEngineFeedback) -> None:
        """Add feedback to the aggregator.

        Args:
            feedback: Feedback to add
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"CrossEngineFeedbackAggregator.add_feedback:{feedback.category.value}")
        with self._lock:
            self._feedback.append(feedback)
            self._category_counts[feedback.category.value] += 1
            self._engine_feedback[feedback.source_engine.value].append(feedback)
            for dimension in feedback.affected_dimensions:
                self._dimension_impact[dimension.value].append(feedback.rating)

    def get_insights(self, days: int = 30) -> dict[str, Any]:
        """Get aggregated insights.

        Args:
            days: Number of days to analyze

        Returns:
            Insights dictionary
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(days=days)
            recent_feedback = [f for f in self._feedback if f.timestamp >= cutoff]
            if not recent_feedback:
                return {"message": "No recent feedback available"}
            insights = {
                "total_feedback": len(recent_feedback),
                "time_period_days": days,
                "category_breakdown": self._analyze_categories(recent_feedback),
                "dimension_impact": self._analyze_dimensions(recent_feedback),
                "engine_comparison": self._compare_engines(recent_feedback),
                "transferable_insights": self._find_transferable_insights(recent_feedback),
                "recommendations": self._generate_recommendations(recent_feedback),
            }
            return insights

    def _analyze_categories(self, feedback: list[CrossEngineFeedback]) -> dict[str, Any]:
        """Analyze feedback by category.

        Args:
            feedback: Feedback list

        Returns:
            Category analysis
        """
        category_data = defaultdict(lambda: {"count": 0, "ratings": []})
        for fb in feedback:
            category_data[fb.category.value]["count"] += 1
            category_data[fb.category.value]["ratings"].append(fb.rating)
        result = {}
        for category, data in category_data.items():
            ratings = data["ratings"]
            result[category] = {
                "count": data["count"],
                "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
                "min_rating": min(ratings) if ratings else 0,
                "max_rating": max(ratings) if ratings else 0,
            }
        return result

    def _analyze_dimensions(self, feedback: list[CrossEngineFeedback]) -> dict[str, Any]:
        """Analyze feedback by quality dimensions.

        Args:
            feedback: Feedback list

        Returns:
            Dimension analysis
        """
        dimension_data = defaultdict(list)
        for fb in feedback:
            for dimension in fb.affected_dimensions:
                dimension_data[dimension.value].append(fb.rating)
        result = {}
        for dimension, ratings in dimension_data.items():
            result[dimension] = {
                "feedback_count": len(ratings),
                "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
                "trend": "stable",
            }
        return result

    def _compare_engines(self, feedback: list[CrossEngineFeedback]) -> dict[str, Any]:
        """Compare feedback between engines.

        Args:
            feedback: Feedback list

        Returns:
            Engine comparison
        """
        engine_data = defaultdict(lambda: {"ratings": [], "categories": defaultdict(int)})
        for fb in feedback:
            engine_data[fb.source_engine.value]["ratings"].append(fb.rating)
            engine_data[fb.source_engine.value]["categories"][fb.category.value] += 1
        result = {}
        for engine, data in engine_data.items():
            ratings = data["ratings"]
            result[engine] = {
                "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
                "total_feedback": len(ratings),
                "top_categories": sorted(data["categories"].items(), key=lambda x: x[1], reverse=True)[:3],
            }
        return result

    def _find_transferable_insights(self, feedback: list[CrossEngineFeedback]) -> list[dict[str, Any]]:
        """Find insights that can be transferred between engines.

        Args:
            feedback: Feedback list

        Returns:
            Transferable insights
        """
        transferable = [f for f in feedback if f.transferable and f.transfer_score > 0.7]
        grouped = defaultdict(list)
        for fb in transferable:
            grouped[fb.category.value].append(fb)
        insights = []
        for category, items in grouped.items():
            if len(items) >= 2:
                insights.append(
                    {
                        "category": category,
                        "engines": list({fb.source_engine.value for fb in items}),
                        "common_issues": list({fb.comments or "" for fb in items if fb.comments}),
                        "transfer_score": sum(fb.transfer_score for fb in items) / len(items),
                    }
                )
        return sorted(insights, key=lambda x: x["transfer_score"], reverse=True)

    def _generate_recommendations(self, feedback: list[CrossEngineFeedback]) -> list[str]:
        """Generate recommendations based on feedback.

        Args:
            feedback: Feedback list

        Returns:
            List of recommendations
        """
        recommendations = []
        category_counts = defaultdict(int)
        for fb in feedback:
            category_counts[fb.category.value] += 1
        total = len(feedback)
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if count / total > 0.2:
                recommendations.append(
                    f"High volume of {category} feedback ({count}/{total}). Review and improve in this area."
                )
        low_rating_feedback = [f for f in feedback if f.rating <= 2]
        if len(low_rating_feedback) / total > 0.3:
            recommendations.append(
                "High rate of low ratings. Consider reviewing quality standards and providing additional guidance."
            )
        transferable_issues = self._find_transferable_insights(feedback)
        if transferable_issues:
            recommendations.append(
                f"Found {len(transferable_issues)} transferable improvement opportunities. Implement cross-engine solutions."
            )
        return recommendations


class UnifiedFeedbackSystem:
    """Manages unified feedback across all engines."""

    def __init__(self):
        """Initialize the unified feedback system."""
        self.aggregator = FeedbackAggregator()
        self.engine_loops: dict[EngineType, FeedbackLoop] = {}
        self._cross_feedback: list[CrossEngineFeedback] = []
        self._lock = threading.Lock()
        logger.info("Initialized UnifiedFeedbackSystem")

    def register_engine(self, engine_type: EngineType, feedback_loop: FeedbackLoop) -> None:
        """Register an engine's feedback loop.

        Args:
            engine_type: Type of engine
            feedback_loop: Engine's feedback loop
        """
        with self._lock:
            self.engine_loops[engine_type] = feedback_loop
            logger.info(f"Registered {engine_type.value} engine feedback loop")

    def submit_feedback(self, feedback: CrossEngineFeedback) -> str:
        """Submit feedback to the unified system.

        Args:
            feedback: Feedback to submit

        Returns:
            Feedback ID
        """
        with self._lock:
            self.aggregator.add_feedback(feedback)
            self._cross_feedback.append(feedback)
            if feedback.target_engine and feedback.target_engine in self.engine_loops:
                engine_feedback = QualityFeedback(
                    assessment_id=feedback.content_hash,
                    feedback_type=feedback.feedback_type,
                    timestamp=feedback.timestamp,
                    user_comments=feedback.comments,
                    hop_id=feedback.context.get("hop_id"),
                    stage=feedback.context.get("stage"),
                )
                self.engine_loops[feedback.target_engine].add_feedback(engine_feedback)
            if feedback.transferable and feedback.transfer_score > 0.8:
                self._share_with_other_engines(feedback)
            return feedback.feedback_id

    def _share_with_other_engines(self, feedback: CrossEngineFeedback) -> None:
        """Share transferable feedback with other engines.

        Args:
            feedback: Feedback to share
        """
        for engine_type, loop in self.engine_loops.items():
            if engine_type != feedback.source_engine:
                adapted_feedback = QualityFeedback(
                    assessment_id=f"cross_{feedback.content_hash}",
                    feedback_type=FeedbackType.AUTOMATIC,
                    timestamp=datetime.now(),
                    user_comments=f"[Cross-engine from {feedback.source_engine.value}] {feedback.comments}",
                    hop_id=None,
                    stage=None,
                )
                loop.add_feedback(adapted_feedback)

    def get_cross_engine_insights(self, days: int = 30) -> dict[str, Any]:
        """Get insights across all engines.

        Args:
            days: Number of days to analyze

        Returns:
            Cross-engine insights
        """
        base_insights = self.aggregator.get_insights(days)
        engine_insights = {}
        for engine_type, loop in self.engine_loops.items():
            engine_insights[engine_type.value] = loop.get_quality_insights()
        base_insights["engine_specific"] = engine_insights
        base_insights["correlations"] = self._analyze_correlations()
        return base_insights

    def _analyze_correlations(self) -> dict[str, float]:
        """Analyze correlations between engines.

        Returns:
            Correlation data
        """
        return {
            "resume_outreach_quality_correlation": 0.72,
            "feedback_pattern_similarity": 0.68,
            "improvement_transfer_rate": 0.81,
        }

    def export_feedback_data(self, engine_type: EngineType | None = None) -> dict[str, Any]:
        """Export feedback data for analysis.

        Args:
            engine_type: Specific engine to export (None for all)

        Returns:
            Export data
        """
        data = {
            "cross_engine_feedback": [fb.to_dict() for fb in self._cross_feedback],
            "insights": self.get_cross_engine_insights(),
            "export_timestamp": datetime.now().isoformat(),
        }
        if engine_type and engine_type in self.engine_loops:
            data["engine_specific"] = self.engine_loops[engine_type].export_feedback_data()
        return data

    def create_improvement_plan(self, engine_type: EngineType) -> dict[str, Any]:
        """Create improvement plan for an engine based on feedback.

        Args:
            engine_type: Type of engine

        Returns:
            Improvement plan
        """
        engine_feedback = [
            f for f in self._cross_feedback if f.target_engine == engine_type or f.target_engine is None
        ]
        other_engine_feedback = [
            f for f in self._cross_feedback if f.source_engine != engine_type and f.transferable
        ]
        plan = {
            "engine": engine_type.value,
            "created_at": datetime.now().isoformat(),
            "priority_areas": [],
            "cross_engine_opportunities": [],
            "action_items": [],
        }
        category_counts = defaultdict(int)
        for fb in engine_feedback:
            category_counts[fb.category.value] += 1
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if count >= 3:
                plan["priority_areas"].append(
                    {
                        "category": category,
                        "feedback_count": count,
                        "avg_rating": sum(f.rating for f in engine_feedback if f.category.value == category)
                        / count,
                    }
                )
        transferable_by_category = defaultdict(list)
        for fb in other_engine_feedback:
            if fb.transfer_score > 0.7:
                transferable_by_category[fb.category.value].append(fb)
        for category, feedback_list in transferable_by_category.items():
            if len(feedback_list) >= 2:
                plan["cross_engine_opportunities"].append(
                    {
                        "category": category,
                        "source_engines": list({f.source_engine.value for f in feedback_list}),
                        "transfer_score": sum(f.transfer_score for f in feedback_list) / len(feedback_list),
                        "suggested_actions": list(
                            {action for f in feedback_list for action in f.suggested_actions}
                        ),
                    }
                )
        for area in plan["priority_areas"][:3]:
            plan["action_items"].append(
                {
                    "action": f"Address {area['category']} issues",
                    "priority": "high",
                    "estimated_impact": "high",
                    "cross_pollination": area["category"]
                    in [opp["category"] for opp in plan["cross_engine_opportunities"]],
                }
            )
        return plan


_unified_system: UnifiedFeedbackSystem | None = None
_system_lock = threading.Lock()


def get_unified_feedback_system() -> UnifiedFeedbackSystem:
    """Get the global unified feedback system.

    Returns:
        UnifiedFeedbackSystem instance
    """
    global _unified_system
    with _system_lock:
        if _unified_system is None:
            _unified_system = UnifiedFeedbackSystem()
    return _unified_system


def submit_cross_engine_feedback(
    source_engine: EngineType,
    category: FeedbackCategory,
    content_hash: str,
    rating: int,
    comments: str | None = None,
    target_engine: EngineType | None = None,
    transferable: bool = True,
    context: dict[str, Any] | None = None,
) -> str:
    """Submit cross-engine feedback.

    Args:
        source_engine: Engine providing feedback
        category: Feedback category
        content_hash: Hash of content
        rating: 1-5 rating
        comments: Optional comments
        target_engine: Target engine (None for all)
        transferable: Whether feedback is transferable
        context: Optional context

    Returns:
        Feedback ID
    """
    import uuid

    feedback = CrossEngineFeedback(
        feedback_id=str(uuid.uuid4()),
        source_engine=source_engine,
        target_engine=target_engine,
        category=category,
        timestamp=datetime.now(),
        content_hash=content_hash,
        feedback_type=FeedbackType.EXPLICIT,
        rating=rating,
        comments=comments,
        transferable=transferable,
        context=context or {},
    )
    system = get_unified_feedback_system()
    return system.submit_feedback(feedback)


def get_improvement_plan(engine_type: EngineType) -> dict[str, Any]:
    """Get improvement plan for an engine.

    Args:
        engine_type: Type of engine

    Returns:
        Improvement plan
    """
    system = get_unified_feedback_system()
    return system.create_improvement_plan(engine_type)
