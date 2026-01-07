from __future__ import annotations
"""HOP-2: Research Agent - Vector-store-first with fallback RAG."""

__version__ = "13.1"

import asyncio
import logging
from typing import Dict, List, Any

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

from apps_shared.utils.state_manager import StateManager
from apps_shared.utils.vector_memory import VectorMemoryStore

Logger = logging.getLogger(__name__)


class HOP2ResearchAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    v13.1: Research Agent - Vector-store-first with fallback RAG (MCP Hardened)
    
    BREAKING CHANGE from v12.0:
    - OLD: All research at runtime (60-80s)
    - NEW: Query vector store first (<1s), fallback RAG only for gaps
    
    Single Responsibility: Synthesize research context
    
    Input:  state/1_profile_analysis.json
    Output: state/2_research_context.json
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        memory_store: VectorMemoryStore,
        search_client: Any = None,
        llm_client: Any = None
    ):
        super().__init__()
        self.config = config["research_agent"]
        self.memory_store = memory_store
        self.search_client = search_client
        self.llm_client = llm_client
        
        self.vector_params = self.config["vector_store_query_params"]
        self.fallback_params = self.config["fallback_rag_params"]
        self.critique_params = self.config["cache_critique_params"]
    
    async def execute(self, state_mgr: StateManager) -> str:
        """Execute HOP-2: Research synthesis with vector-first strategy"""
        print(f"\n{'='*80}")
        print("HOP-2: RESEARCH AGENT (Vector-Store-First)")
        print(f"{'='*80}\n")
        
        profile_state = state_mgr.read_state("HOP-1")
        company = profile_state["recipient_company"]
        recipient = profile_state["recipient_name"]
        Archetype = profile_state["Archetype"]
        
        print("STEP 1: Querying vector store (cached intelligence)...")
        cached_context = await self._query_vector_store(company, recipient, Archetype)
        print(f"  ✓ Retrieved {len(cached_context['all_results'])} cached documents")
        
        print("\nSTEP 2: Evaluating cache quality...")
        is_sufficient, gaps = self._critique_cache(cached_context)
        
        if is_sufficient:
            print(f"  ✓ Cache is sufficient (confidence: {cached_context['cache_confidence']:.2f})")
            final_context = cached_context
        else:
            print(f"  ⚠ Cache has gaps: {gaps}")
            print(f"\nSTEP 3: Running fallback RAG to fill gaps...")
            fallback_context = await self._run_fallback_rag(company, recipient, gaps)
            print(f"  ✓ Retrieved {len(fallback_context['rag_results'])} additional sources")
            final_context = self._merge_contexts(cached_context, fallback_context)
        
        output_state = {
            "recipient_insights": final_context["recipient_insights"],
            "company_context": final_context["company_context"],
            "strategic_brief": final_context["strategic_brief"],
            "rag_results": final_context["all_results"],
            "signal_score": final_context["signal_score"],
            "cache_hit": is_sufficient,
            "fallback_used": not is_sufficient,
            "total_sources": len(final_context["all_results"])
        }
        
        output_path = state_mgr.write_state("HOP-2", output_state)
        
        print(f"\n✓ Research Complete")
        print(f"  Total sources: {output_state['total_sources']}")
        print(f"  Signal score: {output_state['signal_score']:.2f}")
        print(f"  Cache hit: {output_state['cache_hit']}\n")
        
        return output_path
    
    async def _query_vector_store(self, company: str, recipient: str, Archetype: str) -> Dict[str, Any]:
        """Query vector store for pre-computed intelligence"""
        company_results = self.memory_store.query_by_company(
            company_name=company,
            query_text="strategic priorities initiatives roadmap platform",
            n_results=self.vector_params["n_results"]
        )
        
        exec_results = self.memory_store.query_by_executive(
            executive_name=recipient,
            query_text="recent posts presentations LinkedIn about background",
            n_results=10
        )
        
        strategic_briefs = self.memory_store.get_strategic_briefs(
            company_name=company,
            max_age_days=90
        )
        
        recipient_insights = [r["text"][:200] for r in exec_results[:5]]
        company_context = [r["text"][:200] for r in company_results[:5]]
        strategic_brief_text = "\n".join([s["text"] for s in strategic_briefs])
        
        all_results = company_results + exec_results + strategic_briefs
        signal_score = self._calculate_signal_score(all_results)
        cache_confidence = self._calculate_cache_confidence(company_results, exec_results, strategic_briefs)
        
        return {
            "recipient_insights": recipient_insights,
            "company_context": company_context,
            "strategic_brief": strategic_brief_text,
            "all_results": all_results,
            "signal_score": signal_score,
            "cache_confidence": cache_confidence
        }
    
    def _critique_cache(self, cached_context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Evaluate if cached context is sufficient"""
        min_confidence = self.critique_params["min_confidence_score"]
        min_recency = self.critique_params["min_recency_days"]
        min_recipient_count = self.critique_params["min_recipient_specific_count"]
        
        gaps = []
        
        has_strategic_brief = len(cached_context["strategic_brief"]) > 100
        if not has_strategic_brief:
            gaps.append("strategic_brief")
        
        recent_sources = [
            r for r in cached_context["all_results"]
            if r.get("metadata", {}).get("age_days", 999) < min_recency
        ]
        has_recent = len(recent_sources) >= 3
        if not has_recent:
            gaps.append("recent_news")
        
        has_recipient_data = len(cached_context["recipient_insights"]) >= min_recipient_count
        if not has_recipient_data:
            gaps.append("recipient_profile")
        
        confidence_ok = cached_context["cache_confidence"] >= min_confidence
        if not confidence_ok:
            gaps.append("low_confidence")
        
        is_sufficient = len(gaps) == 0
        return is_sufficient, gaps
    
    async def _run_fallback_rag(self, company: str, recipient: str, gaps: List[str]) -> Dict[str, Any]:
        """Run fallback RAG only for identified gaps"""
        fallback_results = []
        
        for gap in gaps:
            if gap == "strategic_brief":
                query = f"{company} strategic priorities 2025 roadmap"
                results = self.search_client.search(query, num_results=3)
                fallback_results.extend(self._format_search_results(results, "STRATEGIC_BRIEF"))
            elif gap == "recent_news":
                query = f"{company} recent news announcements"
                results = self.search_client.search(query, num_results=3)
                fallback_results.extend(self._format_search_results(results, "NEWS_ARTICLE_COMPANY"))
            elif gap == "recipient_profile":
                query = f"{recipient} {company} LinkedIn profile"
                results = self.search_client.search(query, num_results=2)
                fallback_results.extend(self._format_search_results(results, "RECIPIENT_LINKEDIN_ABOUT"))
            
            await asyncio.sleep(1)
        
        return {"rag_results": fallback_results}
    
    def _merge_contexts(self, cached: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Merge cached and fallback contexts"""
        merged = cached.copy()
        merged["all_results"].extend(fallback.get("rag_results", []))
        merged["signal_score"] = self._calculate_signal_score(merged["all_results"])
        return merged
    
    def _calculate_signal_score(self, results: List[Dict[str, Any]]) -> float:
        """Calculate aggregate signal quality score"""
        if not results:
            return 0.0
        scores = [r.get("metadata", {}).get("source_weight", 0.5) for r in results]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_cache_confidence(self, company_results: List[Dict], exec_results: List[Dict], strategic_briefs: List[Dict]) -> float:
        """Calculate confidence in cached data"""
        has_strategic = 1.0 if strategic_briefs else 0.0
        has_company = min(1.0, len(company_results) / 10)
        has_exec = min(1.0, len(exec_results) / 5)
        return has_strategic * 0.5 + has_company * 0.3 + has_exec * 0.2
    
    def _format_search_results(self, results: List[Dict], SourceType: str) -> List[Dict[str, Any]]:
        """Format search results for consistency"""
        formatted = []
        for result in results:
            formatted.append({
                "text": result.get("snippet", ""),
                "metadata": {
                    "SourceType": SourceType,
                    "source_url": result.get("link", ""),
                    "title": result.get("title", ""),
                    "age_days": 0,
                    "source_weight": 1.0
                }
            })
        return formatted

    def heal_repository(self) -> None:
        """Autonomy healing: Validate and auto-correct agent state/config for reliable research synthesis.

        - Chains super() for shared diagnostics/rollback
        - Lic-specific: vector store health, cache integrity, search client availability
        - MCP ensures safe operations (e.g., sanitized queries)
        """
        super().heal_repository()

        self._heal_vector_store()
        self._heal_search_client()
        self._heal_cache_integrity()
        self._run_research_diagnostics()

    def _heal_vector_store(self) -> None:
        """Validate and repair vector store connection if corrupted."""
        try:
            if not self.memory_store:
                Logger.warning("Vector store missing — cannot reinitialize")
                return
            if not hasattr(self.memory_store, 'is_healthy'):
                Logger.warning("Vector store missing health check — skipping")
                return
            if not self.memory_store.is_healthy():
                Logger.warning("Vector store unhealthy — attempting reconnect")
                if hasattr(self.memory_store, 'reconnect'):
                    self.memory_store.reconnect()
        except Exception as e:
            Logger.error(f"Vector store healing failed: {e}")

    def _heal_search_client(self) -> None:
        """Validate search client availability and gracefully degrade if needed."""
        try:
            if not self.search_client:
                Logger.warning("Search client missing — fallback RAG disabled")
                return
            if not hasattr(self.search_client, 'search'):
                Logger.error("Search client missing search method — disabling fallback")
                self.search_client = None
        except Exception as e:
            Logger.error(f"Search client validation failed: {e}")

    def _heal_cache_integrity(self) -> None:
        """Validate cache parameters and repair if corrupted."""
        try:
            if not isinstance(self.critique_params, dict):
                Logger.warning("Critique params corrupted — resetting to defaults")
                self.critique_params = {
                    "min_confidence_score": 0.6,
                    "min_recency_days": 30,
                    "min_recipient_specific_count": 2
                }
            required_keys = ["min_confidence_score", "min_recency_days", "min_recipient_specific_count"]
            for key in required_keys:
                if key not in self.critique_params:
                    Logger.warning(f"Missing critique param {key} — setting default")
                    if key == "min_confidence_score":
                        self.critique_params[key] = 0.6
                    elif key == "min_recency_days":
                        self.critique_params[key] = 30
                    elif key == "min_recipient_specific_count":
                        self.critique_params[key] = 2
        except Exception as e:
            Logger.error(f"Cache integrity check failed: {e}")

    def _run_research_diagnostics(self) -> None:
        """Run research-specific health checks (e.g., mock vector query)."""
        try:
            if not self.memory_store:
                Logger.error("Diagnostics skipped — vector store unavailable")
                return
            test_results = self.memory_store.query_by_company(
                company_name="test_company",
                query_text="test query",
                n_results=1
            )
            if not isinstance(test_results, list):
                Logger.error("Diagnostics failed — invalid vector store response")
        except Exception as e:
            Logger.error(f"Research diagnostics exception: {e}")
