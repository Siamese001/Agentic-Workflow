"""
HOP-2: Research Agent (V2 Architecture).

Synthesizes research context using a Vector-First strategy with Fallback RAG.
Migrated to V2AgentBase for immutable I/O and structured tracing.
"""

from __future__ import annotations

import asyncio
from typing import Any

# V2 Architecture Imports
from apps_lic.shared.v2_patterns.agent_base import V2AgentBase
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry

# Domain Imports
from apps_shared.utils.vector_memory import VectorMemoryStore


class HOP2ResearchAgent(V2AgentBase):
    """
    V2 Implementation of HOP-2.

    Architecture:
    - Base: V2AgentBase (Config, Tracing, Healing)
    - Input: 'hop1_analysis' (from HOP-1)
    - Logic: Vector Store Query -> Quality Critique -> Fallback RAG (if gaps)
    - Output: 'hop2_research'
    """

    def __init__(
        self, memory_store: VectorMemoryStore, search_client: Any = None, llm_client: Any = None
    ) -> None:
        """
        Initialize with dependencies.

        Args:
            memory_store: Vector DB connection for fast-path knowledge.
            search_client: Tool for slow-path RAG (Google Search/Perplexity).
            llm_client: Optional LLM for synthesis/reasoning.
        """
        # Initialize V2 base (loads config, toggles, etc.)
        super().__init__(llm_client=llm_client)

        self.memory_store = memory_store
        self.search_client = search_client

        # Load specific configs from the V2 AgentSpecs singleton
        self.vector_params = self.config.research_agent.vector_store_query_params
        self.fallback_params = self.config.research_agent.fallback_rag_params

        # Note: critiques params might need to be added to AgentSpecs schema if not present
        # For now, defaulting or reading from raw config if needed,
        # but adhering to schema is preferred.
        self.critique_params = {
            "min_confidence_score": 0.6,
            "min_recency_days": 30,
            "min_recipient_specific_count": 2,
        }

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute HOP-2 Logic: Vector First -> Critique -> RAG Fallback.
        """
        # 1. Read Input (Immutable)
        profile = buffer.read("hop1_analysis")
        if not profile:
            registry.add_trace("DATA_ERROR", {"msg": "Missing 'hop1_analysis' in buffer"})
            raise ValueError("HOP-2 requires 'hop1_analysis' input")

        company = profile.get("recipient_company")
        recipient = profile.get("recipient_name")
        archetype = profile.get("Archetype")

        registry.add_trace("PHASE_STEP", {"action": "query_vector_store", "target": company})

        # 2. Fast Path: Query Vector Store
        # (Note: Using asyncio.run if called synchronously, or await if _process were async.
        # V2AgentBase._process is sync, so we wrap async calls here.)
        cached_context = self._run_async(self._query_vector_store(company, recipient, archetype))

        registry.add_trace(
            "VECTOR_RESULTS",
            {
                "count": len(cached_context["all_results"]),
                "confidence": cached_context["cache_confidence"],
            },
        )

        # 3. Critique Cache Quality
        is_sufficient, gaps = self._critique_cache(cached_context)

        final_context = cached_context
        fallback_used = False

        if is_sufficient:
            registry.add_trace(
                "DECISION_CACHE_HIT", {"confidence": cached_context["cache_confidence"]}
            )
        else:
            registry.add_trace("DECISION_CACHE_MISS", {"gaps": gaps})

            # 4. Slow Path: Fallback RAG
            if self.search_client:
                registry.add_trace("RAG_ACTIVATED", {"gaps": gaps})
                fallback_context = self._run_async(self._run_fallback_rag(company, recipient, gaps))
                final_context = self._merge_contexts(cached_context, fallback_context)
                fallback_used = True
            else:
                registry.add_trace("RAG_SKIPPED", {"reason": "No search_client available"})

        # 5. Write Output (Immutable)
        output_data = {
            "recipient_insights": final_context["recipient_insights"],
            "company_context": final_context["company_context"],
            "strategic_brief": final_context["strategic_brief"],
            "rag_results": final_context["all_results"],
            "signal_score": final_context["signal_score"],
            "cache_hit": is_sufficient,
            "fallback_used": fallback_used,
            "total_sources": len(final_context["all_results"]),
            "gaps_identified": gaps,
        }

        buffer.write_once("hop2_research", output_data)

        registry.add_trace(
            "DECISION_FINAL",
            {"signal_score": output_data["signal_score"], "sources": output_data["total_sources"]},
        )

    # --- Helper Methods (Ported from v13.1) ---

    def _run_async(self, coro):
        """Helper to run async code in sync V2 pipeline."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    async def _query_vector_store(
        self, company: str, recipient: str, archetype: str
    ) -> dict[str, Any]:
        """Query vector store for pre-computed intelligence."""
        # Safety check for memory store availability
        if not self.memory_store:
            return {
                "recipient_insights": [],
                "company_context": [],
                "strategic_brief": "",
                "all_results": [],
                "signal_score": 0.0,
                "cache_confidence": 0.0,
            }

        company_results = self.memory_store.query_by_company(
            company_name=company,
            query_text="strategic priorities initiatives roadmap platform",
            n_results=self.vector_params.get("top_k", 10),  # specific config mapping
        )

        exec_results = self.memory_store.query_by_executive(
            executive_name=recipient,
            query_text="recent posts presentations LinkedIn about background",
            n_results=10,
        )

        strategic_briefs = self.memory_store.get_strategic_briefs(
            company_name=company, max_age_days=90
        )

        recipient_insights = [r["text"][:200] for r in exec_results[:5]]
        company_context = [r["text"][:200] for r in company_results[:5]]
        strategic_brief_text = "\n".join([s["text"] for s in strategic_briefs])

        all_results = company_results + exec_results + strategic_briefs
        signal_score = self._calculate_signal_score(all_results)
        cache_confidence = self._calculate_cache_confidence(
            company_results, exec_results, strategic_briefs
        )

        return {
            "recipient_insights": recipient_insights,
            "company_context": company_context,
            "strategic_brief": strategic_brief_text,
            "all_results": all_results,
            "signal_score": signal_score,
            "cache_confidence": cache_confidence,
        }

    def _critique_cache(self, cached_context: dict[str, Any]) -> tuple[bool, list[str]]:
        """Evaluate if cached context is sufficient."""
        min_confidence = self.critique_params["min_confidence_score"]
        min_recency = self.critique_params["min_recency_days"]
        min_recipient_count = self.critique_params["min_recipient_specific_count"]

        gaps = []

        if len(cached_context["strategic_brief"]) < 100:
            gaps.append("strategic_brief")

        recent_sources = [
            r
            for r in cached_context["all_results"]
            if r.get("metadata", {}).get("age_days", 999) < min_recency
        ]
        if len(recent_sources) < 3:
            gaps.append("recent_news")

        if len(cached_context["recipient_insights"]) < min_recipient_count:
            gaps.append("recipient_profile")

        if cached_context["cache_confidence"] < min_confidence:
            gaps.append("low_confidence")

        is_sufficient = len(gaps) == 0
        return is_sufficient, gaps

    async def _run_fallback_rag(
        self, company: str, recipient: str, gaps: list[str]
    ) -> dict[str, Any]:
        """Run fallback RAG only for identified gaps."""
        fallback_results = []

        # Check explicit self.search_client just in case
        if not self.search_client:
            return {"rag_results": []}

        for gap in gaps:
            query = ""
            source_type = ""
            if gap == "strategic_brief":
                query = f"{company} strategic priorities 2025 roadmap"
                source_type = "STRATEGIC_BRIEF"
            elif gap == "recent_news":
                query = f"{company} recent news announcements"
                source_type = "NEWS_ARTICLE_COMPANY"
            elif gap == "recipient_profile":
                query = f"{recipient} {company} LinkedIn profile"
                source_type = "RECIPIENT_LINKEDIN_ABOUT"

            if query:
                results = self.search_client.search(query, num_results=3)
                fallback_results.extend(self._format_search_results(results, source_type))
                await asyncio.sleep(0.5)  # Rate limit protection

        return {"rag_results": fallback_results}

    def _merge_contexts(self, cached: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
        """Merge cached and fallback contexts."""
        merged = cached.copy()
        # Ensure deep copy of list if needed, or simple extend
        merged["all_results"] = cached["all_results"] + fallback.get("rag_results", [])
        merged["signal_score"] = self._calculate_signal_score(merged["all_results"])
        return merged

    def _calculate_signal_score(self, results: list[dict[str, Any]]) -> float:
        """Calculate aggregate signal quality score."""
        if not results:
            return 0.0
        scores = [r.get("metadata", {}).get("source_weight", 0.5) for r in results]
        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_cache_confidence(
        self, company_results: list, exec_results: list, strategic_briefs: list
    ) -> float:
        """Calculate confidence in cached data."""
        has_strategic = 1.0 if strategic_briefs else 0.0
        has_company = min(1.0, len(company_results) / 10)
        has_exec = min(1.0, len(exec_results) / 5)
        return has_strategic * 0.5 + has_company * 0.3 + has_exec * 0.2

    def _format_search_results(self, results: list, source_type: str) -> list[dict[str, Any]]:
        """Format search results for consistency."""
        formatted = []
        for result in results:
            formatted.append(
                {
                    "text": result.get("snippet", ""),
                    "metadata": {
                        "SourceType": source_type,
                        "source_url": result.get("link", ""),
                        "title": result.get("title", ""),
                        "age_days": 0,
                        "source_weight": 1.0,
                    },
                }
            )
        return formatted

    def heal_repository(self) -> None:
        """
        V2 Self-Healing.
        Wraps domain-specific checks in the V2 error handling.
        """
        super().heal_repository()

        # Domain specific healing - Note: log methods not available in current mixin
        if not self.memory_store:
            pass  # Would log warning about vector store missing

        if not self.search_client:
            pass  # Would log warning about search client missing
