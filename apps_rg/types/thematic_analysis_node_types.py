"""
[SSOT] K.0 Thematic Analysis Node.
Extracted from v61.27.10 legacy patterns.
Provides foundational 'Authenticity Patterns' and 'Competitive Intelligence'
before generation begins.
"""

from dataclasses import dataclass
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class AuthenticityPatterns:
    """Authentic language patterns extracted from domain analysis."""

    executive_summary_patterns: list[str]
    achievement_verb_patterns: list[str]
    metric_presentation_patterns: list[str]
    competency_phrasing_patterns: list[str]


@dataclass
class CompetitiveIntelligence:
    """Competitive intelligence from peer job descriptions."""

    peer_jds_analyzed: list[str]
    table_stakes_keywords: list[str]
    differentiator_keywords: list[str]


@dataclass
class ThematicAnalysisOutput:
    """Output from K.0 thematic analysis."""

    primary_theme: str
    secondary_themes: list[str]
    authenticity_patterns: AuthenticityPatterns
    competitive_intelligence: CompetitiveIntelligence
    company_name: str


class ThematicAnalysisNode:
    """
    K.0: Agentic Thematic Resonance Analysis + LinkedIn Authenticity.
    Foundational dependency for all downstream generation nodes.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        # Configuration derived from legacy v61.27.10
        self.linkedin_config = {
            "minimum_profiles": 10,
            "authenticity_transformation": {
                "avoid": ["Expert in", "Skilled in"],
                "prefer": ["Built", "Engineered", "Spearheaded"],
            },
        }

    def __call__(self, job_description: str, company_name: str) -> ThematicAnalysisOutput:
        """
        Execute thematic analysis using functor pattern.
        """
        return self.analyze_thematic_resonance(job_description, company_name)

    def analyze_thematic_resonance(self, job_description: str, company_name: str) -> ThematicAnalysisOutput:
        """
        Perform comprehensive thematic analysis.
        In a full implementation, this would use Agentic RAG.
        Current implementation uses heuristic logic for immediate integration.
        """
        # 1. Extract Themes
        primary, secondary = self._extract_themes(job_description)

        # 2. Analyze Authenticity (Mocked for immediate integration)
        authenticity = AuthenticityPatterns(
            executive_summary_patterns=["Built and scaled", "Led transformation"],
            achievement_verb_patterns=["Spearheaded", "Engineered", "Optimized"],
            metric_presentation_patterns=["resulting in X% improvement"],
            competency_phrasing_patterns=["Specialized in", "Proficient with"],
        )

        # 3. Gather Competitive Intel
        comp_intel = CompetitiveIntelligence(
            peer_jds_analyzed=[f"Competitor to {company_name}"],
            table_stakes_keywords=["leadership", "strategy"],
            differentiator_keywords=["innovation", "scale"],
        )

        return ThematicAnalysisOutput(
            primary_theme=primary,
            secondary_themes=secondary,
            authenticity_patterns=authenticity,
            competitive_intelligence=comp_intel,
            company_name=company_name,
        )

    def _extract_themes(self, jd: str) -> tuple[str, list[str]]:
        """Simple heuristic theme extraction."""
        jd_lower = jd.lower()
        if "engineer" in jd_lower or "developer" in jd_lower:
            return "Engineering Excellence", ["System Architecture", "Scalability"]
        if "manager" in jd_lower or "lead" in jd_lower:
            return "Strategic Leadership", ["Team Building", "Operational Efficiency"]
        return "Professional Impact", ["Execution", "Delivery"]
