"""Capability Gap Analyzer for Agent Improvement.

Phase 4 - Pillar 5: Capability Maturity (Self-Evolving System)
Analyzes failures and recommends new tools or sub-agents to fill capability gaps.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class CapabilityGapType(Enum):
    """Types of capability gaps."""
    MISSING_TOOL = "missing_tool"
    INSUFFICIENT_KNOWLEDGE = "insufficient_knowledge"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    REASONING_LIMITATION = "reasoning_limitation"
    INTEGRATION_FAILURE = "integration_failure"


class RecommendationType(Enum):
    """Types of recommendations."""
    ADD_TOOL = "add_tool"
    ADD_SUB_AGENT = "add_sub_agent"
    RETRAIN_AGENT = "retrain_agent"
    UPDATE_KNOWLEDGE = "update_knowledge"
    OPTIMIZE_PERFORMANCE = "optimize_performance"


@dataclass
class CapabilityGap:
    """Identified capability gap."""
    gap_id: str
    gap_type: CapabilityGapType
    description: str
    affected_scenarios: List[str]
    failure_count: int
    severity: float
    evidence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type.value,
            "description": self.description,
            "affected_scenarios": self.affected_scenarios,
            "failure_count": self.failure_count,
            "severity": self.severity,
            "evidence": self.evidence,
        }


@dataclass
class Recommendation:
    """Improvement recommendation."""
    recommendation_id: str
    recommendation_type: RecommendationType
    title: str
    description: str
    addresses_gaps: List[str]
    priority: float
    implementation_steps: List[str] = field(default_factory=list)
    estimated_impact: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "recommendation_type": self.recommendation_type.value,
            "title": self.title,
            "description": self.description,
            "addresses_gaps": self.addresses_gaps,
            "priority": self.priority,
            "implementation_steps": self.implementation_steps,
            "estimated_impact": self.estimated_impact,
        }


@dataclass
class AnalysisReport:
    """Capability gap analysis report."""
    report_id: str
    agent_id: str
    gaps_identified: List[CapabilityGap]
    recommendations: List[Recommendation]
    overall_health_score: float
    analysis_timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "agent_id": self.agent_id,
            "gaps_identified": [g.to_dict() for g in self.gaps_identified],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "overall_health_score": self.overall_health_score,
            "analysis_timestamp": self.analysis_timestamp,
        }


class CapabilityAnalyzer:
    """Analyzes capability gaps and generates improvement recommendations.
    
    Features:
    - Failure pattern analysis
    - Capability gap identification
    - Tool/sub-agent recommendations
    - Retraining suggestions
    - Impact estimation
    """
    
    def __init__(self, enable_logging: bool = True):
        """Initialize capability analyzer.
        
        Args:
            enable_logging: Enable logging
        """
        self.enable_logging = enable_logging
        
        self._gap_history: Dict[str, List[CapabilityGap]] = {}
        self._recommendation_history: Dict[str, List[Recommendation]] = {}
        
        if self.enable_logging:
            logger.info("capability_analyzer_initialized")
    
    def analyze_failures(
        self,
        agent_id: str,
        failure_reports: List[Dict[str, Any]],
    ) -> List[CapabilityGap]:
        """Analyze failure reports to identify capability gaps.
        
        Args:
            agent_id: Agent identifier
            failure_reports: List of failure reports
            
        Returns:
            List of identified capability gaps
        """
        gaps: List[CapabilityGap] = []
        
        # Group failures by pattern
        failure_patterns = self._identify_failure_patterns(failure_reports)
        
        # Analyze each pattern
        for pattern_type, pattern_failures in failure_patterns.items():
            gap = self._create_gap_from_pattern(
                agent_id=agent_id,
                pattern_type=pattern_type,
                failures=pattern_failures,
            )
            if gap:
                gaps.append(gap)
        
        # Store in history
        if agent_id not in self._gap_history:
            self._gap_history[agent_id] = []
        self._gap_history[agent_id].extend(gaps)
        
        if self.enable_logging:
            logger.info(
                "capability_gaps_identified",
                extra={
                    "agent_id": agent_id,
                    "gap_count": len(gaps),
                }
            )
        
        return gaps
    
    def generate_recommendations(
        self,
        agent_id: str,
        gaps: List[CapabilityGap],
    ) -> List[Recommendation]:
        """Generate improvement recommendations for capability gaps.
        
        Args:
            agent_id: Agent identifier
            gaps: Identified capability gaps
            
        Returns:
            List of recommendations
        """
        recommendations: List[Recommendation] = []
        
        for gap in gaps:
            recs = self._generate_recommendations_for_gap(gap)
            recommendations.extend(recs)
        
        # Prioritize recommendations
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        
        # Store in history
        if agent_id not in self._recommendation_history:
            self._recommendation_history[agent_id] = []
        self._recommendation_history[agent_id].extend(recommendations)
        
        if self.enable_logging:
            logger.info(
                "recommendations_generated",
                extra={
                    "agent_id": agent_id,
                    "recommendation_count": len(recommendations),
                }
            )
        
        return recommendations
    
    def create_analysis_report(
        self,
        agent_id: str,
        failure_reports: List[Dict[str, Any]],
    ) -> AnalysisReport:
        """Create complete capability gap analysis report.
        
        Args:
            agent_id: Agent identifier
            failure_reports: List of failure reports
            
        Returns:
            AnalysisReport
        """
        import time
        
        # Analyze failures
        gaps = self.analyze_failures(agent_id, failure_reports)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(agent_id, gaps)
        
        # Calculate health score
        health_score = self._calculate_health_score(gaps)
        
        report = AnalysisReport(
            report_id=f"analysis_{agent_id}_{int(time.time())}",
            agent_id=agent_id,
            gaps_identified=gaps,
            recommendations=recommendations,
            overall_health_score=health_score,
            analysis_timestamp=time.time(),
        )
        
        return report
    
    def _identify_failure_patterns(
        self,
        failure_reports: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Identify common failure patterns.
        
        Args:
            failure_reports: List of failure reports
            
        Returns:
            Dict mapping pattern type to failures
        """
        patterns: Dict[str, List[Dict[str, Any]]] = {}
        
        for report in failure_reports:
            error_type = report.get("error_type", "unknown")
            
            # Classify error type
            if "tool" in error_type.lower() or "not found" in error_type.lower():
                pattern_type = "missing_tool"
            elif "knowledge" in error_type.lower() or "unknown" in error_type.lower():
                pattern_type = "insufficient_knowledge"
            elif "timeout" in error_type.lower() or "slow" in error_type.lower():
                pattern_type = "performance"
            elif "reasoning" in error_type.lower() or "logic" in error_type.lower():
                pattern_type = "reasoning"
            else:
                pattern_type = "integration"
            
            if pattern_type not in patterns:
                patterns[pattern_type] = []
            patterns[pattern_type].append(report)
        
        return patterns
    
    def _create_gap_from_pattern(
        self,
        agent_id: str,
        pattern_type: str,
        failures: List[Dict[str, Any]],
    ) -> Optional[CapabilityGap]:
        """Create capability gap from failure pattern.
        
        Args:
            agent_id: Agent identifier
            pattern_type: Pattern type
            failures: Failures matching pattern
            
        Returns:
            CapabilityGap or None
        """
        import time
        
        if not failures:
            return None
        
        # Map pattern type to gap type
        gap_type_map = {
            "missing_tool": CapabilityGapType.MISSING_TOOL,
            "insufficient_knowledge": CapabilityGapType.INSUFFICIENT_KNOWLEDGE,
            "performance": CapabilityGapType.PERFORMANCE_DEGRADATION,
            "reasoning": CapabilityGapType.REASONING_LIMITATION,
            "integration": CapabilityGapType.INTEGRATION_FAILURE,
        }
        
        gap_type = gap_type_map.get(pattern_type, CapabilityGapType.INTEGRATION_FAILURE)
        
        # Extract affected scenarios
        scenarios = list(set(f.get("scenario_id", "unknown") for f in failures))
        
        # Calculate severity (0.0-1.0)
        severity = min(len(failures) / 10.0, 1.0)
        
        # Extract evidence
        evidence = [f.get("error_message", "") for f in failures[:5]]
        
        gap = CapabilityGap(
            gap_id=f"gap_{agent_id}_{pattern_type}_{int(time.time())}",
            gap_type=gap_type,
            description=f"{pattern_type.replace('_', ' ').title()} detected in {len(failures)} cases",
            affected_scenarios=scenarios,
            failure_count=len(failures),
            severity=severity,
            evidence=evidence,
        )
        
        return gap
    
    def _generate_recommendations_for_gap(
        self,
        gap: CapabilityGap,
    ) -> List[Recommendation]:
        """Generate recommendations for a specific gap.
        
        Args:
            gap: Capability gap
            
        Returns:
            List of recommendations
        """
        import time
        
        recommendations: List[Recommendation] = []
        
        if gap.gap_type == CapabilityGapType.MISSING_TOOL:
            rec = Recommendation(
                recommendation_id=f"rec_{gap.gap_id}_add_tool",
                recommendation_type=RecommendationType.ADD_TOOL,
                title="Add Missing Tool",
                description=f"Add tool to handle scenarios: {', '.join(gap.affected_scenarios[:3])}",
                addresses_gaps=[gap.gap_id],
                priority=gap.severity,
                implementation_steps=[
                    "Identify required tool functionality",
                    "Search tool registry or implement custom tool",
                    "Integrate tool with action plane",
                    "Test in Agent Gym",
                ],
                estimated_impact=0.8,
            )
            recommendations.append(rec)
        
        elif gap.gap_type == CapabilityGapType.INSUFFICIENT_KNOWLEDGE:
            rec = Recommendation(
                recommendation_id=f"rec_{gap.gap_id}_update_knowledge",
                recommendation_type=RecommendationType.UPDATE_KNOWLEDGE,
                title="Update Knowledge Base",
                description="Enhance knowledge base with missing information",
                addresses_gaps=[gap.gap_id],
                priority=gap.severity * 0.8,
                implementation_steps=[
                    "Identify knowledge gaps from failures",
                    "Source authoritative information",
                    "Update RAG knowledge base",
                    "Validate with golden datasets",
                ],
                estimated_impact=0.7,
            )
            recommendations.append(rec)
        
        elif gap.gap_type == CapabilityGapType.PERFORMANCE_DEGRADATION:
            rec = Recommendation(
                recommendation_id=f"rec_{gap.gap_id}_optimize",
                recommendation_type=RecommendationType.OPTIMIZE_PERFORMANCE,
                title="Optimize Performance",
                description="Improve response time and resource usage",
                addresses_gaps=[gap.gap_id],
                priority=gap.severity * 0.7,
                implementation_steps=[
                    "Profile execution bottlenecks",
                    "Optimize slow operations",
                    "Add caching where appropriate",
                    "Consider model routing for efficiency",
                ],
                estimated_impact=0.6,
            )
            recommendations.append(rec)
        
        elif gap.gap_type == CapabilityGapType.REASONING_LIMITATION:
            rec = Recommendation(
                recommendation_id=f"rec_{gap.gap_id}_retrain",
                recommendation_type=RecommendationType.RETRAIN_AGENT,
                title="Retrain Agent in Gym",
                description="Improve reasoning capabilities through training",
                addresses_gaps=[gap.gap_id],
                priority=gap.severity * 0.9,
                implementation_steps=[
                    "Create adversarial scenarios in Agent Gym",
                    "Run training sessions",
                    "Analyze performance improvements",
                    "Deploy if improvements validated",
                ],
                estimated_impact=0.75,
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _calculate_health_score(self, gaps: List[CapabilityGap]) -> float:
        """Calculate overall health score.
        
        Args:
            gaps: List of capability gaps
            
        Returns:
            Health score (0.0-1.0)
        """
        if not gaps:
            return 1.0
        
        # Weight by severity
        total_severity = sum(g.severity for g in gaps)
        avg_severity = total_severity / len(gaps)
        
        # Health score is inverse of severity
        health_score = 1.0 - min(avg_severity, 1.0)
        
        return health_score


def create_capability_analyzer() -> CapabilityAnalyzer:
    """Factory function to create capability analyzer.
    
    Returns:
        CapabilityAnalyzer instance
    """
    return CapabilityAnalyzer()
