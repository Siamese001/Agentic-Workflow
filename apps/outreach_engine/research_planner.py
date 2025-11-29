"""Research Planner - L1 planning for multi-hop research queries and strategy.

Incorporated from L1 lic_research_planner.py to provide deterministic research
planning with vector-first multi-hop query generation, query expansion strategies,
and LIC-style reasoning for role → responsibilities → signals → evidence.

This is a foundational L1 planning component that feeds into the hop-based
K1-K7 execution pipeline, specifically the K1 research execution phase.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ResearchStrategy(Enum):
    """Research execution strategies"""
    VECTOR_FIRST = "vector_first"
    RAG_FALLBACK = "rag_fallback"
    HYBRID_SEARCH = "hybrid_search"
    MULTI_HOP = "multi_hop"


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


@dataclass
class ResearchQuery:
    """Individual research query with expansion strategy"""
    query_id: str
    base_query: str
    expanded_queries: List[str]
    query_type: str  # "company", "recipient", "strategic", "temporal"
    expansion_strategy: str  # "semantic", "role_synonym", "temporal", "hybrid"
    priority: int  # 1 = highest priority
    expected_sources: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchPlan:
    """Complete research execution plan for K1 phase."""
    target_role: str
    target_company: str
    archetype: str
    primary_strategy: ResearchStrategy
    queries: List[ResearchQuery]
    vector_params: VectorQueryParams
    rag_params: FallbackRAGParams
    cache_params: CacheCritiqueParams
    execution_order: List[str]  # Query IDs in execution order
    fallback_strategy: ResearchStrategy
    confidence_threshold: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResearchPlanner:
    """L1 pure planner for multi-hop research query generation.
    
    Generates deterministic research plans using vector-first approach
    with query expansion strategies and LIC-style reasoning.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize research planner."""
        self.telemetry_bus = telemetry_bus
        
        # Role-to-responsibility mappings for query generation
        self.role_responsibilities = {
            "EXECUTIVE": [
                "strategic initiatives", "business outcomes", "team leadership",
                "market positioning", "financial performance", "operational efficiency"
            ],
            "SENIOR_TA": [
                "technical architecture", "innovation initiatives", "team mentorship",
                "technology strategy", "engineering excellence", "technical debt"
            ],
            "RECRUITER": [
                "talent acquisition", "hiring strategy", "candidate assessment",
                "team building", "culture fit", "skill requirements"
            ],
            "C_LEVEL": [
                "enterprise strategy", "board governance", "market leadership",
                "stakeholder management", "competitive advantage", "growth initiatives"
            ]
        }
        
        # Query expansion templates
        self.semantic_expansions = {
            "company": ["{company} business model", "{company} market position", "{company} strategic initiatives"],
            "recipient": ["{role} responsibilities", "{role} challenges", "{role} success metrics"],
            "strategic": ["{company} {role} alignment", "{role} strategic impact", "{company} competitive landscape"]
        }
        
        self.role_synonym_expansions = {
            "EXECUTIVE": ["leadership", "management", "c-suite", "senior leadership"],
            "SENIOR_TA": ["technical leadership", "engineering management", "principal engineer", "staff engineer"],
            "RECRUITER": ["talent acquisition", "hiring manager", "recruitment", "staffing"],
            "C_LEVEL": ["executive leadership", "c-suite", "board level", "senior executive"]
        }
        
        self.temporal_expansions = [
            "recent {company} developments", "current {role} trends", 
            "latest {company} initiatives", "ongoing {role} challenges"
        ]
        
        # Query type priorities
        self.query_priorities = {
            "company": 1,      # Company info is highest priority
            "recipient": 2,    # Role-specific info next
            "strategic": 3,    # Strategic alignment third
            "temporal": 4      # Temporal context last
        }
    
    def plan(
        self,
        *,
        role_title: str,
        company_name: str,
        archetype: str,
        recipient_profile: Dict[str, Any],
        outreach_context: Dict[str, Any] = None,
    ) -> ResearchPlan:
        """Generate a deterministic research execution plan.
        
        Args:
            role_title: Target role title
            company_name: Target company name
            archetype: Primary archetype for this contact
            recipient_profile: Recipient profile data
            outreach_context: Additional context for planning
            
        Returns:
            Complete research plan with queries and execution parameters
        """
        outreach_context = outreach_context or {}
        
        # 1. Determine primary research strategy
        primary_strategy = self._determine_primary_strategy(archetype, outreach_context)
        
        # 2. Generate base research queries
        base_queries = self._generate_base_queries(role_title, company_name, archetype)
        
        # 3. Apply query expansion strategies
        expanded_queries = self._expand_queries(base_queries, role_title, company_name, archetype)
        
        # 4. Set execution parameters
        vector_params = self._configure_vector_params(archetype, outreach_context)
        rag_params = self._configure_rag_params(archetype, outreach_context)
        cache_params = self._configure_cache_params(archetype, outreach_context)
        
        # 5. Determine execution order
        execution_order = self._determine_execution_order(expanded_queries)
        
        # 6. Set fallback strategy
        fallback_strategy = self._determine_fallback_strategy(primary_strategy, archetype)
        
        # 7. Calculate confidence threshold
        confidence_threshold = self._calculate_confidence_threshold(archetype, expanded_queries)
        
        # 8. Build metadata
        metadata = {
            "archetype": archetype,
            "role_title": role_title,
            "company_name": company_name,
            "query_count": len(expanded_queries),
            "primary_strategy": primary_strategy.value,
            "fallback_strategy": fallback_strategy.value,
            "expansion_strategies_used": list(set(q.expansion_strategy for q in expanded_queries))
        }
        
        # 9. Create research plan
        plan = ResearchPlan(
            target_role=role_title,
            target_company=company_name,
            archetype=archetype,
            primary_strategy=primary_strategy,
            queries=expanded_queries,
            vector_params=vector_params,
            rag_params=rag_params,
            cache_params=cache_params,
            execution_order=execution_order,
            fallback_strategy=fallback_strategy,
            confidence_threshold=confidence_threshold,
            metadata=metadata,
        )
        
        # 10. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)
        
        return plan
    
    def _determine_primary_strategy(self, archetype: str, context: Dict[str, Any]) -> ResearchStrategy:
        """Determine primary research strategy based on archetype and context."""
        # Default to vector-first for most cases
        if archetype in ["EXECUTIVE", "C_LEVEL"]:
            return ResearchStrategy.VECTOR_FIRST
        elif archetype == "SENIOR_TA":
            return ResearchStrategy.HYBRID_SEARCH
        elif archetype == "RECRUITER":
            return ResearchStrategy.RAG_FALLBACK
        else:
            return ResearchStrategy.VECTOR_FIRST
    
    def _generate_base_queries(self, role_title: str, company_name: str, archetype: str) -> List[ResearchQuery]:
        """Generate base research queries using LIC reasoning."""
        queries = []
        
        # Get role responsibilities
        responsibilities = self.role_responsibilities.get(archetype, [])
        
        # Generate company-focused queries
        for i, responsibility in enumerate(responsibilities[:3]):  # Limit to top 3
            query = ResearchQuery(
                query_id=f"company_{i+1}",
                base_query=f"{company_name} {responsibility}",
                expanded_queries=[],
                query_type="company",
                expansion_strategy="semantic",
                priority=self.query_priorities["company"],
                expected_sources=["company_profile", "news", "industry_reports"],
                metadata={"responsibility": responsibility}
            )
            queries.append(query)
        
        # Generate recipient-focused queries
        for i, responsibility in enumerate(responsibilities[:2]):  # Limit to top 2
            query = ResearchQuery(
                query_id=f"recipient_{i+1}",
                base_query=f"{role_title} {responsibility}",
                expanded_queries=[],
                query_type="recipient",
                expansion_strategy="role_synonym",
                priority=self.query_priorities["recipient"],
                expected_sources=["role_descriptions", "industry_blogs", "professional_networks"],
                metadata={"responsibility": responsibility}
            )
            queries.append(query)
        
        # Generate strategic alignment query
        strategic_query = ResearchQuery(
            query_id="strategic_1",
            base_query=f"{company_name} {role_title} strategic alignment",
            expanded_queries=[],
            query_type="strategic",
            expansion_strategy="hybrid",
            priority=self.query_priorities["strategic"],
            expected_sources=["strategic_reports", "company_announcements", "industry_analysis"],
            metadata={"alignment_focus": True}
        )
        queries.append(strategic_query)
        
        return queries
    
    def _expand_queries(self, queries: List[ResearchQuery], role_title: str, company_name: str, archetype: str) -> List[ResearchQuery]:
        """Apply query expansion strategies to base queries."""
        expanded_queries = []
        
        for query in queries:
            expanded_query = self._apply_expansion_strategy(query, role_title, company_name, archetype)
            expanded_queries.append(expanded_query)
        
        # Add temporal queries for high-value research
        if archetype in ["EXECUTIVE", "C_LEVEL"]:
            temporal_query = self._generate_temporal_query(role_title, company_name)
            expanded_queries.append(temporal_query)
        
        return expanded_queries
    
    def _apply_expansion_strategy(self, query: ResearchQuery, role_title: str, company_name: str, archetype: str) -> ResearchQuery:
        """Apply specific expansion strategy to a query."""
        if query.expansion_strategy == "semantic":
            expanded = self._semantic_expansion(query, company_name, role_title)
        elif query.expansion_strategy == "role_synonym":
            expanded = self._role_synonym_expansion(query, archetype)
        elif query.expansion_strategy == "temporal":
            expanded = self._temporal_expansion(query, company_name, role_title)
        elif query.expansion_strategy == "hybrid":
            expanded = self._hybrid_expansion(query, company_name, role_title, archetype)
        else:
            expanded = [query.base_query]
        
        query.expanded_queries = expanded
        return query
    
    def _semantic_expansion(self, query: ResearchQuery, company_name: str, role_title: str) -> List[str]:
        """Apply semantic expansion to query."""
        templates = self.semantic_expansions.get(query.query_type, [])
        
        expanded = []
        for template in templates:
            expanded_query = template.format(company=company_name, role=role_title)
            expanded.append(expanded_query)
        
        return expanded[:3]  # Limit to 3 expansions
    
    def _role_synonym_expansion(self, query: ResearchQuery, archetype: str) -> List[str]:
        """Apply role synonym expansion to query."""
        synonyms = self.role_synonym_expansions.get(archetype, [])
        
        expanded = []
        for synonym in synonyms[:2]:  # Limit to 2 synonyms
            expanded_query = query.base_query.replace(query.base_query.split()[0], synonym)
            expanded.append(expanded_query)
        
        return expanded
    
    def _temporal_expansion(self, query: ResearchQuery, company_name: str, role_title: str) -> List[str]:
        """Apply temporal expansion to query."""
        expanded = []
        for template in self.temporal_expansions[:2]:  # Limit to 2 temporal queries
            expanded_query = template.format(company=company_name, role=role_title)
            expanded.append(expanded_query)
        
        return expanded
    
    def _hybrid_expansion(self, query: ResearchQuery, company_name: str, role_title: str, archetype: str) -> List[str]:
        """Apply hybrid expansion combining multiple strategies."""
        expanded = []
        
        # Combine semantic and role synonym
        semantic = self._semantic_expansion(query, company_name, role_title)
        role_syn = self._role_synonym_expansion(query, archetype)
        
        expanded.extend(semantic[:2])  # Take top 2 from each
        expanded.extend(role_syn[:1])  # Take top 1 from role synonyms
        
        return expanded[:3]  # Limit to 3 total
    
    def _generate_temporal_query(self, role_title: str, company_name: str) -> ResearchQuery:
        """Generate a temporal research query."""
        return ResearchQuery(
            query_id="temporal_1",
            base_query=f"recent developments {company_name} {role_title}",
            expanded_queries=[
                f"latest {company_name} initiatives",
                f"current {role_title} trends",
                f"ongoing {company_name} projects"
            ],
            query_type="temporal",
            expansion_strategy="temporal",
            priority=self.query_priorities["temporal"],
            expected_sources=["news", "company_announcements", "industry_updates"],
            metadata={"temporal_focus": True}
        )
    
    def _configure_vector_params(self, archetype: str, context: Dict[str, Any]) -> VectorQueryParams:
        """Configure vector search parameters."""
        base_params = VectorQueryParams()
        
        # Adjust based on archetype
        if archetype in ["EXECUTIVE", "C_LEVEL"]:
            base_params.n_results = 15  # Fewer, higher quality results
            base_params.similarity_threshold = 0.8
        elif archetype == "SENIOR_TA":
            base_params.n_results = 25  # More technical results
            base_params.similarity_threshold = 0.7
        else:
            base_params.n_results = 20  # Standard
        
        # Apply context overrides
        if context.get("vector_results"):
            base_params.n_results = context["vector_results"]
        if context.get("similarity_threshold"):
            base_params.similarity_threshold = context["similarity_threshold"]
        
        return base_params
    
    def _configure_rag_params(self, archetype: str, context: Dict[str, Any]) -> FallbackRAGParams:
        """Configure fallback RAG parameters."""
        base_params = FallbackRAGParams()
        
        # Adjust based on archetype
        if archetype in ["EXECUTIVE", "C_LEVEL"]:
            base_params.max_sources = 8  # Fewer, high-quality sources
            base_params.quality_threshold = 0.8
        elif archetype == "SENIOR_TA":
            base_params.max_sources = 12  # More technical sources
            base_params.quality_threshold = 0.7
        else:
            base_params.max_sources = 10  # Standard
        
        # Apply context overrides
        if context.get("rag_sources"):
            base_params.max_sources = context["rag_sources"]
        if context.get("quality_threshold"):
            base_params.quality_threshold = context["quality_threshold"]
        
        return base_params
    
    def _configure_cache_params(self, archetype: str, context: Dict[str, Any]) -> CacheCritiqueParams:
        """Configure cache evaluation parameters."""
        base_params = CacheCritiqueParams()
        
        # Adjust based on archetype
        if archetype in ["EXECUTIVE", "C_LEVEL"]:
            base_params.confidence_threshold = 0.9  # Higher confidence required
            base_params.recency_days = 14  # More recent data
        elif archetype == "SENIOR_TA":
            base_params.confidence_threshold = 0.8
            base_params.recency_days = 21
        else:
            base_params.confidence_threshold = 0.7
            base_params.recency_days = 30
        
        # Apply context overrides
        if context.get("cache_confidence"):
            base_params.confidence_threshold = context["cache_confidence"]
        if context.get("cache_recency"):
            base_params.recency_days = context["cache_recency"]
        
        return base_params
    
    def _determine_execution_order(self, queries: List[ResearchQuery]) -> List[str]:
        """Determine optimal query execution order."""
        # Sort by priority (lower number = higher priority)
        sorted_queries = sorted(queries, key=lambda q: q.priority)
        return [q.query_id for q in sorted_queries]
    
    def _determine_fallback_strategy(self, primary: ResearchStrategy, archetype: str) -> ResearchStrategy:
        """Determine fallback research strategy."""
        if primary == ResearchStrategy.VECTOR_FIRST:
            return ResearchStrategy.RAG_FALLBACK
        elif primary == ResearchStrategy.HYBRID_SEARCH:
            return ResearchStrategy.VECTOR_FIRST
        else:
            return ResearchStrategy.VECTOR_FIRST
    
    def _calculate_confidence_threshold(self, archetype: str, queries: List[ResearchQuery]) -> float:
        """Calculate confidence threshold for research completion."""
        base_threshold = 0.7
        
        # Adjust based on archetype
        if archetype in ["EXECUTIVE", "C_LEVEL"]:
            base_threshold = 0.8  # Higher confidence required
        elif archetype == "SENIOR_TA":
            base_threshold = 0.75
        
        # Adjust based on query count
        if len(queries) > 5:
            base_threshold += 0.05  # Slightly higher for complex research
        
        return min(base_threshold, 0.9)
    
    def _safe_record_telemetry(self, plan: ResearchPlan) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("research_plan_created", {
                    "archetype": plan.archetype,
                    "primary_strategy": plan.primary_strategy.value,
                    "query_count": len(plan.queries),
                    "confidence_threshold": plan.confidence_threshold
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_research_summary(self, plan: ResearchPlan) -> Dict[str, Any]:
        """Get a summary of the research plan for debugging/telemetry."""
        return {
            "plan_id": f"research_{plan.archetype}_{plan.target_company}",
            "archetype": plan.archetype,
            "target_role": plan.target_role,
            "target_company": plan.target_company,
            "primary_strategy": plan.primary_strategy.value,
            "fallback_strategy": plan.fallback_strategy.value,
            "query_count": len(plan.queries),
            "confidence_threshold": plan.confidence_threshold,
            "query_types": list(set(q.query_type for q in plan.queries)),
            "expansion_strategies": list(set(q.expansion_strategy for q in plan.queries))
        }
