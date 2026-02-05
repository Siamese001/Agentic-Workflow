"""
Implementation Examples: Historical K-Node Patterns for Modern apps_rg

Based on analysis of 60+ versions of resume generation workflows (v1.0 through v61.27.10),
these implementations incorporate proven patterns from the legacy system.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# PATTERN 1: K.0 Thematic Analysis (Missing from Current apps_rg)
# ============================================================================


@dataclass
class AuthenticityPatterns:
    """Authentic language patterns extracted from LinkedIn profiles."""

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
    related_concepts: list[str]
    authenticity_patterns: AuthenticityPatterns
    competitive_intelligence: CompetitiveIntelligence
    company_name: str
    gics_sector: str
    gics_industry: str


class ThematicAnalysisNode:
    """
    K.0: Agentic Thematic Resonance Analysis + LinkedIn Authenticity + Competitive Intel

    This node provides the foundational thematic analysis that all other K-nodes depend on.
    Extracted from v61.27.10 legacy system with proven production reliability.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}

        # LinkedIn search strategy (from legacy v61.27.10)
        self.linkedin_search_config = {
            "target_profiles": "Senior executives in similar roles",
            "minimum_profiles": 10,
            "extraction_focus": [
                "opening_statements",
                "achievement_phrasing",
                "metric_presentation",
            ],
            "authenticity_transformation": {
                "avoid": ["Expert in machine learning and AI", "Skilled in software development"],
                "prefer": [
                    "Built production ML systems at scale",
                    "Led engineering teams that delivered",
                ],
            },
        }

        # Competitive analysis config
        self.competitive_config = {
            "minimum_peer_jds": 3,
            "table_stakes_threshold": 0.8,
            "differentiator_threshold": 0.2,
        }

    def __call__(self, job_description: str, company_name: str) -> ThematicAnalysisOutput:
        """
        Execute thematic analysis using functor pattern.

        Args:
            job_description: Job description text
            company_name: Target company name

        Returns:
            ThematicAnalysisOutput with comprehensive analysis
        """
        return self.analyze_thematic_resonance(job_description, company_name)

    def analyze_thematic_resonance(
        self, job_description: str, company_name: str
    ) -> ThematicAnalysisOutput:
        """
        Perform comprehensive thematic analysis.

        This mirrors the sophisticated analysis from v61.27.10 that includes:
        - Primary/secondary theme extraction
        - LinkedIn authenticity pattern mining
        - Competitive intelligence gathering
        """
        logger.info(f"Starting thematic analysis for {company_name}")

        # Extract primary and secondary themes
        primary_theme, secondary_themes = self._extract_themes(job_description)

        # Extract related concepts
        related_concepts = self._extract_related_concepts(job_description)

        # Perform LinkedIn authenticity analysis
        authenticity_patterns = self._analyze_linkedin_authenticity(job_description, company_name)

        # Gather competitive intelligence
        competitive_intel = self._gather_competitive_intelligence(job_description, company_name)

        # Classify industry/sector
        gics_sector, gics_industry = self._classify_company_industry(company_name, job_description)

        output = ThematicAnalysisOutput(
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            related_concepts=related_concepts,
            authenticity_patterns=authenticity_patterns,
            competitive_intelligence=competitive_intel,
            company_name=company_name,
            gics_sector=gics_sector,
            gics_industry=gics_industry,
        )

        logger.info(
            f"Thematic analysis complete: {primary_theme} with {len(secondary_themes)} secondary themes"
        )
        return output

    def _extract_themes(self, job_description: str) -> tuple[str, list[str]]:
        """Extract primary and secondary themes from job description."""
        # Simplified theme extraction - in production would use agentic RAG
        if "machine learning" in job_description.lower() or "ai" in job_description.lower():
            primary = "Artificial Intelligence & Machine Learning"
            secondary = ["Data Science", "Software Engineering", "Analytics"]
        elif "software engineer" in job_description.lower():
            primary = "Software Engineering & Development"
            secondary = ["System Architecture", "Team Leadership", "Technical Innovation"]
        else:
            primary = "Technology & Innovation"
            secondary = ["Digital Transformation", "Strategic Leadership"]

        return primary, secondary

    def _extract_related_concepts(self, job_description: str) -> list[str]:
        """Extract related concepts for content generation."""
        concepts = []
        jd_lower = job_description.lower()

        concept_keywords = {
            "cloud": ["cloud computing", "aws", "azure", "gcp"],
            "data": ["analytics", "big data", "data science", "ml"],
            "leadership": ["team management", "mentoring", "strategy", "vision"],
            "innovation": ["r&d", "product development", "emerging tech"],
        }

        for concept, keywords in concept_keywords.items():
            if any(kw in jd_lower for kw in keywords):
                concepts.append(concept.title())

        return concepts

    def _analyze_linkedin_authenticity(
        self, job_description: str, company_name: str
    ) -> AuthenticityPatterns:
        """Analyze LinkedIn profiles for authentic language patterns."""
        # Mock implementation - would use LinkedIn API in production
        return AuthenticityPatterns(
            executive_summary_patterns=[
                "Built and scaled",
                "Led transformation initiatives",
                "Delivered measurable business impact",
            ],
            achievement_verb_patterns=["Spearheaded", "Engineered", "Transformed", "Optimized"],
            metric_presentation_patterns=[
                "resulting in X% improvement",
                "saving $Y through optimization",
                "reducing time by Z hours",
            ],
            competency_phrasing_patterns=["Expertise in", "Proficient with", "Specialized in"],
        )

    def _gather_competitive_intelligence(
        self, job_description: str, company_name: str
    ) -> CompetitiveIntelligence:
        """Gather competitive intelligence from peer job descriptions."""
        # Mock implementation - would analyze peer JDs in production
        return CompetitiveIntelligence(
            peer_jds_analyzed=[f"Similar role at {company_name} competitor"],
            table_stakes_keywords=["python", "aws", "leadership", "analytics"],
            differentiator_keywords=["machine learning", "scalability", "innovation"],
        )

    def _classify_company_industry(
        self, company_name: str, job_description: str
    ) -> tuple[str, str]:
        """Classify company industry using GICS classification."""
        # Simplified classification
        if any(tech in company_name.lower() for tech in ["google", "microsoft", "apple", "amazon"]):
            return "Information Technology", "Software"
        elif any(fin in company_name.lower() for fin in ["jpmorgan", "goldman", "bank"]):
            return "Financials", "Banking"
        else:
            return "Information Technology", "Software"


# ============================================================================
# PATTERN 2: Two-Phase Generation (K.5A/K.5B, K.6A/K.6B)
# ============================================================================


@dataclass
class BulletGenerationOutput:
    """Output from bullet generation phase."""

    bullets: list[str]
    provenance_counts: dict[str, int]  # e.g., {"3V": 3, "3T": 3, "1S": 1}
    word_counts: list[int]
    thematic_alignment_score: float


@dataclass
class OverviewSynthesisOutput:
    """Output from overview synthesis phase."""

    overview: str
    word_count: int
    thematic_coverage: list[str]
    uniqueness_score: float


class TwoPhaseGenerationNode:
    """
    Implements the two-phase generation pattern from v61.27.10:
    Phase A: Generate bullets with provenance requirements
    Phase B: Synthesize overview from bullets
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}

        # Provenance requirements from legacy system
        self.provenance_requirements = {
            "unify_bullets": {"count": 7, "3V": 3, "3T": 3, "1S": 1},
            "ibm_bullets": {"count": 6, "2V": 3, "3T": 1, "1S": 1},
        }

        # Word count constraints
        self.word_constraints = {
            "unify_bullets": {"min": 28, "max": 33},
            "ibm_bullets": {"min": 24, "max": 30},
            "unify_overview": {"min": 25, "max": 33},
            "ibm_overview": {"min": 22, "max": 28},
        }

    def generate_unify_bullets_phase_a(
        self, thematic_output: ThematicAnalysisOutput, role_extraction: dict[str, Any]
    ) -> BulletGenerationOutput:
        """
        Phase A: Generate Unify Consulting bullets (7 bullets with 3V-3T-1S provenance)

        This implements the sophisticated bullet generation from v61.27.10 with:
        - Provenance requirements (3V-3T-1S)
        - Word count constraints
        - Thematic alignment
        """
        logger.info("Starting Phase A: Unify bullet generation")

        # Generate bullets based on themes and authenticity patterns
        bullets = self._generate_bullets_with_provenance(
            company_type="unify",
            themes=thematic_output.secondary_themes,
            patterns=thematic_output.authenticity_patterns.achievement_verb_patterns,
            differentiators=thematic_output.competitive_intelligence.differentiator_keywords,
            count=7,
        )

        # Validate provenance
        provenance_counts = self._validate_provenance(bullets, {"3V": 3, "3T": 3, "1S": 1})

        # Calculate word counts
        word_counts = [len(bullet.split()) for bullet in bullets]

        # Calculate thematic alignment
        thematic_score = self._calculate_thematic_alignment(bullets, thematic_output)

        output = BulletGenerationOutput(
            bullets=bullets,
            provenance_counts=provenance_counts,
            word_counts=word_counts,
            thematic_alignment_score=thematic_score,
        )

        logger.info(f"Phase A complete: {len(bullets)} bullets generated")
        return output

    def synthesize_unify_overview_phase_b(
        self, bullet_output: BulletGenerationOutput, thematic_output: ThematicAnalysisOutput
    ) -> OverviewSynthesisOutput:
        """
        Phase B: Synthesize Unify Consulting overview from generated bullets

        This creates an umbrella overview (25-33 words) that frames the thematic
        scope without repeating specific bullet achievements.
        """
        logger.info("Starting Phase B: Unify overview synthesis")

        # Synthesize overview from bullets
        overview = self._synthesize_overview(
            bullets=bullet_output.bullets,
            themes=thematic_output.secondary_themes,
            differentiators=thematic_output.competitive_intelligence.differentiator_keywords,
            target_words=25,
        )

        # Validate word count
        word_count = len(overview.split())
        if not (25 <= word_count <= 33):
            logger.warning(f"Overview word count {word_count} outside target range 25-33")

        # Calculate thematic coverage
        thematic_coverage = self._extract_thematic_coverage(overview, thematic_output)

        # Calculate uniqueness score
        uniqueness_score = self._calculate_uniqueness_score(overview, bullet_output.bullets)

        output = OverviewSynthesisOutput(
            overview=overview,
            word_count=word_count,
            thematic_coverage=thematic_coverage,
            uniqueness_score=uniqueness_score,
        )

        logger.info(f"Phase B complete: {word_count} word overview synthesized")
        return output

    def _generate_bullets_with_provenance(
        self,
        company_type: str,
        themes: list[str],
        patterns: list[str],
        differentiators: list[str],
        count: int,
    ) -> list[str]:
        """Generate bullets with specific provenance requirements."""
        bullets = []

        # Mock implementation - would use LLM in production

        for i in range(count):
            if company_type == "unify":
                bullet = f"Spearheaded {themes[i % len(themes)]} initiatives achieving 25% improvement in operational efficiency"
            else:
                bullet = f"Led {themes[i % len(themes)]} projects resulting in $2M cost savings through process optimization"
            bullets.append(bullet)

        return bullets

    def _validate_provenance(
        self, bullets: list[str], requirements: dict[str, int]
    ) -> dict[str, int]:
        """Validate that bullets meet provenance requirements."""
        # Mock implementation - would analyze actual content in production
        return {"3V": 3, "3T": 3, "1S": 1}

    def _calculate_thematic_alignment(self, bullets: list[str], themes: Any) -> float:
        """Calculate how well bullets align with themes."""
        return 0.85  # Mock score

    def _synthesize_overview(
        self, bullets: list[str], themes: list[str], differentiators: list[str], target_words: int
    ) -> str:
        """Synthesize overview from bullets without repeating achievements."""
        # Mock implementation - would use LLM in production
        return "Led strategic technology transformation initiatives driving operational excellence and innovation across enterprise platforms"

    def _extract_thematic_coverage(self, overview: str, themes: Any) -> list[str]:
        """Extract which themes are covered in overview."""
        return ["Technology", "Leadership", "Innovation"]

    def _calculate_uniqueness_score(self, overview: str, bullets: list[str]) -> float:
        """Calculate how unique overview is from bullets."""
        return 0.75  # Mock score


# ============================================================================
# PATTERN 3: Word Count Enforcement Engine
# ============================================================================


@dataclass
class ValidationResult:
    """Result of word count validation."""

    is_valid: bool
    word_count: int
    min_required: int
    max_allowed: int
    violation_type: str | None
    regeneration_needed: bool


class WordCountEnforcementEngine:
    """
    Zero-tolerance word count enforcement with regeneration engine.

    Based on v61.27.10 production-hardened validation system that ensures
    all content meets exact word count requirements.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}

        # Word count constraints from legacy system
        self.constraints = {
            "K.1_executive_summary": {"min": 120, "max": 140},
            "K.4_headline": {"min": 8, "max": 12},
            "K.5A_unify_bullets": {"per_bullet_min": 28, "per_bullet_max": 33, "count": 7},
            "K.6A_ibm_bullets": {"per_bullet_min": 24, "per_bullet_max": 30, "count": 6},
            "K.5B_unify_overview": {"min": 25, "max": 33},
            "K.6B_ibm_overview": {"min": 22, "max": 28},
            "K.8_competencies": {"per_item_min": 24, "per_item_max": 30, "count": 6},
        }

        # Regeneration strategies
        self.regeneration_engine = RegenerationEngine()

    def validate_content(self, content: str, content_type: str) -> ValidationResult:
        """
        Validate content against word count constraints.

        Args:
            content: Content to validate
            content_type: Type identifier for constraints lookup

        Returns:
            ValidationResult with validation details
        """
        constraints = self.constraints.get(content_type, {})
        word_count = len(content.split())

        if not constraints:
            return ValidationResult(
                is_valid=True,
                word_count=word_count,
                min_required=0,
                max_allowed=float("inf"),
                violation_type=None,
                regeneration_needed=False,
            )

        min_words = constraints.get("min", 0)
        max_words = constraints.get("max", float("inf"))

        is_valid = min_words <= word_count <= max_words
        violation_type = None
        regeneration_needed = False

        if not is_valid:
            if word_count < min_words:
                violation_type = "UNDERFLOW"
            elif word_count > max_words:
                violation_type = "OVERFLOW"
            regeneration_needed = True

        return ValidationResult(
            is_valid=is_valid,
            word_count=word_count,
            min_required=min_words,
            max_allowed=max_words,
            violation_type=violation_type,
            regeneration_needed=regeneration_needed,
        )

    def enforce_with_regeneration(
        self, content: str, content_type: str, max_attempts: int = 3
    ) -> tuple[str, ValidationResult]:
        """
        Enforce word count constraints with regeneration.

        This implements the zero-tolerance enforcement from v61.27.10
        that regenerates content until constraints are met.
        """
        current_content = content
        last_validation = self.validate_content(current_content, content_type)

        for attempt in range(max_attempts):
            if last_validation.is_valid:
                logger.info(f"Content validated on attempt {attempt + 1}")
                return current_content, last_validation

            logger.warning(
                f"Attempt {attempt + 1}: {last_validation.violation_type} - regenerating"
            )
            current_content = self.regeneration_engine.regenerate(
                current_content, last_validation.violation_type, last_validation
            )
            last_validation = self.validate_content(current_content, content_type)

        # If still invalid after max attempts, halt
        error_msg = f"Content failed validation after {max_attempts} attempts. Final count: {last_validation.word_count}"
        logger.error(error_msg)
        raise ValueError(error_msg)


class RegenerationEngine:
    """
    Intelligent content regeneration engine.

    Implements the sophisticated regeneration strategies from v61.27.10
    that expand or condense content while preserving key information.
    """

    def regenerate(
        self, content: str, violation_type: str, validation_result: ValidationResult
    ) -> str:
        """
        Regenerate content based on violation type.

        Args:
            content: Original content
            violation_type: Type of word count violation
            validation_result: Validation details

        Returns:
            Regenerated content
        """
        if violation_type == "UNDERFLOW":
            return self._expand_with_relevant_detail(content, validation_result)
        elif violation_type == "OVERFLOW":
            return self._smart_condense_preserve_specifics(content, validation_result)
        else:
            return content

    def _expand_with_relevant_detail(
        self, content: str, validation_result: ValidationResult
    ) -> str:
        """Expand content by adding relevant details."""
        validation_result.min_required - validation_result.word_count

        # Mock expansion - would use LLM in production
        expansion_phrases = [
            " with measurable business impact",
            " through strategic initiative leadership",
            " resulting in significant operational improvements",
            " by implementing best practices",
            " while maintaining quality standards",
        ]

        expanded = content
        for phrase in expansion_phrases:
            if len(expanded.split()) >= validation_result.min_required:
                break
            expanded += phrase

        return expanded

    def _smart_condense_preserve_specifics(
        self, content: str, validation_result: ValidationResult
    ) -> str:
        """Condense content while preserving specifics."""
        validation_result.word_count - validation_result.max_allowed

        # Mock condensation - would use LLM in production
        words = content.split()
        condensed_words = words[: validation_result.max_allowed]
        return " ".join(condensed_words)


# ============================================================================
# PATTERN 4: Cryptographic Validation Gates
# ============================================================================


class ValidationGate:
    """
    Cryptographic validation gate system.

    Implements the gate signature system from v61.27.10 that prevents
    validation bypass through cryptographic signatures.
    """

    def __init__(self, gate_id: str, signature_key: str = None):
        self.gate_id = gate_id
        self.signature_key = signature_key or "WORKFLOW_v61.27.10_VALIDATION_KEY"
        self.execution_log = []
        self.signatures = {}

    def execute_and_sign(self, execution_data: dict[str, Any]) -> str:
        """
        Execute validation and sign the result.

        Args:
            execution_data: Data to validate

        Returns:
            Cryptographic signature
        """
        # Execute validation logic
        validation_result = self._execute_validation(execution_data)

        # Create signature
        signature = self._create_signature(validation_result)

        # Log execution
        self._log_execution(execution_data, validation_result, signature)

        return signature

    def verify_signatures(self, required_signatures: list[str]) -> bool:
        """
        Verify that all required signatures are present.

        Args:
            required_signatures: List of required gate signatures

        Returns:
            True if all signatures are present and valid
        """
        for sig in required_signatures:
            if sig not in self.signatures:
                logger.error(f"Missing required signature: {sig}")
                return False
        return True

    def _execute_validation(self, data: dict[str, Any]) -> dict[str, Any]:
        """Execute the actual validation logic."""
        # Mock validation - would implement specific logic per gate
        return {
            "gate_id": self.gate_id,
            "status": "PASS",
            "timestamp": "2025-01-25T10:00:00Z",
            "data_hash": hashlib.md5(json.dumps(data).encode()).hexdigest(),
        }

    def _create_signature(self, validation_result: dict[str, Any]) -> str:
        """Create HMAC-SHA256 signature."""
        message = json.dumps(validation_result, sort_keys=True)
        signature = hmac.new(
            self.signature_key.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        self.signatures[self.gate_id] = signature
        return signature

    def _log_execution(
        self, execution_data: dict[str, Any], validation_result: dict[str, Any], signature: str
    ) -> None:
        """Log execution for audit trail."""
        log_entry = {
            "gate_id": self.gate_id,
            "timestamp": validation_result["timestamp"],
            "signature": signature,
            "status": validation_result["status"],
        }
        self.execution_log.append(log_entry)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================


def example_two_phase_generation():
    """Example of two-phase generation using historical patterns."""

    # Initialize nodes
    thematic_node = ThematicAnalysisNode()
    two_phase_node = TwoPhaseGenerationNode()
    word_enforcer = WordCountEnforcementEngine()

    # Input data
    job_description = (
        "Senior Software Engineer at Google Cloud leading ML infrastructure initiatives"
    )
    company_name = "Google"

    # Step 1: Thematic analysis (K.0)
    thematic_output = thematic_node(job_description, company_name)
    print(f"Primary theme: {thematic_output.primary_theme}")
    print(f"Differentiators: {thematic_output.competitive_intelligence.differentiator_keywords}")

    # Step 2A: Generate bullets (K.5A)
    role_extraction = {"seniority": "SENIOR", "function": "ENGINEERING"}
    bullet_output = two_phase_node.generate_unify_bullets_phase_a(thematic_output, role_extraction)
    print(f"Generated {len(bullet_output.bullets)} bullets")

    # Step 2B: Synthesize overview (K.5B)
    overview_output = two_phase_node.synthesize_unify_overview_phase_b(
        bullet_output, thematic_output
    )
    print(f"Overview: {overview_output.overview}")

    # Step 3: Enforce word count
    final_overview, validation = word_enforcer.enforce_with_regeneration(
        overview_output.overview, "K.5B_unify_overview"
    )
    print(f"Final overview ({validation.word_count} words): {final_overview}")


def example_validation_gates():
    """Example of cryptographic validation gates."""

    # Create validation gates
    word_count_gate = ValidationGate("VG_MANDATORY_WORD_COUNT_COMPLIANCE")
    production_gate = ValidationGate("VG_PRODUCTION_READY_PROOF")

    # Execute validations
    execution_data = {"content": "Sample content", "word_count": 120}

    sig1 = word_count_gate.execute_and_sign(execution_data)
    sig2 = production_gate.execute_and_sign(execution_data)

    # Verify all required signatures are present
    required_sigs = [sig1, sig2]
    all_valid = word_count_gate.verify_signatures(required_sigs)

    print(f"All validations passed: {all_valid}")


if __name__ == "__main__":
    example_two_phase_generation()
    example_validation_gates()
