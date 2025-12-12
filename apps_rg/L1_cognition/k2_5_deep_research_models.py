from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ResearchHopPhase(str, Enum):
    FINANCIAL_STRATEGIC = "financial_strategic"
    TECHNICAL_PRODUCT = "technical_product"
    ORGANIZATIONAL_LEADERSHIP = "organizational_leadership"


class ValidationRejectionReason(str, Enum):
    UNBOUND_METRICS = "unbound_metrics"
    FLUFF_LANGUAGE = "fluff_language"
    ORPHANED_CLAIMS = "orphaned_claims"
    MISSING_CITATIONS = "missing_citations"
    INSUFFICIENT_DEPTH = "insufficient_depth"


@dataclass
class ExecutiveProfile:
    name: str
    title: str
    ownership: str
    strategic_focus: Optional[str] = None
    linkedin_url: Optional[str] = None


@dataclass
class FinancialMetric:
    metric_name: str
    value: str
    period: str
    yoy_change: Optional[str] = None
    source_citation: str
    
    def validate(self) -> bool:
        return bool(self.metric_name and self.value and self.source_citation)


@dataclass
class TechnicalImplementation:
    technology_name: str
    implementation_details: str
    performance_gain: Optional[str] = None
    source_citation: str
    
    def validate(self) -> bool:
        return bool(self.technology_name and self.implementation_details and self.source_citation)


@dataclass
class StrategicLayer:
    core_thesis: str
    financial_proof_points: List[FinancialMetric] = field(default_factory=list)
    strategic_initiatives: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        if not self.core_thesis or len(self.core_thesis) < 20:
            return False
        if len(self.financial_proof_points) < 2:
            return False
        return all(metric.validate() for metric in self.financial_proof_points)


@dataclass
class TechnicalLayer:
    key_technologies: List[TechnicalImplementation] = field(default_factory=list)
    infrastructure_stack: List[str] = field(default_factory=list)
    implementation_summary: Optional[str] = None
    
    def validate(self) -> bool:
        if len(self.key_technologies) < 2:
            return False
        return all(tech.validate() for tech in self.key_technologies)


@dataclass
class LeadershipLayer:
    key_executives: List[ExecutiveProfile] = field(default_factory=list)
    organizational_structure: Optional[str] = None
    
    def validate(self) -> bool:
        if len(self.key_executives) < 2:
            return False
        return all(exec.name and exec.title and exec.ownership for exec in self.key_executives)


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
    company_name: str
    strategic_layer: StrategicLayer
    technical_layer: TechnicalLayer
    leadership_layer: LeadershipLayer
    citation_map: CitationMap
    research_timestamp: Optional[str] = None
    
    def validate(self) -> bool:
        return (
            self.strategic_layer.validate() and
            self.technical_layer.validate() and
            self.leadership_layer.validate() and
            self.citation_map.validate()
        )
    
    def to_dict(self) -> Dict:
        return {
            "company_name": self.company_name,
            "strategic_layer": {
                "core_thesis": self.strategic_layer.core_thesis,
                "financial_proof_points": [
                    {
                        "metric_name": m.metric_name,
                        "value": m.value,
                        "period": m.period,
                        "yoy_change": m.yoy_change,
                        "source_citation": m.source_citation
                    }
                    for m in self.strategic_layer.financial_proof_points
                ],
                "strategic_initiatives": self.strategic_layer.strategic_initiatives
            },
            "technical_layer": {
                "key_technologies": [
                    {
                        "technology_name": t.technology_name,
                        "implementation_details": t.implementation_details,
                        "performance_gain": t.performance_gain,
                        "source_citation": t.source_citation
                    }
                    for t in self.technical_layer.key_technologies
                ],
                "infrastructure_stack": self.technical_layer.infrastructure_stack,
                "implementation_summary": self.technical_layer.implementation_summary
            },
            "leadership_layer": {
                "key_executives": [
                    {
                        "name": e.name,
                        "title": e.title,
                        "ownership": e.ownership,
                        "strategic_focus": e.strategic_focus,
                        "linkedin_url": e.linkedin_url
                    }
                    for e in self.leadership_layer.key_executives
                ],
                "organizational_structure": self.leadership_layer.organizational_structure
            },
            "citation_map": self.citation_map.citations,
            "research_timestamp": self.research_timestamp
        }


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
