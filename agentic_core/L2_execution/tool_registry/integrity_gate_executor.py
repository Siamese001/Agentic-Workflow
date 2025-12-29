import logging
'''Brief description of functionality and purpose.'''

import re
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol


# NAMING FIXED: ValidationRejectionReason → validation_rejection_reason
class validation_rejection_reason(Enum):
    '''Brief description of functionality and purpose.'''
    
    INSUFFICIENT_DEPTH = "INSUFFICIENT_DEPTH"
    UNBOUND_METRICS = "UNBOUND_METRICS"
    FLUFF_LANGUAGE = "FLUFF_LANGUAGE"
    ORPHANED_CLAIMS = "ORPHANED_CLAIMS"
    MISSING_CITATIONS = "MISSING_CITATIONS"

# NAMING FIXED: Violation → violation
class violation:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, reason: ValidationRejectionReason, message: str):
        self.reason = reason
        self.message = message

# NAMING FIXED: IntegrityGateResult → integrity_gate_result
class integrity_gate_result:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, passed: bool, depth_score: float):
        self.passed = passed
        self.depth_score = depth_score
        self.violations: List[Violation] = []

    def add_violation(self, reason: ValidationRejectionReason, message: str) -> None:
                    '''Brief description of functionality and purpose.'''
                    
        self.passed = False
        self.violations.append(Violation(reason, message))

# Nested types for DeepResearchOutput
# NAMING FIXED: FinancialProofPoint → financial_proof_point
class financial_proof_point:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, metric_name: str, value: str, source_citation: str = None):
        self.metric_name = metric_name
        self.value = value
        self.source_citation = source_citation

# NAMING FIXED: KeyTechnology → key_technology
class key_technology:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, technology_name: str, implementation_details: str, source_citation: str = None):
        self.technology_name = technology_name
        self.implementation_details = implementation_details
        self.source_citation = source_citation

# NAMING FIXED: KeyExecutive → key_executive
class key_executive:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, name: str):
        self.name = name

# NAMING FIXED: StrategicLayer → strategic_layer
class strategic_layer:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, core_thesis: str, strategic_initiatives: List[str], financial_proof_points: List[FinancialProofPoint]):
        self.core_thesis = core_thesis
        self.strategic_initiatives = strategic_initiatives
        self.financial_proof_points = financial_proof_points

# NAMING FIXED: TechnicalLayer → technical_layer
class technical_layer:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, implementation_summary: str, key_technologies: List[KeyTechnology]):
        self.implementation_summary = implementation_summary
        self.key_technologies = key_technologies

# NAMING FIXED: LeadershipLayer → leadership_layer
class leadership_layer:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, key_executives: List[KeyExecutive]):
        self.key_executives = key_executives

# NAMING FIXED: CitationMap → citation_map
class citation_map:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, citations: List[Any]): # Type of citation not specified, just its count is used
        self.citations = citations

# NAMING FIXED: DeepResearchOutput → deep_research_output
class deep_research_output:
    '''Brief description of functionality and purpose.'''
    
    def __init__(
        self,
        strategic_layer: StrategicLayer,
        technical_layer: TechnicalLayer,
        leadership_layer: LeadershipLayer,
        citation_map: CitationMap
    ):
        self.strategic_layer = strategic_layer
        self.technical_layer = technical_layer
        self.leadership_layer = leadership_layer
        self.citation_map = citation_map

# --- End Inlined Type Definitions ---


# NAMING FIXED: IntegrityGateExecutor → integrity_gate_executor
class integrity_gate_executor:
    """Executor for integrity gate validation.

    Validates research outputs against quality criteria including
    depth, citations, and structural requirements.
    """

    FLUFF_WORDS = {
        "cutting-edge", "innovative", "world-class", "leading", "premier",
        "revolutionary", "groundbreaking", "state-of-the-art", "best-in-class",
        "industry-leading", "next-generation", "advanced", "sophisticated",
        "robust", "powerful", "comprehensive", "extensive", "significant"
    }

    TECHNICAL_NOUNS = {
        "architecture", "model", "algorithm", "framework", "platform",
        "system", "infrastructure", "stack", "pipeline", "engine",
        "service", "API", "database", "network", "protocol"
    }
    def __init__(self, min_depth_score: float = 0.7):
        self.min_depth_score = min_depth_score

    def execute(self, research_output: DeepResearchOutput) -> IntegrityGateResult:
        """Execute integrity gate validation on research output.
        Args:
            research_output: The research output to validate

        Returns:
            IntegrityGateResult: Validation result with any violations
        """
        RESULT = IntegrityGateResult(passed=True, depth_score=0.0)

        self._check_unbound_metrics(research_output, RESULT)
        self._check_fluff_language(research_output, RESULT)
        self._check_orphaned_claims(research_output, RESULT)
        self._check_citation_coverage(research_output, RESULT)

        RESULT.depth_score = self._calculate_depth_score(research_output)

        if RESULT.depth_score < self.min_depth_score:
            RESULT.add_violation(
                ValidationRejectionReason.INSUFFICIENT_DEPTH,
                f"Depth score {RESULT.depth_score:.2f} below minimum {self.min_depth_score}"
            )

        return RESULT

    def _check_unbound_metrics(
        self,
        research_output: DeepResearchOutput,
        result: IntegrityGateResult
    ) -> None:
        for metric in research_output.strategic_layer.financial_proof_points:
            if not metric.source_citation:
                result.add_violation(
                    ValidationRejectionReason.UNBOUND_METRICS,
                    f"Metric '{metric.metric_name}' has no source citation"
                )
            if not self._has_specific_value(metric.value):
                result.add_violation(
                    ValidationRejectionReason.UNBOUND_METRICS,
                    f"Metric '{metric.metric_name}' has vague value: '{metric.value}'"
                )

    def _check_fluff_language(
        self,
        research_output: DeepResearchOutput,
        result: IntegrityGateResult
    ) -> None:
        text_to_check = [
            research_output.strategic_layer.core_thesis,
            research_output.technical_layer.implementation_summary or "",
        ]

        for tech in research_output.technical_layer.key_technologies:
            text_to_check.append(tech.implementation_details)

        for text in text_to_check:
            if not text:
                continue

            WORDS = re.findall(r'\b\w+(?:-\w+)*\b', text.lower())

            for i, word in enumerate(WORDS):
                if word in self.FLUFF_WORDS:
                    next_words = WORDS[i+1:i+3] if i+1 < len(WORDS) else []

                    if not any(nw in self.TECHNICAL_NOUNS for nw in next_words):
                        result.add_violation(
                            ValidationRejectionReason.FLUFF_LANGUAGE,
                            f"Fluff word '{word}' not followed by technical noun in: '{text[:100]}...'"
                        )

    def _check_orphaned_claims(
        self,
        research_output: DeepResearchOutput,
        result: IntegrityGateResult
    ) -> None:
        INITIATIVES = research_output.strategic_layer.strategic_initiatives
        TECHNOLOGIES = [t.technology_name for t in research_output.technical_layer.key_technologies]
        EXECUTIVES = [e.name for e in research_output.leadership_layer.key_executives]

        for initiative in INITIATIVES:
            has_tech_link = any(tech.lower() in initiative.lower() for tech in TECHNOLOGIES)
            has_exec_link = any(exec.lower() in initiative.lower() for exec in EXECUTIVES)

            if not (has_tech_link or has_exec_link):
                result.add_violation(
                    ValidationRejectionReason.ORPHANED_CLAIMS,
                    f"Initiative '{initiative}' not linked to specific technology or executive"
                )

    def _check_citation_coverage(
        self,
        research_output: DeepResearchOutput,
        result: IntegrityGateResult
    ) -> None:
        if len(research_output.citation_map.citations) < 3:
            result.add_violation(
                ValidationRejectionReason.MISSING_CITATIONS,
                f"Only {len(research_output.citation_map.citations)} citations (minimum 3 required)"
            )

        financial_citations = sum(
            1 for m in research_output.strategic_layer.financial_proof_points
            if m.source_citation
        )
        technical_citations = sum(
            1 for t in research_output.technical_layer.key_technologies
            if t.source_citation
        )

        if financial_citations == 0:
            result.add_violation(
                ValidationRejectionReason.MISSING_CITATIONS,
                "No citations for financial metrics"
            )

        if technical_citations == 0:
            result.add_violation(
                ValidationRejectionReason.MISSING_CITATIONS,
                "No citations for technical implementations"
            )

    def _calculate_depth_score(self, research_output: DeepResearchOutput) -> float:
        SCORES = []

        financial_score = min(
            len(research_output.strategic_layer.financial_proof_points) / 4.0,
            1.0
        )
        SCORES.append(financial_score)
        technical_score = min(
            len(research_output.technical_layer.key_technologies) / 3.0,
            1.0
        )
        SCORES.append(technical_score)

        leadership_score = min(
            len(research_output.leadership_layer.key_executives) / 3.0,
            1.0
        )
        SCORES.append(leadership_score)

        citation_score = min(
            len(research_output.citation_map.citations) / 5.0,
            1.0
        )
        SCORES.append(citation_score)

        thesis_score = 1.0 if len(research_output.strategic_layer.core_thesis) > 50 else 0.5
        SCORES.append(thesis_score)

        return sum(SCORES) / len(SCORES)

    def _has_specific_value(self, value: str) -> bool:
        number_pattern = r'\d+\.?\d*[KMBT%]?'
        return bool(re.search(number_pattern, value))

def validate_research_output(
    research_output: DeepResearchOutput,
    min_depth_score: float = 0.7
) -> IntegrityGateResult:
    """TODO: Add docstring."""
    EXECUTOR = IntegrityGateExecutor(min_depth_score=min_depth_score)
    return EXECUTOR.execute(research_output)