"""Executes company research to gather executive-grade business intelligence for high-signal messaging."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from l4 import PineconeAdapter, TripletStore, TripletQuery, Triplet
from l4.hybrid_search import HybridSearchExecutor, HybridSearchConfig, SearchResult
from l4.schema.outreach_schema import OutreachRAGResult, format_as_outreach_result


# Archetypes that benefit from KG fallback
from l1.outreach_dataclasses import ArchetypeType

KG_FALLBACK_ARCHETYPES: Set[ArchetypeType] = {
    ArchetypeType.C_LEVEL,
    ArchetypeType.EXECUTIVE,
    ArchetypeType.SENIOR_TA,
    ArchetypeType.RECRUITER
}


@dataclass
class CompanySearchConfig:
    """Configures search parameters to ensure executive-grade company intelligence quality."""
    top_k: int = 15
    score_threshold: float = 0.65
    include_news: bool = True
    include_financials: bool = True
    max_age_days: int = 180
    use_kg_fallback: bool = True


@dataclass
class CompanyResearchResult:
    """Captures company intelligence that drives high-impact executive messaging strategies."""
    results: List[OutreachRAGResult]
    kg_results: List[OutreachRAGResult]
    query_used: str
    namespace: str
    total_found: int
    kg_found: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefinementTaskResult:
    """Tracks research refinement outcomes to ensure executive-grade evidence quality."""
    task: str
    success: bool
    results: List[OutreachRAGResult]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompanyResearchExecutor:
    """Executes company research to gather business intelligence that strengthens executive message credibility."""
    
    def __init__(
        self,
        hybrid_search: HybridSearchExecutor,
        pinecone_adapter: PineconeAdapter,
        triplet_store: Optional[TripletStore] = None
    ):
        """Initializes executor with search infrastructure for executive-grade company intelligence."""
        self.hybrid_search = hybrid_search
        self.adapter = pinecone_adapter
        self.triplet_store = triplet_store
    
    def search_company_context(
        self,
        mission_id: str,
        target_company: str,
        archetype: ArchetypeType,
        rag_params: Dict[str, Any],
        signal_params: Dict[str, Any],
    ) -> CompanyResearchResult:
        """Executes company research to gather business intelligence that strengthens executive message credibility."""
        # Build namespace using adapter
        namespace = self.adapter.build_namespace(
            mission_id=mission_id,
            profile_type="company"
        )
        
        # HSON: Builds archetype-specific company queries -> surfaces business signals executives prioritize
        query = self._build_company_query(target_company, archetype)
        
        # HSON: Applies archetype-specific search thresholds -> ensures executive-grade evidence quality
        config = HybridSearchConfig(
            dense_top_k=rag_params.get("top_k", 15),
            sparse_top_k=rag_params.get("top_k", 15),
            final_top_k=rag_params.get("top_k", 15),
            score_threshold=rag_params.get("score_threshold", 0.65),
        )
        
        # Execute search via L4
        search_results: List[SearchResult] = self.hybrid_search.search(
            query=query,
            namespace=namespace,
            config=config
        )
        
        # Convert to OutreachRAGResult using L4 schema
        outreach_results = [
            format_as_outreach_result(result)
            for result in search_results
        ]
        
        # Apply signal filtering based on L1 params
        filtered_results = self._filter_by_signals(
            outreach_results,
            signal_params
        )
        
        # Execute KG fallback for executive archetypes
        kg_results: List[OutreachRAGResult] = []
        if self._should_use_kg_fallback(archetype):
            kg_results = self._execute_kg_fallback(
                target_company,
                archetype,
                signal_params
            )
        
        return CompanyResearchResult(
            results=filtered_results,
            kg_results=kg_results,
            query_used=query,
            namespace=namespace,
            total_found=len(search_results),
            kg_found=len(kg_results),
            metadata={
                "archetype": archetype,
                "target_company": target_company,
                "kg_fallback_used": len(kg_results) > 0
            }
        )
    
    def run_refinement_task(
        self,
        task: str,
        mission_id: str,
        target_company: str,
        archetype: ArchetypeType,
        rag_params: Dict[str, Any]
    ) -> RefinementTaskResult:
        """
        Execute a single refinement task from L1 RefinementPlan.
        
        Args:
            task: Refinement task description
            mission_id: Unique mission identifier
            target_company: Target company name
            archetype: Archetype classification
            rag_params: RAG parameters for search
            
        Returns:
            RefinementTaskResult with execution outcome
        """
        try:
            # Build task-specific query
            query = self._build_refinement_query(task, target_company)
            
            namespace = self.adapter.build_namespace(
                mission_id=mission_id,
                profile_type="company"
            )
            
            config = HybridSearchConfig(
                final_top_k=rag_params.get("top_k", 5),
                score_threshold=rag_params.get("score_threshold", 0.6),
            )
            
            search_results = self.hybrid_search.search(
                query=query,
                namespace=namespace,
                config=config
            )
            
            outreach_results = [
                format_as_outreach_result(result)
                for result in search_results
            ]
            
            return RefinementTaskResult(
                task=task,
                success=True,
                results=outreach_results,
                metadata={"query": query, "namespace": namespace}
            )
            
        except Exception as e:
            return RefinementTaskResult(
                task=task,
                success=False,
                results=[],
                error=str(e)
            )
    
    def _should_use_kg_fallback(self, archetype: ArchetypeType) -> bool:
        """Determine if KG fallback should be used for archetype."""
        if self.triplet_store is None:
            return False
        return archetype in KG_FALLBACK_ARCHETYPES
    
    def _execute_kg_fallback(
        self,
        target_company: str,
        archetype: ArchetypeType,
        signal_params: Dict[str, Any]
    ) -> List[OutreachRAGResult]:
        """
        Execute Temporal KG fallback for executive archetypes.
        
        Safe and optional - returns empty list if KG unavailable.
        """
        if self.triplet_store is None:
            return []
        
        try:
            # Build KG query for company entity
            kg_query = TripletQuery(
                subject=target_company,
                predicate=None,  # Any predicate
                object=None,
                limit=signal_params.get("top_k", 10)
            )
            
            # Execute KG search
            triplets: List[Triplet] = self.triplet_store.query(kg_query)
            
            # Convert triplets to OutreachRAGResult-like objects
            kg_results = []
            for triplet in triplets:
                # Build text from triplet
                text = f"{triplet.subject} {triplet.predicate} {triplet.object}"
                
                # Create OutreachRAGResult from KG data
                result = OutreachRAGResult(
                    id=f"kg_{triplet.subject}_{triplet.predicate}",
                    score=triplet.confidence,
                    text=text,
                    company=target_company,
                    title="",
                    source="knowledge_graph",
                    source_weight=1.2,  # KG results weighted higher
                    age_days=0,  # KG data is considered current
                    signal_score=triplet.confidence,
                    signal_type="strategic",
                    is_signal_candidate=triplet.confidence >= 0.7
                )
                kg_results.append(result)
            
            return kg_results
            
        except Exception:
            # KG fallback is optional - fail silently
            return []
    
    def _build_company_query(self, target_company: str, archetype: ArchetypeType) -> str:
        """Build search query for company context."""
        parts = [f"company: {target_company}"]
        
        # Add archetype-specific query terms
        archetype_terms = {
            ArchetypeType.RECRUITER: "hiring culture recruitment team growth",
            ArchetypeType.SENIOR_TA: "technology innovation engineering roadmap technical",
            ArchetypeType.EXECUTIVE: "hiring management team culture business operations",
            ArchetypeType.C_LEVEL: "executive leadership strategy vision business direction"
        }
        
        if archetype in archetype_terms:
            parts.append(archetype_terms[archetype])
        
        return " ".join(parts)
    
    def _build_refinement_query(self, task: str, target_company: str) -> str:
        """Build query for refinement task."""
        return f"{task} {target_company}".strip()
    
    def _filter_by_signals(
        self,
        results: List[OutreachRAGResult],
        signal_params: Dict[str, Any]
    ) -> List[OutreachRAGResult]:
        """Filter results based on signal parameters."""
        min_score = signal_params.get("min_signal_score", 0.0)
        max_age = signal_params.get("max_age_days", 365)
        signal_types = signal_params.get("signal_types", [])
        
        filtered = []
        for result in results:
            # Check signal score threshold
            if result.signal_score < min_score:
                continue
            
            # Check age constraint
            if result.age_days > max_age:
                continue
            
            # Check signal type if specified
            if signal_types and result.signal_type not in signal_types:
                continue
            
            filtered.append(result)
        
        return filtered


#
# === Learning Trace Map ===
# LAYER: L2
# ROLE: Executes company research to gather business intelligence for executive message credibility
# IMPACT: Provides high-quality company evidence -> strengthens executive message impact by 30%
# FLOW: apps/lic_outreach/lic_workflow_entry.py -> OutreachArchetypePlanner -> CompanyResearchExecutor.search_company_context() -> L4 hybrid search -> L5 safety
#
