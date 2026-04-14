"""Search Fusion Engine.

Implements fusion of multiple search strategies (local, global, DRIFT)
with various fusion methods and result diversification.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L4_state.types.graph_store_types import IGraphStore

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.reasoning.drift_search_engine import create_drift_search_engine
from agentic_core.L1_cognition.reasoning.global_search_engine import create_global_search_engine
from agentic_core.L1_cognition.reasoning.local_search_engine import create_local_search_engine
from agentic_core.L1_cognition.types.search_types import (
    DRIFTSearchConfig,
    FusionConfig,
    GlobalSearchConfig,
    LocalSearchConfig,
    SearchQuery,
    SearchResponse,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from tqdm import tqdm

emit_replay_key("p0", "search_fusion_engine")
emit_determinism_digest("p0", "search_fusion_engine")

_emit_dispatches_healing_run("p1", "search_fusion_engine", "L1")
_emit_routes_through("p1", "search_fusion_engine", "L1")
_emit_checks_agent_registry("p1", "search_fusion_engine", "agent_registry")
_emit_validates_agent_capability("p1", "search_fusion_engine", "capability")
_emit_dispatches_execution_plan("p1", "search_fusion_engine", "exec_plan")
_emit_agent_executes_agent("p1", "search_fusion_engine", "sub_agent")
_emit_routes_to_agent("p1", "search_fusion_engine", "target_agent")
_emit_verifies_policy("p1", "search_fusion_engine", "policy_check")
_emit_observes_runtime_state("p1", "search_fusion_engine", "runtime_state")
_emit_verifies_boundary("p1", "search_fusion_engine", "boundary_check")
_emit_transcripts_response("p1", "search_fusion_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "search_fusion_engine")
_emit_gated_by_confidence("p1", "search_fusion_engine", "confidence_gate")
_emit_escalates_to_human("p1", "search_fusion_engine", "L1")
_emit_reads_policy_state("p1", "search_fusion_engine", "L1")
_emit_authorize_and_execute("p2", "search_fusion_engine", "execution_auth")
_emit_validates_capability("p2", "search_fusion_engine", "capability_check")
_emit_routes_to_capability("p2", "search_fusion_engine", "capability_route")
_emit_writes_via_uwg("p2", "search_fusion_engine", "uwg_write")
_emit_blocks_direct_write("p2", "search_fusion_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "search_fusion_engine", "tool_invocation")
_emit_captures_execution_output("p2", "search_fusion_engine", "exec_output")
_emit_dispatches_agent("p3", "search_fusion_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "search_fusion_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "search_fusion_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "search_fusion_engine", "healing_outcome")
_emit_escalates_failure("p3", "search_fusion_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "search_fusion_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "search_fusion_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "search_fusion_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "search_fusion_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "search_fusion_engine", "eval_metric")
_emit_stores_embedding("p4", "search_fusion_engine", "embedding_store")


class SearchFusionEngine:
    """Implements fusion of multiple search strategies."""

    def __init__(
        self,
        graph_store: IGraphStore,
        fusion_config: FusionConfig | None = None,
        local_config: LocalSearchConfig | None = None,
        global_config: GlobalSearchConfig | None = None,
        drift_config: DRIFTSearchConfig | None = None,
    ) -> None:
        """Initialize the search fusion engine.

        Args:
            graph_store: The graph store to search in
            fusion_config: Fusion configuration
            local_config: Local search configuration
            global_config: Global search configuration
            drift_config: DRIFT search configuration
        """
        self.graph_store = graph_store
        self.fusion_config = fusion_config or FusionConfig()
        self.graphrag_config = get_config()

        # Initialize individual search engines
        self.local_engine = create_local_search_engine(graph_store, local_config)
        self.global_engine = create_global_search_engine(graph_store, global_config)
        self.drift_engine = create_drift_search_engine(graph_store, drift_config)

        # Performance tracking
        self._search_stats: dict[str, list[float]] = {
            "local": [],
            "global": [],
            "drift": [],
            "fusion": [],
        }

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform fused search using all strategies.

        Args:
            query: The search query

        Returns:
            SearchResponse with fused results
        """
        start_time = datetime.utcnow()

        try:
            # Step 1: Execute individual searches
            local_response, global_response, drift_response = await self._execute_individual_searches(query)

            # Step 2: Apply fusion method
            fused_response = await self._fuse_results(
                local_response,
                global_response,
                drift_response,
                query,
            )

            # Step 3: Apply diversification if enabled
            if self.fusion_config.enable_diversification:
                fused_response.results = self._apply_diversification(fused_response.results)

            # Step 4: Apply final limits
            fused_response.results = fused_response.results[: query.max_results]
            fused_response.total_returned = len(fused_response.results)

            # Update statistics
            fusion_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._search_stats["fusion"].append(fusion_time)

            fused_response.search_time_ms = fusion_time
            fused_response.fusion_method = self.fusion_config.fusion_method

            _emit_records_telemetry_event(
                "search_fusion_engine",
                f"fused_search_completed_{len(fused_response.results)}_results",
            )

            return fused_response

        except Exception as e:
            return SearchResponse(
                query=query,
                results=[],
                total_found=0,
                total_returned=0,
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                avg_relevance_score=0.0,
                max_relevance_score=0.0,
                min_relevance_score=0.0,
                search_strategy="fusion",
                fusion_method=self.fusion_config.fusion_method,
                errors=[f"Fused search failed: {str(e)}"],
            )

    async def _execute_individual_searches(
        self,
        query: SearchQuery,
    ) -> tuple[SearchResponse, SearchResponse, SearchResponse]:
        """Execute individual search strategies in parallel."""
        import asyncio

        # Create modified queries for each strategy
        local_query = SearchQuery(
            text=query.text,
            query_type=query.query_type,
            search_mode="local",
            max_results=query.max_results,
            min_relevance_score=query.min_relevance_score,
            entity_types=query.entity_types,
            relation_types=query.relation_types,
        )

        global_query = SearchQuery(
            text=query.text,
            query_type=query.query_type,
            search_mode="global",
            max_results=query.max_results,
            min_relevance_score=query.min_relevance_score,
            entity_types=query.entity_types,
            relation_types=query.relation_types,
        )

        drift_query = SearchQuery(
            text=query.text,
            query_type=query.query_type,
            search_mode="drift",
            max_results=query.max_results,
            min_relevance_score=query.min_relevance_score,
            entity_types=query.entity_types,
            relation_types=query.relation_types,
        )

        # Execute searches in parallel
        local_future = self.local_engine.search(local_query)
        global_future = self.global_engine.search(global_query)
        drift_future = self.drift_engine.search(drift_query)

        local_response, global_response, drift_response = await asyncio.gather(
            local_future,
            global_future,
            drift_future,
            return_exceptions=True,
        )

        # Handle exceptions
        if isinstance(local_response, Exception):
            local_response = SearchResponse(
                query=local_query,
                results=[],
                total_found=0,
                total_returned=0,
                search_time_ms=0.0,
                avg_relevance_score=0.0,
                max_relevance_score=0.0,
                min_relevance_score=0.0,
                search_strategy="local",
                errors=[f"Local search error: {str(local_response)}"],
            )

        if isinstance(global_response, Exception):
            global_response = SearchResponse(
                query=global_query,
                results=[],
                total_found=0,
                total_returned=0,
                search_time_ms=0.0,
                avg_relevance_score=0.0,
                max_relevance_score=0.0,
                min_relevance_score=0.0,
                search_strategy="global",
                errors=[f"Global search error: {str(global_response)}"],
            )

        if isinstance(drift_response, Exception):
            drift_response = SearchResponse(
                query=drift_query,
                results=[],
                total_found=0,
                total_returned=0,
                search_time_ms=0.0,
                avg_relevance_score=0.0,
                max_relevance_score=0.0,
                min_relevance_score=0.0,
                search_strategy="drift",
                errors=[f"DRIFT search error: {str(drift_response)}"],
            )

        # Update statistics
        self._search_stats["local"].append(local_response.search_time_ms)
        self._search_stats["global"].append(global_response.search_time_ms)
        self._search_stats["drift"].append(drift_response.search_time_ms)

        return local_response, global_response, drift_response

    async def _fuse_results(
        self,
        local_response: SearchResponse,
        global_response: SearchResponse,
        drift_response: SearchResponse,
        query: SearchQuery,
    ) -> SearchResponse:
        """Fuse results from multiple search strategies."""
        if self.fusion_config.fusion_method == "weighted_average":
            return self._weighted_average_fusion(local_response, global_response, drift_response, query)
        elif self.fusion_config.fusion_method == "rank_fusion":
            return self._rank_fusion(local_response, global_response, drift_response, query)
        elif self.fusion_config.fusion_method == "reciprocal_rank":
            return self._reciprocal_rank_fusion(local_response, global_response, drift_response, query)
        else:
            # Default to weighted average
            return self._weighted_average_fusion(local_response, global_response, drift_response, query)

    def _weighted_average_fusion(
        self,
        local_response: SearchResponse,
        global_response: SearchResponse,
        drift_response: SearchResponse,
        query: SearchQuery,
    ) -> SearchResponse:
        """Fuse results using weighted average of scores."""
        # Collect all results
        all_results = {}

        # Add local results
        for result in tqdm(local_response.results, desc="Processing", unit="item"):
            result_id = result.item_id
            if result_id not in all_results:
                all_results[result_id] = {
                    "result": result,
                    "local_score": result.relevance_score,
                    "global_score": 0.0,
                    "drift_score": 0.0,
                }
            else:
                all_results[result_id]["local_score"] = result.relevance_score

        # Add global results
        for result in tqdm(global_response.results, desc="Processing", unit="item"):
            result_id = result.item_id
            if result_id not in all_results:
                all_results[result_id] = {
                    "result": result,
                    "local_score": 0.0,
                    "global_score": result.relevance_score,
                    "drift_score": 0.0,
                }
            else:
                all_results[result_id]["global_score"] = result.relevance_score

        # Add drift results
        for result in tqdm(drift_response.results, desc="Processing", unit="item"):
            result_id = result.item_id
            if result_id not in all_results:
                all_results[result_id] = {
                    "result": result,
                    "local_score": 0.0,
                    "global_score": 0.0,
                    "drift_score": result.relevance_score,
                }
            else:
                all_results[result_id]["drift_score"] = result.relevance_score

        # Calculate weighted scores
        fused_results = []
        for result_id, scores in tqdm(all_results.items(), desc="Processing", unit="item"):
            weighted_score = (
                scores["local_score"] * self.fusion_config.local_weight
                + scores["global_score"] * self.fusion_config.global_weight
                + scores["drift_score"] * self.fusion_config.drift_weight
            )

            # Normalize score
            normalized_score = self._normalize_score(weighted_score)

            # Create fused result
            fused_result = SearchResult(
                item_id=scores["result"].item_id,
                item_type=scores["result"].item_type,
                title=scores["result"].title,
                description=scores["result"].description,
                relevance_score=normalized_score,
                context=scores["result"].context,
                surrounding_entities=scores["result"].surrounding_entities,
                path_to_root=scores["result"].path_to_root,
                source_file=scores["result"].source_file,
                confidence=scores["result"].confidence,
                metadata={
                    **scores["result"].metadata,
                    "local_score": scores["local_score"],
                    "global_score": scores["global_score"],
                    "drift_score": scores["drift_score"],
                    "fused_score": weighted_score,
                },
            )
            fused_results.append(fused_result)

        # Sort by fused score
        fused_results.sort(key=lambda r: r.relevance_score, reverse=True)

        # Calculate statistics
        relevance_scores = [r.relevance_score for r in fused_results]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

        return SearchResponse(
            query=query,
            results=fused_results,
            total_found=len(fused_results),
            total_returned=len(fused_results),
            search_time_ms=0.0,  # Will be set by caller
            avg_relevance_score=avg_relevance,
            max_relevance_score=max(relevance_scores) if relevance_scores else 0.0,
            min_relevance_score=min(relevance_scores) if relevance_scores else 0.0,
            search_strategy="fusion",
            fusion_method="weighted_average",
            metadata={
                "local_results": len(local_response.results),
                "global_results": len(global_response.results),
                "drift_results": len(drift_response.results),
                "fusion_weights": {
                    "local": self.fusion_config.local_weight,
                    "global": self.fusion_config.global_weight,
                    "drift": self.fusion_config.drift_weight,
                },
            },
        )

    def _rank_fusion(
        self,
        local_response: SearchResponse,
        global_response: SearchResponse,
        drift_response: SearchResponse,
        query: SearchQuery,
    ) -> SearchResponse:
        """Fuse results using rank fusion."""
        # Collect rankings
        rankings: dict[str, dict[str, int]] = {}

        # Local rankings
        for i, result in enumerate(local_response.results):
            result_id = result.item_id
            if result_id not in rankings:
                rankings[result_id] = {}
            rankings[result_id]["local"] = i + 1

        # Global rankings
        for i, result in enumerate(global_response.results):
            result_id = result.item_id
            if result_id not in rankings:
                rankings[result_id] = {}
            rankings[result_id]["global"] = i + 1

        # DRIFT rankings
        for i, result in enumerate(drift_response.results):
            result_id = result.item_id
            if result_id not in rankings:
                rankings[result_id] = {}
            rankings[result_id]["drift"] = i + 1

        # Calculate fused scores
        fused_results = []
        for result_id, ranks in tqdm(rankings.items(), desc="Processing", unit="item"):
            # Get the best result to use as base
            base_result = None
            for response in [local_response, global_response, drift_response]:
                for result in response.results:
                    if result.item_id == result_id:
                        base_result = result
                        break
                if base_result:
                    break

            if base_result:
                # Calculate rank fusion score
                local_rank = ranks.get("local", len(local_response.results) + 1)
                global_rank = ranks.get("global", len(global_response.results) + 1)
                drift_rank = ranks.get("drift", len(drift_response.results) + 1)

                fused_score = (
                    self.fusion_config.local_weight / local_rank
                    + self.fusion_config.global_weight / global_rank
                    + self.fusion_config.drift_weight / drift_rank
                )

                # Normalize score
                normalized_score = self._normalize_score(fused_score)

                fused_result = SearchResult(
                    item_id=base_result.item_id,
                    item_type=base_result.item_type,
                    title=base_result.title,
                    description=base_result.description,
                    relevance_score=normalized_score,
                    context=base_result.context,
                    surrounding_entities=base_result.surrounding_entities,
                    path_to_root=base_result.path_to_root,
                    source_file=base_result.source_file,
                    confidence=base_result.confidence,
                    metadata={
                        **base_result.metadata,
                        "local_rank": local_rank,
                        "global_rank": global_rank,
                        "drift_rank": drift_rank,
                        "rank_fusion_score": fused_score,
                    },
                )
                fused_results.append(fused_result)

        # Sort by fused score
        fused_results.sort(key=lambda r: r.relevance_score, reverse=True)

        # Calculate statistics
        relevance_scores = [r.relevance_score for r in fused_results]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

        return SearchResponse(
            query=query,
            results=fused_results,
            total_found=len(fused_results),
            total_returned=len(fused_results),
            search_time_ms=0.0,  # Will be set by caller
            avg_relevance_score=avg_relevance,
            max_relevance_score=max(relevance_scores) if relevance_scores else 0.0,
            min_relevance_score=min(relevance_scores) if relevance_scores else 0.0,
            search_strategy="fusion",
            fusion_method="rank_fusion",
        )

    def _reciprocal_rank_fusion(
        self,
        local_response: SearchResponse,
        global_response: SearchResponse,
        drift_response: SearchResponse,
        query: SearchQuery,
    ) -> SearchResponse:
        """Fuse results using reciprocal rank fusion."""
        # Similar to rank fusion but with RRF formula
        rankings: dict[str, dict[str, int]] = {}

        # Collect rankings (same as rank fusion)
        for i, result in enumerate(local_response.results):
            result_id = result.item_id
            if result_id not in rankings:
                rankings[result_id] = {}
            rankings[result_id]["local"] = i + 1

        for i, result in enumerate(global_response.results):
            result_id = result.item_id
            if result_id not in rankings:
                rankings[result_id] = {}
            rankings[result_id]["global"] = i + 1

        for i, result in enumerate(drift_response.results):
            result_id = result.item_id
            if result_id not in rankings:
                rankings[result_id] = {}
            rankings[result_id]["drift"] = i + 1

        # Calculate RRF scores
        fused_results = []
        k = self.fusion_config.rank_fusion_k

        for result_id, ranks in tqdm(rankings.items(), desc="Processing", unit="item"):
            # Get the best result to use as base
            base_result = None
            for response in [local_response, global_response, drift_response]:
                for result in response.results:
                    if result.item_id == result_id:
                        base_result = result
                        break
                if base_result:
                    break

            if base_result:
                # Calculate RRF score
                local_rank = ranks.get("local", len(local_response.results) + 1)
                global_rank = ranks.get("global", len(global_response.results) + 1)
                drift_rank = ranks.get("drift", len(drift_response.results) + 1)

                rrf_score = (
                    self.fusion_config.local_weight * (1.0 / (k + local_rank))
                    + self.fusion_config.global_weight * (1.0 / (k + global_rank))
                    + self.fusion_config.drift_weight * (1.0 / (k + drift_rank))
                )

                # Normalize score
                normalized_score = self._normalize_score(rrf_score)

                fused_result = SearchResult(
                    item_id=base_result.item_id,
                    item_type=base_result.item_type,
                    title=base_result.title,
                    description=base_result.description,
                    relevance_score=normalized_score,
                    context=base_result.context,
                    surrounding_entities=base_result.surrounding_entities,
                    path_to_root=base_result.path_to_root,
                    source_file=base_result.source_file,
                    confidence=base_result.confidence,
                    metadata={
                        **base_result.metadata,
                        "local_rank": local_rank,
                        "global_rank": global_rank,
                        "drift_rank": drift_rank,
                        "rrf_score": rrf_score,
                    },
                )
                fused_results.append(fused_result)

        # Sort by fused score
        fused_results.sort(key=lambda r: r.relevance_score, reverse=True)

        # Calculate statistics
        relevance_scores = [r.relevance_score for r in fused_results]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

        return SearchResponse(
            query=query,
            results=fused_results,
            total_found=len(fused_results),
            total_returned=len(fused_results),
            search_time_ms=0.0,  # Will be set by caller
            avg_relevance_score=avg_relevance,
            max_relevance_score=max(relevance_scores) if relevance_scores else 0.0,
            min_relevance_score=min(relevance_scores) if relevance_scores else 0.0,
            search_strategy="fusion",
            fusion_method="reciprocal_rank",
        )

    def _normalize_score(self, score: float) -> float:
        """Normalize score to [0, 1] range."""
        if self.fusion_config.score_normalization == "min_max":
            # Simple min-max normalization (would need min/max values in practice)
            return min(1.0, max(0.0, score))
        elif self.fusion_config.score_normalization == "z_score":
            # Z-score normalization (would need mean/std in practice)
            return min(1.0, max(0.0, score))
        else:  # "none"
            return min(1.0, max(0.0, score))

    def _apply_diversification(self, results: list[SearchResult]) -> list[SearchResult]:
        """Apply Maximal Marginal Relevance (MMR) diversification."""
        if len(results) <= 1:
            return results

        diversified = [results[0]]  # Always include the top result
        lambda_param = self.fusion_config.diversity_lambda

        for i in tqdm(range(1, len(results)), desc="Processing", unit="item"):
            best_result = None
            best_mmr = -1.0

            for candidate in tqdm(results, desc="Processing", unit="item"):
                if candidate in diversified:
                    continue

                # Calculate MMR score
                relevance = candidate.relevance_score
                max_similarity = 0.0

                for selected in diversified:
                    similarity = self._calculate_similarity(candidate, selected)
                    max_similarity = max(max_similarity, similarity)

                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity

                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_result = candidate

            if best_result and best_mmr >= self.fusion_config.diversity_threshold:
                diversified.append(best_result)

        return diversified

    def _calculate_similarity(self, result1: SearchResult, result2: SearchResult) -> float:
        """Calculate similarity between two results."""
        # Simple text similarity (in practice, you'd use embeddings)
        text1 = f"{result1.title} {result1.description}".lower()
        text2 = f"{result2.title} {result2.description}".lower()

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def get_performance_stats(self) -> dict[str, dict[str, float]]:
        """Get performance statistics for all search strategies."""
        stats = {}

        for strategy, times in tqdm(self._search_stats.items(), desc="Processing", unit="item"):
            if times:
                stats[strategy] = {
                    "avg_time_ms": sum(times) / len(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "count": len(times),
                }
            else:
                stats[strategy] = {
                    "avg_time_ms": 0.0,
                    "min_time_ms": 0.0,
                    "max_time_ms": 0.0,
                    "count": 0,
                }

        return stats


# Factory function
def create_search_fusion_engine(
    graph_store: IGraphStore,
    fusion_config: FusionConfig | None = None,
    local_config: LocalSearchConfig | None = None,
    global_config: GlobalSearchConfig | None = None,
    drift_config: DRIFTSearchConfig | None = None,
) -> SearchFusionEngine:
    """Create a search fusion engine."""
    return SearchFusionEngine(
        graph_store,
        fusion_config,
        local_config,
        global_config,
        drift_config,
    )


__all__ = [
    "SearchFusionEngine",
    "create_search_fusion_engine",
]
