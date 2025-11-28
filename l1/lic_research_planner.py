"""LIC Research Planner - L1 pure planning for multi-hop research queries.

Implements nuclear prompt requirements for deterministic research planning:
- Vector-first multi-hop research query generation
- Query expansion strategies (semantic, temporal, role_synonym, hybrid)
- LIC-style reasoning (role → responsibilities → signals → evidence)
- Pure L1 planning with no external calls or execution
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# Backward compatibility stubs for downstream modules
class ResearchStrategy(Enum):
    """Research execution strategies (backward compatibility)"""
    VECTOR_FIRST = "vector_first"
    RAG_FALLBACK = "rag_fallback"
    HYBRID_SEARCH = "hybrid_search"
    MULTI_HOP = "multi_hop"


@dataclass
class VectorQueryParams:
    """Parameters for vector store queries (backward compatibility)"""
    n_results: int = 20
    similarity_threshold: float = 0.7
    filter_metadata: Optional[Dict[str, Any]] = None
    query_types: List[str] = field(default_factory=lambda: ["company", "recipient", "strategic"])


@dataclass
class FallbackRAGParams:
    """Parameters for fallback RAG execution (backward compatibility)"""
    max_sources: int = 10
    search_depth: str = "comprehensive"
    source_types: List[str] = field(default_factory=lambda: ["company", "news", "industry"])
    quality_threshold: float = 0.6


@dataclass
class CacheCritiqueParams:
    """Parameters for cache sufficiency evaluation (backward compatibility)"""
    confidence_threshold: float = 0.8
    recency_days: int = 30
    source_diversity_min: int = 3
    signal_score_min: float = 0.7


@dataclass
class ResearchGap:
    """Identified research gap requiring fallback (backward compatibility)"""
    gap_type: str
    description: str
    priority: str
    suggested_queries: List[str]


class CacheSufficiency(Enum):
    """Cache critique outcomes (backward compatibility)"""
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"
    PARTIAL = "partial"
    STALE = "stale"


@dataclass
class LICResearchHop:
    """Single research hop in the multi-hop query plan."""
    hop_index: int                     # 1-based hop index
    query_text: str                    # final expanded query string
    query_seed: str                    # original seed prompt
    expansion_strategy: str            # "semantic" | "temporal" | "role_synonym" | "hybrid"
    requires_freshness: bool
    expected_evidence: List[str]       # e.g. ["funding", "strategy", "product", ...]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LICResearchPlan:
    """Complete research plan for role and company investigation."""
    role_title: str
    company_name: str
    seed_queries: List[str]
    hops: List[LICResearchHop]
    max_hops: int
    stop_condition: str                # "cache_good_enough" | "max_hops" | "signal_sufficient"
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICResearchPlanner:
    """L1 pure planner for multi-hop research queries.
    
    Generates deterministic research plans with vector-first queries,
    expansion strategies, and evidence targets without external calls.
    """
    
    def __init__(
        self,
        *,
        max_hops: int = 3,
        enable_temporal_signal: bool = True,
        enable_synonym_expansion: bool = True,
        enable_cache_critique: bool = True,
        telemetry_bus: Optional[Any] = None,
    ) -> None:
        """Initialize LIC research planner with configuration."""
        self.max_hops = max_hops
        self.enable_temporal_signal = enable_temporal_signal
        self.enable_synonym_expansion = enable_synonym_expansion
        self.enable_cache_critique = enable_cache_critique
        self.telemetry_bus = telemetry_bus
        
        logger.debug(f"LIC Research Planner initialized: max_hops={max_hops}")
    
    def plan(
        self,
        *,
        role_title: str,
        company_name: str,
        outreach_context: Dict[str, Any],
    ) -> LICResearchPlan:
        """Generate a deterministic research plan for role and company.
        
        Args:
            role_title: Target role title (e.g., "Senior Software Engineer")
            company_name: Target company name
            outreach_context: Context data for planning (treated as opaque)
            
        Returns:
            Complete LIC research plan with multi-hop queries
        """
        # 1. Build vector-first seed queries
        seed_queries = self._build_seed_queries(role_title, company_name)
        
        # 2. Generate multi-hop research plan
        hops = []
        for hop_index in range(1, self.max_hops + 1):
            hop = self._create_research_hop(
                hop_index=hop_index,
                role_title=role_title,
                company_name=company_name,
                seed_queries=seed_queries,
            )
            hops.append(hop)
        
        # 3. Determine stop condition
        stop_condition = (
            "cache_good_enough" if self.enable_cache_critique else "max_hops"
        )
        
        # 4. Build metadata with signal targets
        metadata = {
            "signal_targets": ["funding", "product", "strategy", "personnel", "market"],
            "cache_critique_enabled": self.enable_cache_critique,
            "temporal_signal_enabled": self.enable_temporal_signal,
            "synonym_expansion_enabled": self.enable_synonym_expansion,
        }
        
        # 5. Create research plan
        plan = LICResearchPlan(
            role_title=role_title,
            company_name=company_name,
            seed_queries=seed_queries,
            hops=hops,
            max_hops=self.max_hops,
            stop_condition=stop_condition,
            metadata=metadata,
        )
        
        # 6. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)
        
        return plan
    
    def _build_seed_queries(self, role_title: str, company_name: str) -> List[str]:
        """Build vector-first seed queries for research.
        
        Args:
            role_title: Target role title
            company_name: Target company name
            
        Returns:
            List of seed query strings
        """
        return [
            f"{role_title} responsibilities at {company_name}",
            f"{company_name} strategy {role_title}",
            f"{company_name} product roadmap",
        ]
    
    def _create_research_hop(
        self,
        hop_index: int,
        role_title: str,
        company_name: str,
        seed_queries: List[str],
    ) -> LICResearchHop:
        """Create a single research hop with expansion strategy.
        
        Args:
            hop_index: 1-based hop index
            role_title: Target role title
            company_name: Target company name
            seed_queries: Base seed queries
            
        Returns:
            Configured research hop
        """
        # Choose expansion strategy based on hop index
        expansion_strategy = self._choose_expansion_strategy(hop_index)
        
        # Select seed query for this hop
        query_seed = seed_queries[(hop_index - 1) % len(seed_queries)]
        
        # Expand query using chosen strategy
        query_text = self._expand_query(
            query_seed, expansion_strategy, hop_index, role_title, company_name
        )
        
        # Determine freshness requirement
        requires_freshness = expansion_strategy == "temporal"
        
        # Build expected evidence list with signal targets
        expected_evidence = [
            "funding", "strategy", "product", "leadership moves", 
            "hiring signals", "technology stack"
        ]
        
        # Create hop metadata
        hop_metadata = {
            "expansion_applied": True,
            "role_aware": True,
            "vector_first": True,
        }
        
        return LICResearchHop(
            hop_index=hop_index,
            query_text=query_text,
            query_seed=query_seed,
            expansion_strategy=expansion_strategy,
            requires_freshness=requires_freshness,
            expected_evidence=expected_evidence,
            metadata=hop_metadata,
        )
    
    def _choose_expansion_strategy(self, hop_index: int) -> str:
        """Choose expansion strategy based on hop index and configuration.
        
        Args:
            hop_index: 1-based hop index
            
        Returns:
            Expansion strategy string
        """
        if hop_index == 1:
            return "semantic"
        elif hop_index == 2 and self.enable_temporal_signal:
            return "temporal"
        elif self.enable_synonym_expansion:
            return "role_synonym"
        else:
            return "hybrid"
    
    def _expand_query(
        self,
        query_seed: str,
        strategy: str,
        hop_index: int,
        role_title: str,
        company_name: str,
    ) -> str:
        """Expand query using the specified strategy.
        
        Args:
            query_seed: Original seed query
            strategy: Expansion strategy to apply
            hop_index: Current hop index
            role_title: Target role title
            company_name: Target company name
            
        Returns:
            Expanded query string
        """
        if strategy == "semantic":
            return self._semantic_expand(query_seed, role_title, company_name)
        elif strategy == "temporal":
            return self._temporal_expand(query_seed, role_title, company_name)
        elif strategy == "role_synonym":
            return self._synonym_expand(query_seed, role_title, company_name)
        elif strategy == "hybrid":
            return self._hybrid_expand(query_seed, hop_index, role_title, company_name)
        else:
            return query_seed
    
    def _semantic_expand(self, query_seed: str, role_title: str, company_name: str) -> str:
        """Apply semantic expansion to query.
        
        Args:
            query_seed: Original seed query
            role_title: Target role title
            company_name: Target company name
            
        Returns:
            Semantically expanded query
        """
        semantic_terms = [
            "engineering leadership", "technical strategy", "team dynamics",
            "development practices", "innovation initiatives"
        ]
        term = semantic_terms[(hash(role_title) % len(semantic_terms))]
        return f"{query_seed} {term} technical requirements"
    
    def _temporal_expand(self, query_seed: str, role_title: str, company_name: str) -> str:
        """Apply temporal expansion to query.
        
        Args:
            query_seed: Original seed query
            role_title: Target role title
            company_name: Target company name
            
        Returns:
            Temporally expanded query
        """
        temporal_terms = [
            "last 6 months", "recent announcements", "Q4 earnings call",
            "current quarter", "latest updates"
        ]
        term = temporal_terms[(hash(company_name) % len(temporal_terms))]
        return f"{query_seed} {term} developments changes"
    
    def _synonym_expand(self, query_seed: str, role_title: str, company_name: str) -> str:
        """Apply role synonym expansion to query.
        
        Args:
            query_seed: Original seed query
            role_title: Target role title
            company_name: Target company name
            
        Returns:
            Role-synonym expanded query
        """
        role_synonyms = {
            "engineer": "developer",
            "manager": "leader",
            "director": "head",
            "senior": "principal",
            "junior": "associate"
        }
        
        # Simple synonym replacement
        expanded_seed = query_seed
        for base, synonym in role_synonyms.items():
            if base in role_title.lower():
                expanded_seed = expanded_seed.replace(base, f"{base} {synonym}")
                break
        
        return f"{expanded_seed} IC-to-manager transitions career growth"
    
    def _hybrid_expand(
        self, 
        query_seed: str, 
        hop_index: int, 
        role_title: str, 
        company_name: str
    ) -> str:
        """Apply hybrid expansion combining multiple strategies.
        
        Args:
            query_seed: Original seed query
            hop_index: Current hop index
            role_title: Target role title
            company_name: Target company name
            
        Returns:
            Hybrid expanded query
        """
        # Combine semantic and role-specific elements
        semantic_part = self._semantic_expand(query_seed, role_title, company_name)
        role_specific = f"{role_title} interview preparation hiring process"
        
        return f"{semantic_part} {role_specific} team culture"
    
    def _safe_record_telemetry(self, plan: LICResearchPlan) -> None:
        """Record telemetry event safely without breaking planning.
        
        Args:
            plan: Generated research plan
        """
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_research_plan_created",
                layer="L1",
                payload={
                    "role_title": plan.role_title,
                    "company_name": plan.company_name,
                    "max_hops": plan.max_hops,
                    "stop_condition": plan.stop_condition,
                    "hop_count": len(plan.hops),
                    "cache_critique_enabled": plan.metadata.get("cache_critique_enabled", False),
                },
            )
        except Exception:
            # Telemetry failures should never break planning logic
            logger.debug("Failed to record telemetry for LIC research plan")
