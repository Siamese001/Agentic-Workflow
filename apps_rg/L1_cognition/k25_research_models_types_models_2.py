"""Dataclass models for k25_research_models_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .k25_research_models_types_enums import *

@dataclass
class LeadershipLayer:
    key_executives: List[ExecutiveProfile] = field(default_factory=list)
    organizational_structure: Optional[str] = None

    def validate(self) -> bool:
        if len(self.key_executives) < 2:
            return False
        return all((exec.name and exec.title and exec.ownership for exec in self.key_executives))

@dataclass
class CitationMap:
    citations: Dict[str, str] = field(default_factory=dict)

    def add_citation(self, source_id: str, url: str) -> None:
        self.citations[source_id] = url

    def get_citation(self, source_id: str) -> Optional[str]:
        return self.citations.get(source_id)

    def validate(self) -> bool:
        return len(self.citations) >= 3

@dataclass
class DeepResearchOutput:
    """Output data structure for K.2.5 deep research results.
    
    Contains comprehensive research findings across strategic, technical,
    and organizational dimensions with proper citations.
    """
    company_name: str
    strategic_layer: StrategicLayer
    technical_layer: TechnicalLayer
    leadership_layer: LeadershipLayer
    citation_map: CitationMap
    research_timestamp: Optional[str] = None

    def validate(self) -> bool:
        return self.strategic_layer.validate() and self.technical_layer.validate() and self.leadership_layer.validate() and self.citation_map.validate()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the research output to a dictionary format.
        
        Returns:
            Dictionary representation of the research output
        """
        return {'company_name': self.company_name, 'strategic_layer': {'core_thesis': self.strategic_layer.core_thesis, 'financial_proof_points': [{'metric_name': m.metric_name, 'value': m.value, 'period': m.period, 'yoy_change': m.yoy_change, 'source_citation': m.source_citation} for m in self.strategic_layer.financial_proof_points], 'strategic_initiatives': self.strategic_layer.strategic_initiatives}, 'technical_layer': {'key_technologies': [{'technology_name': t.technology_name, 'implementation_details': t.implementation_details, 'performance_gain': t.performance_gain, 'source_citation': t.source_citation} for t in self.technical_layer.key_technologies], 'infrastructure_stack': self.technical_layer.infrastructure_stack, 'implementation_summary': self.technical_layer.implementation_summary}, 'leadership_layer': {'key_executives': [{'name': e.name, 'title': e.title, 'ownership': e.ownership, 'strategic_focus': e.strategic_focus, 'linkedin_url': e.linkedin_url} for e in self.leadership_layer.key_executives], 'organizational_structure': self.leadership_layer.organizational_structure}, 'citation_map': self.citation_map.citations, 'research_timestamp': self.research_timestamp}

@dataclass
class ResearchHopResult:
    phase: ResearchHopPhase
    query: str
    results: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class IntegrityGateResult:
    passed: bool
    rejection_reasons: List[ValidationRejectionReason] = field(default_factory=list)
    detailed_violations: List[str] = field(default_factory=list)
    depth_score: float = 0.0

    def add_violation(self, reason: ValidationRejectionReason, detail: str) -> None:
        self.rejection_reasons.append(reason)
        self.detailed_violations.append(detail)
        self.passed = False

