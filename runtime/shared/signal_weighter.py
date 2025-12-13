"""Dynamic Signal Weighter - Archetype-Aware Document Scoring.

This module provides dynamic weighting of retrieved documents based on recipient
archetype and industry, enabling more relevant content selection for personalized
outreach and resume generation.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Union


logger = logging.getLogger(__name__)


@dataclass
class SignalWeights:
    """Weight coefficients for different signal types (0.0-1.0)."""
    
    technical_depth: float = 0.5  # Weight for code samples, stack details, architecture
    business_impact: float = 0.5  # Weight for revenue, % growth, cost savings
    leadership_scope: float = 0.5  # Weight for team size, mentorship, strategic initiatives
    cultural_fit: float = 0.5  # Weight for soft skills, mission alignment
    
    def __post_init__(self):
        """Validate weight ranges."""
        for field_name, value in self.__dict__.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"Weight {field_name} must be a number, got {type(value)}")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Weight {field_name} must be between 0.0 and 1.0, got {value}")
    
    def as_dict(self) -> Dict[str, float]:
        """Convert weights to dictionary."""
        return {
            "technical_depth": self.technical_depth,
            "business_impact": self.business_impact,
            "leadership_scope": self.leadership_scope,
            "cultural_fit": self.cultural_fit,
        }


@dataclass
class WeightingResult:
    """Result of reweighting operation."""
    
    original_score: float
    adjusted_score: float
    weights_applied: SignalWeights
    signal_type: str
    adjustment_factor: float
    
    @property
    def score_change(self) -> float:
        """Calculate the change in score."""
        return self.adjusted_score - self.original_score
    
    @property
    def percent_change(self) -> float:
        """Calculate percentage change."""
        if self.original_score == 0:
            return 0.0
        return (self.score_change / self.original_score) * 100


class SignalWeighter:
    """Dynamic signal weighter for archetype-aware document scoring.
    
    This component adjusts relevance scores of retrieved documents based on the
    target recipient's persona (e.g., CTO vs. Recruiter) and industry context.
    """
    
    def __init__(self, default_weights: Optional[SignalWeights] = None):
        """Initialize the signal weighter.
        
        Args:
            default_weights: Default weights to use when no specific mapping exists
        """
        self.default_weights = default_weights or SignalWeights()
        
        # Archetype weight mappings
        self._archetype_mappings = {
            # Technical Leadership
            "CTO": SignalWeights(
                technical_depth=0.9,
                leadership_scope=0.7,
                business_impact=0.4,
                cultural_fit=0.3
            ),
            "VP Engineering": SignalWeights(
                technical_depth=0.8,
                leadership_scope=0.8,
                business_impact=0.5,
                cultural_fit=0.4
            ),
            "Engineering Manager": SignalWeights(
                technical_depth=0.6,
                leadership_scope=0.9,
                business_impact=0.4,
                cultural_fit=0.6
            ),
            "Staff Engineer": SignalWeights(
                technical_depth=1.0,
                leadership_scope=0.4,
                business_impact=0.3,
                cultural_fit=0.5
            ),
            "Principal Engineer": SignalWeights(
                technical_depth=1.0,
                leadership_scope=0.5,
                business_impact=0.4,
                cultural_fit=0.5
            ),
            
            # Executive Leadership
            "CEO": SignalWeights(
                technical_depth=0.3,
                leadership_scope=0.8,
                business_impact=1.0,
                cultural_fit=0.7
            ),
            "Founder": SignalWeights(
                technical_depth=0.4,
                leadership_scope=0.7,
                business_impact=1.0,
                cultural_fit=0.8
            ),
            "CFO": SignalWeights(
                technical_depth=0.2,
                leadership_scope=0.6,
                business_impact=1.0,
                cultural_fit=0.5
            ),
            
            # Product & Design
            "CPO": SignalWeights(
                technical_depth=0.5,
                leadership_scope=0.6,
                business_impact=0.7,
                cultural_fit=0.9
            ),
            "VP Product": SignalWeights(
                technical_depth=0.4,
                leadership_scope=0.7,
                business_impact=0.8,
                cultural_fit=0.8
            ),
            "Product Manager": SignalWeights(
                technical_depth=0.5,
                leadership_scope=0.5,
                business_impact=0.7,
                cultural_fit=0.8
            ),
            
            # Talent & HR
            "Recruiter": SignalWeights(
                technical_depth=0.5,
                leadership_scope=0.4,
                business_impact=0.5,
                cultural_fit=0.9
            ),
            "Talent Acquisition": SignalWeights(
                technical_depth=0.5,
                leadership_scope=0.4,
                business_impact=0.5,
                cultural_fit=0.9
            ),
            "HR Manager": SignalWeights(
                technical_depth=0.3,
                leadership_scope=0.5,
                business_impact=0.6,
                cultural_fit=1.0
            ),
            
            # Sales & Marketing
            "VP Sales": SignalWeights(
                technical_depth=0.3,
                leadership_scope=0.6,
                business_impact=1.0,
                cultural_fit=0.7
            ),
            "Account Executive": SignalWeights(
                technical_depth=0.3,
                leadership_scope=0.4,
                business_impact=0.9,
                cultural_fit=0.8
            ),
        }
        
        # Industry-specific adjustments
        self._industry_modifiers = {
            "technology": {
                "technical_depth": 1.2,
                "business_impact": 0.9,
                "leadership_scope": 1.0,
                "cultural_fit": 0.9
            },
            "finance": {
                "technical_depth": 0.7,
                "business_impact": 1.2,
                "leadership_scope": 1.1,
                "cultural_fit": 0.8
            },
            "healthcare": {
                "technical_depth": 0.9,
                "business_impact": 0.8,
                "leadership_scope": 1.0,
                "cultural_fit": 1.1
            },
            "retail": {
                "technical_depth": 0.6,
                "business_impact": 1.1,
                "leadership_scope": 0.9,
                "cultural_fit": 1.0
            },
            "consulting": {
                "technical_depth": 0.8,
                "business_impact": 1.1,
                "leadership_scope": 1.0,
                "cultural_fit": 0.9
            }
        }
        
        logger.info(f"Initialized SignalWeighter with {len(self._archetype_mappings)} archetype mappings")
    
    def get_weights(self, archetype: str, industry: Optional[str] = None) -> SignalWeights:
        """Get weights for a specific archetype and industry.
        
        Args:
            archetype: Target recipient archetype (e.g., "CTO", "Recruiter")
            industry: Industry context for additional adjustment (optional)
            
        Returns:
            SignalWeights configured for the archetype and industry
        """
        # Get base weights for archetype
        base_weights = self._archetype_mappings.get(archetype, self.default_weights)
        
        # Apply industry modifiers if provided
        if industry and industry.lower() in self._industry_modifiers:
            modifiers = self._industry_modifiers[industry.lower()]
            
            # Create adjusted weights
            adjusted_weights = SignalWeights(
                technical_depth=min(1.0, base_weights.technical_depth * modifiers["technical_depth"]),
                business_impact=min(1.0, base_weights.business_impact * modifiers["business_impact"]),
                leadership_scope=min(1.0, base_weights.leadership_scope * modifiers["leadership_scope"]),
                cultural_fit=min(1.0, base_weights.cultural_fit * modifiers["cultural_fit"])
            )
            
            logger.debug(f"Applied industry modifiers for {industry}: {base_weights.as_dict()} -> {adjusted_weights.as_dict()}")
            return adjusted_weights
        
        logger.debug(f"Using base weights for archetype {archetype}: {base_weights.as_dict()}")
        return base_weights
    
    def reweight_score(
        self,
        original_score: float,
        doc_metadata: Dict[str, Union[str, float]],
        weights: SignalWeights
    ) -> WeightingResult:
        """Apply dynamic weighting to a document score.
        
        Args:
            original_score: Original relevance score (0.0-1.0)
            doc_metadata: Document metadata with signal type tags
            weights: SignalWeights to apply
            
        Returns:
            WeightingResult with adjusted score and metadata
        """
        if not 0.0 <= original_score <= 1.0:
            raise ValueError(f"Original score must be between 0.0 and 1.0, got {original_score}")
        
        # Determine signal type from metadata
        signal_type = self._extract_signal_type(doc_metadata)
        
        # Get the appropriate weight
        weight = self._get_weight_for_signal_type(signal_type, weights)
        
        # Apply weight to score
        adjusted_score = original_score * weight
        
        # Ensure score stays within bounds
        adjusted_score = max(0.0, min(1.0, adjusted_score))
        
        result = WeightingResult(
            original_score=original_score,
            adjusted_score=adjusted_score,
            weights_applied=weights,
            signal_type=signal_type,
            adjustment_factor=weight
        )
        
        logger.debug(
            f"Reweighted score: {original_score:.3f} -> {adjusted_score:.3f} "
            f"(signal: {signal_type}, weight: {weight:.2f})"
        )
        
        return result
    
    def _extract_signal_type(self, metadata: Dict[str, Union[str, float]]) -> str:
        """Extract signal type from document metadata.
        
        Args:
            metadata: Document metadata
            
        Returns:
            Signal type string
        """
        # Check explicit type field
        if "type" in metadata:
            return str(metadata["type"])
        
        # Check category field
        if "category" in metadata:
            return str(metadata["category"])
        
        # Check tags
        if "tags" in metadata and metadata["tags"]:
            if isinstance(metadata["tags"], list):
                return str(metadata["tags"][0])
            else:
                return str(metadata["tags"])
        
        # Infer from content keywords
        content_lower = str(metadata.get("content", "")).lower()
        if any(keyword in content_lower for keyword in ["revenue", "growth", "savings", "roi"]):
            return "business_impact"
        elif any(keyword in content_lower for keyword in ["team", "managed", "led", "mentorship"]):
            return "leadership_scope"
        elif any(keyword in content_lower for keyword in ["python", "java", "architecture", "algorithm"]):
            return "technical_depth"
        elif any(keyword in content_lower for keyword in ["culture", "mission", "values", "collaboration"]):
            return "cultural_fit"
        
        # Default to balanced weighting
        return "balanced"
    
    def _get_weight_for_signal_type(self, signal_type: str, weights: SignalWeights) -> float:
        """Get the appropriate weight for a signal type.
        
        Args:
            signal_type: Type of signal
            weights: SignalWeights to extract from
            
        Returns:
            Weight value for the signal type
        """
        weight_map = {
            "technical_depth": weights.technical_depth,
            "technical": weights.technical_depth,
            "business_impact": weights.business_impact,
            "business": weights.business_impact,
            "leadership_scope": weights.leadership_scope,
            "leadership": weights.leadership_scope,
            "cultural_fit": weights.cultural_fit,
            "cultural": weights.cultural_fit,
            "balanced": 0.5  # Average weight for balanced signals
        }
        
        return weight_map.get(signal_type.lower(), 0.5)
    
    def batch_reweight(
        self,
        documents: List[Dict[str, Union[str, float]]],
        archetype: str,
        industry: Optional[str] = None
    ) -> List[WeightingResult]:
        """Apply dynamic weighting to a batch of documents.
        
        Args:
            documents: List of documents with scores and metadata
            archetype: Target recipient archetype
            industry: Industry context (optional)
            
        Returns:
            List of WeightingResult objects
        """
        weights = self.get_weights(archetype, industry)
        results = []
        
        for doc in documents:
            score = float(doc.get("score", 0.0))
            metadata = {k: v for k, v in doc.items() if k != "score"}
            result = self.reweight_score(score, metadata, weights)
            results.append(result)
        
        return results


# Factory function for easy instantiation
def create_signal_weighter(default_weights: Optional[SignalWeights] = None) -> SignalWeighter:
    """Create a SignalWeighter instance.
    
    Args:
        default_weights: Default weights to use
        
    Returns:
        Configured SignalWeighter instance
    """
    return SignalWeighter(default_weights=default_weights)


# Convenience function for quick reweighting
def weight_results(
    documents: List[Dict[str, Union[str, float]]],
    archetype: str,
    industry: Optional[str] = None
) -> List[WeightingResult]:
    """Quickly weight a batch of results for an archetype.
    
    Args:
        documents: List of documents with scores and metadata
        archetype: Target recipient archetype
        industry: Industry context (optional)
        
    Returns:
        List of WeightingResult objects
    """
    weighter = create_signal_weighter()
    return weighter.batch_reweight(documents, archetype, industry)
