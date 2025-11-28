"""LIC Research Planning - L1 Planning Layer

Implements HOP-2 multi-hop research planning from legacy LIC system.
Plans vector-first research strategy with cache critique and fallback RAG.
Pure planning - no execution, IO, or LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class ResearchStrategy(Enum):
    """Research execution strategies"""
    VECTOR_FIRST = "vector_first"
    RAG_FALLBACK = "rag_fallback"
    HYBRID_SEARCH = "hybrid_search"
    MULTI_HOP = "multi_hop"


class CacheSufficiency(Enum):
    """Cache critique outcomes"""
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"
    PARTIAL = "partial"
    STALE = "stale"


@dataclass
class VectorQueryParams:
    """Parameters for vector store queries"""
    n_results: int = 20
    similarity_threshold: float = 0.7
    filter_metadata: Optional[Dict[str, Any]] = None
    query_types: List[str] = field(default_factory=lambda: ["company", "recipient", "strategic"])


@dataclass
class FallbackRAGParams:
    """Parameters for fallback RAG execution"""
    max_sources: int = 10
    search_depth: str = "comprehensive"
    source_types: List[str] = field(default_factory=lambda: ["company", "news", "industry"])
    quality_threshold: float = 0.6


@dataclass
class CacheCritiqueParams:
    """Parameters for cache sufficiency evaluation"""
    confidence_threshold: float = 0.8
    recency_days: int = 30
    source_diversity_min: int = 3
    signal_score_min: float = 0.7


@dataclass
class ResearchGap:
    """Identified research gap requiring fallback"""
    gap_type: str
    description: str
    priority: str
    suggested_queries: List[str]


@dataclass
class LICResearchPlan:
    """Complete research execution plan"""
    # Core planning data
    recipient_company: str
    recipient_name: str
    recipient_archetype: str
    
    # Strategy decisions
    primary_strategy: ResearchStrategy
    cache_sufficiency: CacheSufficiency
    requires_fallback: bool
    
    # Execution parameters
    vector_params: VectorQueryParams
    fallback_params: FallbackRAGParams
    critique_params: CacheCritiqueParams
    
    # Identified gaps and queries
    identified_gaps: List[ResearchGap]
    vector_queries: List[str]
    fallback_queries: List[str]
    
    # Planning metadata
    plan_id: str
    created_at: str
    expected_sources: int
    confidence_score: float
    
    # Research targets
    research_targets: Dict[str, List[str]] = field(default_factory=dict)


class LICResearchPlanner:
    """
    L1 Planner for LIC HOP-2 Multi-hop Research
    
    Creates comprehensive research plans with vector-first strategy,
    cache critique logic, and fallback RAG planning.
    Pure deterministic planning - no external execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize research planner with configuration
        
        Args:
            config: Optional configuration for research parameters
        """
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default research configuration"""
        return {
            "research_agent": {
                "vector_store_query_params": {
                    "n_results": 20,
                    "similarity_threshold": 0.7,
                    "query_types": ["company", "recipient", "strategic"]
                },
                "fallback_rag_params": {
                    "max_sources": 10,
                    "search_depth": "comprehensive",
                    "source_types": ["company", "news", "industry"],
                    "quality_threshold": 0.6
                },
                "cache_critique_params": {
                    "confidence_threshold": 0.8,
                    "recency_days": 30,
                    "source_diversity_min": 3,
                    "signal_score_min": 0.7
                }
            }
        }
    
    def plan_research(
        self,
        recipient_company: str,
        recipient_name: str,
        recipient_archetype: str,
        plan_id: Optional[str] = None
    ) -> LICResearchPlan:
        """
        Create comprehensive research plan
        
        Args:
            recipient_company: Target company name
            recipient_name: Target recipient name
            recipient_archetype: Classified recipient archetype
            plan_id: Optional plan identifier
            
        Returns:
            Complete research execution plan
        """
        # Generate plan ID if not provided
        if plan_id is None:
            import hashlib
            id_string = f"{recipient_company}_{recipient_name}_{recipient_archetype}"
            plan_id = hashlib.md5(id_string.encode()).hexdigest()[:12]
        
        # Extract configuration
        agent_config = self.config["research_agent"]
        vector_config = VectorQueryParams(**agent_config["vector_store_query_params"])
        fallback_config = FallbackRAGParams(**agent_config["fallback_rag_params"])
        critique_config = CacheCritiqueParams(**agent_config["cache_critique_params"])
        
        # Determine primary strategy (always vector-first for LIC)
        primary_strategy = ResearchStrategy.VECTOR_FIRST
        
        # Generate vector queries based on archetype and context
        vector_queries = self._generate_vector_queries(
            recipient_company, recipient_name, recipient_archetype
        )
        
        # Generate fallback queries for potential gaps
        fallback_queries = self._generate_fallback_queries(
            recipient_company, recipient_name, recipient_archetype
        )
        
        # Identify potential research gaps
        identified_gaps = self._identify_potential_gaps(
            recipient_company, recipient_name, recipient_archetype
        )
        
        # Set research targets based on archetype
        research_targets = self._define_research_targets(recipient_archetype)
        
        # Calculate expected sources and confidence
        expected_sources = vector_config.n_results + (fallback_config.max_sources if identified_gaps else 0)
        confidence_score = self._calculate_confidence(recipient_archetype, len(identified_gaps))
        
        # Determine cache sufficiency (will be evaluated at execution)
        cache_sufficiency = CacheSufficiency.PARTIAL  # Default to partial evaluation
        requires_fallback = len(identified_gaps) > 0
        
        # Get timestamp
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        return LICResearchPlan(
            recipient_company=recipient_company,
            recipient_name=recipient_name,
            recipient_archetype=recipient_archetype,
            primary_strategy=primary_strategy,
            cache_sufficiency=cache_sufficiency,
            requires_fallback=requires_fallback,
            vector_params=vector_config,
            fallback_params=fallback_config,
            critique_params=critique_config,
            identified_gaps=identified_gaps,
            vector_queries=vector_queries,
            fallback_queries=fallback_queries,
            plan_id=plan_id,
            created_at=created_at,
            expected_sources=expected_sources,
            confidence_score=confidence_score,
            research_targets=research_targets
        )
    
    def _generate_vector_queries(
        self,
        company: str,
        recipient: str,
        archetype: str
    ) -> List[str]:
        """Generate vector store queries based on context"""
        queries = []
        
        # Company strategic queries
        queries.extend([
            f"{company} strategic priorities initiatives roadmap",
            f"{company} platform technology stack engineering",
            f"{company} business model revenue growth",
            f"{company} leadership team organizational structure"
        ])
        
        # Role-specific queries based on archetype
        if archetype == "executive":
            queries.extend([
                f"{company} C-level strategic decisions",
                f"{company} board priorities investor relations",
                f"{company} market positioning competitive landscape"
            ])
        elif archetype == "hiring_manager":
            queries.extend([
                f"{company} team structure hiring needs",
                f"{company} engineering culture work environment",
                f"{company} current job openings recruitment"
            ])
        elif archetype == "technical_lead":
            queries.extend([
                f"{company} technical architecture infrastructure",
                f"{company} engineering practices development methodology",
                f"{company} technology challenges technical debt"
            ])
        elif archetype == "recruiter":
            queries.extend([
                f"{company} recruitment process talent acquisition",
                f"{company} company culture employee benefits",
                f"{company} hiring pipeline recruitment strategy"
            ])
        
        # Recipient-specific queries
        if recipient:
            queries.extend([
                f"{recipient} {company} role responsibilities",
                f"{recipient} professional background experience",
                f"{recipient} career achievements recognition"
            ])
        
        return queries
    
    def _generate_fallback_queries(
        self,
        company: str,
        recipient: str,
        archetype: str
    ) -> List[str]:
        """Generate fallback RAG queries for potential gaps"""
        queries = []
        
        # Recent news and developments
        queries.extend([
            f"{company} recent news developments 2024",
            f"{company} quarterly earnings financial performance",
            f"{company} product launches updates announcements"
        ])
        
        # Industry context
        queries.extend([
            f"{company} industry analysis market trends",
            f"{company} competitive analysis market share",
            f"{company} sector challenges opportunities"
        ])
        
        # Role-specific fallback queries
        if archetype == "executive":
            queries.extend([
                f"{company} executive leadership strategic vision",
                f"{company} corporate governance policies"
            ])
        elif archetype == "technical_lead":
            queries.extend([
                f"{company} technical innovation patents R&D",
                f"{company} engineering challenges solutions"
            ])
        
        return queries
    
    def _identify_potential_gaps(
        self,
        company: str,
        recipient: str,
        archetype: str
    ) -> List[ResearchGap]:
        """Identify potential research gaps that might require fallback"""
        gaps = []
        
        # Recent information gaps
        gaps.append(ResearchGap(
            gap_type="recency",
            description="Recent developments and news may be missing from vector store",
            priority="high",
            suggested_queries=[f"{company} recent news 2024", f"{company} latest updates"]
        ))
        
        # Recipient-specific gaps
        if recipient:
            gaps.append(ResearchGap(
                gap_type="recipient_specific",
                description=f"Detailed information about {recipient} may be limited",
                priority="medium",
                suggested_queries=[f"{recipient} professional background", f"{recipient} career achievements"]
            ))
        
        # Role-specific gaps
        if archetype == "technical_lead":
            gaps.append(ResearchGap(
                gap_type="technical_details",
                description="Detailed technical architecture and engineering practices",
                priority="medium",
                suggested_queries=[f"{company} technical stack", f"{company} engineering practices"]
            ))
        
        return gaps
    
    def _define_research_targets(self, archetype: str) -> Dict[str, List[str]]:
        """Define research targets based on recipient archetype"""
        targets = {
            "company_context": [
                "strategic_priorities",
                "business_model", 
                "market_position",
                "competitive_landscape"
            ],
            "recipient_insights": [
                "role_responsibilities",
                "career_background",
                "professional_achievements"
            ],
            "engagement_angles": [
                "pain_points",
                "opportunities",
                "value_propositions"
            ]
        }
        
        # Add archetype-specific targets
        if archetype == "executive":
            targets["strategic_focus"] = [
                "growth_initiatives",
                "market_expansion",
                "investor_relations"
            ]
        elif archetype == "hiring_manager":
            targets["hiring_context"] = [
                "team_needs",
                "skill_requirements",
                "company_culture"
            ]
        elif archetype == "technical_lead":
            targets["technical_focus"] = [
                "technology_stack",
                "engineering_challenges",
                "innovation_priorities"
            ]
        
        return targets
    
    def _calculate_confidence(self, archetype: str, gap_count: int) -> float:
        """Calculate confidence score for research plan"""
        base_confidence = {
            "executive": 0.8,
            "hiring_manager": 0.7,
            "technical_lead": 0.7,
            "recruiter": 0.6,
            "influencer": 0.5,
            "peer": 0.5
        }.get(archetype, 0.5)
        
        # Reduce confidence based on identified gaps
        gap_penalty = min(gap_count * 0.1, 0.3)
        final_confidence = max(base_confidence - gap_penalty, 0.3)
        
        return final_confidence
    
    def validate_plan(self, plan: LICResearchPlan) -> List[str]:
        """
        Validate research plan for completeness and correctness
        
        Args:
            plan: Research plan to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not plan.recipient_company:
            errors.append("recipient_company is required")
        
        if not plan.recipient_name:
            errors.append("recipient_name is required")
        
        if not plan.recipient_archetype:
            errors.append("recipient_archetype is required")
        
        if not plan.vector_queries:
            errors.append("vector_queries cannot be empty")
        
        if not plan.plan_id:
            errors.append("plan_id is required")
        
        if plan.confidence_score < 0.0 or plan.confidence_score > 1.0:
            errors.append("confidence_score must be between 0.0 and 1.0")
        
        if plan.expected_sources <= 0:
            errors.append("expected_sources must be positive")
        
        return errors
