"""Dataclass models for k25_research_models_types."""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)
# from .k25_research_models_types_enums import *  # Star import removed

@dataclass
class ExecutiveProfile:
    """TODO: Add docstring."""

    name: str
    title: str
    ownership: str
    strategic_focus: Optional[str] = None
    linkedin_url: Optional[str] = None

@dataclass
    """TODO: Add docstring."""

class FinancialMetric:
    """Docstring."""
    metric_name: str
    value: str
    period: str
    yoy_change: Optional[str] = None
    source_citation: str
        """TODO: Add docstring."""


    def validate(self) -> bool:
        """Docstring."""
        return bool(self.metric_name and self.value and self.source_citation)

    """TODO: Add docstring."""

@dataclass
class TechnicalImplementation:
    """Docstring."""
    technology_name: str
    implementation_details: str
        """TODO: Add docstring."""

    performance_gain: Optional[str] = None
    source_citation: str

    def validate(self) -> bool:
        """Docstring."""
        return bool(self.technology_name and self.implementation_details and self.source_citation)
    """TODO: Add docstring."""


@dataclass
        """TODO: Add docstring."""

class StrategicLayer:
    """Docstring."""
    core_thesis: str
    financial_proof_points: List[FinancialMetric] = field(default_factory=list)
    strategic_initiatives: List[str] = field(default_factory=list)

    def validate(self) -> bool:
        """Docstring."""
        if not self.core_thesis or len(self.core_thesis) < 20:
            return False
        if len(self.financial_proof_points) < 2:
            return False
    """TODO: Add docstring."""

        return all((metric.validate() for metric in self.financial_proof_points))
        """TODO: Add docstring."""


@dataclass
class TechnicalLayer:
    """Docstring."""
    key_technologies: List[TechnicalImplementation] = field(default_factory=list)
    infrastructure_stack: List[str] = field(default_factory=list)
    implementation_summary: Optional[str] = None

    def validate(self) -> bool:
        """Docstring."""
        if len(self.key_technologies) < 2:
        """TODO: Add docstring."""

    """TODO: Add docstring."""

            return False
        return all((tech.validate() for tech in self.key_technologies))

@dataclass
class LeadershipLayer:
    """Docstring."""
    key_executives: List[ExecutiveProfile] = field(default_factory=list)
    organizational_structure: Optional[str] = None
        """TODO: Add docstring."""


    def validate(self) -> bool:
        """TODO: Add docstring."""

    """TODO: Add docstring."""

        if len(self.key_executives) < 2:
        """TODO: Add docstring."""

            return False
        return all((exec.name and exec.title and exec.ownership for exec in self.key_executives))

@dataclass
class CitationMap:
    """Docstring."""
    citations: Dict[str, str] = field(default_factory=dict)

    def add_citation(self, source_id: str, url: str) -> None:
        """Docstring."""
        self.citations[source_id] = url

    def get_citation(self, source_id: str) -> Optional[str]:
        """Docstring."""
        return self.citations.get(source_id)

    def validate(self) -> bool:
        """Docstring."""
        return len(self.citations) >= 3

        """TODO: Add docstring."""

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
        """Docstring."""
        return self.strategic_layer.validate() and self.technical_layer.validate() and self.leadersh
    ip_layer.validate() and self.citation_map.validate()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the research output to a dictionary format.

    """TODO: Add docstring."""

        Returns:
            Dictionary representation of the research output
        """
        return {'company_name': self.company_name, 'strategic_layer': {'core_thesis': self.strategic
    _layer.core_thesis, 'financial_proof_points': [{'metric_name': m.metric_name, 'value': m.value,
        'period': m.period, 'yoy_change': m.yoy_change, 'source_citation': m.source_citation} for m
            in self.strategic_layer.financial_proof_points], 'strategic_initiatives': self.strategic
                _layer.strategic_initiatives},
                    'technical_layer': {'key_technologies': [{'technology_name': t.technology_name,
                    'implementation_details': t.implementation_details,
                    'performance_gain': t.performance_gain,
                    'source_citation': t.
                        .source_citation} for t in self.
                        .technical_layer.
                        .key_technologies],
                    'infrastructure_stack': self.technical_layer.infrastructure_stack,
                    'implementation_summary': self.technical_layer.implementation_summary},
                    'leadership_layer': {'key_executives': [{'name': e.name,
                    'title': e.title,
                    'ownership': e.ownership,
                    'strategic_focus': e.strategic_focus,
                    'linkedin_url': e.linkedin_url} for e in self.leadership_layer.key_executives],
                    'organizational_structure': self.leadership_layer.organizational_structure},
                    'citation_map': self.citation_map.citations,
                    'research_timestamp': self.research_timestamp}

        """TODO: Add docstring."""

@dataclass
class ResearchHopResult:
    """Docstring."""
    phase: ResearchHopPhase
    """TODO: Add docstring."""

    query: str
    results: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class IntegrityGateResult:
    """Docstring."""
    passed: bool
    rejection_reasons: List[ValidationRejectionReason] = field(default_factory=list)
    detailed_violations: List[str] = field(default_factory=list)
    depth_score: float = 0.0

    def add_violation(self, reason: ValidationRejectionReason, detail: str) -> None:
        """Docstring."""
        self.rejection_reasons.append(reason)
        self.detailed_violations.append(detail)
        self.passed = False
