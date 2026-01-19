from __future__ import annotations
"""Types and models for CapabilityAnalyzer."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)

class CapabilityGapType(Enum):
    """Types of capability gaps."""
    MISSING_TOOL: Any = 'missing_tool'
    INSUFFICIENT_KNOWLEDGE: Any = 'insufficient_knowledge'
    PERFORMANCE_DEGRADATION: Any = 'performance_degradation'
    REASONING_LIMITATION: Any = 'reasoning_limitation'
    INTEGRATION_FAILURE: Any = 'integration_failure'

class RecommendationType(Enum):
    """Types of recommendations."""
    ADD_TOOL: Any = 'add_tool'
    ADD_SUB_AGENT: Any = 'add_sub_agent'
    RETRAIN_AGENT: Any = 'retrain_agent'
    UPDATE_KNOWLEDGE: Any = 'update_knowledge'
    OPTIMIZE_PERFORMANCE: Any = 'optimize_performance'

@dataclass
class CapabilityGap:
    """Identified capability gap."""
    gap_id: str
    GapType: CapabilityGapType
    description: str
    affected_scenarios: List[str]
    failure_count: int
    Severity: float
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'gap_id': self.gap_id, 'GapType': self.GapType.value, 'description': self.description, 'affected_scenarios': self.affected_scenarios, 'failure_count': self.failure_count, 'Severity': self.Severity, 'evidence': self.evidence}

@dataclass
class Recommendation:
    """Improvement Recommendation."""
    recommendation_id: str
    RecommendationType: RecommendationType
    title: str
    description: str
    addresses_gaps: List[str]
    priority: float
    implementation_steps: List[str] = field(default_factory=list)
    estimated_impact: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'recommendation_id': self.recommendation_id, 'RecommendationType': self.RecommendationType.value, 'title': self.title, 'description': self.description, 'addresses_gaps': self.addresses_gaps, 'priority': self.priority, 'implementation_steps': self.implementation_steps, 'estimated_impact': self.estimated_impact}

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
        return {'report_id': self.report_id, 'agent_id': self.agent_id, 'gaps_identified': [g.to_dict() for g in self.gaps_identified], 'recommendations': [r.to_dict() for r in self.recommendations], 'overall_health_score': self.overall_health_score, 'analysis_timestamp': self.analysis_timestamp}