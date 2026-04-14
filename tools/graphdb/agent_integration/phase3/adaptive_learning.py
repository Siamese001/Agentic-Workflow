"""Adaptive Learning - Pattern recognition and self-improving architectural models.

This module provides adaptive learning capabilities that enable
agents to learn from architectural patterns and improve over time.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
from datetime import datetime, timedelta

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from ..phase2.contextual_engine import ContextualIntelligenceEngine, AnalysisResult
from tqdm import tqdm

logger = logging.getLogger(__name__)


class LearningType(Enum):
    """Types of learning patterns."""

    PATTERN_RECOGNITION = "pattern_recognition"
    ANOMALY_DETECTION = "anomaly_detection"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    RISK_PREDICTION = "risk_prediction"
    ARCHITECTURAL_EVOLUTION = "architectural_evolution"


class PatternType(Enum):
    """Types of architectural patterns."""

    DEPENDENCY_PATTERN = "dependency_pattern"
    LAYER_VIOLATION_PATTERN = "layer_violation_pattern"
    PERFORMANCE_PATTERN = "performance_pattern"
    SECURITY_PATTERN = "security_pattern"
    COLLABORATION_PATTERN = "collaboration_pattern"


@dataclass
class LearningPattern:
    """Represents a learned architectural pattern."""

    pattern_id: str
    pattern_type: PatternType
    description: str
    confidence: float  # 0.0 to 1.0
    frequency: int  # How often this pattern occurs
    last_seen: datetime
    examples: List[Dict[str, Any]]
    recommendations: List[str]
    risk_implications: List[str]


@dataclass
class LearningInsight:
    """Insight generated from adaptive learning."""

    insight_id: str
    insight_type: LearningType
    title: str
    description: str
    confidence: float
    supporting_patterns: List[str]
    actionable_recommendations: List[str]
    predicted_impact: str
    generated_at: datetime


@dataclass
class LearningResult:
    """Result of adaptive learning analysis."""

    patterns_discovered: List[LearningPattern]
    insights_generated: List[LearningInsight]
    model_accuracy: float
    learning_progress: float  # 0.0 to 1.0
    recommendations: List[str]
    confidence_score: float
    execution_time_seconds: float = 0.0


class AdaptiveLearningEngine:
    """Adaptive learning engine for pattern recognition and self-improvement."""

    def __init__(self, contextual_engine: ContextualIntelligenceEngine):
        """Initialize adaptive learning engine.

        Args:
            contextual_engine: Contextual intelligence engine for base analysis
        """
        self.contextual_engine = contextual_engine

        # Learning data storage
        self.pattern_registry: Dict[str, LearningPattern] = {}
        self.insight_history: List[LearningInsight] = []
        self.learning_data: deque[Dict[str, Any]] = deque(maxlen=10000)

        # Learning models
        self.pattern_models: Dict[PatternType, Any] = {}
        self.anomaly_detector: Optional[Any] = None
        self.performance_predictor: Optional[Any] = None

        # Learning configuration
        self.learning_config = {
            "min_pattern_frequency": 3,
            "pattern_confidence_threshold": 0.7,
            "learning_window_days": 30,
            "max_patterns_per_type": 50,
        }

        # Initialize learning models
        self._initialize_learning_models()

        logger.info("AdaptiveLearningEngine initialized")

    def learn_from_context(
        self, context: ArchitecturalContext, result: AnalysisResult
    ) -> List[LearningInsight]:
        """Learn from architectural context and analysis results.

        Args:
            context: Architectural context to learn from
            result: Analysis result to learn from

        Returns:
            List of learning insights generated
        """
        logger.info("Learning from architectural context")

        # Store learning data
        learning_data_point = {
            "timestamp": datetime.now(),
            "context": context,
            "result": result,
            "features": self._extract_features(context, result),
        }
        self.learning_data.append(learning_data_point)

        # Generate insights
        insights = []

        # Pattern recognition insights
        pattern_insights = self._generate_pattern_insights(context, result)
        insights.extend(pattern_insights)

        # Anomaly detection insights
        anomaly_insights = self._detect_anomalies(context, result)
        insights.extend(anomaly_insights)

        # Performance optimization insights
        performance_insights = self._generate_performance_insights(context, result)
        insights.extend(performance_insights)

        # Store insights
        self.insight_history.extend(insights)

        # Update learning models
        self._update_learning_models()

        logger.info(f"Generated {len(insights)} learning insights")

        return insights

    def analyze_learning_patterns(self, time_window: Optional[int] = None) -> LearningResult:
        """Analyze learning patterns over time.

        Args:
            time_window: Time window in days (None for all available data)

        Returns:
            LearningResult with pattern analysis and insights
        """
        start_time = time.time()

        logger.info("Analyzing learning patterns")

        # Filter learning data by time window
        filtered_data = self._filter_data_by_time_window(time_window)

        # Discover patterns
        discovered_patterns = self._discover_patterns(filtered_data)

        # Generate insights
        generated_insights = self._generate_insights_from_patterns(discovered_patterns)

        # Calculate model accuracy
        model_accuracy = self._calculate_model_accuracy()

        # Calculate learning progress
        learning_progress = self._calculate_learning_progress()

        # Generate recommendations
        recommendations = self._generate_learning_recommendations(
            discovered_patterns, generated_insights, model_accuracy
        )

        # Calculate confidence score
        confidence_score = self._calculate_learning_confidence(
            discovered_patterns, model_accuracy, learning_progress
        )

        result = LearningResult(
            patterns_discovered=discovered_patterns,
            insights_generated=generated_insights,
            model_accuracy=model_accuracy,
            learning_progress=learning_progress,
            recommendations=recommendations,
            confidence_score=confidence_score,
            execution_time_seconds=time.time() - start_time,
        )

        logger.info(f"Pattern analysis completed in {result.execution_time_seconds:.3f}s")

        return result

    def predict_architectural_risk(self, context: ArchitecturalContext) -> Dict[str, Any]:
        """Predict architectural risks based on learned patterns.

        Args:
            context: Architectural context for risk prediction

        Returns:
            Risk prediction with confidence and recommendations
        """
        # Extract features from context
        features = self._extract_features(context, None)

        # Find similar historical patterns
        similar_patterns = self._find_similar_patterns(features)

        # Calculate risk probability
        risk_probability = self._calculate_risk_probability(similar_patterns)

        # Generate risk factors
        risk_factors = self._identify_risk_factors(context, similar_patterns)

        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(risk_factors)

        return {
            "risk_probability": risk_probability,
            "confidence": self._calculate_prediction_confidence(similar_patterns),
            "risk_factors": risk_factors,
            "mitigation_strategies": mitigation_strategies,
            "similar_patterns": [p.pattern_id for p in similar_patterns],
            "prediction_timestamp": datetime.now().isoformat(),
        }

    def recommend_architectural_improvements(self, context: ArchitecturalContext) -> List[Dict[str, Any]]:
        """Recommend architectural improvements based on learning.

        Args:
            context: Architectural context for improvement recommendations

        Returns:
            List of architectural improvement recommendations
        """
        recommendations = []

        # Analyze current context against learned patterns
        features = self._extract_features(context, None)

        # Find anti-patterns
        anti_patterns = self._identify_anti_patterns(features)
        for anti_pattern in anti_patterns:
            recommendations.append(
                {
                    "type": "anti_pattern_resolution",
                    "pattern_id": anti_pattern.pattern_id,
                    "description": f"Resolve anti-pattern: {anti_pattern.description}",
                    "priority": "high" if anti_pattern.confidence > 0.8 else "medium",
                    "recommendations": anti_pattern.recommendations,
                }
            )

        # Find optimization opportunities
        optimization_opportunities = self._find_optimization_opportunities(features)
        for opportunity in optimization_opportunities:
            recommendations.append(
                {
                    "type": "optimization",
                    "description": opportunity["description"],
                    "priority": opportunity["priority"],
                    "expected_impact": opportunity["impact"],
                    "implementation_effort": opportunity["effort"],
                }
            )

        # Find pattern applications
        applicable_patterns = self._find_applicable_patterns(features)
        for pattern in applicable_patterns:
            recommendations.append(
                {
                    "type": "pattern_application",
                    "pattern_id": pattern.pattern_id,
                    "description": f"Apply pattern: {pattern.description}",
                    "priority": "medium",
                    "benefits": pattern.recommendations,
                }
            )

        return recommendations

    def _extract_features(
        self, context: ArchitecturalContext, result: Optional[AnalysisResult]
    ) -> Dict[str, Any]:
        """Extract features from context and result for learning."""
        features = {
            "action_type": context.action_type,
            "target_module_count": len(context.target_modules),
            "target_modules": context.target_modules,
            "proposed_changes": context.proposed_changes,
            "session_id": context.session_id,
        }

        if result:
            features.update(
                {
                    "analysis_depth": result.analysis_depth.value,
                    "risk_level": result.base_result.risk_level.value,
                    "confidence_score": result.confidence_score,
                    "contextual_insights_count": len(result.contextual_insights),
                    "recommendations_count": len(result.recommendations),
                }
            )

        return features

    def _generate_pattern_insights(
        self, context: ArchitecturalContext, result: AnalysisResult
    ) -> List[LearningInsight]:
        """Generate insights from pattern recognition."""
        insights = []

        # Analyze action type patterns
        action_pattern = self._analyze_action_type_pattern(context.action_type)
        if action_pattern:
            insights.append(action_pattern)

        # Analyze module interaction patterns
        module_pattern = self._analyze_module_interaction_pattern(context.target_modules)
        if module_pattern:
            insights.append(module_pattern)

        # Analyze risk level patterns
        if result:
            risk_pattern = self._analyze_risk_level_pattern(result.base_result.risk_level)
            if risk_pattern:
                insights.append(risk_pattern)

        return insights

    def _detect_anomalies(
        self, context: ArchitectableContext, result: AnalysisResult
    ) -> List[LearningInsight]:
        """Detect anomalies in architectural patterns."""
        insights = []

        # This would integrate with actual anomaly detection models
        # For now, provide mock anomaly detection

        # Check for unusual action patterns
        if context.action_type not in ["read_file", "write_file", "analyze_code"]:
            insights.append(
                LearningInsight(
                    insight_id=f"anomaly_action_{int(time.time())}",
                    insight_type=LearningType.ANOMALY_DETECTION,
                    title="Unusual Action Pattern",
                    description=f"Uncommon action type detected: {context.action_type}",
                    confidence=0.7,
                    supporting_patterns=[],
                    actionable_recommendations=["Review action purpose", "Validate architectural compliance"],
                    predicted_impact="Low impact on overall architecture",
                    generated_at=datetime.now(),
                )
            )

        # Check for unusual module patterns
        if len(context.target_modules) > 10:
            insights.append(
                LearningInsight(
                    insight_id=f"anomaly_modules_{int(time.time())}",
                    insight_type=LearningType.ANOMALY_DETECTION,
                    title="Large Module Set",
                    description=f"Unusually large number of target modules: {len(context.target_modules)}",
                    confidence=0.8,
                    supporting_patterns=[],
                    actionable_recommendations=[
                        "Consider breaking into smaller actions",
                        "Validate necessity of all modules",
                    ],
                    predicted_impact="High complexity and risk",
                    generated_at=datetime.now(),
                )
            )

        return insights

    def _generate_performance_insights(
        self, context: ArchitecturalContext, result: AnalysisResult
    ) -> List[LearningInsight]:
        """Generate performance optimization insights."""
        insights = []

        if result and result.execution_time_seconds > 2.0:
            insights.append(
                LearningInsight(
                    insight_id=f"performance_slow_{int(time.time())}",
                    insight_type=LearningType.PERFORMANCE_OPTIMIZATION,
                    title="Slow Analysis Performance",
                    description=f"Analysis took {result.execution_time_seconds:.2f} seconds",
                    confidence=0.9,
                    supporting_patterns=[],
                    actionable_recommendations=["Optimize analysis depth", "Improve caching strategy"],
                    predicted_impact="Improved agent responsiveness",
                    generated_at=datetime.now(),
                )
            )

        return insights

    def _analyze_action_type_pattern(self, action_type: str) -> Optional[LearningInsight]:
        """Analyze patterns in action types."""
        # Count recent occurrences of this action type
        recent_data = [d for d in self.learning_data if d["timestamp"] > datetime.now() - timedelta(days=7)]

        action_count = sum(1 for d in recent_data if d["context"].action_type == action_type)

        if action_count >= self.learning_config["min_pattern_frequency"]:
            return LearningInsight(
                insight_id=f"pattern_action_{action_type}_{int(time.time())}",
                insight_type=LearningType.PATTERN_RECOGNITION,
                title=f"Frequent Action Pattern: {action_type}",
                description=f"Action type '{action_type}' occurs frequently ({action_count} times in 7 days)",
                confidence=0.8,
                supporting_patterns=[],
                actionable_recommendations=[
                    f"Optimize workflow for {action_type}",
                    f"Consider automation for {action_type}",
                ],
                predicted_impact="Improved efficiency for common actions",
                generated_at=datetime.now(),
            )

        return None

    def _analyze_module_interaction_pattern(self, target_modules: List[str]) -> Optional[LearningInsight]:
        """Analyze patterns in module interactions."""
        if len(target_modules) < 2:
            return None

        # Check for common module combinations
        module_signature = tuple(sorted(target_modules))

        recent_data = [d for d in self.learning_data if d["timestamp"] > datetime.now() - timedelta(days=30)]

        signature_count = sum(
            1 for d in recent_data if tuple(sorted(d["context"].target_modules)) == module_signature
        )

        if signature_count >= self.learning_config["min_pattern_frequency"]:
            return LearningInsight(
                insight_id=f"pattern_modules_{hash(module_signature)}_{int(time.time())}",
                insight_type=LearningType.PATTERN_RECOGNITION,
                title="Module Interaction Pattern",
                description=f"Module combination occurs frequently: {', '.join(target_modules)}",
                confidence=0.7,
                supporting_patterns=[],
                actionable_recommendations=["Consider creating abstraction", "Optimize module coupling"],
                predicted_impact="Reduced complexity and improved maintainability",
                generated_at=datetime.now(),
            )

        return None

    def _analyze_risk_level_pattern(self, risk_level: RiskLevel) -> Optional[LearningInsight]:
        """Analyze patterns in risk levels."""
        recent_data = [d for d in self.learning_data if d["timestamp"] > datetime.now() - timedelta(days=7)]

        risk_count = sum(
            1 for d in recent_data if d.get("result") and d["result"].base_result.risk_level == risk_level
        )

        if risk_count >= self.learning_config["min_pattern_frequency"] and risk_level in [
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ]:
            return LearningInsight(
                insight_id=f"pattern_risk_{risk_level.value}_{int(time.time())}",
                insight_type=LearningType.RISK_PREDICTION,
                title=f"High Risk Pattern: {risk_level.value}",
                description=f"High risk level '{risk_level.value}' occurs frequently ({risk_count} times in 7 days)",
                confidence=0.9,
                supporting_patterns=[],
                actionable_recommendations=[
                    "Review risk assessment criteria",
                    "Implement additional safeguards",
                ],
                predicted_impact="Improved risk management and prevention",
                generated_at=datetime.now(),
            )

        return None

    def _discover_patterns(self, learning_data: List[Dict[str, Any]]) -> List[LearningPattern]:
        """Discover patterns from learning data."""
        patterns = []

        # This would integrate with actual pattern discovery algorithms
        # For now, provide mock pattern discovery

        # Dependency patterns
        dependency_pattern = LearningPattern(
            pattern_id="dependency_pattern_1",
            pattern_type=PatternType.DEPENDENCY_PATTERN,
            description="Common dependency pattern: service -> database -> cache",
            confidence=0.8,
            frequency=15,
            last_seen=datetime.now(),
            examples=[],
            recommendations=["Consider dependency injection", "Implement circuit breakers"],
            risk_implications=["High coupling risk", "Single point of failure"],
        )
        patterns.append(dependency_pattern)

        # Layer violation patterns
        violation_pattern = LearningPattern(
            pattern_id="violation_pattern_1",
            pattern_type=PatternType.LAYER_VIOLATION_PATTERN,
            description="Frequent layer violations: L3 -> L1 direct access",
            confidence=0.7,
            frequency=8,
            last_seen=datetime.now(),
            examples=[],
            recommendations=["Enforce layer boundaries", "Implement proper abstractions"],
            risk_implications=["Architectural degradation", "Maintenance complexity"],
        )
        patterns.append(violation_pattern)

        return patterns

    def _generate_insights_from_patterns(self, patterns: List[LearningPattern]) -> List[LearningInsight]:
        """Generate insights from discovered patterns."""
        insights = []

        for pattern in tqdm(patterns, desc="Processing", unit="item"):
            if pattern.confidence > self.learning_config["pattern_confidence_threshold"]:
                insight = LearningInsight(
                    insight_id=f"insight_{pattern.pattern_id}_{int(time.time())}",
                    insight_type=LearningType.PATTERN_RECOGNITION,
                    title=f"Pattern Insight: {pattern.pattern_type.value}",
                    description=f"High-confidence pattern discovered: {pattern.description}",
                    confidence=pattern.confidence,
                    supporting_patterns=[pattern.pattern_id],
                    actionable_recommendations=pattern.recommendations,
                    predicted_impact="Improved architectural quality",
                    generated_at=datetime.now(),
                )
                insights.append(insight)

        return insights

    def _calculate_model_accuracy(self) -> float:
        """Calculate accuracy of learning models."""
        # This would integrate with actual model accuracy calculation
        # For now, return mock accuracy
        return 0.85

    def _calculate_learning_progress(self) -> float:
        """Calculate learning progress over time."""
        if len(self.learning_data) < 100:
            return 0.3
        elif len(self.learning_data) < 500:
            return 0.6
        else:
            return 0.9

    def _generate_learning_recommendations(
        self, patterns: List[LearningPattern], insights: List[LearningInsight], model_accuracy: float
    ) -> List[str]:
        """Generate learning improvement recommendations."""
        recommendations = []

        if model_accuracy < 0.8:
            recommendations.append("Improve model accuracy with more training data")

        if len(patterns) < 5:
            recommendations.append("Increase pattern discovery sensitivity")

        if len(insights) < 3:
            recommendations.append("Enhance insight generation algorithms")

        if len(self.learning_data) < 1000:
            recommendations.append("Collect more architectural data for better learning")

        return recommendations

    def _calculate_learning_confidence(
        self, patterns: List[LearningPattern], model_accuracy: float, learning_progress: float
    ) -> float:
        """Calculate confidence in learning results."""
        base_confidence = 0.5

        # Adjust based on pattern quality
        if patterns:
            avg_pattern_confidence = sum(p.confidence for p in patterns) / len(patterns)
            base_confidence += avg_pattern_confidence * 0.3

        # Adjust based on model accuracy
        base_confidence += model_accuracy * 0.2

        # Adjust based on learning progress
        base_confidence += learning_progress * 0.2

        return min(1.0, base_confidence)

    def _filter_data_by_time_window(self, time_window: Optional[int]) -> List[Dict[str, Any]]:
        """Filter learning data by time window."""
        if not time_window:
            return list(self.learning_data)

        cutoff_date = datetime.now() - timedelta(days=time_window)
        return [d for d in self.learning_data if d["timestamp"] > cutoff_date]

    def _find_similar_patterns(self, features: Dict[str, Any]) -> List[LearningPattern]:
        """Find patterns similar to current features."""
        similar_patterns = []

        # This would integrate with actual pattern matching
        # For now, return mock similar patterns
        for pattern in self.pattern_registry.values():
            if pattern.confidence > 0.7:
                similar_patterns.append(pattern)

        return similar_patterns[:5]  # Return top 5 similar patterns

    def _calculate_risk_probability(self, similar_patterns: List[LearningPattern]) -> float:
        """Calculate risk probability based on similar patterns."""
        if not similar_patterns:
            return 0.1  # Low base risk

        # Count high-risk patterns
        high_risk_count = sum(
            1
            for p in similar_patterns
            if "risk" in p.description.lower() or "violation" in p.description.lower()
        )

        return min(1.0, high_risk_count / len(similar_patterns))

    def _identify_risk_factors(
        self, context: ArchitecturalContext, similar_patterns: List[LearningPattern]
    ) -> List[str]:
        """Identify risk factors based on patterns."""
        risk_factors = []

        for pattern in similar_patterns:
            risk_factors.extend(pattern.risk_implications)

        return list(set(risk_factors))

    def _generate_mitigation_strategies(self, risk_factors: List[str]) -> List[str]:
        """Generate mitigation strategies for identified risks."""
        strategies = []

        for factor in risk_factors:
            if "coupling" in factor.lower():
                strategies.append("Implement loose coupling patterns")
            elif "violation" in factor.lower():
                strategies.append("Strengthen architectural governance")
            elif "performance" in factor.lower():
                strategies.append("Optimize performance bottlenecks")
            elif "security" in factor.lower():
                strategies.append("Enhance security measures")

        return list(set(strategies))

    def _calculate_prediction_confidence(self, similar_patterns: List[LearningPattern]) -> float:
        """Calculate confidence in risk prediction."""
        if not similar_patterns:
            return 0.3  # Low confidence with no similar patterns

        avg_confidence = sum(p.confidence for p in similar_patterns) / len(similar_patterns)
        return avg_confidence

    def _identify_anti_patterns(self, features: Dict[str, Any]) -> List[LearningPattern]:
        """Identify anti-patterns in current context."""
        anti_patterns = []

        # This would integrate with actual anti-pattern detection
        # For now, return mock anti-patterns
        if features.get("target_module_count", 0) > 5:
            anti_pattern = LearningPattern(
                pattern_id="anti_pattern_large_scope",
                pattern_type=PatternType.DEPENDENCY_PATTERN,
                description="Large scope action affecting many modules",
                confidence=0.8,
                frequency=1,
                last_seen=datetime.now(),
                examples=[],
                recommendations=["Break into smaller actions", "Use incremental approach"],
                risk_implications=["High complexity", "Increased risk"],
            )
            anti_patterns.append(anti_pattern)

        return anti_patterns

    def _find_optimization_opportunities(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find optimization opportunities."""
        opportunities = []

        # This would integrate with actual optimization analysis
        # For now, return mock opportunities
        if features.get("action_type") == "analyze_code":
            opportunities.append(
                {
                    "description": "Optimize code analysis with caching",
                    "priority": "medium",
                    "impact": "Improved performance",
                    "effort": "low",
                }
            )

        return opportunities

    def _find_applicable_patterns(self, features: Dict[str, Any]) -> List[LearningPattern]:
        """Find patterns applicable to current context."""
        applicable_patterns = []

        # This would integrate with actual pattern matching
        # For now, return mock applicable patterns
        for pattern in self.pattern_registry.values():
            if pattern.confidence > 0.6:
                applicable_patterns.append(pattern)

        return applicable_patterns[:3]  # Return top 3 applicable patterns

    def _update_learning_models(self) -> None:
        """Update learning models with new data."""
        # This would integrate with actual model updating
        # For now, just log the update
        logger.debug("Learning models updated with new data")

    def _initialize_learning_models(self) -> None:
        """Initialize learning models."""
        # This would integrate with actual model initialization
        # For now, just log the initialization
        logger.info("Learning models initialized")

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get adaptive learning statistics."""
        return {
            "total_patterns": len(self.pattern_registry),
            "total_insights": len(self.insight_history),
            "learning_data_points": len(self.learning_data),
            "pattern_types": {
                pattern_type.value: len(
                    [p for p in self.pattern_registry.values() if p.pattern_type == pattern_type]
                )
                for pattern_type in PatternType
            },
            "insight_types": {
                insight_type.value: len([i for i in self.insight_history if i.insight_type == insight_type])
                for insight_type in LearningType
            },
            "average_pattern_confidence": sum(p.confidence for p in self.pattern_registry.values())
            / len(self.pattern_registry)
            if self.pattern_registry
            else 0.0,
        }
