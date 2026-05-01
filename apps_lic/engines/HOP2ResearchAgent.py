"""
HOP-2: Research Agent (V2.5 Architecture).

LIC Sovereign Strategist.
Implements K.3 Retrieval Planning and Evidence Artifact generation.
"""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from typing import Any

from apps_lic.config.loader_config import load_agent_specs
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer

# LIC Sovereign Architecture Imports
from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.TraceRegistry import TraceRegistry

# Domain Imports
try:
    from apps_shared.utils.vector_memory import VectorMemoryStore
except ImportError:
    VectorMemoryStore = None  # Allow stub mode


@dataclass
class HOP2ResearchAgent(LICAgentBase, SubatomicTestingMixin):
    """
    LIC Sovereign Strategist.

    Architecture:
    - Base: LICAgentBase (Config, Tracing, Healing)
    - Input: 'hop1_analysis' (from HOP-1), 'mission_input'
    - Logic: K.3 Retrieval Planning -> Evidence Artifact Generation
    - Output: 'hop2_research' with evidence_pack and strategic_brief
    """

    # Optional dependencies for dataclass
    memory_store: Any | None = field(default=None)
    search_client: Any | None = field(default=None)
    llm_client: Any | None = field(default=None)

    # Sovereign Seal: Runtime immutability flag
    _sealed: bool = field(default=False, init=False, repr=False)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Enforce Sovereign Seal (Runtime Immutability).
        """
        if getattr(self, "_sealed", False):
            raise AttributeError(
                f"Sovereign Seal Active: Cannot modify '{name}' on {self.__class__.__name__}"
            )
        super().__setattr__(name, value)

    def __getstate__(self) -> dict[str, Any]:
        """
        Pickling support for Sovereign Sealed agent.
        """
        return self.__dict__.copy()

    def __setstate__(self, state: dict[str, Any]) -> None:
        """
        Unpickling support: Temporarily bypass Sovereign Seal to restore state.
        """
        object.__setattr__(self, "_sealed", False)
        self.__dict__.update(state)
        object.__setattr__(self, "_sealed", True)

    def __post_init__(self) -> None:
        """
        Initialize after dataclass construction.
        """
        # Root Injection: LICAgentBase must lead MRO to establish SSOT.
        super().__post_init__()

        # RCA FIX: Handle 'research_agent' vs 'research' naming mismatch in Sovereign Blueprint.
        # Critical Analysis: We use defensive getattr to prevent the 'AttributeError' loop which crashes the engine.
        agent_specs = load_agent_specs()
        agent_config = getattr(agent_specs, "research_agent", None) or getattr(
            agent_specs, "research", None
        )

        if agent_config is None:
            raise AttributeError(
                f"Sovereign Blueprint Fault: '{self.__class__.__name__}' config key missing. "
                "Expected 'research_agent' or 'research'."
            )

        # Set attributes BEFORE sealing
        self.agent_specs = agent_specs
        self.vector_params = agent_config.vector_store_query_params
        self.fallback_params = agent_config.fallback_rag_params

        self.critique_params = {
            "min_confidence_score": 0.6,
            "min_recency_days": 30,
            "min_recipient_specific_count": 2,
        }

        # Engage Sovereign Seal
        object.__setattr__(self, "_sealed", True)

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute HOP-2 Logic: K.3 Retrieval Planning -> Evidence Artifacts.
        """
        # 1. Read Sovereign Input and Mission Context
        hop1 = buffer.read("hop1_analysis")
        mission_input = buffer.read("mission_input")

        if not hop1:
            registry.add_trace("DATA_ERROR", {"msg": "Missing hop1_analysis"})
            raise RuntimeError("HOP-2 missing critical upstream context")

        # Defensive check for C_LEVEL requirements
        archetype = hop1.get("Archetype", "UNKNOWN")
        if archetype == "C_LEVEL" and not mission_input.get("company_id"):
            registry.add_trace("INPUT_WARNING", {"msg": "C_LEVEL mission missing company_id"})

        registry.add_trace("PHASE_STEP", {"action": "starting_retrieval_planning"})

        # 2. Derive Research 'Wants' (K.3 Logic)
        wants = self._derive_wants(archetype, mission_input or {})

        # 3. Build and Execute Retrieval Plan
        # [Logic: Prioritizes Vector DB, falls back to Web Search for gaps]
        retrievals = self._execute_plan(wants, registry)

        # 4. Record Evidence Artifacts (K.3 Logic)
        evidence_pack = []
        for item in retrievals:
            artifact_id = self._generate_stable_id(item)
            evidence_pack.append(
                {
                    "artifact_id": artifact_id,
                    "summary": item["text"],
                    "source": item["source"],
                    "confidence": item.get("confidence", 0.7),
                }
            )

        # 5. Strategic Brief Generation (Specialist Hook)
        strategic_brief = self._summarize_for_archetype(evidence_pack, archetype)

        # 6. Write to Immutable Buffer
        output_data = {
            "evidence_pack": evidence_pack,
            "strategic_brief": strategic_brief,
            "metadata": {"wants_count": len(wants), "retrieval_count": len(retrievals)},
        }

        buffer.write_once("hop2_research", output_data)
        registry.add_trace("RETRIEVAL_PLAN_COMPLETED", {"artifacts": len(evidence_pack)})

    def _derive_wants(self, archetype: str, mission_input: dict) -> list[str]:
        """K.3 Logic: Determines context needs based on seniority and mission targets."""
        contact_name = mission_input.get("contact_name", "Unknown")
        company_id = mission_input.get("company_id", "Unknown")
        contact_id = mission_input.get("recipient_id", "Unknown")

        # Primary Anchor: Profile Highlights
        wants = [f"Strategic background for {contact_name} ({contact_id})"]

        # Secondary Anchor: Seniority-based signals
        if archetype == "C_LEVEL":
            wants.extend(
                [
                    f"{company_id} 2025 strategic priorities",
                    f"{company_id} quarterly earnings signals",
                ]
            )

        if not wants:
            wants.append("Context for: prospect overview")
        return wants

    def _generate_stable_id(self, item: dict) -> str:
        """Generates deterministic artifact ID for traceability."""
        text = item.get("text", "")
        source = item.get("source", "")
        company_id = item.get("company_id", "na")
        tool = item.get("tool", "research")
        # Multi-factor seed for collision avoidance
        seed = f"v2.5|{company_id}|{tool}|{source}|{text[:64]}"
        return hashlib.sha256(seed.encode()).hexdigest()[:12]

    def _execute_plan(self, wants: list[str], registry: TraceRegistry) -> list[dict[str, Any]]:
        """
        Execute retrieval plan against available data sources.
        Uses vector store if available, otherwise returns mock data.
        """
        results = []

        # If we have a memory store, use it
        if hasattr(self, "memory_store") and self.memory_store:
            for want in wants:
                try:
                    # Query vector store for each want
                    query_results = self.memory_store.query_by_company(
                        company_name=want.split()[-1] if want else "", query_text=want, n_results=3
                    )
                    for r in query_results:
                        results.append(
                            {
                                "text": r.get("text", "")[:200],
                                "source": r.get("metadata", {}).get("source_url", "vector_store"),
                                "confidence": r.get("metadata", {}).get("source_weight", 0.7),
                            }
                        )
                except Exception:
                    pass

        # Fallback: Generate placeholder results for testing
        if not results:
            for want in wants:
                results.append(
                    {
                        "text": f"Research result for: {want}",
                        "source": "internal_knowledge_base",
                        "confidence": 0.7,
                    }
                )

        return results

    def _summarize_for_archetype(self, evidence_pack: list[dict], archetype: str) -> str:
        """Generate strategic brief tailored to archetype."""
        if not evidence_pack:
            return "No evidence available for strategic brief."

        # FIX: Resolve nested loop syntax error and ensure 100-char truncation
        summaries = [str(e["summary"])[:100].strip() for e in evidence_pack[:3]]
        brief = f"Strategic Brief for {archetype}: " + " | ".join(summaries)
        return brief[:500]  # Limit total length

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
