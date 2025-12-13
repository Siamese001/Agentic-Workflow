"""Types and models for capability_analyzer."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class CapabilityGapType(Enum):
    """Types of capability gaps."""
    MISSING_TOOL = 'missing_tool'
    INSUFFICIENT_KNOWLEDGE = 'insufficient_knowledge'
    PERFORMANCE_DEGRADATION = 'performance_degradation'
    REASONING_LIMITATION = 'reasoning_limitation'
    INTEGRATION_FAILURE = 'integration_failure'

class RecommendationType(Enum):
    """Types of recommendations."""
    ADD_TOOL = 'add_tool'
    ADD_SUB_AGENT = 'add_sub_agent'
    RETRAIN_AGENT = 'retrain_agent'
    UPDATE_KNOWLEDGE = 'update_knowledge'
    OPTIMIZE_PERFORMANCE = 'optimize_performance'

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
        return {'gap_id': self.gap_id, 'gap_type': self.gap_type.value, 'description': self.description, 'affected_scenarios': self.affected_scenarios, 'failure_count': self.failure_count, 'severity': self.severity, 'evidence': self.evidence}

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
        return {'recommendation_id': self.recommendation_id, 'recommendation_type': self.recommendation_type.value, 'title': self.title, 'description': self.description, 'addresses_gaps': self.addresses_gaps, 'priority': self.priority, 'implementation_steps': self.implementation_steps, 'estimated_impact': self.estimated_impact}

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
