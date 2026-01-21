"""Cross-Engine Quality Standards - Unified quality benchmarks.

This module defines unified quality standards that apply across all engines
while allowing for domain-specific customizations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..core.quality.signal_enhancer import QualityThresholds
from .signal_infrastructure import DomainConfig, EngineType


class StandardType(Enum):
    """Types of quality standards."""

    BASE = "base"  # Minimum acceptable for all engines
    PREFERRED = "preferred"  # Target quality for production
    EXCELLENCE = "excellence"  # Aspirational quality level


class QualityDimension(Enum):
    """Dimensions of quality assessment."""

    ACCURACY = "accuracy"  # Factual correctness
    RELEVANCE = "relevance"  # Pertinence to context
    CLARITY = "clarity"  # Readability and comprehension
    COMPLETENESS = "completeness"  # Coverage of requirements
    CONSISTENCY = "consistency"  # Internal coherence
    VALUE = "value"  # Utility and impact


@dataclass
class QualityStandard:
    """Definition of a quality standard."""

    name: str
    description: str
    dimension: QualityDimension
    standard_type: StandardType
    criteria: dict[str, Any]
    measurement_method: str
    validation_rules: list[str] = field(default_factory=list)

    def evaluate(self, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate content against this standard.

        Args:
            content: Content to evaluate
            context: Evaluation context

        Returns:
            Evaluation results
        """
        # This would be implemented by specific standard types
        return {"score": 0.0, "passed": False, "details": {}}


@dataclass
class EngineQualityProfile:
    """Quality profile for a specific engine."""

    engine_type: EngineType
    base_standards: set[str]
    preferred_standards: set[str]
    excellence_standards: set[str]
    custom_thresholds: QualityThresholds
    domain_weights: dict[str, float]

    def get_standards_for_level(self, level: StandardType) -> set[str]:
        """Get standards for a quality level.

        Args:
            level: Quality level

        Returns:
            Set of standard names
        """
        if level == StandardType.BASE:
            return self.base_standards
        elif level == StandardType.PREFERRED:
            return self.base_standards | self.preferred_standards
        else:  # EXCELLENCE
            return self.base_standards | self.preferred_standards | self.excellence_standards


class CrossEngineQualityStandards:
    """Manages quality standards across all engines."""

    def __init__(self):
        """Initialize the quality standards manager."""
        self._standards: dict[str, QualityStandard] = {}
        self._profiles: dict[EngineType, EngineQualityProfile] = {}

        # Initialize base standards
        self._initialize_base_standards()

        # Initialize engine profiles
        self._initialize_engine_profiles()

        logger.info("Initialized CrossEngineQualityStandards")

    def _initialize_base_standards(self) -> None:
        """Initialize base quality standards."""

        # Accuracy standards
        self._standards["factual_accuracy"] = QualityStandard(
            name="factual_accuracy",
            description="Content must be factually correct and verifiable",
            dimension=QualityDimension.ACCURACY,
            standard_type=StandardType.BASE,
            criteria={"min_confidence": 0.8, "max_unverified_claims": 0, "requires_sources": True},
            measurement_method="claim_verification",
            validation_rules=["no_false_claims", "verify_statistics", "check_dates"],
        )

        self._standards["no_hallucination"] = QualityStandard(
            name="no_hallucination",
            description="Content must not contain hallucinated information",
            dimension=QualityDimension.ACCURACY,
            standard_type=StandardType.BASE,
            criteria={
                "max_hallucination_risk": 0.2,
                "no_speculative_language": True,
                "grounded_in_context": True,
            },
            measurement_method="risk_assessment",
            validation_rules=["check_speculative_claims", "verify_context_grounding"],
        )

        # Relevance standards
        self._standards["context_relevance"] = QualityStandard(
            name="context_relevance",
            description="Content must be relevant to the given context",
            dimension=QualityDimension.RELEVANCE,
            standard_type=StandardType.BASE,
            criteria={
                "min_relevance_score": 0.7,
                "addresses_requirements": True,
                "avoids_irrelevant_content": True,
            },
            measurement_method="semantic_analysis",
            validation_rules=["check_keyword_alignment", "validate_requirement_coverage"],
        )

        # Clarity standards
        self._standards["readability"] = QualityStandard(
            name="readability",
            description="Content must be clear and readable",
            dimension=QualityDimension.CLARITY,
            standard_type=StandardType.BASE,
            criteria={
                "max_sentence_length": 25,
                "min_readability_score": 0.6,
                "proper_grammar": True,
            },
            measurement_method="readability_analysis",
            validation_rules=["check_grammar", "analyze_sentence_structure"],
        )

        self._standards["coherence"] = QualityStandard(
            name="coherence",
            description="Content must be internally coherent",
            dimension=QualityDimension.CONSISTENCY,
            standard_type=StandardType.BASE,
            criteria={
                "logical_flow": True,
                "no_contradictions": True,
                "consistent_terminology": True,
            },
            measurement_method="coherence_analysis",
            validation_rules=["check_logical_flow", "detect_contradictions"],
        )

        # Value standards
        self._standards["adds_value"] = QualityStandard(
            name="adds_value",
            description="Content must provide value to the reader",
            dimension=QualityDimension.VALUE,
            standard_type=StandardType.PREFERRED,
            criteria={
                "min_value_score": 0.7,
                "actionable_insights": True,
                "unique_perspective": True,
            },
            measurement_method="value_assessment",
            validation_rules=["check_insight_quality", "validate_uniqueness"],
        )

        # Completeness standards
        self._standards["completeness"] = QualityStandard(
            name="completeness",
            description="Content must fully address requirements",
            dimension=QualityDimension.COMPLETENESS,
            standard_type=StandardType.BASE,
            criteria={
                "covers_all_requirements": True,
                "no_missing_sections": True,
                "adequate_detail": True,
            },
            measurement_method="requirement_analysis",
            validation_rules=["check_requirement_coverage", "validate_section_completeness"],
        )

        # Preferred standards
        self._standards["professional_tone"] = QualityStandard(
            name="professional_tone",
            description="Content maintains professional tone",
            dimension=QualityDimension.CLARITY,
            standard_type=StandardType.PREFERRED,
            criteria={
                "appropriate_formality": True,
                "no_casual_language": True,
                "respectful_language": True,
            },
            measurement_method="tone_analysis",
            validation_rules=["check_formality_level", "scan_inappropriate_language"],
        )

        self._standards["concise"] = QualityStandard(
            name="concise",
            description="Content is concise and to the point",
            dimension=QualityDimension.CLARITY,
            standard_type=StandardType.PREFERRED,
            criteria={
                "min_information_density": 0.7,
                "no_redundancy": True,
                "efficient_communication": True,
            },
            measurement_method="density_analysis",
            validation_rules=["check_redundancy", "calculate_information_density"],
        )

        # Excellence standards
        self._standards["exceptional_quality"] = QualityStandard(
            name="exceptional_quality",
            description="Content demonstrates exceptional quality",
            dimension=QualityDimension.VALUE,
            standard_type=StandardType.EXCELLENCE,
            criteria={
                "min_overall_score": 0.9,
                "innovative_insights": True,
                "exemplary_writing": True,
            },
            measurement_method="comprehensive_assessment",
            validation_rules=["comprehensive_quality_check", "innovation_assessment"],
        )

    def _initialize_engine_profiles(self) -> None:
        """Initialize quality profiles for each engine."""

        # Resume engine profile
        self._profiles[EngineType.RESUME] = EngineQualityProfile(
            engine_type=EngineType.RESUME,
            base_standards={
                "factual_accuracy",
                "no_hallucination",
                "context_relevance",
                "readability",
                "coherence",
                "completeness",
            },
            preferred_standards={"professional_tone", "concise", "adds_value"},
            excellence_standards={"exceptional_quality"},
            custom_thresholds=QualityThresholds(
                MIN_RELEVANCE=0.75, MIN_AUTHORITY=0.6, MIN_SPECIFICITY=0.7, MIN_COHERENCE=0.7
            ),
            domain_weights={
                "accuracy": 0.3,
                "relevance": 0.2,
                "specificity": 0.2,
                "coherence": 0.2,
                "value": 0.1,
            },
        )

        # Outreach engine profile
        self._profiles[EngineType.OUTREACH] = EngineQualityProfile(
            engine_type=EngineType.OUTREACH,
            base_standards={
                "factual_accuracy",
                "no_hallucination",
                "context_relevance",
                "readability",
                "coherence",
                "completeness",
            },
            preferred_standards={"professional_tone", "adds_value"},
            excellence_standards={"concise", "exceptional_quality"},
            custom_thresholds=QualityThresholds(
                MIN_RELEVANCE=0.8, MIN_AUTHORITY=0.5, MIN_SPECIFICITY=0.6, MIN_COHERENCE=0.7
            ),
            domain_weights={"accuracy": 0.25, "relevance": 0.3, "clarity": 0.25, "value": 0.2},
        )

    def get_standard(self, name: str) -> QualityStandard | None:
        """Get a quality standard by name.

        Args:
            name: Standard name

        Returns:
            Quality standard if found
        """
        return self._standards.get(name)

    def get_engine_profile(self, engine_type: EngineType) -> EngineQualityProfile | None:
        """Get quality profile for an engine.

        Args:
            engine_type: Type of engine

        Returns:
            Engine quality profile
        """
        return self._profiles.get(engine_type)

    def evaluate_against_standards(
        self,
        content: str,
        engine_type: EngineType,
        quality_level: StandardType = StandardType.BASE,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate content against engine-specific standards.

        Args:
            content: Content to evaluate
            engine_type: Type of engine
            quality_level: Quality level to evaluate against
            context: Optional context

        Returns:
            Evaluation results
        """
        profile = self.get_engine_profile(engine_type)
        if not profile:
            return {"error": f"No profile found for engine {engine_type}"}

        required_standards = profile.get_standards_for_level(quality_level)
        results = {
            "engine_type": engine_type.value,
            "quality_level": quality_level.value,
            "standards_evaluated": len(required_standards),
            "standards_passed": 0,
            "standards_failed": [],
            "overall_score": 0.0,
            "detailed_results": {},
        }

        total_score = 0.0

        for standard_name in required_standards:
            standard = self.get_standard(standard_name)
            if not standard:
                continue

            # Evaluate against standard
            standard_result = standard.evaluate(content, context or {})

            # Record results
            results["detailed_results"][standard_name] = standard_result

            if standard_result.get("passed", False):
                results["standards_passed"] += 1
            else:
                results["standards_failed"].append(standard_name)

            total_score += standard_result.get("score", 0.0)

        # Calculate overall score
        if results["standards_evaluated"] > 0:
            results["overall_score"] = total_score / results["standards_evaluated"]

        return results

    def get_quality_gates(self, engine_type: EngineType) -> dict[str, dict[str, Any]]:
        """Get quality gates for an engine.

        Args:
            engine_type: Type of engine

        Returns:
            Quality gates configuration
        """
        profile = self.get_engine_profile(engine_type)
        if not profile:
            return {}

        return {
            "base_gate": {
                "required_standards": list(profile.base_standards),
                "min_score": 0.6,
                "description": "Minimum acceptable quality",
            },
            "preferred_gate": {
                "required_standards": list(profile.base_standards | profile.preferred_standards),
                "min_score": 0.75,
                "description": "Preferred quality for production",
            },
            "excellence_gate": {
                "required_standards": list(
                    profile.base_standards
                    | profile.preferred_standards
                    | profile.excellence_standards
                ),
                "min_score": 0.9,
                "description": "Excellence quality level",
            },
        }

    def create_domain_config_from_standards(
        self, engine_type: EngineType, quality_level: StandardType = StandardType.PREFERRED
    ) -> DomainConfig:
        """Create domain config based on quality standards.

        Args:
            engine_type: Type of engine
            quality_level: Quality level

        Returns:
            Domain configuration
        """
        profile = self.get_engine_profile(engine_type)
        if not profile:
            raise ValueError(f"No profile found for engine {engine_type}")

        # Adjust thresholds based on quality level
        if quality_level == StandardType.BASE:
            thresholds = QualityThresholds(
                EXCELLENT_MIN=0.8, HIGH_MIN=0.65, GOOD_MIN=0.5, MARGINAL_MIN=0.3
            )
        elif quality_level == StandardType.PREFERRED:
            thresholds = profile.custom_thresholds
        else:  # EXCELLENCE
            thresholds = QualityThresholds(
                EXCELLENT_MIN=0.95, HIGH_MIN=0.85, GOOD_MIN=0.75, MARGINAL_MIN=0.6
            )

        # Create validation rules from standards
        validation_rules = {}
        for standard_name in profile.get_standards_for_level(quality_level):
            standard = self.get_standard(standard_name)
            if standard:
                validation_rules[standard_name] = standard.validation_rules

        return DomainConfig(
            engine_type=engine_type,
            quality_thresholds=thresholds,
            validation_rules=validation_rules,
            custom_metrics=list(profile.domain_weights.keys()),
            metric_weights=profile.domain_weights,
        )

    def export_standards(self) -> dict[str, Any]:
        """Export all standards for documentation.

        Returns:
            Standards export
        """
        return {
            "standards": {
                name: {
                    "description": std.description,
                    "dimension": std.dimension.value,
                    "type": std.standard_type.value,
                    "criteria": std.criteria,
                    "validation_rules": std.validation_rules,
                }
                for name, std in self._standards.items()
            },
            "engine_profiles": {
                engine.value: {
                    "base_standards": list(profile.base_standards),
                    "preferred_standards": list(profile.preferred_standards),
                    "excellence_standards": list(profile.excellence_standards),
                    "domain_weights": profile.domain_weights,
                }
                for engine, profile in self._profiles.items()
            },
        }


# Global standards instance
_standards: CrossEngineQualityStandards | None = None


def get_quality_standards() -> CrossEngineQualityStandards:
    """Get the global quality standards instance.

    Returns:
        CrossEngineQualityStandards instance
    """
    global _standards
    if _standards is None:
        _standards = CrossEngineQualityStandards()
    return _standards


# Convenience functions
def evaluate_content_quality(
    content: str,
    engine_type: EngineType,
    quality_level: StandardType = StandardType.BASE,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate content quality against standards.

    Args:
        content: Content to evaluate
        engine_type: Type of engine
        quality_level: Quality level
        context: Optional context

    Returns:
        Evaluation results
    """
    standards = get_quality_standards()
    return standards.evaluate_against_standards(content, engine_type, quality_level, context)


def get_engine_quality_gates(engine_type: EngineType) -> dict[str, dict[str, Any]]:
    """Get quality gates for an engine.

    Args:
        engine_type: Type of engine

    Returns:
        Quality gates configuration
    """
    standards = get_quality_standards()
    return standards.get_quality_gates(engine_type)
