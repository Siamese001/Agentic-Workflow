"""Hybrid Scorer - Dense + Sparse + Context Scoring Engine.

This module provides a scoring engine that combines Semantic (Vector) scores with
Keyword (BM25) scores, with proper normalization and context boosts for industry
alignment and hero content prioritization.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from pydantic import BaseModel, Field, validator


logger = logging.getLogger(__name__)


class HybridScoreResult(BaseModel):
    """Result of hybrid scoring with component scores."""
    
    doc_id: str = Field(..., description="Document identifier")
    final_score: float = Field(..., ge=0.0, le=1.0, description="Final combined score")
    dense_score: float = Field(..., ge=0.0, le=1.0, description="Dense (vector) score")
    sparse_score: float = Field(..., ge=0.0, le=1.0, description="Sparse (BM25) score, normalized")
    metadata_boost: float = Field(..., ge=0.0, le=1.0, description="Context/industry boost applied")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    @validator('sparse_score', pre=True)
    def validate_sparse_score(cls, v):
        """Ensure sparse score is properly normalized."""
        if isinstance(v, (int, float)):
            return max(0.0, min(1.0, v))
        return v
    
    @property
    def is_boosted(self) -> bool:
        """Check if result received a boost."""
        return self.metadata_boost > 0
    
    @property
    def score_breakdown(self) -> Dict[str, float]:
        """Get breakdown of score components."""
        return {
            "dense": self.dense_score,
            "sparse": self.sparse_score,
            "boost": self.metadata_boost,
            "final": self.final_score
        }


class HybridScorer:
    """Hybrid scorer that combines dense and sparse scores with context boosts.
    
    This scorer properly normalizes different score types and applies contextual
    boosts for industry matching and hero content prioritization.
    """
    
    def __init__(
        self,
        alpha: float = 0.7,
        industry_boost: float = 0.15,
        hero_boost: float = 0.1,
        max_score: float = 1.0
    ):
        """Initialize the hybrid scorer.
        
        Args:
            alpha: Weight for dense (vector) scores vs sparse (0.0-1.0)
            industry_boost: Boost amount for industry matches
            hero_boost: Boost amount for hero content
            max_score: Maximum allowed score (cap)
        """
        self.alpha = max(0.0, min(1.0, alpha))  # Clamp to valid range
        self.industry_boost = max(0.0, industry_boost)
        self.hero_boost = max(0.0, hero_boost)
        self.max_score = max(0.0, max_score)
        
        logger.info(f"Initialized HybridScorer: alpha={self.alpha}, "
                   f"industry_boost={self.industry_boost}, hero_boost={self.hero_boost}")
    
    def score_documents(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        target_industry: Optional[str] = None
    ) -> List[HybridScoreResult]:
        """Score documents using hybrid approach.
        
        Args:
            dense_results: List of dense (vector) search results
            sparse_results: List of sparse (BM25) search results
            target_industry: Target industry for context boosting
            
        Returns:
            List of HybridScoreResult sorted by final_score descending
        """
        try:
            # Validate inputs
            if not isinstance(dense_results, list):
                logger.warning("Invalid dense_results type, using empty list")
                dense_results = []
            
            if not isinstance(sparse_results, list):
                logger.warning("Invalid sparse_results type, using empty list")
                sparse_results = []
            
            # Normalize sparse scores
            normalized_sparse = self._normalize_scores(sparse_results)
            
            # Combine scores
            hybrid_results = self.compute_hybrid(dense_results, normalized_sparse)
            
            # Apply context boosts
            boosted_results = self._apply_boosts(hybrid_results, target_industry)
            
            # Sort by final score
            boosted_results.sort(key=lambda x: x.final_score, reverse=True)
            
            logger.info(f"Hybrid scoring: {len(dense_results)} dense, "
                       f"{len(sparse_results)} sparse, {len(boosted_results)} final")
            
            return boosted_results
            
        except Exception as e:
            logger.error(f"Error in score_documents: {str(e)}")
            return []
    
    def _normalize_scores(self, sparse_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Normalize sparse scores using Min-Max normalization.
        
        Args:
            sparse_results: List of sparse results with unnormalized scores
            
        Returns:
            Dictionary mapping doc_id to normalized score (0.0-1.0)
        """
        try:
            if not sparse_results:
                return {}
            
            # Extract scores with validation
            scores = []
            valid_results = []
            
            for result in sparse_results:
                try:
                    doc_id = result.get("doc_id")
                    score = float(result.get("score", 0.0))
                    
                    if doc_id is not None:
                        scores.append(score)
                        valid_results.append((doc_id, score))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid score in sparse results: {e}")
                    continue
            
            if not scores:
                return {}
            
            # Handle edge case: all scores are the same
            min_score = min(scores)
            max_score = max(scores)
            
            if max_score == min_score:
                # All scores equal, return 1.0 for all
                return {doc_id: 1.0 for doc_id, _ in valid_results}
            
            # Apply Min-Max normalization
            normalized = {}
            score_range = max_score - min_score
            
            for doc_id, raw_score in valid_results:
                # Normalize to 0-1 range
                normalized_score = (raw_score - min_score) / score_range
                normalized[doc_id] = max(0.0, min(1.0, normalized_score))
            
            logger.debug(f"Normalized sparse scores: min={min_score:.3f}, "
                        f"max={max_score:.3f}, range={score_range:.3f}")
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing scores: {str(e)}")
            return {}
    
    def compute_hybrid(
        self,
        dense_results: List[Dict[str, Any]],
        normalized_sparse: Dict[str, float]
    ) -> List[HybridScoreResult]:
        """Combine dense and sparse scores using weighted sum.
        
        Args:
            dense_results: List of dense results
            normalized_sparse: Dictionary of normalized sparse scores
            
        Returns:
            List of HybridScoreResult with combined scores
        """
        try:
            hybrid_results = []
            
            # Create lookup for sparse scores
            sparse_lookup = normalized_sparse
            
            # Process each dense result
            for idx, dense_result in enumerate(dense_results):
                try:
                    # Extract and validate data
                    doc_id = dense_result.get("doc_id")
                    if doc_id is None:
                        logger.warning(f"Dense result at index {idx} missing doc_id")
                        continue
                    
                    dense_score = float(dense_result.get("score", 0.0))
                    dense_score = max(0.0, min(1.0, dense_score))  # Clamp to [0,1]
                    
                    # Get corresponding sparse score (default 0 if not found)
                    sparse_score = sparse_lookup.get(doc_id, 0.0)
                    
                    # Calculate weighted combination
                    base_score = (dense_score * self.alpha) + (sparse_score * (1 - self.alpha))
                    base_score = max(0.0, min(1.0, base_score))  # Clamp to [0,1]
                    
                    # Create hybrid result
                    hybrid = HybridScoreResult(
                        doc_id=doc_id,
                        final_score=base_score,
                        dense_score=dense_score,
                        sparse_score=sparse_score,
                        metadata_boost=0.0,
                        metadata=dense_result.get("metadata", {})
                    )
                    
                    hybrid_results.append(hybrid)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing dense result at index {idx}: {e}")
                    continue
            
            # Also include documents that only appear in sparse results
            sparse_only_docs = set(sparse_lookup.keys()) - set(r.doc_id for r in hybrid_results)
            
            for doc_id in sparse_only_docs:
                try:
                    sparse_score = sparse_lookup[doc_id]
                    
                    # Only dense score is 0, so final score is just sparse
                    base_score = sparse_score * (1 - self.alpha)
                    base_score = max(0.0, min(1.0, base_score))
                    
                    hybrid = HybridScoreResult(
                        doc_id=doc_id,
                        final_score=base_score,
                        dense_score=0.0,
                        sparse_score=sparse_score,
                        metadata_boost=0.0,
                        metadata={}
                    )
                    
                    hybrid_results.append(hybrid)
                    
                except Exception as e:
                    logger.warning(f"Error processing sparse-only doc {doc_id}: {e}")
                    continue
            
            logger.debug(f"Combined scores: {len(hybrid_results)} total documents")
            
            return hybrid_results
            
        except Exception as e:
            logger.error(f"Error computing hybrid scores: {str(e)}")
            return []
    
    def _apply_boosts(
        self,
        hybrid_results: List[HybridScoreResult],
        target_industry: Optional[str] = None
    ) -> List[HybridScoreResult]:
        """Apply context boosts to hybrid scores.
        
        Args:
            hybrid_results: List of hybrid score results
            target_industry: Target industry for matching
            
        Returns:
            List of boosted HybridScoreResult
        """
        try:
            boosted_results = []
            boosted_count = 0
            
            for result in hybrid_results:
                boost_amount = 0.0
                metadata = result.metadata
                
                # Ensure metadata is a dictionary
                if not isinstance(metadata, dict):
                    metadata = {}
                
                # Industry match boost
                if target_industry and self._matches_industry(metadata, target_industry):
                    boost_amount += self.industry_boost
                    logger.debug(f"Applied industry boost to {result.doc_id}: +{self.industry_boost}")
                
                # Hero content boost
                if metadata.get("is_hero_content", False):
                    boost_amount += self.hero_boost
                    logger.debug(f"Applied hero boost to {result.doc_id}: +{self.hero_boost}")
                
                # Apply boost with cap
                if boost_amount > 0:
                    boosted_count += 1
                    result.final_score = min(self.max_score, result.final_score + boost_amount)
                    result.metadata_boost = boost_amount
                
                boosted_results.append(result)
            
            logger.info(f"Applied boosts to {boosted_count}/{len(hybrid_results)} documents")
            
            return boosted_results
            
        except Exception as e:
            logger.error(f"Error applying boosts: {str(e)}")
            return hybrid_results
    
    def _matches_industry(self, metadata: Dict[str, Any], target_industry: str) -> bool:
        """Check if document matches target industry.
        
        Args:
            metadata: Document metadata
            target_industry: Target industry to match
            
        Returns:
            True if document matches industry
        """
        try:
            if not target_industry or not isinstance(target_industry, str):
                return False
            
            target_lower = target_industry.lower().strip()
            
            # Check direct industry field
            if "industry" in metadata:
                doc_industries = metadata["industry"]
                if isinstance(doc_industries, str):
                    doc_industries = [doc_industries]
                
                for industry in doc_industries:
                    if isinstance(industry, str) and industry.lower().strip() == target_lower:
                        return True
            
            # Check industries field (plural)
            if "industries" in metadata:
                doc_industries = metadata["industries"]
                if isinstance(doc_industries, str):
                    doc_industries = [doc_industries]
                
                for industry in doc_industries:
                    if isinstance(industry, str) and industry.lower().strip() == target_lower:
                        return True
            
            # Check tags for industry mentions
            if "tags" in metadata:
                tags = metadata["tags"]
                if isinstance(tags, str):
                    tags = [tags]
                
                for tag in tags:
                    if isinstance(tag, str) and target_lower in tag.lower():
                        return True
            
            # Check content for industry keywords
            if "content" in metadata:
                content = str(metadata["content"]).lower()
                
                # Simple keyword matching
                industry_keywords = {
                    "technology": ["tech", "software", "engineering", "development"],
                    "finance": ["financial", "banking", "investment", "trading"],
                    "healthcare": ["health", "medical", "pharmaceutical", "hospital"],
                    "retail": ["retail", "ecommerce", "sales", "consumer"],
                    "consulting": ["consulting", "advisory", "strategy", "management"]
                }
                
                if target_lower in industry_keywords:
                    for keyword in industry_keywords[target_lower]:
                        if keyword in content:
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking industry match: {str(e)}")
            return False
    
    def get_scoring_summary(self, results: List[HybridScoreResult]) -> Dict[str, Any]:
        """Get summary statistics for scoring results.
        
        Args:
            results: List of hybrid score results
            
        Returns:
            Summary statistics
        """
        try:
            if not results:
                return {"total": 0}
            
            boosted_count = sum(1 for r in results if r.is_boosted)
            
            return {
                "total": len(results),
                "boosted": boosted_count,
                "avg_final_score": sum(r.final_score for r in results) / len(results),
                "avg_dense_score": sum(r.dense_score for r in results) / len(results),
                "avg_sparse_score": sum(r.sparse_score for r in results) / len(results),
                "top_score": results[0].final_score,
                "bottom_score": results[-1].final_score,
                "score_range": results[0].final_score - results[-1].final_score
            }
        except Exception as e:
            logger.error(f"Error getting scoring summary: {str(e)}")
            return {"error": str(e)}


# Factory function for easy instantiation
def create_hybrid_scorer(
    alpha: float = 0.7,
    industry_boost: float = 0.15,
    hero_boost: float = 0.1,
    semantic_weighted: bool = True
) -> HybridScorer:
    """Create a HybridScorer instance.
    
    Args:
        alpha: Weight for dense vs sparse scores
        industry_boost: Boost for industry matches
        hero_boost: Boost for hero content
        semantic_weighted: Whether to emphasize semantic scores
        
    Returns:
        Configured HybridScorer instance
    """
    if semantic_weighted:
        return HybridScorer(alpha=alpha, industry_boost=industry_boost, hero_boost=hero_boost)
    else:
        # Keyword-weighted configuration
        return HybridScorer(alpha=0.3, industry_boost=industry_boost, hero_boost=hero_boost)


# Convenience function for quick scoring
def score_documents(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    target_industry: Optional[str] = None,
    semantic_priority: bool = True
) -> List[HybridScoreResult]:
    """Quickly score documents with hybrid approach.
    
    Args:
        dense_results: Dense (vector) search results
        sparse_results: Sparse (BM25) search results
        target_industry: Target industry for boosting
        semantic_priority: Whether to prioritize semantic scores
        
    Returns:
        List of scored and ranked documents
    """
    scorer = create_hybrid_scorer(
        alpha=0.7 if semantic_priority else 0.3,
        semantic_weighted=semantic_priority
    )
    
    return scorer.score_documents(dense_results, sparse_results, target_industry)
