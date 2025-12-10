"""
Claim Confidence Scorer - Atomic Claim Extraction and Confidence Scoring
Ported from legacy_engines/lic_insights.py

Extracts atomic claims from content and scores confidence
based on source verification and evidence support.
"""

import logging
import re
from typing import Dict, List, object, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ClaimType(Enum):
    """Types of claims"""
    FACTUAL = "factual"
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    COMPARATIVE = "comparative"
    CAUSAL = "causal"
    TEMPORAL = "temporal"


class ConfidenceLevel(Enum):
    """Confidence levels for claims"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"


@dataclass
class Claim:
    """Individual claim extracted from content"""
    claim_id: str
    text: str
    claim_type: ClaimType
    confidence_score: float
    confidence_level: ConfidenceLevel
    source_support: bool
    deductions: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ClaimAnalysisResult:
    """Result of claim analysis"""
    original_content: str
    claims: List[Claim]
    aggregate_confidence: float
    claims_below_threshold: int
    total_claims: int
    meets_threshold: bool
    recommendations: List[str] = field(default_factory=list)


class ClaimConfidenceScorer:
    """
    Claim Confidence Scoring System
    
    Extracts atomic claims from content and scores confidence
    based on source verification and evidence support.
    """
    
    def __init__(
        self,
        per_claim_minimum: float = 0.8,
        aggregate_minimum: float = 0.9,
        claim_splitters: Optional[List[str]] = None
    ):
        """
        Initialize claim confidence scorer.
        
        Args:
            per_claim_minimum: Minimum confidence per claim
            aggregate_minimum: Minimum aggregate confidence
            claim_splitters: Patterns to split claims
        """
        self.per_claim_minimum = per_claim_minimum
        self.aggregate_minimum = aggregate_minimum
        self.claim_splitters = claim_splitters or [".", " and ", " while ", " by ", "; "]
        
        # Deduction rules
        self.deduction_rules = [
            {
                "condition": "no_source",
                "penalty": -0.2,
                "description": "No RAG source found for claim"
            },
            {
                "condition": "unsourced_metric",
                "penalty": -0.15,
                "description": "Metric has no source mapping"
            },
            {
                "condition": "unauthorized_entity",
                "penalty": -0.1,
                "description": "Entity not in verified list"
            },
            {
                "condition": "role_drift",
                "penalty": -0.1,
                "description": "Role terminology drifted from source"
            },
            {
                "condition": "low_coherence",
                "penalty": -0.2,
                "description": "Low context coherence with sources"
            }
        ]
    
    def analyze_claims(
        self,
        content: str,
        sources: Optional[List[Dict[str, object]]] = None,
        context: Optional[Dict[str, object]] = None
    ) -> ClaimAnalysisResult:
        """
        Analyze claims in content and score confidence.
        
        Args:
            content: Content to analyze
            sources: RAG sources for verification
            context: Additional context
            
        Returns:
            ClaimAnalysisResult with scored claims
        """
        sources = sources or []
        context = context or {}
        
        # Extract claims
        raw_claims = self.extract_claims(content)
        
        # Score each claim
        scored_claims = []
        for i, claim_text in enumerate(raw_claims):
            claim = self.score_claim(claim_text, sources, i)
            scored_claims.append(claim)
        
        # Calculate aggregate confidence
        if scored_claims:
            aggregate_confidence = sum(c.confidence_score for c in scored_claims) / len(scored_claims)
        else:
            aggregate_confidence = 0.0
        
        # Count claims below threshold
        claims_below = sum(1 for c in scored_claims if c.confidence_score < self.per_claim_minimum)
        
        # Check if meets threshold
        meets_threshold = aggregate_confidence >= self.aggregate_minimum
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scored_claims, aggregate_confidence)
        
        logger.info(f"Analyzed {len(scored_claims)} claims, aggregate confidence: {aggregate_confidence:.2f}")
        
        return ClaimAnalysisResult(
            original_content=content,
            claims=scored_claims,
            aggregate_confidence=round(aggregate_confidence, 4),
            claims_below_threshold=claims_below,
            total_claims=len(scored_claims),
            meets_threshold=meets_threshold,
            recommendations=recommendations
        )
    
    def extract_claims(self, content: str) -> List[str]:
        """
        Extract atomic claims from content.
        
        Args:
            content: Content to extract claims from
            
        Returns:
            List of claim strings
        """
        if not content:
            return []
        
        # Split by claim splitters
        claims = [content]
        for splitter in self.claim_splitters:
            new_claims = []
            for claim in claims:
                parts = claim.split(splitter)
                new_claims.extend(parts)
            claims = new_claims
        
        # Clean and filter claims
        cleaned_claims = []
        claim_indicators = [
            "i", "my", "our", "we", "led", "built", "created", "improved",
            "reduced", "increased", "developed", "managed", "achieved",
            "delivered", "implemented", "designed", "launched", "grew"
        ]
        
        for claim in claims:
            claim = claim.strip()
            # Filter out very short or non-claim phrases
            if len(claim) > 15:
                claim_lower = claim.lower()
                if any(indicator in claim_lower for indicator in claim_indicators):
                    cleaned_claims.append(claim)
        
        return cleaned_claims
    
    def score_claim(
        self,
        claim_text: str,
        sources: List[Dict[str, object]],
        claim_index: int
    ) -> Claim:
        """
        Score confidence of a single claim.
        
        Args:
            claim_text: Claim text to score
            sources: RAG sources for verification
            claim_index: Index of claim
            
        Returns:
            Scored Claim object
        """
        base_score = 1.0
        deductions = []
        
        # Check for source support
        has_source_support = self._check_source_support(claim_text, sources)
        if not has_source_support:
            base_score -= 0.2
            deductions.append("No RAG source found for claim")
        
        # Check for unsourced metrics
        if self._has_unsourced_metric(claim_text, sources):
            base_score -= 0.15
            deductions.append("Metric has no source mapping")
        
        # Check for unauthorized entities
        if self._has_unauthorized_entity(claim_text, sources):
            base_score -= 0.1
            deductions.append("Entity not in verified list")
        
        # Check for role drift
        if self._has_role_drift(claim_text, sources):
            base_score -= 0.1
            deductions.append("Role terminology drifted from source")
        
        # Check coherence
        if self._has_low_coherence(claim_text, sources):
            base_score -= 0.2
            deductions.append("Low context coherence with sources")
        
        # Ensure score doesn't go below 0
        final_score = max(0.0, base_score)
        
        # Determine claim type
        claim_type = self._determine_claim_type(claim_text)
        
        # Determine confidence level
        if final_score >= 0.9:
            confidence_level = ConfidenceLevel.HIGH
        elif final_score >= 0.7:
            confidence_level = ConfidenceLevel.MEDIUM
        elif final_score >= 0.5:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.UNVERIFIED
        
        return Claim(
            claim_id=f"claim_{claim_index}",
            text=claim_text,
            claim_type=claim_type,
            confidence_score=round(final_score, 4),
            confidence_level=confidence_level,
            source_support=has_source_support,
            deductions=deductions
        )
    
    def _check_source_support(self, claim: str, sources: List[Dict[str, object]]) -> bool:
        """Check if claim is supported by sources."""
        if not sources:
            return False
        
        claim_words = set(claim.lower().split())
        
        for source in sources:
            content = source.get('content', '').lower()
            content_words = set(content.split())
            
            # Check for word overlap
            overlap = len(claim_words & content_words)
            if overlap >= len(claim_words) * 0.4:  # 40% overlap threshold
                return True
        
        return False
    
    def _has_unsourced_metric(self, claim: str, sources: List[Dict[str, object]]) -> bool:
        """Check if claim has metrics without source mapping."""
        # Extract metrics from claim
        metric_pattern = r'(\d+%|\d+x|\d+\.?\d*\s*(?:million|billion|thousand|k|m|b))'
        metrics = re.findall(metric_pattern, claim, re.IGNORECASE)
        
        if not metrics:
            return False
        
        # Check if metrics are found in sources
        for metric in metrics:
            metric_found = False
            for source in sources:
                if metric.lower() in source.get('content', '').lower():
                    metric_found = True
                    break
            
            if not metric_found:
                return True
        
        return False
    
    def _has_unauthorized_entity(self, claim: str, sources: List[Dict[str, object]]) -> bool:
        """Check if claim mentions unauthorized entities."""
        # Extract potential company/organization names
        entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|LLC|Ltd|Co))?\b'
        entities = re.findall(entity_pattern, claim)
        
        if not entities:
            return False
        
        # Build authorized entities from sources
        authorized = set()
        for source in sources:
            content = source.get('content', '')
            source_entities = re.findall(entity_pattern, content)
            authorized.update(source_entities)
        
        # Check for unauthorized entities
        for entity in entities:
            if entity not in authorized and len(entity) > 3:
                return True
        
        return False
    
    def _has_role_drift(self, claim: str, sources: List[Dict[str, object]]) -> bool:
        """Check for role terminology drift."""
        role_keywords = [
            "engineer", "developer", "coordinator", "director", "lead",
            "architect", "analyst", "specialist", "coordinator", "executive"
        ]
        
        claim_roles = [kw for kw in role_keywords if kw in claim.lower()]
        
        if not claim_roles:
            return False
        
        # Check if roles appear in sources
        for role in claim_roles:
            role_found = False
            for source in sources:
                if role in source.get('content', '').lower():
                    role_found = True
                    break
            
            if not role_found:
                return True
        
        return False
    
    def _has_low_coherence(self, claim: str, sources: List[Dict[str, object]]) -> bool:
        """Check for low context coherence."""
        if not sources:
            return True
        
        claim_words = set(claim.lower().split())
        
        max_overlap = 0.0
        for source in sources:
            content_words = set(source.get('content', '').lower().split())
            
            if claim_words and content_words:
                overlap = len(claim_words & content_words) / len(claim_words | content_words)
                max_overlap = max(max_overlap, overlap)
        
        return max_overlap < 0.15  # Low coherence threshold
    
    def _determine_claim_type(self, claim: str) -> ClaimType:
        """Determine the type of claim."""
        claim_lower = claim.lower()
        
        # Check for quantitative claims
        if re.search(r'\d+%|\d+x|\$\d+|\d+\s*(?:million|billion|thousand)', claim_lower):
            return ClaimType.QUANTITATIVE
        
        # Check for comparative claims
        if any(word in claim_lower for word in ['more than', 'less than', 'better', 'worse', 'compared']):
            return ClaimType.COMPARATIVE
        
        # Check for causal claims
        if any(word in claim_lower for word in ['because', 'caused', 'resulted', 'led to', 'due to']):
            return ClaimType.CAUSAL
        
        # Check for temporal claims
        if any(word in claim_lower for word in ['before', 'after', 'during', 'since', 'until']):
            return ClaimType.TEMPORAL
        
        # Check for qualitative claims
        if any(word in claim_lower for word in ['excellent', 'good', 'bad', 'best', 'worst', 'quality']):
            return ClaimType.QUALITATIVE
        
        return ClaimType.FACTUAL
    
    def _generate_recommendations(
        self,
        claims: List[Claim],
        aggregate_confidence: float
    ) -> List[str]:
        """Generate recommendations based on claim analysis."""
        recommendations = []
        
        if aggregate_confidence < self.aggregate_minimum:
            recommendations.append(
                f"Aggregate confidence ({aggregate_confidence:.2f}) is below threshold ({self.aggregate_minimum})"
            )
        
        # Count claims by confidence level
        low_confidence = [c for c in claims if c.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.UNVERIFIED]]
        if low_confidence:
            recommendations.append(
                f"{len(low_confidence)} claims have low or unverified confidence - consider adding sources"
            )
        
        # Check for shared deductions
        deduction_counts: Dict[str, int] = {}
        for claim in claims:
            for deduction in claim.deductions:
                deduction_counts[deduction] = deduction_counts.get(deduction, 0) + 1
        
        for deduction, count in sorted(deduction_counts.items(), key=lambda x: x[1], reverse=True):
            if count >= 2:
                recommendations.append(f"shared issue: {deduction} ({count} claims)")
        
        return recommendations
    
    def get_analysis_summary(self, result: ClaimAnalysisResult) -> Dict[str, object]:
        """Get summary of claim analysis."""
        confidence_distribution = {
            ConfidenceLevel.HIGH.value: 0,
            ConfidenceLevel.MEDIUM.value: 0,
            ConfidenceLevel.LOW.value: 0,
            ConfidenceLevel.UNVERIFIED.value: 0
        }
        
        for claim in result.claims:
            confidence_distribution[claim.confidence_level.value] += 1
        
        return {
            'total_claims': result.total_claims,
            'aggregate_confidence': result.aggregate_confidence,
            'meets_threshold': result.meets_threshold,
            'claims_below_threshold': result.claims_below_threshold,
            'confidence_distribution': confidence_distribution,
            'recommendations_count': len(result.recommendations)
        }


# builder functions
def create_claim_scorer(
    per_claim_minimum: float = 0.8,
    aggregate_minimum: float = 0.9
) -> ClaimConfidenceScorer:
    """Create claim confidence scorer instance."""
    return ClaimConfidenceScorer(per_claim_minimum, aggregate_minimum)


def analyze_claims(
    content: str,
    sources: Optional[List[Dict[str, object]]] = None
) -> ClaimAnalysisResult:
    """Convenience function to analyze claims."""
    scorer = ClaimConfidenceScorer()
    return scorer.analyze_claims(content, sources)
