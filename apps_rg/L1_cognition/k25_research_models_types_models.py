"""Dataclass models for k25_research_models_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .k25_research_models_types_enums import *

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
        return all((metric.validate() for metric in self.financial_proof_points))

@dataclass
class TechnicalLayer:
    key_technologies: List[TechnicalImplementation] = field(default_factory=list)
    infrastructure_stack: List[str] = field(default_factory=list)
    implementation_summary: Optional[str] = None

    def validate(self) -> bool:
        if len(self.key_technologies) < 2:
            return False
        return all((tech.validate() for tech in self.key_technologies))

