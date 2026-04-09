"""Explanation Generator - Architectural reasoning for agent decisions.

This module provides explanation generation capabilities that enable
agents to provide detailed architectural reasoning for their decisions.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from .contextual_engine import ContextualIntelligenceEngine, AnalysisResult, AnalysisDepth
from .collaborative_intelligence import CollaborationResult
from .predictive_analytics import PredictionResult, ImpactPrediction

logger = logging.getLogger(__name__)


class ExplanationType(Enum):
    """Types of explanations."""

    DECISION_RATIONALE = "decision_rationale"
    RISK_ASSESSMENT = "risk_assessment"
    ARCHITECTURAL_IMPLICATIONS = "architectural_implications"
    ALTERNATIVE_ANALYSIS = "alternative_analysis"
    COLLABORATIVE_JUSTIFICATION = "collaborative_justification"
    PREDICTIVE_FORECAST = "predictive_forecast"


class ExplanationDetail(Enum):
    """Levels of explanation detail."""

    SUMMARY = "summary"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    TECHNICAL = "technical"


@dataclass
class ExplanationComponent:
    """Component of an explanation."""

    component_type: str
    content: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    priority: int = 5  # 1-10, 10 being highest


@dataclass
class Explanation:
    """Complete explanation with multiple components."""

    explanation_type: ExplanationType
    title: str
    summary: str
    components: List[ExplanationComponent]
    confidence_score: float
    detail_level: ExplanationDetail
    generation_time_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExplanationGenerator:
    """Explanation generator for architectural reasoning."""

    def __init__(self, contextual_engine: ContextualIntelligenceEngine):
        """Initialize explanation generator.

        Args:
            contextual_engine: Contextual intelligence engine for analysis
        """
        self.contextual_engine = contextual_engine

        # Explanation templates
        self.explanation_templates = self._initialize_templates()

        # Evidence sources
        self.evidence_sources = [
            "architectural_analysis",
            "risk_assessment",
            "historical_data",
            "collaborative_insights",
            "predictive_models",
        ]

        logger.info("ExplanationGenerator initialized")

    def explain_decision(
        self,
        context: ArchitecturalContext,
        result: DecisionResult,
        detail_level: ExplanationDetail = ExplanationDetail.DETAILED,
    ) -> Explanation:
        """Generate explanation for a decision.

        Args:
            context: Architectural context for the decision
            result: Decision result to explain
            detail_level: Level of detail for the explanation

        Returns:
            Explanation with decision rationale
        """
        start_time = time.time()

        logger.info(f"Generating decision explanation for {context.action_type}")

        # Generate explanation components
        components = []

        # Decision rationale component
        rationale = self._generate_decision_rationale(context, result)
        components.append(rationale)

        # Risk assessment component
        if detail_level in [ExplanationDetail.DETAILED, ExplanationDetail.COMPREHENSIVE]:
            risk_assessment = self._generate_risk_assessment(context, result)
            components.append(risk_assessment)

        # Architectural implications component
        if detail_level == ExplanationDetail.COMPREHENSIVE:
            implications = self._generate_architectural_implications(context, result)
            components.append(implications)

        # Alternative analysis component
        if result.alternatives and detail_level != ExplanationDetail.SUMMARY:
            alternatives = self._generate_alternative_analysis(result)
            components.append(alternatives)

        # Calculate confidence
        confidence_score = self._calculate_explanation_confidence(components)

        # Generate summary
        summary = self._generate_summary(components)

        explanation = Explanation(
            explanation_type=ExplanationType.DECISION_RATIONALE,
            title=f"Decision Explanation: {context.action_type}",
            summary=summary,
            components=components,
            confidence_score=confidence_score,
            detail_level=detail_level,
            generation_time_seconds=time.time() - start_time,
            metadata={
                "action_type": context.action_type,
                "risk_level": result.risk_level.value,
                "approved": result.approved,
            },
        )

        return explanation

    def explain_analysis(
        self,
        context: ArchitecturalContext,
        analysis_result: AnalysisResult,
        detail_level: ExplanationDetail = ExplanationDetail.DETAILED,
    ) -> Explanation:
        """Generate explanation for contextual analysis.

        Args:
            context: Architectural context for the analysis
            analysis_result: Analysis result to explain
            detail_level: Level of detail for the explanation

        Returns:
            Explanation with analysis rationale
        """
        start_time = time.time()

        logger.info(f"Generating analysis explanation for depth {analysis_result.analysis_depth.value}")

        components = []

        # Analysis depth rationale
        depth_rationale = self._generate_depth_rationale(context, analysis_result)
        components.append(depth_rationale)

        # Contextual insights explanation
        if analysis_result.contextual_insights:
            insights_explanation = self._generate_insights_explanation(analysis_result)
            components.append(insights_explanation)

        # Confidence score explanation
        confidence_explanation = self._generate_confidence_explanation(analysis_result)
        components.append(confidence_explanation)

        # Context factors applied
        if analysis_result.context_factors_applied:
            factors_explanation = self._generate_factors_explanation(analysis_result)
            components.append(factors_explanation)

        confidence_score = self._calculate_explanation_confidence(components)
        summary = self._generate_summary(components)

        return Explanation(
            explanation_type=ExplanationType.ARCHITECTURAL_IMPLICATIONS,
            title=f"Analysis Explanation: {analysis_result.analysis_depth.value}",
            summary=summary,
            components=components,
            confidence_score=confidence_score,
            detail_level=detail_level,
            generation_time_seconds=time.time() - start_time,
            metadata={
                "analysis_depth": analysis_result.analysis_depth.value,
                "confidence": analysis_result.confidence_score,
            },
        )

    def explain_collaboration(
        self,
        context: ArchitecturalContext,
        collab_result: CollaborationResult,
        detail_level: ExplanationDetail = ExplanationDetail.DETAILED,
    ) -> Explanation:
        """Generate explanation for collaborative analysis.

        Args:
            context: Architectural context for the collaboration
            collab_result: Collaboration result to explain
            detail_level: Level of detail for the explanation

        Returns:
            Explanation with collaboration rationale
        """
        start_time = time.time()

        logger.info(
            f"Generating collaboration explanation with {len(collab_result.participating_agents)} agents"
        )

        components = []

        # Collaboration rationale
        collab_rationale = self._generate_collaboration_rationale(context, collab_result)
        components.append(collab_rationale)

        # Agent contributions
        if collab_result.collaborative_insights:
            contributions = self._generate_agent_contributions(collab_result)
            components.append(contributions)

        # Consensus explanation
        consensus_explanation = self._generate_consensus_explanation(collab_result)
        components.append(consensus_explanation)

        # Conflict resolution
        if collab_result.conflicts_detected:
            conflict_explanation = self._generate_conflict_explanation(collab_result)
            components.append(conflict_explanation)

        confidence_score = self._calculate_explanation_confidence(components)
        summary = self._generate_summary(components)

        return Explanation(
            explanation_type=ExplanationType.COLLABORATIVE_JUSTIFICATION,
            title=f"Collaboration Explanation: {len(collab_result.participating_agents)} agents",
            summary=summary,
            components=components,
            confidence_score=confidence_score,
            detail_level=detail_level,
            generation_time_seconds=time.time() - start_time,
            metadata={
                "participating_agents": len(collab_result.participating_agents),
                "consensus_reached": collab_result.consensus_reached,
                "confidence_boost": collab_result.confidence_boost,
            },
        )

    def explain_prediction(
        self,
        context: ArchitecturalContext,
        prediction_result: PredictionResult,
        detail_level: ExplanationDetail = ExplanationDetail.DETAILED,
    ) -> Explanation:
        """Generate explanation for predictive analysis.

        Args:
            context: Architectural context for the prediction
            prediction_result: Prediction result to explain
            detail_level: Level of detail for the explanation

        Returns:
            Explanation with predictive rationale
        """
        start_time = time.time()

        logger.info(f"Generating prediction explanation for {prediction_result.prediction_type.value}")

        components = []

        # Prediction methodology
        methodology = self._generate_prediction_methodology(prediction_result)
        components.append(methodology)

        # Scenario analysis
        if prediction_result.scenarios:
            scenario_explanation = self._generate_scenario_explanation(prediction_result)
            components.append(scenario_explanation)

        # Risk projection
        risk_projection = self._generate_risk_projection(prediction_result)
        components.append(risk_projection)

        # Recommendation rationale
        if prediction_result.recommendations:
            recommendation_rationale = self._generate_recommendation_rationale(prediction_result)
            components.append(recommendation_rationale)

        confidence_score = self._calculate_explanation_confidence(components)
        summary = self._generate_summary(components)

        return Explanation(
            explanation_type=ExplanationType.PREDICTIVE_FORECAST,
            title=f"Prediction Explanation: {prediction_result.prediction_type.value}",
            summary=summary,
            components=components,
            confidence_score=confidence_score,
            detail_level=detail_level,
            generation_time_seconds=time.time() - start_time,
            metadata={
                "prediction_type": prediction_result.prediction_type.value,
                "scenarios": len(prediction_result.scenarios),
                "confidence": prediction_result.confidence_score,
            },
        )

    def _generate_decision_rationale(
        self, context: ArchitecturalContext, result: DecisionResult
    ) -> ExplanationComponent:
        """Generate decision rationale component."""
        content_parts = []
        evidence = []

        # Base decision logic
        if result.approved:
            content_parts.append(
                f"The action '{context.action_type}' was approved based on architectural analysis."
            )
            content_parts.append(f"Risk assessment indicates {result.risk_level.value} risk level.")
        else:
            content_parts.append(
                f"The action '{context.action_type}' was blocked due to architectural concerns."
            )
            content_parts.append(
                f"Risk assessment indicates {result.risk_level.value} risk level exceeding acceptable thresholds."
            )

        # Add insights as evidence
        if result.insights:
            content_parts.append("Key architectural insights informed this decision:")
            for insight in result.insights:
                content_parts.append(f"- {insight}")
                evidence.append(insight)

        # Add warnings as evidence
        if result.warnings:
            content_parts.append("Risk factors considered:")
            for warning in result.warnings:
                content_parts.append(f"- {warning}")
                evidence.append(warning)

        return ExplanationComponent(
            component_type="decision_rationale",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.8,
            priority=10,
        )

    def _generate_risk_assessment(
        self, context: ArchitecturalContext, result: DecisionResult
    ) -> ExplanationComponent:
        """Generate risk assessment component."""
        content_parts = []
        evidence = []

        content_parts.append("Risk Assessment Details:")
        content_parts.append(f"Overall Risk Level: {result.risk_level.value}")

        # Risk factors analysis
        if result.risk_level == RiskLevel.CRITICAL:
            content_parts.append("Critical risks identified that could compromise system integrity:")
        elif result.risk_level == RiskLevel.HIGH:
            content_parts.append("High risks identified that require careful mitigation:")
        elif result.risk_level == RiskLevel.MEDIUM:
            content_parts.append("Medium risks identified that should be monitored:")
        else:
            content_parts.append("Low risks identified with minimal impact expected:")

        # Add specific risk factors
        for warning in result.warnings:
            content_parts.append(f"- {warning}")
            evidence.append(warning)

        return ExplanationComponent(
            component_type="risk_assessment",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.7,
            priority=8,
        )

    def _generate_architectural_implications(
        self, context: ArchitecturalContext, result: DecisionResult
    ) -> ExplanationComponent:
        """Generate architectural implications component."""
        content_parts = []
        evidence = []

        content_parts.append("Architectural Implications:")

        # Analyze target modules
        if context.target_modules:
            content_parts.append(f"Target modules affected: {', '.join(context.target_modules)}")

            # Module-specific implications
            for module in context.target_modules:
                if "spine" in module.lower():
                    content_parts.append(
                        f"- {module}: Critical spine component - high impact on system stability"
                    )
                    evidence.append("spine_component_impact")
                elif "gateway" in module.lower():
                    content_parts.append(f"- {module}: Gateway component - affects data flow patterns")
                    evidence.append("gateway_component_impact")
                else:
                    content_parts.append(f"- {module}: Standard component - localized impact expected")

        # Action-specific implications
        if context.action_type in ["delete_file", "remove_module"]:
            content_parts.append("Deletion action: Potential orphaned dependencies and breaking changes")
            evidence.append("deletion_risk")
        elif context.action_type in ["write_file", "create_module"]:
            content_parts.append("Creation action: New dependencies and integration points introduced")
            evidence.append("creation_impact")

        return ExplanationComponent(
            component_type="architectural_implications",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.6,
            priority=7,
        )

    def _generate_alternative_analysis(self, result: DecisionResult) -> ExplanationComponent:
        """Generate alternative analysis component."""
        content_parts = []
        evidence = []

        if not result.alternatives:
            content_parts.append("No alternative approaches were identified for this action.")
        else:
            content_parts.append("Alternative Approaches Considered:")

            for i, alt in enumerate(result.alternatives, 1):
                content_parts.append(f"{i}. {alt.get('description', 'Alternative approach')}")
                content_parts.append(f"   Type: {alt.get('type', 'Unknown')}")
                content_parts.append(f"   Impact: {alt.get('impact', 'Unknown')}")

                if alt.get("implementation"):
                    content_parts.append(f"   Implementation: {alt['implementation']}")
                    evidence.append(alt["implementation"])

        return ExplanationComponent(
            component_type="alternative_analysis",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.5,
            priority=6,
        )

    def _generate_depth_rationale(
        self, context: ArchitecturalContext, analysis_result: AnalysisResult
    ) -> ExplanationComponent:
        """Generate analysis depth rationale."""
        content_parts = []
        evidence = []

        content_parts.append(f"Analysis Depth: {analysis_result.analysis_depth.value}")
        content_parts.append("Depth selection rationale:")

        # Context factors that influenced depth
        if analysis_result.context_factors_applied:
            content_parts.append("Contextual factors applied:")
            for factor in analysis_result.context_factors_applied:
                content_parts.append(f"- {factor}")
                evidence.append(factor)

        # Progressive deepening explanation
        if analysis_result.analysis_depth != AnalysisDepth.SURFACE:
            content_parts.append("Progressive deepening was performed based on:")
            content_parts.append(f"- Risk level: {analysis_result.base_result.risk_level.value}")
            content_parts.append(f"- Warning count: {len(analysis_result.base_result.warnings)}")
            content_parts.append(f"- Insights generated: {len(analysis_result.contextual_insights)}")

        return ExplanationComponent(
            component_type="depth_rationale",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.7,
            priority=8,
        )

    def _generate_insights_explanation(self, analysis_result: AnalysisResult) -> ExplanationComponent:
        """Generate insights explanation."""
        content_parts = []
        evidence = []

        if analysis_result.contextual_insights:
            content_parts.append("Contextual Insights Generated:")

            for insight in analysis_result.contextual_insights:
                content_parts.append(f"- {insight}")
                evidence.append(insight)
        else:
            content_parts.append("No additional contextual insights were generated beyond the base analysis.")

        return ExplanationComponent(
            component_type="insights_explanation",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.6,
            priority=5,
        )

    def _generate_confidence_explanation(self, analysis_result: AnalysisResult) -> ExplanationComponent:
        """Generate confidence score explanation."""
        content_parts = []
        evidence = []

        content_parts.append(f"Confidence Score: {analysis_result.confidence_score:.2f}")
        content_parts.append("Confidence factors:")

        # Analysis depth contribution
        depth_contribution = {
            AnalysisDepth.SURFACE: 0.0,
            AnalysisDepth.CONTEXTUAL: 0.2,
            AnalysisDepth.DEEP: 0.3,
            AnalysisDepth.COMPREHENSIVE: 0.4,
        }

        depth_contrib = depth_contribution.get(analysis_result.analysis_depth, 0.0)
        content_parts.append(f"- Analysis depth: +{depth_contrib:.1f}")
        evidence.append(f"depth_{analysis_result.analysis_depth.value}")

        # Insight quality contribution
        if analysis_result.contextual_insights:
            insight_contrib = min(0.1, len(analysis_result.contextual_insights) * 0.02)
            content_parts.append(f"- Insight quality: +{insight_contrib:.1f}")
            evidence.append("insight_quality")

        return ExplanationComponent(
            component_type="confidence_explanation",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.8,
            priority=6,
        )

    def _generate_factors_explanation(self, analysis_result: AnalysisResult) -> ExplanationComponent:
        """Generate context factors explanation."""
        content_parts = []
        evidence = []

        content_parts.append("Context Factors Applied:")

        for factor in analysis_result.context_factors_applied:
            content_parts.append(f"- {factor}")
            evidence.append(factor)

        return ExplanationComponent(
            component_type="factors_explanation",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.7,
            priority=5,
        )

    def _generate_collaboration_rationale(
        self, context: ArchitecturalContext, collab_result: CollaborationResult
    ) -> ExplanationComponent:
        """Generate collaboration rationale."""
        content_parts = []
        evidence = []

        content_parts.append(f"Collaborative Analysis with {len(collab_result.participating_agents)} agents")
        content_parts.append("Collaboration enhanced the analysis through:")

        if collab_result.confidence_boost > 0:
            content_parts.append(f"- Confidence boost: +{collab_result.confidence_boost:.2f}")
            evidence.append("confidence_boost")

        if collab_result.collaborative_insights:
            content_parts.append(f"- Additional insights: {len(collab_result.collaborative_insights)}")
            evidence.append("collaborative_insights")

        if collab_result.consensus_reached:
            content_parts.append("- Consensus achieved among participating agents")
            evidence.append("consensus_achieved")

        return ExplanationComponent(
            component_type="collaboration_rationale",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.8,
            priority=9,
        )

    def _generate_agent_contributions(self, collab_result: CollaborationResult) -> ExplanationComponent:
        """Generate agent contributions explanation."""
        content_parts = []
        evidence = []

        content_parts.append("Agent Contributions:")

        for insight in collab_result.collaborative_insights:
            content_parts.append(f"- {insight}")
            evidence.append(insight)

        return ExplanationComponent(
            component_type="agent_contributions",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.6,
            priority=6,
        )

    def _generate_consensus_explanation(self, collab_result: CollaborationResult) -> ExplanationComponent:
        """Generate consensus explanation."""
        content_parts = []
        evidence = []

        if collab_result.consensus_reached:
            content_parts.append("Consensus was reached among collaborating agents.")
            evidence.append("consensus_positive")
        else:
            content_parts.append("Consensus was not reached. Coordination actions were taken:")
            for action in collab_result.coordination_actions:
                content_parts.append(f"- {action}")
                evidence.append(action)

        return ExplanationComponent(
            component_type="consensus_explanation",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.7,
            priority=7,
        )

    def _generate_conflict_explanation(self, collab_result: CollaborationResult) -> ExplanationComponent:
        """Generate conflict explanation."""
        content_parts = []
        evidence = []

        content_parts.append("Conflicts Detected and Resolved:")

        for conflict in collab_result.conflicts_detected:
            content_parts.append(
                f"- {conflict.get('type', 'Unknown conflict')}: {conflict.get('details', 'No details')}"
            )
            evidence.append(str(conflict))

        if collab_result.coordination_actions:
            content_parts.append("Resolution actions:")
            for action in collab_result.coordination_actions:
                content_parts.append(f"- {action}")
                evidence.append(action)

        return ExplanationComponent(
            component_type="conflict_explanation",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.6,
            priority=5,
        )

    def _generate_prediction_methodology(self, prediction_result: PredictionResult) -> ExplanationComponent:
        """Generate prediction methodology explanation."""
        content_parts = []
        evidence = []

        content_parts.append(f"Prediction Methodology: {prediction_result.prediction_type.value}")
        content_parts.append("Data sources used:")

        for source in prediction_result.data_sources:
            content_parts.append(f"- {source}")
            evidence.append(source)

        content_parts.append(f"Prediction confidence: {prediction_result.confidence_score:.2f}")

        return ExplanationComponent(
            component_type="prediction_methodology",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.8,
            priority=9,
        )

    def _generate_scenario_explanation(self, prediction_result: PredictionResult) -> ExplanationComponent:
        """Generate scenario explanation."""
        content_parts = []
        evidence = []

        content_parts.append("Scenario Analysis:")

        for scenario in prediction_result.scenarios:
            content_parts.append(f"- {scenario.description}")
            content_parts.append(f"  Type: {scenario.scenario_type.value}")
            content_parts.append(f"  Probability: {scenario.probability:.2f}")
            content_parts.append(f"  Confidence: {scenario.confidence:.2f}")

            # Add outcome if available
            if scenario.description in prediction_result.outcomes:
                outcome = prediction_result.outcomes[scenario.description]
                content_parts.append(f"  Predicted outcome: {outcome.get('approved', 'Unknown')}")
                evidence.append(f"scenario_{scenario.scenario_type.value}")

        return ExplanationComponent(
            component_type="scenario_explanation",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.7,
            priority=7,
        )

    def _generate_risk_projection(self, prediction_result: PredictionResult) -> ExplanationComponent:
        """Generate risk projection explanation."""
        content_parts = []
        evidence = []

        content_parts.append("Risk Projections:")

        for scenario_desc, risk_level in prediction_result.risk_assessments.items():
            content_parts.append(f"- {scenario_desc}: {risk_level.value} risk")
            evidence.append(f"risk_{scenario_desc}")

        return ExplanationComponent(
            component_type="risk_projection",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.6,
            priority=6,
        )

    def _generate_recommendation_rationale(self, prediction_result: PredictionResult) -> ExplanationComponent:
        """Generate recommendation rationale."""
        content_parts = []
        evidence = []

        if prediction_result.recommendations:
            content_parts.append("Recommendations:")
            for rec in prediction_result.recommendations:
                content_parts.append(f"- {rec}")
                evidence.append(rec)
        else:
            content_parts.append("No specific recommendations were generated.")

        return ExplanationComponent(
            component_type="recommendation_rationale",
            content="\n".join(content_parts),
            evidence=evidence,
            confidence=0.5,
            priority=5,
        )

    def _calculate_explanation_confidence(self, components: List[ExplanationComponent]) -> float:
        """Calculate overall confidence in the explanation."""
        if not components:
            return 0.0

        # Weight by priority
        total_weighted_confidence = 0.0
        total_weight = 0.0

        for component in components:
            weight = component.priority / 10.0  # Normalize priority to 0-1
            total_weighted_confidence += component.confidence * weight
            total_weight += weight

        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0

    def _generate_summary(self, components: List[ExplanationComponent]) -> str:
        """Generate summary from components."""
        if not components:
            return "No explanation components available."

        # Use highest priority component for summary
        primary_component = max(components, key=lambda c: c.priority)

        # Extract first few lines as summary
        lines = primary_component.content.split("\n")
        summary_lines = [line for line in lines if line.strip()][:3]

        return "\n".join(summary_lines)

    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize explanation templates."""
        return {
            "decision_approved": "The action was approved based on architectural analysis indicating acceptable risk levels.",
            "decision_blocked": "The action was blocked due to architectural concerns exceeding acceptable risk thresholds.",
            "risk_low": "Low risk level indicates minimal architectural impact.",
            "risk_medium": "Medium risk level requires monitoring and potential mitigation.",
            "risk_high": "High risk level requires careful planning and risk mitigation strategies.",
            "risk_critical": "Critical risk level indicates potential system integrity compromise.",
        }

    def format_explanation(self, explanation: Explanation, format_type: str = "markdown") -> str:
        """Format explanation for display.

        Args:
            explanation: Explanation to format
            format_type: Format type (markdown, plain, json)

        Returns:
            Formatted explanation string
        """
        if format_type == "markdown":
            return self._format_markdown(explanation)
        elif format_type == "plain":
            return self._format_plain(explanation)
        elif format_type == "json":
            return self._format_json(explanation)
        else:
            return str(explanation)

    def _format_markdown(self, explanation: Explanation) -> str:
        """Format explanation as markdown."""
        lines = []

        lines.append(f"# {explanation.title}")
        lines.append("")

        lines.append(f"**Summary:** {explanation.summary}")
        lines.append("")

        lines.append(f"**Confidence:** {explanation.confidence_score:.2f}")
        lines.append(f"**Detail Level:** {explanation.detail_level.value}")
        lines.append("")

        for component in explanation.components:
            lines.append(f"## {component.component_type.replace('_', ' ').title()}")
            lines.append("")

            for line in component.content.split("\n"):
                lines.append(line)

            if component.evidence:
                lines.append("**Evidence:**")
                for evidence in component.evidence:
                    lines.append(f"- {evidence}")

            lines.append("")

        return "\n".join(lines)

    def _format_plain(self, explanation: Explanation) -> str:
        """Format explanation as plain text."""
        lines = []

        lines.append(f"{explanation.title}")
        lines.append("=" * len(explanation.title))
        lines.append("")

        lines.append(f"Summary: {explanation.summary}")
        lines.append(f"Confidence: {explanation.confidence_score:.2f}")
        lines.append("")

        for component in explanation.components:
            lines.append(f"{component.component_type.upper()}:")
            lines.append(component.content)
            lines.append("")

        return "\n".join(lines)

    def _format_json(self, explanation: Explanation) -> str:
        """Format explanation as JSON."""
        import json

        return json.dumps(
            {
                "title": explanation.title,
                "summary": explanation.summary,
                "confidence_score": explanation.confidence_score,
                "detail_level": explanation.detail_level.value,
                "components": [
                    {
                        "type": comp.component_type,
                        "content": comp.content,
                        "evidence": comp.evidence,
                        "confidence": comp.confidence,
                        "priority": comp.priority,
                    }
                    for comp in explanation.components
                ],
                "metadata": explanation.metadata,
            },
            indent=2,
        )
