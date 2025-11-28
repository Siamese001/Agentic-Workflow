"""LIC Research Executor - L2 execution for multi-hop research pipeline.

Implements nuclear prompt requirements for deterministic research execution:
- Take LICResearchPlan from L1 and execute multi-hop RAG/search pipeline
- L2 only: may call tools/LLMs/clients, MUST NOT plan
- Iterate over hops, aggregate results into signals, defer scoring to L4
- Async-safe with explicit awaits, no asyncio.run()
"""

from typing import Any, Dict, List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class LICResearchExecutor:
    """L2 executor for LIC research plan execution.
    
    Executes multi-hop research plans by calling vector search,
    aggregating results, and delegating scoring to L4 modules.
    """
    
    def __init__(
        self,
        *,
        vector_memory: Optional[Any] = None,
        signal_scoring: Optional[Any] = None,
        cache_critique: Optional[Any] = None,
        telemetry_bus: Optional[Any] = None,
    ) -> None:
        """Initialize LIC research executor with dependencies."""
        self.vector_memory = vector_memory
        self.signal_scoring = signal_scoring
        self.cache_critique = cache_critique
        self.telemetry_bus = telemetry_bus
        
        if not self.vector_memory:
            logger.warning("No vector memory provided to research executor")
    
    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a multi-hop research plan.
        
        Args:
            plan: LICResearchPlan from L1 planner with hops and configuration
            
        Returns:
            Research signals dict consumed by L1 fusion planner
        """
        try:
            # 1. Extract plan configuration
            hops = plan.get("hops", [])
            max_hops = plan.get("max_hops", len(hops))
            role_title = plan.get("role_title", "")
            company_name = plan.get("company_name", "")
            
            # 2. Check cache critique if available
            if self.cache_critique:
                existing_cache = await self._get_existing_cache(company_name, role_title)
                targets = [hop.get("query_type", "general") for hop in hops]
                
                critique_result = await self.cache_critique.evaluate(
                    existing_signals=existing_cache,
                    targets=targets,
                )
                
                if critique_result.is_good_enough:
                    logger.debug(f"Using cached research for {company_name}")
                    return existing_cache
            
            # 3. Execute research hops
            research_signals = await self._execute_research_hops(
                hops, max_hops, role_title, company_name
            )
            
            # 4. Score signals if scoring module available
            if self.signal_scoring:
                research_signals = await self._score_research_signals(research_signals)
            
            # 5. Store results in vector memory for future cache
            if self.vector_memory:
                await self._store_research_signals(research_signals, company_name, role_title)
            
            # 6. Record telemetry (best-effort)
            self._safe_record_telemetry(plan, research_signals)
            
            return research_signals
            
        except Exception as e:
            logger.error(f"Research execution failed: {e}")
            return {"error": str(e), "signals": {}}
    
    async def _execute_research_hops(
        self,
        hops: List[Dict[str, Any]],
        max_hops: int,
        role_title: str,
        company_name: str,
    ) -> Dict[str, Any]:
        """Execute individual research hops and aggregate results."""
        research_signals = {
            "company_signals": [],
            "role_signals": [],
            "strategic_themes": [],
            "market_signals": [],
            "personnel_signals": [],
        }
        
        # Execute hops up to max_hops limit
        for i, hop in enumerate(hops[:max_hops]):
            try:
                hop_results = await self._execute_single_hop(hop, role_title, company_name)
                
                # Aggregate results by signal type
                signal_type = hop.get("signal_type", "company_signals")
                if signal_type in research_signals:
                    research_signals[signal_type].extend(hop_results)
                else:
                    research_signals[signal_type] = hop_results
                
                logger.debug(f"Completed hop {i+1}/{max_hops}, found {len(hop_results)} signals")
                
            except Exception as e:
                logger.error(f"Hop {i+1} execution failed: {e}")
                continue
        
        return research_signals
    
    async def _execute_single_hop(
        self,
        hop: Dict[str, Any],
        role_title: str,
        company_name: str,
    ) -> List[Dict[str, Any]]:
        """Execute a single research hop."""
        if not self.vector_memory:
            logger.warning("No vector memory available for hop execution")
            return []
        
        # Build query from hop configuration
        query_text = self._build_hop_query(hop, role_title, company_name)
        top_k = hop.get("top_k", 10)
        
        # Execute vector search
        try:
            raw_results = await self.vector_memory.query(query_text=query_text, top_k=top_k)
            
            # Process and normalize results
            processed_results = []
            for result in raw_results:
                processed_result = {
                    "id": result.get("id", f"hop_{hop.get('hop_id', 'unknown')}_{len(processed_results)}"),
                    "text": result.get("text", ""),
                    "signal_type": hop.get("signal_type", "company_signals"),
                    "source": result.get("source", "vector_db"),
                    "score": result.get("score", 0.0),
                    "metadata": {
                        "hop_id": hop.get("hop_id"),
                        "query_type": hop.get("query_type", "general"),
                        "company_name": company_name,
                        "role_title": role_title,
                        "hop_index": hop.get("hop_index", 0),
                        **result.get("metadata", {}),
                    },
                }
                processed_results.append(processed_result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Vector search failed for hop: {e}")
            return []
    
    def _build_hop_query(self, hop: Dict[str, Any], role_title: str, company_name: str) -> str:
        """Build query text for a research hop."""
        base_query = hop.get("query", "")
        
        # Enhance query with context
        if company_name:
            base_query = f"{company_name} {base_query}"
        
        if role_title:
            base_query = f"{role_title} {base_query}"
        
        # Add query type modifiers
        query_type = hop.get("query_type", "general")
        type_modifiers = {
            "funding": "funding investment round series",
            "strategy": "strategic initiatives vision direction",
            "product": "product roadmap features development",
            "personnel": "hiring team leadership employment",
            "market": "market competition industry position",
        }
        
        if query_type in type_modifiers:
            base_query = f"{base_query} {type_modifiers[query_type]}"
        
        return base_query.strip()
    
    async def _score_research_signals(self, research_signals: Dict[str, Any]) -> Dict[str, Any]:
        """Score research signals using L4 signal scoring module."""
        if not self.signal_scoring:
            return research_signals
        
        try:
            scored_signals = {}
            
            for signal_type, signals in research_signals.items():
                if isinstance(signals, list) and signals:
                    # Score signals of this type
                    scored_results = self.signal_scoring.score(signals)
                    
                    # Convert back to dict format with scores
                    scored_signals[signal_type] = []
                    for scored_signal in scored_results:
                        signal_dict = {
                            "id": scored_signal.signal_id,
                            "text": scored_signal.text,
                            "signal_type": signal_type,
                            "relevance_score": scored_signal.relevance_score,
                            "recency_score": scored_signal.recency_score,
                            "source_score": scored_signal.source_score,
                            "keyword_score": scored_signal.keyword_score,
                            "metadata": scored_signal.metadata,
                        }
                        scored_signals[signal_type].append(signal_dict)
                else:
                    scored_signals[signal_type] = signals
            
            return scored_signals
            
        except Exception as e:
            logger.error(f"Signal scoring failed: {e}")
            return research_signals
    
    async def _store_research_signals(
        self,
        research_signals: Dict[str, Any],
        company_name: str,
        role_title: str,
    ) -> None:
        """Store research signals in vector memory for future cache."""
        if not self.vector_memory:
            return
        
        try:
            # Flatten all signals for storage
            all_signals = []
            for signal_type, signals in research_signals.items():
                if isinstance(signals, list):
                    for signal in signals:
                        if isinstance(signal, dict):
                            # Add storage metadata
                            storage_signal = signal.copy()
                            storage_signal.update({
                                "company_name": company_name,
                                "role_title": role_title,
                                "signal_type": signal_type,
                                "storage_timestamp": asyncio.get_event_loop().time(),
                            })
                            all_signals.append(storage_signal)
            
            if all_signals:
                await self.vector_memory.upsert_signals(all_signals)
                logger.debug(f"Stored {len(all_signals)} signals in vector memory")
            
        except Exception as e:
            logger.error(f"Failed to store research signals: {e}")
    
    async def _get_existing_cache(self, company_name: str, role_title: str) -> Dict[str, Any]:
        """Get existing cached research signals."""
        if not self.vector_memory:
            return {}
        
        try:
            # Try to retrieve cached signals for this company/role
            cache_key = f"{company_name}_{role_title}"
            
            # Query vector memory for existing signals
            cached_results = await self.vector_memory.query(
                query_text=cache_key,
                top_k=50,  # Get more results for comprehensive cache
            )
            
            # Organize cached results by signal type
            cached_signals = {
                "company_signals": [],
                "role_signals": [],
                "strategic_themes": [],
                "market_signals": [],
                "personnel_signals": [],
            }
            
            for result in cached_results:
                signal_type = result.get("metadata", {}).get("signal_type", "company_signals")
                if signal_type in cached_signals:
                    cached_signals[signal_type].append(result)
            
            return cached_signals
            
        except Exception as e:
            logger.error(f"Failed to get existing cache: {e}")
            return {}
    
    def _safe_record_telemetry(self, plan: Dict[str, Any], research_signals: Dict[str, Any]) -> None:
        """Record telemetry event safely without breaking execution."""
        if not self.telemetry_bus:
            return
        
        try:
            total_signals = sum(
                len(signals) for signals in research_signals.values() 
                if isinstance(signals, list)
            )
            
            self.telemetry_bus.record_event(
                "lic_research_execution_completed",
                layer="L2",
                payload={
                    "company_name": plan.get("company_name", ""),
                    "role_title": plan.get("role_title", ""),
                    "hops_executed": len(plan.get("hops", [])),
                    "total_signals_found": total_signals,
                    "signal_types": list(research_signals.keys()),
                },
            )
        except Exception:
            # Telemetry failures should never break execution logic
            logger.debug("Failed to record telemetry for LIC research execution")
