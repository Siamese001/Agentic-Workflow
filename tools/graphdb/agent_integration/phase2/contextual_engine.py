"""Contextual Intelligence Engine - Progressive query deepening and adaptive analysis.

This module provides advanced contextual intelligence capabilities that
progressively deepen analysis based on agent context and risk levels.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from ..cache import QueryCache

logger = logging.getLogger(__name__)


class AnalysisDepth(Enum):
    """Analysis depth levels for progressive deepening."""

    SURFACE = "surface"  # Basic architectural check
    CONTEXTUAL = "contextual"  # Context-aware analysis
    DEEP = "deep"  # Deep architectural investigation
    COMPREHENSIVE = "comprehensive"  # Full ecosystem analysis


class ContextType(Enum):
    """Types of agent context for analysis adaptation."""

    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    TESTING = "testing"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"


@dataclass
class ContextualFactors:
    """Contextual factors that influence analysis depth and approach."""

    agent_experience: str = "intermediate"  # novice, intermediate, expert
    session_complexity: float = 0.5  # 0.0 to 1.0
    historical_success_rate: float = 0.8  # 0.0 to 1.0
    time_constraints: Optional[float] = None  # seconds
    risk_tolerance: str = "medium"  # low, medium, high
    domain_familiarity: Dict[str, float] = field(default_factory=dict)  # domain -> familiarity


@dataclass
class AnalysisResult:
    """Result of contextual analysis with progressive deepening."""

    base_result: DecisionResult
    contextual_insights: List[str]
    deep_analysis: Optional[Dict[str, Any]] = None
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    analysis_depth: AnalysisDepth = AnalysisDepth.SURFACE
    execution_time_seconds: float = 0.0
    context_factors_applied: List[str] = field(default_factory=list)


class ContextualIntelligenceEngine:
    """Advanced contextual intelligence engine with progressive query deepening."""

    def __init__(self, decision_engine: AgentDecisionEngine, cache: Optional[QueryCache] = None):
        """Initialize contextual intelligence engine.

        Args:
            decision_engine: Base decision engine for architectural analysis
            cache: Optional cache for contextual analysis results
        """
        self.decision_engine = decision_engine
        self.cache = cache or QueryCache(max_size=500, default_ttl=600.0)

        # Context learning
        self.agent_context_history: Dict[str, List[ArchitecturalContext]] = defaultdict(list)
        self.context_effectiveness: Dict[str, float] = defaultdict(float)

        # Analysis depth thresholds
        self.depth_thresholds = {
            AnalysisDepth.SURFACE: {"time_limit": 0.1, "risk_threshold": RiskLevel.LOW},
            AnalysisDepth.CONTEXTUAL: {"time_limit": 0.5, "risk_threshold": RiskLevel.MEDIUM},
            AnalysisDepth.DEEP: {"time_limit": 2.0, "risk_threshold": RiskLevel.HIGH},
            AnalysisDepth.COMPREHENSIVE: {"time_limit": 10.0, "risk_threshold": RiskLevel.CRITICAL},
        }

        logger.info("ContextualIntelligenceEngine initialized")

    def analyze_with_context(
        self, context: ArchitecturalContext, contextual_factors: Optional[ContextualFactors] = None
    ) -> AnalysisResult:
        """Perform contextual analysis with progressive deepening.

        Args:
            context: Architectural context for analysis
            contextual_factors: Optional contextual factors for adaptation

        Returns:
            AnalysisResult with progressive insights and recommendations
        """
        start_time = time.time()

        # Determine initial analysis depth
        contextual_factors = contextual_factors or ContextualFactors()
        initial_depth = self._determine_initial_depth(context, contextual_factors)

        logger.info(f"Starting contextual analysis at depth: {initial_depth.value}")

        # Record context for learning
        self._record_agent_context(context)

        # Perform progressive analysis
        analysis_result = self._progressive_analysis(context, contextual_factors, initial_depth)

        # Calculate execution time
        analysis_result.execution_time_seconds = time.time() - start_time

        # Update learning models
        self._update_context_learning(context, analysis_result)

        logger.info(
            f"Contextual analysis completed in {analysis_result.execution_time_seconds:.3f}s "
            f"at depth: {analysis_result.analysis_depth.value}"
        )

        return analysis_result

    def _determine_initial_depth(
        self, context: ArchitecturalContext, factors: ContextualFactors
    ) -> AnalysisDepth:
        """Determine initial analysis depth based on context and factors."""
        # Base depth on action type and risk tolerance
        action_depth_map = {
            "read_file": AnalysisDepth.SURFACE,
            "analyze_code": AnalysisDepth.CONTEXTUAL,
            "write_file": AnalysisDepth.CONTEXTUAL,
            "modify_module": AnalysisDepth.DEEP,
            "refactor": AnalysisDepth.DEEP,
            "delete_file": AnalysisDepth.COMPREHENSIVE,
        }

        base_depth = action_depth_map.get(context.action_type, AnalysisDepth.CONTEXTUAL)

        # Adjust based on risk tolerance
        if factors.risk_tolerance == "low":
            depth_adjustment = 1  # Go deeper for low risk tolerance
        elif factors.risk_tolerance == "high":
            depth_adjustment = -1  # Stay shallower for high risk tolerance
        else:
            depth_adjustment = 0

        # Adjust based on agent experience
        if factors.agent_experience == "expert":
            depth_adjustment += 1
        elif factors.agent_experience == "novice":
            depth_adjustment -= 1

        # Apply depth adjustment within bounds
        depth_order = [
            AnalysisDepth.SURFACE,
            AnalysisDepth.CONTEXTUAL,
            AnalysisDepth.DEEP,
            AnalysisDepth.COMPREHENSIVE,
        ]

        current_index = depth_order.index(base_depth)
        new_index = max(0, min(len(depth_order) - 1, current_index + depth_adjustment))

        return depth_order[new_index]

    def _progressive_analysis(
        self, context: ArchitecturalContext, factors: ContextualFactors, initial_depth: AnalysisDepth
    ) -> AnalysisResult:
        """Perform progressive analysis with deepening based on findings."""

        # Start with base analysis
        base_result = self.decision_engine.analyze_action(context)

        # Initialize analysis result
        analysis_result = AnalysisResult(
            base_result=base_result,
            contextual_insights=[],
            confidence_score=0.5,
            analysis_depth=initial_depth,
            context_factors_applied=[],
        )

        # Apply contextual factors
        self._apply_contextual_factors(analysis_result, context, factors)

        # Progressive deepening based on risk and findings
        current_depth = initial_depth

        while self._should_deepend_analysis(analysis_result, current_depth, factors):
            next_depth = self._get_next_depth(current_depth)
            if not next_depth:
                break

            logger.info(f"Deepening analysis from {current_depth.value} to {next_depth.value}")

            # Perform deeper analysis
            deep_insights = self._perform_deep_analysis(context, next_depth, analysis_result)
            analysis_result.contextual_insights.extend(deep_insights)
            analysis_result.analysis_depth = next_depth

            current_depth = next_depth

            # Check time constraints
            if factors.time_constraints and analysis_result.execution_time_seconds > factors.time_constraints:
                logger.info("Time limit reached, stopping analysis deepening")
                break

        # Generate final recommendations
        analysis_result.recommendations = self._generate_contextual_recommendations(
            analysis_result, context, factors
        )

        # Calculate confidence score
        analysis_result.confidence_score = self._calculate_confidence_score(analysis_result, factors)

        return analysis_result

    def _apply_contextual_factors(
        self, result: AnalysisResult, context: ArchitecturalContext, factors: ContextualFactors
    ) -> None:
        """Apply contextual factors to adjust analysis."""

        # Agent experience adjustment
        if factors.agent_experience == "novice":
            result.contextual_insights.append("Novice agent detected: providing additional guidance")
            result.context_factors_applied.append("novice_guidance")
        elif factors.agent_experience == "expert":
            result.contextual_insights.append("Expert agent detected: enabling advanced analysis")
            result.context_factors_applied.append("expert_analysis")

        # Domain familiarity adjustment
        relevant_domains = self._extract_relevant_domains(context)
        for domain in relevant_domains:
            familiarity = factors.domain_familiarity.get(domain, 0.5)
            if familiarity < 0.3:
                result.contextual_insights.append(
                    f"Low familiarity with {domain}: enhanced validation recommended"
                )
                result.context_factors_applied.append(f"domain_familiarity_{domain}")

        # Session complexity adjustment
        if factors.session_complexity > 0.8:
            result.contextual_insights.append("High session complexity: increased caution recommended")
            result.context_factors_applied.append("complexity_adjustment")

        # Historical success rate adjustment
        if factors.historical_success_rate < 0.6:
            result.contextual_insights.append("Low historical success rate: additional safeguards applied")
            result.context_factors_applied.append("success_rate_adjustment")

    def _should_deepend_analysis(
        self, result: AnalysisResult, current_depth: AnalysisDepth, factors: ContextualFactors
    ) -> bool:
        """Determine if analysis should be deepened further."""

        # Don't deepen if already at maximum depth
        if current_depth == AnalysisDepth.COMPREHENSIVE:
            return False

        # Check time constraints
        if factors.time_constraints and result.execution_time_seconds > factors.time_constraints * 0.8:
            return False

        # Deepen based on risk level
        if result.base_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True

        # Deepen based on warnings count
        if len(result.base_result.warnings) > 2:
            return True

        # Deepen based on contextual factors
        if factors.session_complexity > 0.7 or factors.risk_tolerance == "low":
            return True

        return False

    def _get_next_depth(self, current_depth: AnalysisDepth) -> Optional[AnalysisDepth]:
        """Get next analysis depth level."""
        depth_order = [
            AnalysisDepth.SURFACE,
            AnalysisDepth.CONTEXTUAL,
            AnalysisDepth.DEEP,
            AnalysisDepth.COMPREHENSIVE,
        ]

        current_index = depth_order.index(current_depth)
        if current_index < len(depth_order) - 1:
            return depth_order[current_index + 1]

        return None

    def _perform_deep_analysis(
        self, context: ArchitecturalContext, depth: AnalysisDepth, current_result: AnalysisResult
    ) -> List[str]:
        """Perform deep analysis at specified depth level."""
        insights = []

        if depth == AnalysisDepth.CONTEXTUAL:
            insights.extend(self._contextual_analysis(context, current_result))
        elif depth == AnalysisDepth.DEEP:
            insights.extend(self._deep_analysis(context, current_result))
        elif depth == AnalysisDepth.COMPREHENSIVE:
            insights.extend(self._comprehensive_analysis(context, current_result))

        return insights

    def _contextual_analysis(
        self, context: ArchitecturalContext, current_result: AnalysisResult
    ) -> List[str]:
        """Perform contextual analysis."""
        insights = []

        # Analyze agent action patterns
        similar_contexts = self._find_similar_contexts(context)
        if similar_contexts:
            insights.append(f"Found {len(similar_contexts)} similar historical actions")

            # Analyze success patterns
            success_rate = self._calculate_historical_success_rate(similar_contexts)
            if success_rate < 0.7:
                insights.append("Historical success rate below 70%: increased caution recommended")

        # Analyze module interaction patterns
        interaction_insights = self._analyze_module_interactions(context)
        insights.extend(interaction_insights)

        return insights

    def _deep_analysis(self, context: ArchitecturalContext, current_result: AnalysisResult) -> List[str]:
        """Perform deep architectural analysis."""
        insights = []

        # Analyze architectural impact chains
        impact_chains = self._analyze_impact_chains(context)
        if impact_chains:
            insights.append(f"Identified {len(impact_chains)} architectural impact chains")

        # Analyze dependency evolution
        evolution_insights = self._analyze_dependency_evolution(context)
        insights.extend(evolution_insights)

        # Analyze governance implications
        governance_insights = self._analyze_governance_implications(context)
        insights.extend(governance_insights)

        return insights

    def _comprehensive_analysis(
        self, context: ArchitecturalContext, current_result: AnalysisResult
    ) -> List[str]:
        """Perform comprehensive ecosystem analysis."""
        insights = []

        # Analyze ecosystem-wide implications
        ecosystem_insights = self._analyze_ecosystem_implications(context)
        insights.extend(ecosystem_insights)

        # Analyze long-term architectural trends
        trend_insights = self._analyze_architectural_trends(context)
        insights.extend(trend_insights)

        # Analyze cross-system dependencies
        cross_system_insights = self._analyze_cross_system_dependencies(context)
        insights.extend(cross_system_insights)

        return insights

    def _find_similar_contexts(self, context: ArchitecturalContext) -> List[ArchitecturalContext]:
        """Find similar historical contexts."""
        similar_contexts = []

        # Simple similarity based on action type and target modules
        for agent_id, contexts in self.agent_context_history.items():
            for hist_context in contexts:
                if hist_context.action_type == context.action_type and any(
                    target in hist_context.target_modules for target in context.target_modules
                ):
                    similar_contexts.append(hist_context)

        return similar_contexts[:10]  # Limit to top 10 similar contexts

    def _calculate_historical_success_rate(self, contexts: List[ArchitecturalContext]) -> float:
        """Calculate historical success rate for similar contexts."""
        if not contexts:
            return 0.8  # Default assumption

        # This would integrate with actual success tracking
        # For now, return a mock calculation
        return sum(self.context_effectiveness.get(str(ctx), 0.8) for ctx in contexts) / len(contexts)

    def _analyze_module_interactions(self, context: ArchitecturalContext) -> List[str]:
        """Analyze module interaction patterns."""
        insights = []

        # This would integrate with GraphDB queries for interaction analysis
        # For now, provide mock insights
        if len(context.target_modules) > 1:
            insights.append("Multi-module action detected: analyzing cross-module dependencies")

        return insights

    def _analyze_impact_chains(self, context: ArchitecturalContext) -> List[Dict[str, Any]]:
        """Analyze architectural impact chains."""
        # This would integrate with blast radius and dependency analysis
        return []

    def _analyze_dependency_evolution(self, context: ArchitecturalContext) -> List[str]:
        """Analyze dependency evolution patterns."""
        # This would integrate with historical analysis
        return []

    def _analyze_governance_implications(self, context: ArchitecturalContext) -> List[str]:
        """Analyze governance implications."""
        # This would integrate with structural queries
        return []

    def _analyze_ecosystem_implications(self, context: ArchitecturalContext) -> List[str]:
        """Analyze ecosystem-wide implications."""
        # This would integrate with comprehensive graph analysis
        return []

    def _analyze_architectural_trends(self, context: ArchitecturalContext) -> List[str]:
        """Analyze long-term architectural trends."""
        # This would integrate with trend analysis
        return []

    def _analyze_cross_system_dependencies(self, context: ArchitecturalContext) -> List[str]:
        """Analyze cross-system dependencies."""
        # This would integrate with cross-system analysis
        return []

    def _generate_contextual_recommendations(
        self, result: AnalysisResult, context: ArchitecturalContext, factors: ContextualFactors
    ) -> List[str]:
        """Generate contextual recommendations based on analysis."""
        recommendations = []

        # Base recommendations from decision result
        recommendations.extend(result.base_result.alternatives)

        # Context-specific recommendations
        if factors.agent_experience == "novice":
            recommendations.append("Consider breaking this action into smaller, safer steps")

        if result.base_result.risk_level == RiskLevel.HIGH:
            recommendations.append("Schedule peer review before proceeding with this action")

        if len(result.contextual_insights) > 5:
            recommendations.append("High complexity detected: consider architectural consultation")

        # Time-based recommendations
        if factors.time_constraints and result.execution_time_seconds > factors.time_constraints * 0.5:
            recommendations.append("Analysis taking significant time: consider caching results")

        return recommendations

    def _calculate_confidence_score(self, result: AnalysisResult, factors: ContextualFactors) -> float:
        """Calculate confidence score for the analysis."""
        base_confidence = 0.5

        # Adjust based on analysis depth
        depth_bonus = {
            AnalysisDepth.SURFACE: 0.0,
            AnalysisDepth.CONTEXTUAL: 0.2,
            AnalysisDepth.DEEP: 0.3,
            AnalysisDepth.COMPREHENSIVE: 0.4,
        }

        base_confidence += depth_bonus.get(result.analysis_depth, 0.0)

        # Adjust based on agent experience
        if factors.agent_experience == "expert":
            base_confidence += 0.1
        elif factors.agent_experience == "novice":
            base_confidence -= 0.1

        # Adjust based on insights quality
        insight_quality = min(1.0, len(result.contextual_insights) / 10.0)
        base_confidence += insight_quality * 0.2

        # Adjust based on historical success
        base_confidence += (factors.historical_success_rate - 0.5) * 0.2

        return max(0.0, min(1.0, base_confidence))

    def _extract_relevant_domains(self, context: ArchitecturalContext) -> List[str]:
        """Extract relevant domains from context."""
        domains = []

        # Extract from target modules
        for module in context.target_modules:
            if "database" in module.lower():
                domains.append("database")
            elif "api" in module.lower():
                domains.append("api")
            elif "ui" in module.lower():
                domains.append("ui")
            elif "security" in module.lower():
                domains.append("security")

        return list(set(domains))

    def _record_agent_context(self, context: ArchitecturalContext) -> None:
        """Record agent context for learning."""
        agent_id = context.session_id.split("_")[0]  # Extract agent identifier
        self.agent_context_history[agent_id].append(context)

        # Limit history size
        if len(self.agent_context_history[agent_id]) > 100:
            self.agent_context_history[agent_id] = self.agent_context_history[agent_id][-50:]

    def _update_context_learning(self, context: ArchitecturalContext, result: AnalysisResult) -> None:
        """Update context learning models."""
        agent_id = context.session_id.split("_")[0]

        # Update effectiveness based on confidence and success indicators
        effectiveness = result.confidence_score
        if result.base_result.approved and result.base_result.risk_level != RiskLevel.CRITICAL:
            effectiveness += 0.1

        self.context_effectiveness[str(context)] = effectiveness

    def get_context_statistics(self) -> Dict[str, Any]:
        """Get contextual intelligence statistics."""
        return {
            "total_agents": len(self.agent_context_history),
            "total_contexts_analyzed": sum(len(contexts) for contexts in self.agent_context_history.values()),
            "average_effectiveness": sum(self.context_effectiveness.values())
            / len(self.context_effectiveness)
            if self.context_effectiveness
            else 0.0,
            "cache_statistics": self.cache.get_statistics(),
        }
