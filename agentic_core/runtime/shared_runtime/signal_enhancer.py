from __future__ import annotations

"""Signal Enhancer - Hardened quality gates for high-signal outputs.

This module provides strict validation gates, signal-to-noise optimization,
and Claim confidence scoring to ensure maximum output quality.
"""

import hashlib
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

Logger = logging.getLogger(__name__)


class SignalQuality(Enum):
    """Signal quality levels."""
    EXCELLENT = "excellent"  # >= 0.9
    HIGH = "high"           # >= 0.75
    GOOD = "good"           # >= 0.6
    MARGINAL = "marginal"   # >= 0.4
    POOR = "poor"          # < 0.4


@dataclass
class QualityThresholds:
    """Strict quality thresholds for different aspects."""
    # Composite score thresholds
    EXCELLENT_MIN: float = 0.9
    HIGH_MIN: float = 0.75
    GOOD_MIN: float = 0.6
    MARGINAL_MIN: float = 0.4

    # Individual component thresholds
    MIN_RELEVANCE: float = 0.7  # Increased from 0.5
    MIN_AUTHORITY: float = 0.6   # Increased from 0.4
    MIN_SPECIFICITY: float = 0.5 # Increased from 0.3
    MIN_COHERENCE: float = 0.6   # Increased from 0.4

    # Content quality thresholds
    MAX_HALLUCINATION_RISK: float = 0.2
    MIN_FACT_VERIFICATION: float = 0.8
    MAX_REPETITION_RATIO: float = 0.3
    MIN_CLAIM_CONFIDENCE: float = 0.7


@dataclass
class ClaimAnalysis:
    """Analysis of claims within content."""
    Claim: str
    confidence: float
    verifiable: bool
    sources: list[str]
    risk_level: str  # low, medium, high


@dataclass
class SignalAssessment:
    """Comprehensive signal quality assessment."""
    content: str
    content_hash: str
    timestamp: datetime

    # Quality scores
    relevance_score: float
    authority_score: float
    specificity_score: float
    coherence_score: float
    composite_score: float
    quality_level: SignalQuality

    # Signal metrics
    signal_to_noise_ratio: float
    information_density: float
    factual_accuracy: float
    originality_score: float

    # Risk indicators
    hallucination_risk: float
    repetition_ratio: float
    claim_analyses: list[ClaimAnalysis]

    # Flags and recommendations
    flags: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def is_acceptable(self, min_quality: SignalQuality = SignalQuality.GOOD) -> bool:
        """Check if signal meets minimum quality threshold.

        Args:
            min_quality: Minimum acceptable quality level

        Returns:
            True if acceptable
        """
        quality_hierarchy = {
            SignalQuality.POOR: 0,
            SignalQuality.MARGINAL: 1,
            SignalQuality.GOOD: 2,
            SignalQuality.HIGH: 3,
            SignalQuality.EXCELLENT: 4
        }

        return (quality_hierarchy[self.quality_level] >=
                quality_hierarchy[min_quality] and
                self.hallucination_risk < QualityThresholds.MAX_HALLUCINATION_RISK and
                self.factual_accuracy >= QualityThresholds.MIN_FACT_VERIFICATION)


class SignalEnhancer:
    """Enhances signal quality through multi-stage validation."""

    def __init__(self, name: str = "default", thresholds: QualityThresholds | None = None):
        """Initialize the signal enhancer.

        Args:
            name: Enhancer name for logging
            thresholds: Quality thresholds (uses defaults if not provided)
        """
        self.name = name
        self.thresholds = thresholds or QualityThresholds()

        # Statistics
        self._stats = {
            "assessments": 0,
            "accepted": 0,
            "rejected": 0,
            "average_quality": 0.0,
            "flag_distribution": {}
        }

        Logger.debug(f"Initialized SignalEnhancer: {name}")

    def assess_signal(
        self,
        content: str,
        context: dict[str, Any] | None = None
    ) -> SignalAssessment:
        """Assess the quality of content signal.

        Args:
            content: Content to assess
            context: Optional context for assessment

        Returns:
            Signal assessment
        """
        self._stats["assessments"] += 1

        # Generate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Base quality assessment
        relevance = self._assess_relevance(content, context)
        authority = self._assess_authority(content, context)
        specificity = self._assess_specificity(content)
        coherence = self._assess_coherence(content)

        # Calculate composite score
        composite = (
            relevance * 0.3 +
            authority * 0.3 +
            specificity * 0.2 +
            coherence * 0.2
        )

        # Determine quality level
        if composite >= self.thresholds.EXCELLENT_MIN:
            quality = SignalQuality.EXCELLENT
        elif composite >= self.thresholds.HIGH_MIN:
            quality = SignalQuality.HIGH
        elif composite >= self.thresholds.GOOD_MIN:
            quality = SignalQuality.GOOD
        elif composite >= self.thresholds.MARGINAL_MIN:
            quality = SignalQuality.MARGINAL
        else:
            quality = SignalQuality.POOR

        # Signal metrics
        snr = self._calculate_signal_to_noise(content)
        density = self._calculate_information_density(content)
        accuracy = self._assess_factual_accuracy(content)
        originality = self._assess_originality(content)

        # Risk analysis
        hallucination_risk = self._assess_hallucination_risk(content)
        repetition = self._calculate_repetition_ratio(content)
        claims = self._analyze_claims(content)

        # Generate flags and recommendations
        flags, recommendations = self._generate_flags_and_recommendations(
            content, composite, hallucination_risk, repetition, claims
        )

        assessment = SignalAssessment(
            content=content,
            content_hash=content_hash,
            timestamp=datetime.now(),
            relevance_score=relevance,
            authority_score=authority,
            specificity_score=specificity,
            coherence_score=coherence,
            composite_score=composite,
            quality_level=quality,
            signal_to_noise_ratio=snr,
            information_density=density,
            factual_accuracy=accuracy,
            originality_score=originality,
            hallucination_risk=hallucination_risk,
            repetition_ratio=repetition,
            claim_analyses=claims,
            flags=flags,
            recommendations=recommendations
        )

        # Update statistics
        self._update_stats(assessment)

        return assessment

    def _assess_relevance(self, content: str, context: dict[str, Any] | None) -> float:
        """Assess content relevance.

        Args:
            content: Content to assess
            context: Optional context

        Returns:
            Relevance score (0-1)
        """
        if not context or "query" not in context:
            return 0.5  # Default without context

        query = context["query"].lower()
        content_lower = content.lower()

        # Exact phrase matches
        exact_matches = len(re.findall(rf"\b{re.escape(query)}\b", content_lower))

        # Partial matches
        query_words = set(query.split())
        content_words = set(content_lower.split())
        word_overlap = len(query_words & content_words)

        # Semantic indicators
        relevance_indicators = [
            "specifically", "directly", "addresses", "answers",
            "relevant", "pertinent", "applicable"
        ]
        semantic_score = sum(1 for indicator in relevance_indicators
                           if indicator in content_lower) / len(relevance_indicators)

        # Calculate score
        score = min(1.0, (exact_matches * 0.3 + word_overlap * 0.05 + semantic_score * 0.2))

        return max(score, self.thresholds.MIN_RELEVANCE if score > 0.3 else score)

    def _assess_authority(self, content: str, context: dict[str, Any] | None) -> float:
        """Assess source authority.

        Args:
            content: Content to assess
            context: Optional context

        Returns:
            Authority score (0-1)
        """
        if not context or "sources" not in context:
            return 0.5  # Default without context

        sources = context.get("sources", [])
        if not sources:
            return 0.3  # Low authority without sources

        # Authority indicators
        high_authority_domains = [
            "edu", "gov", "org", "nature", "science", "ieee",
            "acm", "pubmed", "arxiv", "scholar"
        ]

        authority_score = 0.0
        for source in sources:
            # Check domain authority
            domain_score = 0.3 if any(domain in source.lower()
                                    for domain in high_authority_domains) else 0.1

            # Check for citations
            citation_score = 0.2 if "doi:" in source.lower() or "isbn:" in source.lower() else 0.0

            # Check recency (more recent is better for some domains)
            recency_score = 0.1  # Simplified

            authority_score += domain_score + citation_score + recency_score

        return min(1.0, authority_score / len(sources))

    def _assess_specificity(self, content: str) -> float:
        """Assess content specificity.

        Args:
            content: Content to assess

        Returns:
            Specificity score (0-1)
        """
        # Specificity indicators
        specific_patterns = [
            r"\d+(?:\.\d+)?%",  # Percentages
            r"\$\d+(?:,\d{3})*(?:\.\d+)?",  # Money
            r"\b\d{4}\b",  # Years
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b",  # Months
            r"\b\d{1,2}(?:st|nd|rd|th)\b",  # Ordinals
        ]

        specificity_count = sum(len(re.findall(pattern, content, re.IGNORECASE))
                              for pattern in specific_patterns)

        # Technical terms
        technical_words = [
            "algorithm", "methodology", "analysis", "implementation",
            "architecture", "framework", "protocol", "specification"
        ]
        tech_count = sum(1 for word in technical_words if word in content.lower())

        # Calculate specificity based on content length
        word_count = len(content.split())
        if word_count == 0:
            return 0.0

        specificity_ratio = (specificity_count + tech_count) / word_count

        # Normalize to 0-1 scale
        return min(1.0, specificity_ratio * 10)

    def _assess_coherence(self, content: str) -> float:
        """Assess content coherence.

        Args:
            content: Content to assess

        Returns:
            Coherence score (0-1)
        """
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5

        # Check for logical connectors
        connectors = [
            "however", "therefore", "furthermore", "moreover",
            "consequently", "nevertheless", "thus", "hence"
        ]
        connector_count = sum(1 for connector in connectors
                            if connector in content.lower())

        # Check sentence length variation (good coherence has variation)
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        length_score = min(1.0, variance / 50)  # Normalize

        # Check for topic consistency
        words = content.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # High frequency words indicate consistency
        if word_freq:
            max_freq = max(word_freq.values())
            consistency_score = min(1.0, max_freq / len(words) * 10)
        else:
            consistency_score = 0.0

        # Combine scores
        coherence_score = (
            (connector_count / len(sentences)) * 0.3 +
            length_score * 0.3 +
            consistency_score * 0.4
        )

        return min(1.0, coherence_score)

    def _calculate_signal_to_noise(self, content: str) -> float:
        """Calculate signal-to-noise ratio.

        Args:
            content: Content to analyze

        Returns:
            SNR value
        """
        # Signal: informative words
        signal_words = {
            "because", "therefore", "result", "conclusion", "evidence",
            "data", "analysis", "research", "study", "finding",
            "method", "approach", "technique", "algorithm", "system"
        }

        # Noise: filler words
        noise_words = {
            "um", "uh", "like", "you know", "sort of", "kind of",
            "probably", "maybe", "perhaps", "basically", "actually"
        }

        words = content.lower().split()
        signal_count = sum(1 for word in words if word in signal_words)
        noise_count = sum(1 for word in words if word in noise_words)

        if noise_count == 0:
            return min(10.0, signal_count)  # Cap at 10:1 ratio

        return signal_count / noise_count

    def _calculate_information_density(self, content: str) -> float:
        """Calculate information density.

        Args:
            content: Content to analyze

        Returns:
            Information density (0-1)
        """
        # Remove common words
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have",
            "has", "had", "do", "does", "did", "will", "would", "could", "should"
        }

        words = content.lower().split()
        unique_words = set(words) - common_words

        if not words:
            return 0.0

        # Density is ratio of unique informative words to total words
        return len(unique_words) / len(words)

    def _assess_factual_accuracy(self, content: str) -> float:
        """Assess factual accuracy (simplified).

        Args:
            content: Content to assess

        Returns:
            Accuracy score (0-1)
        """
        # Look for factual indicators
        factual_indicators = [
            r"\d{4}",  # Years
            r"\b\d+(?:\.\d+)?%",  # Percentages
            r"\$\d+(?:,\d{3})*(?:\.\d+)?",  # Money
            r"(?:according to|research shows|studies indicate|data suggests)"
        ]

        factual_count = sum(len(re.findall(pattern, content, re.IGNORECASE))
                          for pattern in factual_indicators)

        # Look for uncertainty indicators
        uncertainty_words = [
            "might", "could", "possibly", "perhaps", "maybe",
            "seems", "appears", "suggests", "potentially"
        ]

        uncertainty_count = sum(1 for word in uncertainty_words
                               if word in content.lower())

        # Calculate accuracy based on factual vs uncertainty ratio
        total_indicators = factual_count + uncertainty_count
        if total_indicators == 0:
            return 0.5  # Default

        return factual_count / total_indicators

    def _assess_originality(self, content: str) -> float:
        """Assess content originality.

        Args:
            content: Content to assess

        Returns:
            Originality score (0-1)
        """
        # Check for common phrases
        common_phrases = [
            "in conclusion", "as mentioned above", "it is important to note",
            "on the other hand", "at the end of the day", "when all is said and done"
        ]

        phrase_count = sum(1 for phrase in common_phrases
                         if phrase in content.lower())

        # Check sentence variety
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5

        # Calculate sentence length variation
        lengths = [len(s) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variety = sum(1 for length in lengths
                     if abs(length - avg_length) > avg_length * 0.3)

        variety_score = variety / len(sentences)
        phrase_penalty = min(0.5, phrase_count * 0.1)

        return max(0.0, variety_score - phrase_penalty)

    def _assess_hallucination_risk(self, content: str) -> float:
        """Assess hallucination risk.

        Args:
            content: Content to assess

        Returns:
            Hallucination risk (0-1)
        """
        # Risk indicators
        risk_patterns = [
            r"\b(?:I believe|I think|In my opinion|Personally)\b",
            r"\b(?:obviously|clearly|certainly|definitely)\b",
            r"\b(?:everyone knows|it goes without saying)\b"
        ]

        risk_count = sum(len(re.findall(pattern, content, re.IGNORECASE))
                        for pattern in risk_patterns)

        # Check for unsupported claims
        unsupported_indicators = [
            "never", "always", "only", "best", "worst",
            "impossible", "perfect", "flawless"
        ]

        unsupported_count = sum(1 for word in unsupported_indicators
                               if word in content.lower())

        # Calculate risk
        word_count = len(content.split())
        if word_count == 0:
            return 0.0

        risk_ratio = (risk_count + unsupported_count) / word_count

        return min(1.0, risk_ratio * 20)  # Scale to 0-1

    def _calculate_repetition_ratio(self, content: str) -> float:
        """Calculate repetition ratio.

        Args:
            content: Content to analyze

        Returns:
            Repetition ratio (0-1)
        """
        words = content.lower().split()
        if len(words) < 2:
            return 0.0

        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Calculate repetition
        repeated_words = sum(1 for count in word_freq.values() if count > 1)
        repetition_ratio = repeated_words / len(words)

        return repetition_ratio

    def _analyze_claims(self, content: str) -> list[ClaimAnalysis]:
        """Analyze claims in content.

        Args:
            content: Content to analyze

        Returns:
            List of Claim analyses
        """
        # Simplified Claim extraction
        claim_patterns = [
            r"([^.]*(?:is|are|shows|indicates|proves|demonstrates)[^.]*\.)",
            r"([^.]*(?:according to|research|study|data)[^.]*\.)"
        ]

        claims = []
        for pattern in claim_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Simplified analysis
                confidence = 0.7 if "according to" in match.lower() else 0.5
                verifiable = "according to" in match.lower() or "study" in match.lower()

                Claim = ClaimAnalysis(
                    Claim=match.strip(),
                    confidence=confidence,
                    verifiable=verifiable,
                    sources=[],  # Would extract in real implementation
                    risk_level="low" if confidence > 0.7 else "medium"
                )
                claims.append(Claim)

        return claims[:5]  # Limit to top 5 claims

    def _generate_flags_and_recommendations(
        self,
        content: str,
        composite_score: float,
        hallucination_risk: float,
        repetition_ratio: float,
        claims: list[ClaimAnalysis]
    ) -> tuple[list[str], list[str]]:
        """Generate flags and recommendations.

        Args:
            content: Content being assessed
            composite_score: Overall quality score
            hallucination_risk: Hallucination risk
            repetition_ratio: Repetition ratio
            claims: Claim analyses

        Returns:
            Tuple of (flags, recommendations)
        """
        flags = []
        recommendations = []

        # Flags
        if composite_score < self.thresholds.GOOD_MIN:
            flags.append("LOW_QUALITY")

        if hallucination_risk > self.thresholds.MAX_HALLUCINATION_RISK:
            flags.append("HALLUCINATION_RISK")

        if repetition_ratio > self.thresholds.MAX_REPETITION_RATIO:
            flags.append("HIGHLY_REPETITIVE")

        if len(content.split()) < 50:
            flags.append("TOO_BRIEF")

        unverifiable_claims = [c for c in claims if not c.verifiable]
        if len(unverifiable_claims) > len(claims) * 0.5:
            flags.append("UNVERIFIABLE_CLAIMS")

        # Recommendations
        if hallucination_risk > 0.3:
            recommendations.append("Reduce speculative language and add supporting evidence")

        if repetition_ratio > 0.3:
            recommendations.append("Vary sentence structure and avoid repetition")

        if composite_score < 0.7:
            recommendations.append("Add specific examples and data to strengthen claims")

        if not any("according to" in c.Claim.lower() for c in claims):
            recommendations.append("Include sources or references for key claims")

        return flags, recommendations

    def _update_stats(self, assessment: SignalAssessment) -> None:
        """Update internal statistics.

        Args:
            assessment: Latest assessment
        """
        if assessment.is_acceptable():
            self._stats["accepted"] += 1
        else:
            self._stats["rejected"] += 1

        # Update average quality
        total = self._stats["assessments"]
        current_avg = self._stats["average_quality"]
        self._stats["average_quality"] = (
            (current_avg * (total - 1) + assessment.composite_score) / total
        )

        # Update flag distribution
        for flag in assessment.flags:
            self._stats["flag_distribution"][flag] = (
                self._stats["flag_distribution"].get(flag, 0) + 1
            )

    def get_stats(self) -> dict[str, Any]:
        """Get enhancer statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        if stats["assessments"] > 0:
            stats["acceptance_rate"] = stats["accepted"] / stats["assessments"]
        else:
            stats["acceptance_rate"] = 0.0

        return stats


# Global enhancer registry
_enhancers: dict[str, SignalEnhancer] = {}


def get_signal_enhancer(name: str = "default", thresholds: QualityThresholds | None = None) -> SignalEnhancer:
    """Get or create a signal enhancer.

    Args:
        name: Enhancer name
        thresholds: Optional quality thresholds

    Returns:
        SignalEnhancer instance
    """
    if name not in _enhancers:
        _enhancers[name] = SignalEnhancer(name, thresholds)
    return _enhancers[name]
