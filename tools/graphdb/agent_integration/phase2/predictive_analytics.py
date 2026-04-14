"""Predictive Analytics - What-if scenario analysis and architectural foresight.

This module provides predictive analytics capabilities that enable
agents to analyze potential outcomes and make informed decisions.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import statistics

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from .contextual_engine import ContextualIntelligenceEngine, AnalysisResult
from tqdm import tqdm

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of predictive analysis."""

    IMPACT_ANALYSIS = "impact_analysis"
    RISK_PROJECTION = "risk_projection"
    TREND_FORECASTING = "trend_forecasting"
    SCENARIO_SIMULATION = "scenario_simulation"
    OPTIMIZATION_RECOMMENDATION = "optimization_recommendation"


class ScenarioType(Enum):
    """Types of what-if scenarios."""

    BEST_CASE = "best_case"
    WORST_CASE = "worst_case"
    MOST_LIKELY = "most_likely"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"


@dataclass
class Scenario:
    """What-if scenario definition."""

    scenario_type: ScenarioType
    description: str
    parameters: Dict[str, Any]
    probability: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.0  # 0.0 to 1.0


@dataclass
class PredictionResult:
    """Result of predictive analysis."""

    prediction_type: PredictionType
    scenarios: List[Scenario]
    outcomes: Dict[str, Any]  # scenario_id -> outcome
    risk_assessments: Dict[str, RiskLevel]
    recommendations: List[str]
    confidence_score: float
    execution_time_seconds: float = 0.0
    data_sources: List[str] = field(default_factory=list)


@dataclass
class ImpactPrediction:
    """Prediction of architectural impact."""

    affected_modules: List[str]
    blast_radius: int
    risk_level: RiskLevel
    downstream_impact: Dict[str, float]  # module -> impact_score
    upstream_dependencies: List[str]
    ecosystem_implications: List[str]


@dataclass
class TrendAnalysis:
    """Analysis of architectural trends."""

    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0.0 to 1.0
    timeframe: str  # short_term, medium_term, long_term
    confidence: float
    influencing_factors: List[str]


class PredictiveAnalytics:
    """Predictive analytics engine for architectural foresight."""

    def __init__(self, contextual_engine: ContextualIntelligenceEngine):
        """Initialize predictive analytics engine.

        Args:
            contextual_engine: Contextual intelligence engine for base analysis
        """
        self.contextual_engine = contextual_engine

        # Historical data for trend analysis
        self.historical_predictions: List[PredictionResult] = []
        self.prediction_accuracy: Dict[str, float] = defaultdict(float)

        # Scenario templates
        self.scenario_templates = self._initialize_scenario_templates()

        # Impact models
        self.impact_models = {
            "module_change": self._predict_module_change_impact,
            "dependency_addition": self._predict_dependency_impact,
            "architectural_refactor": self._predict_refactor_impact,
            "performance_optimization": self._predict_optimization_impact,
        }

        logger.info("PredictiveAnalytics initialized")

    def analyze_impact(
        self, context: ArchitecturalContext, prediction_horizon: str = "medium_term"
    ) -> ImpactPrediction:
        """Analyze potential impact of proposed changes.

        Args:
            context: Architectural context for impact analysis
            prediction_horizon: Time horizon for impact prediction

        Returns:
            ImpactPrediction with detailed impact analysis
        """
        logger.info(f"Analyzing impact for {context.action_type} with horizon {prediction_horizon}")

        # Base impact analysis
        base_result = self.contextual_engine.analyze_with_context(context)

        # Predict affected modules
        affected_modules = self._predict_affected_modules(context, base_result)

        # Calculate blast radius
        blast_radius = len(affected_modules)

        # Assess downstream impact
        downstream_impact = self._calculate_downstream_impact(affected_modules, context)

        # Identify upstream dependencies
        upstream_dependencies = self._identify_upstream_dependencies(context)

        # Analyze ecosystem implications
        ecosystem_implications = self._analyze_ecosystem_implications(context, affected_modules)

        # Determine risk level
        risk_level = self._assess_impact_risk(blast_radius, downstream_impact, ecosystem_implications)

        return ImpactPrediction(
            affected_modules=affected_modules,
            blast_radius=blast_radius,
            risk_level=risk_level,
            downstream_impact=downstream_impact,
            upstream_dependencies=upstream_dependencies,
            ecosystem_implications=ecosystem_implications,
        )

    def run_scenario_analysis(
        self, context: ArchitecturalContext, scenarios: Optional[List[Scenario]] = None
    ) -> PredictionResult:
        """Run what-if scenario analysis.

        Args:
            context: Architectural context for scenario analysis
            scenarios: List of scenarios to analyze (None for default scenarios)

        Returns:
            PredictionResult with scenario outcomes and recommendations
        """
        start_time = time.time()

        logger.info(f"Running scenario analysis for {context.action_type}")

        # Use default scenarios if none provided
        if scenarios is None:
            scenarios = self._generate_default_scenarios(context)

        # Analyze each scenario
        outcomes = {}
        risk_assessments = {}

        for scenario in tqdm(scenarios, desc="Processing", unit="item"):
            scenario_context = self._apply_scenario_parameters(context, scenario)
            scenario_result = self.contextual_engine.analyze_with_context(scenario_context)

            outcomes[scenario.description] = {
                "approved": scenario_result.base_result.approved,
                "risk_level": scenario_result.base_result.risk_level.value,
                "insights": scenario_result.contextual_insights,
                "confidence": scenario_result.confidence_score,
            }

            risk_assessments[scenario.description] = scenario_result.base_result.risk_level

        # Generate recommendations
        recommendations = self._generate_scenario_recommendations(outcomes, risk_assessments)

        # Calculate overall confidence
        confidence_score = self._calculate_scenario_confidence(outcomes)

        result = PredictionResult(
            prediction_type=PredictionType.SCENARIO_SIMULATION,
            scenarios=scenarios,
            outcomes=outcomes,
            risk_assessments=risk_assessments,
            recommendations=recommendations,
            confidence_score=confidence_score,
            execution_time_seconds=time.time() - start_time,
            data_sources=["contextual_engine", "scenario_models"],
        )

        # Store for learning
        self.historical_predictions.append(result)

        return result

    def forecast_trends(
        self, context: ArchitecturalContext, trend_type: str = "architectural_complexity"
    ) -> TrendAnalysis:
        """Forecast architectural trends.

        Args:
            context: Architectural context for trend analysis
            trend_type: Type of trend to forecast

        Returns:
            TrendAnalysis with trend forecast and confidence
        """
        logger.info(f"Forecasting {trend_type} trends")

        # Analyze historical data
        historical_data = self._extract_historical_data(trend_type)

        # Calculate trend direction and strength
        trend_direction, trend_strength = self._calculate_trend_metrics(historical_data)

        # Determine timeframe
        timeframe = self._determine_trend_timeframe(context)

        # Calculate confidence
        confidence = self._calculate_trend_confidence(historical_data, trend_strength)

        # Identify influencing factors
        influencing_factors = self._identify_influencing_factors(context, trend_type)

        return TrendAnalysis(
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            timeframe=timeframe,
            confidence=confidence,
            influencing_factors=influencing_factors,
        )

    def optimize_recommendations(
        self, context: ArchitecturalContext, optimization_goal: str = "minimize_risk"
    ) -> PredictionResult:
        """Generate optimization recommendations.

        Args:
            context: Architectural context for optimization
            optimization_goal: Goal for optimization (minimize_risk, maximize_performance, etc.)

        Returns:
            PredictionResult with optimization recommendations
        """
        start_time = time.time()

        logger.info(f"Generating optimization recommendations for goal: {optimization_goal}")

        # Generate optimization scenarios
        optimization_scenarios = self._generate_optimization_scenarios(context, optimization_goal)

        # Analyze each optimization scenario
        outcomes = {}
        risk_assessments = {}

        for scenario in tqdm(optimization_scenarios, desc="Processing", unit="item"):
            scenario_context = self._apply_scenario_parameters(context, scenario)
            scenario_result = self.contextual_engine.analyze_with_context(scenario_context)

            outcomes[scenario.description] = {
                "approved": scenario_result.base_result.approved,
                "risk_level": scenario_result.base_result.risk_level.value,
                "insights": scenario_result.contextual_insights,
                "optimization_score": self._calculate_optimization_score(scenario_result, optimization_goal),
            }

            risk_assessments[scenario.description] = scenario_result.base_result.risk_level

        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(outcomes, optimization_goal)

        # Calculate confidence
        confidence_score = self._calculate_optimization_confidence(outcomes)

        return PredictionResult(
            prediction_type=PredictionType.OPTIMIZATION_RECOMMENDATION,
            scenarios=optimization_scenarios,
            outcomes=outcomes,
            risk_assessments=risk_assessments,
            recommendations=recommendations,
            confidence_score=confidence_score,
            execution_time_seconds=time.time() - start_time,
            data_sources=["contextual_engine", "optimization_models"],
        )

    def _predict_affected_modules(
        self, context: ArchitecturalContext, base_result: AnalysisResult
    ) -> List[str]:
        """Predict modules that will be affected by the change."""
        affected_modules = set(context.target_modules)

        # Add modules from blast radius analysis
        if "blast_radius" in str(base_result.contextual_insights):
            # Extract module names from insights
            for insight in base_result.contextual_insights:
                if "affect" in insight.lower() and "dependenc" in insight.lower():
                    # This would integrate with actual blast radius data
                    pass

        # Add related modules based on action type
        if context.action_type in ["write_file", "modify_module"]:
            # Look for modules that import or depend on target modules
            for module in context.target_modules:
                related = self._find_related_modules(module)
                affected_modules.update(related)

        return list(affected_modules)

    def _calculate_downstream_impact(
        self, affected_modules: List[str], context: ArchitecturalContext
    ) -> Dict[str, float]:
        """Calculate downstream impact scores for affected modules."""
        impact_scores = {}

        for module in tqdm(affected_modules, desc="Processing", unit="item"):
            # Base impact score
            base_score = 0.5

            # Adjust based on module importance
            if "core" in module.lower() or "critical" in module.lower():
                base_score += 0.3
            if "spine" in module.lower():
                base_score += 0.4

            # Adjust based on action type
            if context.action_type in ["delete_file", "remove_module"]:
                base_score += 0.2

            impact_scores[module] = min(1.0, base_score)

        return impact_scores

    def _identify_upstream_dependencies(self, context: ArchitecturalContext) -> List[str]:
        """Identify upstream dependencies for the context."""
        # This would integrate with dependency analysis
        # For now, return mock dependencies
        dependencies = []

        for module in context.target_modules:
            # Mock dependency identification
            if "database" in module.lower():
                dependencies.append("database_connection_pool")
            if "api" in module.lower():
                dependencies.append("api_gateway")

        return list(set(dependencies))

    def _analyze_ecosystem_implications(
        self, context: ArchitecturalContext, affected_modules: List[str]
    ) -> List[str]:
        """Analyze ecosystem-wide implications."""
        implications = []

        # Check for cross-system impacts
        if len(affected_modules) > 5:
            implications.append("Large-scale impact detected: potential ecosystem-wide effects")

        # Check for critical path impacts
        if any("spine" in module or "critical" in module for module in affected_modules):
            implications.append("Critical path impact: potential system stability concerns")

        # Check for performance implications
        if context.action_type in ["add_dependency", "import_module"]:
            implications.append("Dependency addition: potential performance implications")

        return implications

    def _assess_impact_risk(
        self, blast_radius: int, downstream_impact: Dict[str, float], ecosystem_implications: List[str]
    ) -> RiskLevel:
        """Assess overall risk level of the impact."""
        risk_score = 0.0

        # Blast radius contribution
        if blast_radius > 20:
            risk_score += 0.4
        elif blast_radius > 10:
            risk_score += 0.2
        elif blast_radius > 5:
            risk_score += 0.1

        # Downstream impact contribution
        avg_impact = statistics.mean(downstream_impact.values()) if downstream_impact else 0.0
        risk_score += avg_impact * 0.3

        # Ecosystem implications contribution
        if len(ecosystem_implications) > 2:
            risk_score += 0.3
        elif len(ecosystem_implications) > 0:
            risk_score += 0.1

        # Convert to risk level
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_default_scenarios(self, context: ArchitecturalContext) -> List[Scenario]:
        """Generate default what-if scenarios."""
        scenarios = []

        # Best case scenario
        scenarios.append(
            Scenario(
                scenario_type=ScenarioType.BEST_CASE,
                description="Best case - minimal impact, high success rate",
                parameters={"risk_tolerance": "high", "experience_level": "expert"},
                probability=0.2,
                confidence=0.7,
            )
        )

        # Worst case scenario
        scenarios.append(
            Scenario(
                scenario_type=ScenarioType.WORST_CASE,
                description="Worst case - maximum impact, low success rate",
                parameters={"risk_tolerance": "low", "experience_level": "novice"},
                probability=0.1,
                confidence=0.6,
            )
        )

        # Most likely scenario
        scenarios.append(
            Scenario(
                scenario_type=ScenarioType.MOST_LIKELY,
                description="Most likely - moderate impact, standard success rate",
                parameters={"risk_tolerance": "medium", "experience_level": "intermediate"},
                probability=0.6,
                confidence=0.8,
            )
        )

        return scenarios

    def _apply_scenario_parameters(
        self, context: ArchitecturalContext, scenario: Scenario
    ) -> ArchitecturalContext:
        """Apply scenario parameters to create modified context."""
        # Create a copy of the context
        modified_context = ArchitecturalContext(
            agent_type=context.agent_type,
            action_type=context.action_type,
            target_modules=context.target_modules.copy(),
            proposed_changes=context.proposed_changes.copy(),
            session_id=f"{context.session_id}_{scenario.scenario_type.value}",
        )

        # Apply scenario-specific modifications
        if scenario.parameters.get("risk_tolerance") == "high":
            # High risk tolerance - reduce perceived risk
            modified_context.proposed_changes["risk_adjustment"] = -0.2
        elif scenario.parameters.get("risk_tolerance") == "low":
            # Low risk tolerance - increase perceived risk
            modified_context.proposed_changes["risk_adjustment"] = 0.2

        return modified_context

    def _generate_scenario_recommendations(
        self, outcomes: Dict[str, Any], risk_assessments: Dict[str, RiskLevel]
    ) -> List[str]:
        """Generate recommendations based on scenario outcomes."""
        recommendations = []

        # Analyze scenario outcomes
        approved_scenarios = [desc for desc, outcome in outcomes.items() if outcome["approved"]]
        high_risk_scenarios = [
            desc for desc, risk in risk_assessments.items() if risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]

        # Generate recommendations
        if len(approved_scenarios) == 0:
            recommendations.append("No scenarios approved: action should be reconsidered")
        elif len(approved_scenarios) < len(outcomes):
            recommendations.append("Partial approval: consider risk mitigation strategies")

        if high_risk_scenarios:
            recommendations.append(f"High risk scenarios detected: {', '.join(high_risk_scenarios)}")

        # Recommend best scenario
        best_scenario = max(outcomes.items(), key=lambda x: x[1].get("confidence", 0))
        recommendations.append(f"Recommended scenario: {best_scenario[0]}")

        return recommendations

    def _calculate_scenario_confidence(self, outcomes: Dict[str, Any]) -> float:
        """Calculate confidence in scenario analysis."""
        if not outcomes:
            return 0.0

        confidences = [outcome.get("confidence", 0.5) for outcome in outcomes.values()]
        return statistics.mean(confidences)

    def _extract_historical_data(self, trend_type: str) -> List[float]:
        """Extract historical data for trend analysis."""
        # This would integrate with actual historical data
        # For now, return mock data
        return [0.5, 0.6, 0.7, 0.8, 0.9]  # Mock increasing trend

    def _calculate_trend_metrics(self, historical_data: List[float]) -> Tuple[str, float]:
        """Calculate trend direction and strength."""
        if len(historical_data) < 2:
            return "stable", 0.0

        # Calculate trend direction
        if historical_data[-1] > historical_data[0]:
            direction = "increasing"
        elif historical_data[-1] < historical_data[0]:
            direction = "decreasing"
        else:
            direction = "stable"

        # Calculate trend strength (simplified)
        if len(historical_data) > 1:
            change = abs(historical_data[-1] - historical_data[0])
            strength = min(1.0, change)
        else:
            strength = 0.0

        return direction, strength

    def _determine_trend_timeframe(self, context: ArchitecturalContext) -> str:
        """Determine appropriate timeframe for trend analysis."""
        # Based on action type and scope
        if len(context.target_modules) > 10:
            return "long_term"
        elif len(context.target_modules) > 3:
            return "medium_term"
        else:
            return "short_term"

    def _calculate_trend_confidence(self, historical_data: List[float], trend_strength: float) -> float:
        """Calculate confidence in trend analysis."""
        if len(historical_data) < 3:
            return 0.3  # Low confidence with limited data

        # Confidence increases with data points and trend strength
        data_confidence = min(1.0, len(historical_data) / 10.0)
        strength_confidence = trend_strength

        return (data_confidence + strength_confidence) / 2

    def _identify_influencing_factors(self, context: ArchitecturalContext, trend_type: str) -> List[str]:
        """Identify factors influencing the trend."""
        factors = []

        # Action-based factors
        if context.action_type in ["write_file", "create_module"]:
            factors.append("Code generation volume")
        elif context.action_type in ["refactor", "modify_module"]:
            factors.append("Refactoring frequency")

        # Module-based factors
        for module in context.target_modules:
            if "test" in module.lower():
                factors.append("Test coverage trends")
            if "performance" in module.lower():
                factors.append("Performance optimization trends")

        return list(set(factors))

    def _generate_optimization_scenarios(
        self, context: ArchitecturalContext, optimization_goal: str
    ) -> List[Scenario]:
        """Generate optimization scenarios."""
        scenarios = []

        if optimization_goal == "minimize_risk":
            scenarios.append(
                Scenario(
                    scenario_type=ScenarioType.CONSERVATIVE,
                    description="Conservative approach - minimize risk",
                    parameters={"risk_reduction": 0.3, "additional_validation": True},
                    probability=0.7,
                    confidence=0.8,
                )
            )

        elif optimization_goal == "maximize_performance":
            scenarios.append(
                Scenario(
                    scenario_type=ScenarioType.AGGRESSIVE,
                    description="Aggressive optimization - maximize performance",
                    parameters={"performance_boost": 0.4, "risk_acceptance": True},
                    probability=0.3,
                    confidence=0.6,
                )
            )

        return scenarios

    def _calculate_optimization_score(self, result: AnalysisResult, optimization_goal: str) -> float:
        """Calculate optimization score for a scenario."""
        base_score = 0.5

        if optimization_goal == "minimize_risk":
            if result.base_result.risk_level == RiskLevel.LOW:
                base_score += 0.4
            elif result.base_result.risk_level == RiskLevel.MEDIUM:
                base_score += 0.2
            elif result.base_result.risk_level == RiskLevel.HIGH:
                base_score -= 0.2

        elif optimization_goal == "maximize_performance":
            # This would integrate with performance metrics
            base_score += 0.1  # Mock performance boost

        return min(1.0, max(0.0, base_score))

    def _generate_optimization_recommendations(
        self, outcomes: Dict[str, Any], optimization_goal: str
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Find best optimization scenario
        best_scenario = max(outcomes.items(), key=lambda x: x[1].get("optimization_score", 0))

        recommendations.append(f"Optimal scenario: {best_scenario[0]}")
        recommendations.append(f"Optimization score: {best_scenario[1].get('optimization_score', 0):.2f}")

        # Add goal-specific recommendations
        if optimization_goal == "minimize_risk":
            recommendations.append("Implement additional validation steps")
            recommendations.append("Consider phased rollout approach")
        elif optimization_goal == "maximize_performance":
            recommendations.append("Monitor performance metrics closely")
            recommendations.append("Prepare rollback procedures")

        return recommendations

    def _calculate_optimization_confidence(self, outcomes: Dict[str, Any]) -> float:
        """Calculate confidence in optimization recommendations."""
        if not outcomes:
            return 0.0

        optimization_scores = [outcome.get("optimization_score", 0.5) for outcome in outcomes.values()]
        return statistics.mean(optimization_scores)

    def _find_related_modules(self, module: str) -> List[str]:
        """Find modules related to the given module."""
        # This would integrate with dependency analysis
        # For now, return mock related modules
        related = []

        if "database" in module.lower():
            related.append("database_schema")
            related.append("connection_pool")
        elif "api" in module.lower():
            related.append("api_gateway")
            related.append("authentication")

        return related

    def _predict_module_change_impact(self, context: ArchitecturalContext) -> Dict[str, Any]:
        """Predict impact of module changes."""
        return {"impact_type": "module_change", "severity": "medium"}

    def _predict_dependency_impact(self, context: ArchitecturalContext) -> Dict[str, Any]:
        """Predict impact of dependency changes."""
        return {"impact_type": "dependency", "severity": "high"}

    def _predict_refactor_impact(self, context: ArchitecturalContext) -> Dict[str, Any]:
        """Predict impact of refactoring."""
        return {"impact_type": "refactor", "severity": "medium"}

    def _predict_optimization_impact(self, context: ArchitecturalContext) -> Dict[str, Any]:
        """Predict impact of optimization."""
        return {"impact_type": "optimization", "severity": "low"}

    def _initialize_scenario_templates(self) -> Dict[str, Scenario]:
        """Initialize scenario templates."""
        return {
            "conservative": Scenario(
                scenario_type=ScenarioType.CONSERVATIVE,
                description="Conservative approach",
                parameters={"risk_tolerance": "low"},
                probability=0.5,
                confidence=0.8,
            ),
            "aggressive": Scenario(
                scenario_type=ScenarioType.AGGRESSIVE,
                description="Aggressive approach",
                parameters={"risk_tolerance": "high"},
                probability=0.3,
                confidence=0.6,
            ),
        }

    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Get predictive analytics statistics."""
        return {
            "total_predictions": len(self.historical_predictions),
            "average_confidence": sum(p.confidence_score for p in self.historical_predictions)
            / len(self.historical_predictions)
            if self.historical_predictions
            else 0.0,
            "accuracy_by_type": dict(self.prediction_accuracy),
            "available_scenarios": list(self.scenario_templates.keys()),
        }
