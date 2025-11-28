"""LIC Cache Critique - L4 Memory/State Layer

Implements LIC-style cache sufficiency evaluation.
Determines when cached intelligence is sufficient vs when fallback RAG is needed.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re


logger = logging.getLogger(__name__)


@dataclass
class CacheCritiqueResult:
    """Result of cache sufficiency evaluation"""
    cache_sufficient: bool
    confidence_score: float
    identified_gaps: List[str]
    quality_assessment: str
    recommendations: List[str]
    requires_fallback: bool


@dataclass
class ResearchGap:
    """Identified research gap requiring fallback"""
    gap_type: str
    description: str
    priority: str
    suggested_queries: List[str]


class CacheCritiquer:
    """
    L4 Cache Critique Engine for LIC Intelligence
    
    Evaluates cache sufficiency and identifies gaps that require
    fallback RAG research following LIC cache critique methodology.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize cache critiquer
        
        Args:
            config: Optional critique configuration
        """
        self.config = config or self._get_default_config()
        
        # Critique thresholds
        self.thresholds = self.config["critique"]["thresholds"]
        
        # Quality assessment parameters
        self.quality_params = self.config["critique"]["quality"]
        
        # Gap detection parameters
        self.gap_params = self.config["critique"]["gap_detection"]
        
        logger.info("CacheCritiquer initialized with LIC cache critique methodology")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default critique configuration"""
        return {
            "critique": {
                "thresholds": {
                    "confidence_threshold": 0.8,
                    "recency_days": 30,
                    "source_diversity_min": 3,
                    "signal_score_min": 0.7,
                    "coverage_threshold": 0.75
                },
                "quality": {
                    "min_content_length": 200,
                    "max_age_days": 90,
                    "required_source_types": ["company_intelligence", "news_article"],
                    "min_quality_score": 0.6
                },
                "gap_detection": {
                    "recency_gap_days": 7,
                    "company_specific_gap": True,
                    "archetype_specific_gap": True,
                    "strategic_gap_keywords": ["recent", "latest", "current", "new", "updated"]
                }
            }
        }
    
    async def evaluate_cache_sufficiency(
        self,
        sources: List[Dict[str, Any]],
        plan: Any,
        recipient_company: str,
        recipient_name: str
    ) -> CacheCritiqueResult:
        """
        Evaluate cache sufficiency for research needs
        
        Args:
            sources: List of cached sources
            plan: Research plan for context
            recipient_company: Target company name
            recipient_name: Target recipient name
            
        Returns:
            Cache critique result with gap analysis
        """
        try:
            logger.info(f"Evaluating cache sufficiency for {len(sources)} sources")
            
            # Step 1: Basic quality assessment
            quality_score = self._assess_cache_quality(sources)
            
            # Step 2: Recency analysis
            recency_score = self._assess_recency(sources)
            
            # Step 3: Coverage analysis
            coverage_score = self._assess_coverage(sources, plan)
            
            # Step 4: Identify specific gaps
            identified_gaps = await self._identify_research_gaps(sources, plan, recipient_company, recipient_name)
            
            # Step 5: Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                quality_score, recency_score, coverage_score, identified_gaps
            )
            
            # Step 6: Determine sufficiency
            cache_sufficient = overall_confidence >= self.thresholds["confidence_threshold"]
            requires_fallback = not cache_sufficient or len(identified_gaps) > 0
            
            # Step 7: Generate recommendations
            recommendations = self._generate_recommendations(
                quality_score, recency_score, coverage_score, identified_gaps
            )
            
            # Step 8: Quality assessment summary
            quality_assessment = self._summarize_quality_assessment(
                quality_score, recency_score, coverage_score, len(sources)
            )
            
            result = CacheCritiqueResult(
                cache_sufficient=cache_sufficient,
                confidence_score=overall_confidence,
                identified_gaps=[gap.description for gap in identified_gaps],
                quality_assessment=quality_assessment,
                recommendations=recommendations,
                requires_fallback=requires_fallback
            )
            
            logger.info(f"Cache critique completed: sufficient={cache_sufficient}, confidence={overall_confidence:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Cache critique failed: {str(e)}")
            
            # Return conservative result on error
            return CacheCritiqueResult(
                cache_sufficient=False,
                confidence_score=0.0,
                identified_gaps=["Cache critique evaluation failed"],
                quality_assessment="Evaluation error - fallback required",
                recommendations=["Use fallback RAG due to evaluation failure"],
                requires_fallback=True
            )
    
    def _assess_cache_quality(self, sources: List[Dict[str, Any]]) -> float:
        """Assess quality of cached sources"""
        
        if not sources:
            return 0.0
        
        quality_scores = []
        
        for source in sources:
            score = self._assess_single_source_quality(source)
            quality_scores.append(score)
        
        # Return average quality score
        return sum(quality_scores) / len(quality_scores)
    
    def _assess_single_source_quality(self, source: Dict[str, Any]) -> float:
        """Assess quality of a single source"""
        
        score = 0.0
        
        # Content length assessment
        text = source.get("text", "")
        if len(text) >= self.quality_params["min_content_length"]:
            score += 0.3
        
        # Source type assessment
        metadata = source.get("metadata", {})
        source_type = metadata.get("source_type", "")
        if source_type in self.quality_params["required_source_types"]:
            score += 0.3
        
        # Quality score from metadata
        quality_score = metadata.get("quality_score", 0.0)
        if quality_score >= self.quality_params["min_quality_score"]:
            score += 0.2
        score += quality_score * 0.2  # Weighted contribution
        
        # Metadata completeness
        if metadata.get("source_url") and metadata.get("retrieved_at"):
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_recency(self, sources: List[Dict[str, Any]]) -> float:
        """Assess recency of cached sources"""
        
        if not sources:
            return 0.0
        
        recency_scores = []
        max_age_days = self.thresholds["recency_days"]
        
        for source in sources:
            metadata = source.get("metadata", {})
            date_str = metadata.get("retrieved_at") or metadata.get("published_at")
            
            if not date_str:
                recency_scores.append(0.3)  # Penalty for undated sources
                continue
            
            try:
                if isinstance(date_str, str):
                    source_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    source_date = date_str
                
                age_days = (datetime.now() - source_date).days
                
                if age_days <= 7:
                    recency_scores.append(1.0)
                elif age_days <= max_age_days:
                    # Linear decay
                    score = 1.0 - (age_days / max_age_days) * 0.5
                    recency_scores.append(max(score, 0.5))
                else:
                    recency_scores.append(0.3)  # Low score for old sources
                    
            except Exception as e:
                logger.warning(f"Failed to parse date {date_str}: {str(e)}")
                recency_scores.append(0.3)
        
        return sum(recency_scores) / len(recency_scores)
    
    def _assess_coverage(self, sources: List[Dict[str, Any]], plan: Any) -> float:
        """Assess coverage of research targets"""
        
        if not sources or not hasattr(plan, 'research_targets'):
            return 0.5
        
        research_targets = getattr(plan, 'research_targets', {})
        if not research_targets:
            return 0.7  # Default coverage if no targets specified
        
        coverage_scores = []
        
        # Check coverage for each target category
        for category, targets in research_targets.items():
            category_sources = self._filter_sources_by_category(sources, category)
            
            if not category_sources:
                coverage_scores.append(0.0)
                continue
            
            # Simple coverage based on source count vs targets
            coverage = min(len(category_sources) / max(len(targets), 1), 1.0)
            coverage_scores.append(coverage)
        
        # Return average coverage
        return sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0.0
    
    def _filter_sources_by_category(self, sources: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Filter sources by research category"""
        
        category_sources = []
        
        for source in sources:
            text = source.get("text", "").lower()
            metadata = source.get("metadata", {})
            
            # Simple keyword-based categorization
            if category == "company_context":
                if any(keyword in text for keyword in ["company", "business", "strategy", "market"]):
                    category_sources.append(source)
            elif category == "recipient_insights":
                if any(keyword in text for keyword in ["leadership", "team", "management", "role"]):
                    category_sources.append(source)
            elif category == "strategic_brief":
                if any(keyword in text for keyword in ["strategic", "initiative", "priority", "roadmap"]):
                    category_sources.append(source)
            else:
                # Default inclusion
                category_sources.append(source)
        
        return category_sources
    
    async def _identify_research_gaps(
        self,
        sources: List[Dict[str, Any]],
        plan: Any,
        recipient_company: str,
        recipient_name: str
    ) -> List[ResearchGap]:
        """Identify specific research gaps"""
        
        gaps = []
        
        # Check for recency gaps
        recency_gaps = self._identify_recency_gaps(sources)
        gaps.extend(recency_gaps)
        
        # Check for company-specific gaps
        company_gaps = self._identify_company_gaps(sources, recipient_company)
        gaps.extend(company_gaps)
        
        # Check for archetype-specific gaps
        if hasattr(plan, 'recipient_archetype'):
            archetype_gaps = self._identify_archetype_gaps(sources, getattr(plan, 'recipient_archetype'))
            gaps.extend(archetype_gaps)
        
        # Check for strategic gaps
        strategic_gaps = self._identify_strategic_gaps(sources, plan)
        gaps.extend(strategic_gaps)
        
        return gaps
    
    def _identify_recency_gaps(self, sources: List[Dict[str, Any]]) -> List[ResearchGap]:
        """Identify recency-related gaps"""
        
        gaps = []
        recency_gap_days = self.gap_params["recency_gap_days"]
        
        recent_sources = 0
        for source in sources:
            metadata = source.get("metadata", {})
            date_str = metadata.get("retrieved_at") or metadata.get("published_at")
            
            if date_str:
                try:
                    if isinstance(date_str, str):
                        source_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        source_date = date_str
                    
                    if (datetime.now() - source_date).days <= recency_gap_days:
                        recent_sources += 1
                        
                except Exception:
                    pass
        
        # If few recent sources, flag recency gap
        if recent_sources < 2:
            gaps.append(ResearchGap(
                gap_type="recency",
                description=f"Insufficient recent intelligence (only {recent_sources} sources from last {recency_gap_days} days)",
                priority="high",
                suggested_queries=["recent developments", "latest news", "current updates"]
            ))
        
        return gaps
    
    def _identify_company_gaps(self, sources: List[Dict[str, Any]], recipient_company: str) -> List[ResearchGap]:
        """Identify company-specific intelligence gaps"""
        
        gaps = []
        company_lower = recipient_company.lower()
        
        company_specific_sources = 0
        for source in sources:
            text = source.get("text", "").lower()
            metadata = source.get("metadata", {})
            
            # Check if source is company-specific
            if (company_lower in text or 
                metadata.get("company_name", "").lower() == company_lower):
                company_specific_sources += 1
        
        # If few company-specific sources, flag gap
        if company_specific_sources < 3:
            gaps.append(ResearchGap(
                gap_type="company_specific",
                description=f"Insufficient company-specific intelligence (only {company_specific_sources} sources)",
                priority="high",
                suggested_queries=[f"{recipient_company} company profile", f"{recipient_company} business strategy"]
            ))
        
        return gaps
    
    def _identify_archetype_gaps(self, sources: List[Dict[str, Any]], archetype: str) -> List[ResearchGap]:
        """Identify archetype-specific intelligence gaps"""
        
        gaps = []
        
        # Define archetype-specific keywords
        archetype_keywords = {
            "executive": ["strategic", "leadership", "business", "executive"],
            "hiring_manager": ["hiring", "recruitment", "team", "management"],
            "technical_lead": ["technical", "engineering", "development", "architecture"],
            "recruiter": ["recruiting", "talent", "opportunity", "position"]
        }
        
        keywords = archetype_keywords.get(archetype, [])
        if not keywords:
            return gaps
        
        relevant_sources = 0
        for source in sources:
            text = source.get("text", "").lower()
            if any(keyword in text for keyword in keywords):
                relevant_sources += 1
        
        # If few archetype-relevant sources, flag gap
        if relevant_sources < 2:
            gaps.append(ResearchGap(
                gap_type="archetype_specific",
                description=f"Insufficient {archetype}-specific intelligence (only {relevant_sources} relevant sources)",
                priority="medium",
                suggested_queries=[f"{archetype} role responsibilities", f"{archetype} decision criteria"]
            ))
        
        return gaps
    
    def _identify_strategic_gaps(self, sources: List[Dict[str, Any]], plan: Any) -> List[ResearchGap]:
        """Identify strategic intelligence gaps"""
        
        gaps = []
        strategic_keywords = self.gap_params["strategic_gap_keywords"]
        
        strategic_sources = 0
        for source in sources:
            text = source.get("text", "").lower()
            if any(keyword in text for keyword in strategic_keywords):
                strategic_sources += 1
        
        # If few strategic sources, flag gap
        if strategic_sources < 2:
            gaps.append(ResearchGap(
                gap_type="strategic",
                description=f"Insufficient strategic intelligence (only {strategic_sources} sources with strategic focus)",
                priority="medium",
                suggested_queries=["strategic priorities", "current initiatives", "recent developments"]
            ))
        
        return gaps
    
    def _calculate_overall_confidence(
        self,
        quality_score: float,
        recency_score: float,
        coverage_score: float,
        identified_gaps: List[ResearchGap]
    ) -> float:
        """Calculate overall confidence in cache sufficiency"""
        
        # Weighted base confidence
        base_confidence = (
            quality_score * 0.4 +
            recency_score * 0.3 +
            coverage_score * 0.3
        )
        
        # Penalty for identified gaps
        gap_penalty = min(len(identified_gaps) * 0.1, 0.3)
        
        # Additional penalty for high-priority gaps
        high_priority_gaps = [gap for gap in identified_gaps if gap.priority == "high"]
        if high_priority_gaps:
            gap_penalty += len(high_priority_gaps) * 0.05
        
        overall_confidence = max(base_confidence - gap_penalty, 0.0)
        
        return overall_confidence
    
    def _generate_recommendations(
        self,
        quality_score: float,
        recency_score: float,
        coverage_score: float,
        identified_gaps: List[ResearchGap]
    ) -> List[str]:
        """Generate recommendations based on critique results"""
        
        recommendations = []
        
        # Quality-based recommendations
        if quality_score < 0.7:
            recommendations.append("Improve source quality through better filtering")
        
        # Recency-based recommendations
        if recency_score < 0.6:
            recommendations.append("Prioritize recent intelligence sources")
        
        # Coverage-based recommendations
        if coverage_score < 0.7:
            recommendations.append("Expand coverage across research target categories")
        
        # Gap-specific recommendations
        for gap in identified_gaps:
            if gap.gap_type == "recency":
                recommendations.append("Execute fallback RAG for recent developments")
            elif gap.gap_type == "company_specific":
                recommendations.append("Conduct company-specific research")
            elif gap.gap_type == "archetype_specific":
                recommendations.append("Research archetype-specific decision criteria")
            elif gap.gap_type == "strategic":
                recommendations.append("Gather strategic intelligence and priorities")
        
        # General recommendation if fallback needed
        if identified_gaps:
            recommendations.append("Use fallback RAG to fill identified intelligence gaps")
        
        return recommendations
    
    def _summarize_quality_assessment(
        self,
        quality_score: float,
        recency_score: float,
        coverage_score: float,
        source_count: int
    ) -> str:
        """Generate quality assessment summary"""
        
        if quality_score >= 0.8 and recency_score >= 0.7 and coverage_score >= 0.7:
            return f"High-quality cache with {source_count} sources meeting quality standards"
        elif quality_score >= 0.6 and recency_score >= 0.5 and coverage_score >= 0.5:
            return f"Moderate-quality cache with {source_count} sources, some improvements needed"
        else:
            return f"Low-quality cache with {source_count} sources requiring significant improvement"
    
    def get_critique_thresholds(self) -> Dict[str, Any]:
        """Get current critique thresholds"""
        return self.thresholds.copy()
    
    def update_critique_thresholds(self, new_thresholds: Dict[str, Any]):
        """Update critique thresholds"""
        self.thresholds.update(new_thresholds)
        logger.info(f"Updated critique thresholds: {self.thresholds}")
