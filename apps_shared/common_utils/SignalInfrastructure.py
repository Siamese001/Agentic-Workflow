"""Shared Signal Infrastructure - Common quality components for all engines.

This module provides shared signal enhancement infrastructure that can be
used by both resume and outreach engines while maintaining domain-specific
customization.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
import json

from ..core.quality.signal_enhancer import (
    SignalAssessment,
    SignalEnhancer,
    QualityThresholds,
    SignalQuality
)
from ..core.quality.feedback_loop import (
    FeedbackLoop,
    QualityFeedback,
    FeedbackType
)

logger = logging.getLogger(__name__)


class EngineType(Enum):
    """Types of engines using shared infrastructure."""
    RESUME = "resume"
    OUTREACH = "outreach"
    GENERAL = "general"


@dataclass
class DomainConfig:
    """Domain-specific configuration for signal enhancement."""
    
    engine_type: EngineType
    quality_thresholds: QualityThresholds
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: List[str] = field(default_factory=list)
    feedback_prompts: Dict[str, str] = field(default_factory=dict)
    
    # Domain-specific weights
    metric_weights: Dict[str, float] = field(default_factory=lambda: {
        "relevance": 0.3,
        "authority": 0.2,
        "specificity": 0.2,
        "coherence": 0.2,
        "accuracy": 0.1
    })


class DomainValidator(ABC):
    """Abstract base for domain-specific validation."""
    
    @abstractmethod
    def validate_domain_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content for specific domain.
        
        Args:
            content: Content to validate
            context: Domain context
            
        Returns:
            Validation results
        """
        pass
    
    @abstractmethod
    def extract_domain_metrics(self, content: str) -> Dict[str, float]:
        """Extract domain-specific metrics.
        
        Args:
            content: Content to analyze
            
        Returns:
            Domain metrics
        """
        pass


class ResumeValidator(DomainValidator):
    """Validator for resume-specific content."""
    
    def validate_domain_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resume content."""
        results = {
            "has_achievements": self._has_achievements(content),
            "has_metrics": self._has_metrics(content),
            "action_verbs": self._count_action_verbs(content),
            "bullet_quality": self._assess_bullet_quality(content),
            "completeness": self._assess_completeness(content, context)
        }
        return results
    
    def extract_domain_metrics(self, content: str) -> Dict[str, float]:
        """Extract resume-specific metrics."""
        return {
            "achievement_density": self._calculate_achievement_density(content),
            "metric_usage": self._calculate_metric_usage(content),
            "verb_diversity": self._calculate_verb_diversity(content),
            "impact_score": self._calculate_impact_score(content)
        }
    
    def _has_achievements(self, content: str) -> bool:
        """Check if content has achievement statements."""
        achievement_patterns = [
            r"\bincreased\b",
            r"\bdecreased\b",
            r"\bsaved\b",
            r"\bgenerated\b",
            r"\breduced\b",
            r"\boptimized\b",
            r"\blead\b.*\bteam\b"
        ]
        import re
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in achievement_patterns)
    
    def _has_metrics(self, content: str) -> bool:
        """Check if content includes metrics."""
        import re
        metric_patterns = [
            r"\d+%",
            r"\$\d+(?:,\d{3})*(?:\.\d+)?",
            r"\d+(?:,\d{3})*\s*(?:employees|people|users|customers)",
            r"\d+(?:,\d{3})*\s*(?:hours|days|weeks|months)"
        ]
        return any(re.search(pattern, content) for pattern in metric_patterns)
    
    def _count_action_verbs(self, content: str) -> int:
        """Count action verbs in content."""
        action_verbs = {
            "led", "managed", "developed", "created", "implemented", "optimized",
            "reduced", "increased", "improved", "achieved", "delivered", "launched",
            "coordinated", "directed", "supervised", "mentored", "trained"
        }
        words = content.lower().split()
        return sum(1 for word in words if word in action_verbs)
    
    def _assess_bullet_quality(self, content: str) -> float:
        """Assess bullet point quality."""
        bullets = [b.strip() for b in content.split('\n') if b.strip().startswith('•') or b.strip().startswith('-')]
        if not bullets:
            return 0.0
        
        quality_scores = []
        for bullet in bullets:
            score = 0.0
            # Has action verb
            if any(verb in bullet.lower() for verb in ["led", "managed", "developed"]):
                score += 0.3
            # Has metric
            if any(char.isdigit() for char in bullet):
                score += 0.4
            # Has result
            if any(word in bullet.lower() for word in ["resulted", "achieved", "led to"]):
                score += 0.3
            quality_scores.append(score)
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    def _assess_completeness(self, content: str, context: Dict[str, Any]) -> float:
        """Assess content completeness."""
        required_sections = context.get("required_sections", [])
        present_sections = 0
        
        for section in required_sections:
            if section.lower() in content.lower():
                present_sections += 1
        
        return present_sections / len(required_sections) if required_sections else 0.5
    
    def _calculate_achievement_density(self, content: str) -> float:
        """Calculate achievement statement density."""
        sentences = content.split('.')
        achievements = sum(1 for s in sentences if self._has_achievements(s))
        return achievements / len(sentences) if sentences else 0.0
    
    def _calculate_metric_usage(self, content: str) -> float:
        """Calculate metric usage frequency."""
        sentences = content.split('.')
        with_metrics = sum(1 for s in sentences if self._has_metrics(s))
        return with_metrics / len(sentences) if sentences else 0.0
    
    def _calculate_verb_diversity(self, content: str) -> float:
        """Calculate action verb diversity."""
        verbs = self._count_action_verbs(content)
        unique_verbs = len(set(word.lower() for word in content.split() 
                             if word in ["led", "managed", "developed", "created"]))
        return unique_verbs / max(verbs, 1)
    
    def _calculate_impact_score(self, content: str) -> float:
        """Calculate overall impact score."""
        return (
            self._calculate_achievement_density(content) * 0.4 +
            self._calculate_metric_usage(content) * 0.4 +
            self._assess_bullet_quality(content) * 0.2
        )


class OutreachValidator(DomainValidator):
    """Validator for outreach-specific content."""
    
    def validate_domain_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate outreach content."""
        results = {
            "has_personalization": self._has_personalization(content, context),
            "has_cta": self._has_call_to_action(content),
            "tone_appropriate": self._assess_tone(content, context),
            "value_proposition": self._has_value_proposition(content),
            "recipient_relevance": self._assess_recipient_relevance(content, context)
        }
        return results
    
    def extract_domain_metrics(self, content: str) -> Dict[str, float]:
        """Extract outreach-specific metrics."""
        return {
            "personalization_score": self._calculate_personalization_score(content),
            "engagement_potential": self._calculate_engagement_potential(content),
            "professionalism": self._calculate_professionalism(content),
            "clarity": self._calculate_clarity(content)
        }
    
    def _has_personalization(self, content: str, context: Dict[str, Any]) -> bool:
        """Check if content has personalization."""
        recipient_info = context.get("recipient_info", {})
        if not recipient_info:
            return False
        
        # Check for recipient name, company, role
        personalization_indicators = []
        if "name" in recipient_info:
            personalization_indicators.append(recipient_info["name"].lower())
        if "company" in recipient_info:
            personalization_indicators.append(recipient_info["company"].lower())
        if "role" in recipient_info:
            personalization_indicators.append(recipient_info["role"].lower())
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in personalization_indicators)
    
    def _has_call_to_action(self, content: str) -> bool:
        """Check if content has call to action."""
        cta_phrases = [
            "let's discuss",
            "would love to",
            "looking forward to",
            "please let me know",
            "feel free to",
            "would be happy to"
        ]
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in cta_phrases)
    
    def _assess_tone(self, content: str, context: Dict[str, Any]) -> float:
        """Assess tone appropriateness."""
        recipient_level = context.get("recipient_level", "professional")
        
        # Check formality indicators
        formal_indicators = ["dear", "sincerely", "regards", "respectfully"]
        informal_indicators = ["hey", "hi", "what's up", "yo"]
        
        content_lower = content.lower()
        
        if recipient_level == "c_level":
            # Should be very formal
            formal_count = sum(1 for indicator in formal_indicators if indicator in content_lower)
            informal_count = sum(1 for indicator in informal_indicators if indicator in content_lower)
            return min(1.0, formal_count * 0.3 - informal_count * 0.5)
        else:
            # Can be slightly less formal
            return 0.7  # Default moderate formality
    
    def _has_value_proposition(self, content: str) -> bool:
        """Check if content has clear value proposition."""
        value_indicators = [
            "bring to",
            "contribute to",
            "help you",
            "benefit",
            "value",
            "expertise",
            "experience"
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in value_indicators)
    
    def _assess_recipient_relevance(self, content: str, context: Dict[str, Any]) -> float:
        """Assess relevance to recipient."""
        recipient_role = context.get("recipient_info", {}).get("role", "").lower()
        recipient_company = context.get("recipient_info", {}).get("company", "").lower()
        
        if not recipient_role and not recipient_company:
            return 0.5  # Default
        
        content_lower = content.lower()
        relevance_score = 0.0
        
        # Check role relevance
        if recipient_role:
            role_keywords = recipient_role.split()
            role_matches = sum(1 for keyword in role_keywords if keyword in content_lower)
            relevance_score += role_matches / len(role_keywords) * 0.5
        
        # Check company relevance
        if recipient_company:
            if recipient_company in content_lower:
                relevance_score += 0.5
        
        return min(1.0, relevance_score)
    
    def _calculate_personalization_score(self, content: str) -> float:
        """Calculate personalization score."""
        # Simplified - count personalization indicators
        personal_indicators = ["you", "your", "specific", "particular", "unique"]
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in personal_indicators if indicator in content_lower)
        return min(1.0, indicator_count * 0.2)
    
    def _calculate_engagement_potential(self, content: str) -> float:
        """Calculate engagement potential."""
        engaging_words = [
            "exciting", "opportunity", "innovative", "breakthrough",
            "transform", "revolutionize", "game-changing"
        ]
        content_lower = content.lower()
        engaging_count = sum(1 for word in engaging_words if word in content_lower)
        return min(1.0, engaging_count * 0.15)
    
    def _calculate_professionalism(self, content: str) -> float:
        """Calculate professionalism score."""
        # Check for professional language
        professional_words = [
            "expertise", "experience", "background", "qualifications",
            "accomplished", "achieved", "delivered", "executed"
        ]
        content_lower = content.lower()
        professional_count = sum(1 for word in professional_words if word in content_lower)
        
        # Penalize overly casual language
        casual_words = ["awesome", "cool", "super", "really", "totally"]
        casual_count = sum(1 for word in casual_words if word in content_lower)
        
        return min(1.0, professional_count * 0.1 - casual_count * 0.2)
    
    def _calculate_clarity(self, content: str) -> float:
        """Calculate clarity score."""
        # Simple clarity based on sentence length and structure
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if not sentences:
            return 0.0
        
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Optimal sentence length is 15-20 words
        if 10 <= avg_sentence_length <= 25:
            length_score = 1.0
        elif avg_sentence_length < 10:
            length_score = 0.7
        else:
            length_score = max(0.0, 1.0 - (avg_sentence_length - 25) * 0.05)
        
        return length_score


class SharedSignalInfrastructure:
    """Shared infrastructure for signal enhancement across engines."""
    
    def __init__(self):
        """Initialize the shared infrastructure."""
        self._validators: Dict[EngineType, DomainValidator] = {
            EngineType.RESUME: ResumeValidator(),
            EngineType.OUTREACH: OutreachValidator()
        }
        self._enhancers: Dict[str, SignalEnhancer] = {}
        self._feedback_loops: Dict[str, FeedbackLoop] = {}
        
        logger.info("Initialized SharedSignalInfrastructure")
    
    def get_enhancer(
        self,
        engine_type: EngineType,
        domain_config: DomainConfig
    ) -> SignalEnhancer:
        """Get a signal enhancer for the specified engine.
        
        Args:
            engine_type: Type of engine
            domain_config: Domain-specific configuration
            
        Returns:
            Configured signal enhancer
        """
        enhancer_key = f"{engine_type.value}_{id(domain_config)}"
        
        if enhancer_key not in self._enhancers:
            enhancer = SignalEnhancer(
                name=f"{engine_type.value}_enhancer",
                thresholds=domain_config.quality_thresholds
            )
            
            # Store with domain config reference
            enhancer.domain_config = domain_config
            enhancer.domain_validator = self._validators.get(engine_type)
            
            self._enhancers[enhancer_key] = enhancer
        
        return self._enhancers[enhancer_key]
    
    def assess_signal(
        self,
        content: str,
        engine_type: EngineType,
        domain_config: DomainConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> SignalAssessment:
        """Assess signal quality with domain-specific validation.
        
        Args:
            content: Content to assess
            engine_type: Type of engine
            domain_config: Domain configuration
            context: Optional context
            
        Returns:
            Enhanced signal assessment
        """
        # Get base assessment
        enhancer = self.get_enhancer(engine_type, domain_config)
        assessment = enhancer.assess_signal(content, context)
        
        # Add domain-specific validation
        if engine_type in self._validators:
            validator = self._validators[engine_type]
            
            # Add domain metrics
            domain_metrics = validator.extract_domain_metrics(content)
            assessment.domain_metrics = domain_metrics
            
            # Add domain validation results
            if context:
                domain_validation = validator.validate_domain_content(content, context)
                assessment.domain_validation = domain_validation
                
                # Adjust composite score based on domain validation
                domain_score = sum(domain_validation.values()) / len(domain_validation)
                assessment.composite_score = (
                    assessment.composite_score * 0.7 + domain_score * 0.3
                )
        
        return assessment
    
    def get_feedback_loop(
        self,
        engine_type: EngineType,
        loop_name: Optional[str] = None
    ) -> FeedbackLoop:
        """Get feedback loop for the engine.
        
        Args:
            engine_type: Type of engine
            loop_name: Optional loop name
            
        Returns:
            Feedback loop instance
        """
        loop_key = f"{engine_type.value}_{loop_name or 'default'}"
        
        if loop_key not in self._feedback_loops:
            self._feedback_loops[loop_key] = FeedbackLoop(loop_key)
        
        return self._feedback_loops[loop_key]
    
    def create_domain_config(
        self,
        engine_type: EngineType,
        custom_thresholds: Optional[QualityThresholds] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> DomainConfig:
        """Create domain configuration.
        
        Args:
            engine_type: Type of engine
            custom_thresholds: Custom quality thresholds
            custom_weights: Custom metric weights
            
        Returns:
            Domain configuration
        """
        thresholds = custom_thresholds or QualityThresholds()
        
        # Domain-specific default configurations
        if engine_type == EngineType.RESUME:
            validation_rules = {
                "require_achievements": True,
                "require_metrics": True,
                "min_bullet_points": 3,
                "max_bullet_length": 200
            }
            custom_metrics = ["achievement_density", "metric_usage", "verb_diversity", "impact_score"]
        elif engine_type == EngineType.OUTREACH:
            validation_rules = {
                "require_personalization": True,
                "require_cta": True,
                "max_length": 500,
                "min_recipient_references": 2
            }
            custom_metrics = ["personalization_score", "engagement_potential", "professionalism", "clarity"]
        else:
            validation_rules = {}
            custom_metrics = []
        
        return DomainConfig(
            engine_type=engine_type,
            quality_thresholds=thresholds,
            validation_rules=validation_rules,
            custom_metrics=custom_metrics,
            metric_weights=custom_weights or {}
        )
    
    def get_cross_engine_insights(self) -> Dict[str, Any]:
        """Get insights across all engines.
        
        Returns:
            Cross-engine insights
        """
        insights = {
            "engines": {},
            "shared_patterns": {},
            "recommendations": []
        }
        
        # Collect insights from each engine
        for engine_type in EngineType:
            if engine_type == EngineType.GENERAL:
                continue
                
            loop = self.get_feedback_loop(engine_type)
            engine_insights = loop.get_quality_insights()
            insights["engines"][engine_type.value] = engine_insights
        
        # Identify shared patterns
        all_thresholds = {}
        for enhancer in self._enhancers.values():
            if hasattr(enhancer, 'domain_config'):
                engine = enhancer.domain_config.engine_type
                all_thresholds[engine.value] = enhancer.domain_config.quality_thresholds
        
        insights["shared_patterns"] = {
            "threshold_comparison": all_thresholds,
            "common_flags": self._find_common_flags(),
            "quality_correlation": self._analyze_quality_correlation()
        }
        
        # Generate recommendations
        insights["recommendations"] = self._generate_cross_engine_recommendations(insights)
        
        return insights
    
    def _find_common_flags(self) -> Dict[str, List[str]]:
        """Find common quality flags across engines."""
        flag_counts = {}
        
        for loop in self._feedback_loops.values():
            loop_insights = loop.get_quality_insights()
            if "common_flags" in loop_insights:
                for flag, count in loop_insights["common_flags"].items():
                    if flag not in flag_counts:
                        flag_counts[flag] = []
                    flag_counts[flag].append(count)
        
        return flag_counts
    
    def _analyze_quality_correlation(self) -> Dict[str, float]:
        """Analyze quality correlations between engines."""
        # Simplified - would need actual data for real correlation
        return {
            "resume_outreach_correlation": 0.65,
            "quality_convergence": 0.72
        }
    
    def _generate_cross_engine_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on cross-engine analysis."""
        recommendations = []
        
        # Check for quality gaps
        for engine, engine_insights in insights["engines"].items():
            avg_quality = engine_insights.get("average_scores", {}).get("composite", 0)
            if avg_quality < 0.7:
                recommendations.append(
                    f"Engine {engine} has low average quality ({avg_quality:.2f}). "
                    "Consider reviewing domain-specific validation rules."
                )
        
        # Check for common issues
        common_flags = insights["shared_patterns"].get("common_flags", {})
        if "LOW_QUALITY" in common_flags and len(common_flags["LOW_QUALITY"]) > 1:
            recommendations.append(
                "Multiple engines experiencing LOW_QUALITY flags. "
                "Consider strengthening base validation criteria."
            )
        
        return recommendations


# Global shared infrastructure instance
_shared_infrastructure: Optional[SharedSignalInfrastructure] = None


def get_shared_infrastructure() -> SharedSignalInfrastructure:
    """Get the global shared infrastructure instance.
    
    Returns:
        SharedSignalInfrastructure instance
    """
    global _shared_infrastructure
    if _shared_infrastructure is None:
        _shared_infrastructure = SharedSignalInfrastructure()
    return _shared_infrastructure


# Convenience functions for engines
def assess_resume_signal(
    content: str,
    context: Optional[Dict[str, Any]] = None,
    strict_mode: bool = True
) -> SignalAssessment:
    """Assess resume signal quality.
    
    Args:
        content: Resume content
        context: Optional context
        strict_mode: Use strict thresholds
        
    Returns:
        Signal assessment
    """
    infrastructure = get_shared_infrastructure()
    
    # Create resume config
    thresholds = QualityThresholds() if strict_mode else QualityThresholds(
        GOOD_MIN=0.5, MARGINAL_MIN=0.3
    )
    config = infrastructure.create_domain_config(
        EngineType.RESUME,
        custom_thresholds=thresholds
    )
    
    return infrastructure.assess_signal(content, EngineType.RESUME, config, context)


def assess_outreach_signal(
    content: str,
    context: Optional[Dict[str, Any]] = None,
    strict_mode: bool = True
) -> SignalAssessment:
    """Assess outreach signal quality.
    
    Args:
        content: Outreach content
        context: Optional context
        strict_mode: Use strict thresholds
        
    Returns:
        Signal assessment
    """
    infrastructure = get_shared_infrastructure()
    
    # Create outreach config
    thresholds = QualityThresholds() if strict_mode else QualityThresholds(
        GOOD_MIN=0.5, MARGINAL_MIN=0.3
    )
    config = infrastructure.create_domain_config(
        EngineType.OUTREACH,
        custom_thresholds=thresholds
    )
    
    return infrastructure.assess_signal(content, EngineType.OUTREACH, config, context)
