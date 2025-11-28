"""LIC Research Executor - L2 Execution Layer

Implements HOP-2 multi-hop research execution from legacy LIC system.
Executes vector-first research with cache critique and fallback RAG.
Consumes L1 research plans - no embedded reasoning.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from l1.lic_research_planner import (
    LICResearchPlan, VectorQueryParams, FallbackRAGParams
)
from l4.lic_vector_memory import VectorMemoryStore
from l4.lic_signal_scoring import SignalScorer
from l4.lic_cache_critique import CacheCritiquer
from l2.interfaces import L2ExecutionResult as ExecutorResult


logger = logging.getLogger(__name__)


@dataclass
class ResearchContext:
    """Research execution context"""
    plan: LICResearchPlan
    vector_store: VectorMemoryStore
    signal_scorer: SignalScorer
    cache_critiquer: CacheCritiquer
    execution_start_time: datetime
    
    
@dataclass
class VectorQueryResult:
    """Result from vector store query"""
    query: str
    results: List[Dict[str, Any]]
    total_found: int
    avg_similarity: float
    execution_time_ms: int


@dataclass
class FallbackRAGResult:
    """Result from fallback RAG execution"""
    query: str
    sources: List[Dict[str, Any]]
    total_sources: int
    quality_score: float
    execution_time_ms: int


@dataclass
class ResearchExecutionResult:
    """Complete research execution result"""
    # Execution metadata
    plan_id: str
    execution_time_ms: int
    cache_hit: bool
    fallback_used: bool
    
    # Research results
    recipient_insights: Dict[str, Any]
    company_context: Dict[str, Any]
    strategic_brief: Dict[str, Any]
    
    # Source information
    vector_results: List[VectorQueryResult]
    fallback_results: List[FallbackRAGResult]
    all_sources: List[Dict[str, Any]]
    
    # Quality metrics
    signal_score: float
    confidence_score: float
    coverage_completeness: float
    
    # Execution summary
    total_sources: int
    gaps_filled: int
    execution_summary: str


class LICResearchExecutor:
    """
    L2 Executor for LIC HOP-2 Multi-hop Research
    
    Executes research plans with vector-first strategy, cache critique,
    and fallback RAG for identified gaps. Pure execution - no planning logic.
    """
    
    def __init__(
        self,
        vector_store: VectorMemoryStore,
        signal_scorer: SignalScorer,
        cache_critiquer: CacheCritiquer,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize research executor
        
        Args:
            vector_store: Vector memory store for cached intelligence
            signal_scorer: Signal scoring engine
            cache_critiquer: Cache sufficiency evaluator
            config: Optional execution configuration
        """
        self.vector_store = vector_store
        self.signal_scorer = signal_scorer
        self.cache_critiquer = cache_critiquer
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default execution configuration"""
        return {
            "execution": {
                "max_concurrent_queries": 5,
                "query_timeout_ms": 30000,
                "rag_timeout_ms": 60000,
                "max_sources_per_query": 50,
                "enable_parallel_execution": True
            }
        }
    
    async def execute_research(self, plan: LICResearchPlan) -> ExecutorResult[ResearchExecutionResult]:
        """
        Execute research plan
        
        Args:
            plan: Research execution plan from L1 planner
            
        Returns:
            Complete research execution result
        """
        execution_start = datetime.now()
        
        try:
            # Create execution context
            context = ResearchContext(
                plan=plan,
                vector_store=self.vector_store,
                signal_scorer=self.signal_scorer,
                cache_critiquer=self.cache_critiquer,
                execution_start_time=execution_start
            )
            
            logger.info(f"Executing research plan {plan.plan_id} for {plan.recipient_company}")
            
            # Step 1: Execute vector queries
            vector_results = await self._execute_vector_queries(context)
            
            # Step 2: Evaluate cache sufficiency
            cache_evaluation = await self._evaluate_cache_sufficiency(context, vector_results)
            
            # Step 3: Execute fallback RAG if needed
            fallback_results = []
            if cache_evaluation.requires_fallback:
                fallback_results = await self._execute_fallback_rag(context, cache_evaluation.gaps_to_fill)
            
            # Step 4: Merge and synthesize results
            merged_results = await self._merge_research_results(context, vector_results, fallback_results)
            
            # Step 5: Score and validate results
            scored_results = await self._score_research_results(context, merged_results)
            
            # Calculate execution time
            execution_time = int((datetime.now() - execution_start).total_seconds() * 1000)
            
            # Create final result
            result = ResearchExecutionResult(
                plan_id=plan.plan_id,
                execution_time_ms=execution_time,
                cache_hit=cache_evaluation.cache_sufficient,
                fallback_used=len(fallback_results) > 0,
                recipient_insights=scored_results.recipient_insights,
                company_context=scored_results.company_context,
                strategic_brief=scored_results.strategic_brief,
                vector_results=vector_results,
                fallback_results=fallback_results,
                all_sources=scored_results.all_sources,
                signal_score=scored_results.signal_score,
                confidence_score=scored_results.confidence_score,
                coverage_completeness=scored_results.coverage_completeness,
                total_sources=len(scored_results.all_sources),
                gaps_filled=len(fallback_results),
                execution_summary=scored_results.execution_summary
            )
            
            logger.info(f"Research execution completed in {execution_time}ms with {result.total_sources} sources")
            
            return ExecutorResult(
                success=True,
                data=result,
                message=f"Research executed successfully with {result.total_sources} sources"
            )
            
        except Exception as e:
            execution_time = int((datetime.now() - execution_start).total_seconds() * 1000)
            logger.error(f"Research execution failed after {execution_time}ms: {str(e)}")
            
            return ExecutorResult(
                success=False,
                data=None,
                message=f"Research execution failed: {str(e)}",
                error_code="RESEARCH_EXECUTION_ERROR"
            )
    
    async def _execute_vector_queries(self, context: ResearchContext) -> List[VectorQueryResult]:
        """Execute vector store queries in parallel"""
        plan = context.plan
        queries = plan.vector_queries
        params = plan.vector_params
        
        if not queries:
            return []
        
        logger.info(f"Executing {len(queries)} vector queries")
        
        # Execute queries in parallel if enabled
        if self.config["execution"]["enable_parallel_execution"]:
            tasks = [
                self._execute_single_vector_query(context, query, params)
                for query in queries
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            vector_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Vector query {i} failed: {str(result)}")
                    # Create empty result for failed query
                    vector_results.append(VectorQueryResult(
                        query=queries[i],
                        results=[],
                        total_found=0,
                        avg_similarity=0.0,
                        execution_time_ms=0
                    ))
                else:
                    vector_results.append(result)
        else:
            # Execute sequentially
            vector_results = []
            for query in queries:
                try:
                    result = await self._execute_single_vector_query(context, query, params)
                    vector_results.append(result)
                except Exception as e:
                    logger.error(f"Vector query failed: {str(e)}")
                    vector_results.append(VectorQueryResult(
                        query=query,
                        results=[],
                        total_found=0,
                        avg_similarity=0.0,
                        execution_time_ms=0
                    ))
        
        total_found = sum(r.total_found for r in vector_results)
        logger.info(f"Vector queries completed with {total_found} total results")
        
        return vector_results
    
    async def _execute_single_vector_query(
        self,
        context: ResearchContext,
        query: str,
        params: VectorQueryParams
    ) -> VectorQueryResult:
        """Execute a single vector query"""
        start_time = datetime.now()
        
        try:
            # Query vector store
            results = await context.vector_store.query_memory(
                query_text=query,
                n_results=params.n_results,
                filter_metadata=params.filter_metadata
            )
            
            # Calculate metrics
            total_found = len(results)
            avg_similarity = sum(r.get("distance", 0) for r in results) / total_found if total_found > 0 else 0.0
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return VectorQueryResult(
                query=query,
                results=results,
                total_found=total_found,
                avg_similarity=avg_similarity,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Vector query failed for '{query}': {str(e)}")
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return VectorQueryResult(
                query=query,
                results=[],
                total_found=0,
                avg_similarity=0.0,
                execution_time_ms=execution_time
            )
    
    async def _evaluate_cache_sufficiency(
        self,
        context: ResearchContext,
        vector_results: List[VectorQueryResult]
    ) -> Any:
        """Evaluate cache sufficiency using cache critiquer"""
        # Flatten all vector results
        all_sources = []
        for result in vector_results:
            all_sources.extend(result.results)
        
        # Use cache critiquer to evaluate sufficiency
        cache_evaluation = await context.cache_critiquer.evaluate_cache_sufficiency(
            sources=all_sources,
            plan=context.plan,
            recipient_company=context.plan.recipient_company,
            recipient_name=context.plan.recipient_name
        )
        
        return cache_evaluation
    
    async def _execute_fallback_rag(
        self,
        context: ResearchContext,
        gaps_to_fill: List[str]
    ) -> List[FallbackRAGResult]:
        """Execute fallback RAG for identified gaps"""
        plan = context.plan
        fallback_queries = plan.fallback_queries[:len(gaps_to_fill)]  # Limit to gap count
        
        if not fallback_queries:
            return []
        
        logger.info(f"Executing fallback RAG for {len(fallback_queries)} queries")
        
        # Execute RAG queries (this would integrate with actual RAG system)
        fallback_results = []
        for query in fallback_queries:
            try:
                result = await self._execute_single_fallback_rag(context, query, plan.fallback_params)
                fallback_results.append(result)
            except Exception as e:
                logger.error(f"Fallback RAG query failed for '{query}': {str(e)}")
                fallback_results.append(FallbackRAGResult(
                    query=query,
                    sources=[],
                    total_sources=0,
                    quality_score=0.0,
                    execution_time_ms=0
                ))
        
        total_sources = sum(r.total_sources for r in fallback_results)
        logger.info(f"Fallback RAG completed with {total_sources} sources")
        
        return fallback_results
    
    async def _execute_single_fallback_rag(
        self,
        context: ResearchContext,
        query: str,
        params: FallbackRAGParams
    ) -> FallbackRAGResult:
        """Execute a single fallback RAG query"""
        start_time = datetime.now()
        
        try:
            # This would integrate with actual RAG system
            # For now, return mock results
            mock_sources = [
                {
                    "title": f"Recent development about {context.plan.recipient_company}",
                    "content": f"Latest information about {context.plan.recipient_company} and {context.plan.recipient_name}",
                    "source_url": "https://example.com/news",
                    "retrieved_at": datetime.now().isoformat(),
                    "quality_score": 0.8
                }
            ]
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return FallbackRAGResult(
                query=query,
                sources=mock_sources,
                total_sources=len(mock_sources),
                quality_score=0.8,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Fallback RAG query failed for '{query}': {str(e)}")
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return FallbackRAGResult(
                query=query,
                sources=[],
                total_sources=0,
                quality_score=0.0,
                execution_time_ms=execution_time
            )
    
    async def _merge_research_results(
        self,
        context: ResearchContext,
        vector_results: List[VectorQueryResult],
        fallback_results: List[FallbackRAGResult]
    ) -> Any:
        """Merge vector and fallback research results"""
        # Flatten all results
        all_sources = []
        
        # Add vector results
        for vector_result in vector_results:
            for source in vector_result.results:
                source["source_type"] = "vector_cache"
                all_sources.append(source)
        
        # Add fallback results
        for fallback_result in fallback_results:
            for source in fallback_result.sources:
                source["source_type"] = "fallback_rag"
                all_sources.append(source)
        
        # Organize by research targets
        organized_results = {
            "recipient_insights": [],
            "company_context": [],
            "strategic_brief": [],
            "all_sources": all_sources
        }
        
        # Categorize sources based on content and metadata
        for source in all_sources:
            content = source.get("text", "").lower()
            metadata = source.get("metadata", {})
            
            # Simple categorization based on content keywords
            if any(keyword in content for keyword in ["leadership", "executive", "management", "team"]):
                organized_results["recipient_insights"].append(source)
            elif any(keyword in content for keyword in ["company", "business", "strategy", "market"]):
                organized_results["company_context"].append(source)
            else:
                organized_results["strategic_brief"].append(source)
        
        return organized_results
    
    async def _score_research_results(self, context: ResearchContext, merged_results: Any) -> Any:
        """Score research results for quality and completeness"""
        all_sources = merged_results["all_sources"]
        
        # Calculate signal score using signal scorer
        signal_score = await context.signal_scorer.score_sources(
            sources=all_sources,
            plan=context.plan,
            recipient_company=context.plan.recipient_company,
            recipient_archetype=context.plan.recipient_archetype
        )
        
        # Calculate confidence score based on source quality and quantity
        confidence_score = self._calculate_confidence_score(all_sources, context.plan)
        
        # Calculate coverage completeness
        coverage_completeness = self._calculate_coverage_completeness(merged_results, context.plan)
        
        # Generate execution summary
        execution_summary = self._generate_execution_summary(
            merged_results, signal_score, confidence_score, coverage_completeness
        )
        
        # Add scores to merged results
        merged_results["signal_score"] = signal_score
        merged_results["confidence_score"] = confidence_score
        merged_results["coverage_completeness"] = coverage_completeness
        merged_results["execution_summary"] = execution_summary
        
        return merged_results
    
    def _calculate_confidence_score(self, sources: List[Dict[str, Any]], plan: LICResearchPlan) -> float:
        """Calculate confidence score based on source quality and quantity"""
        if not sources:
            return 0.0
        
        # Base confidence from plan
        base_confidence = plan.confidence_score
        
        # Adjust based on source count
        source_count_factor = min(len(sources) / plan.expected_sources, 1.0)
        
        # Adjust based on source quality
        quality_scores = [source.get("quality_score", 0.5) for source in sources]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Calculate final confidence
        final_confidence = base_confidence * (0.6 + 0.2 * source_count_factor + 0.2 * avg_quality)
        
        return min(final_confidence, 1.0)
    
    def _calculate_coverage_completeness(self, merged_results: Any, plan: LICResearchPlan) -> float:
        """Calculate coverage completeness across research targets"""
        research_targets = plan.research_targets
        
        if not research_targets:
            return 0.0
        
        # Check coverage for each target category
        coverage_scores = []
        
        for category, targets in research_targets.items():
            category_sources = merged_results.get(category, [])
            
            if not category_sources:
                coverage_scores.append(0.0)
                continue
            
            # Simple coverage based on source count vs expected targets
            coverage = min(len(category_sources) / len(targets), 1.0)
            coverage_scores.append(coverage)
        
        # Return average coverage
        return sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0.0
    
    def _generate_execution_summary(
        self,
        merged_results: Any,
        signal_score: float,
        confidence_score: float,
        coverage_completeness: float
    ) -> str:
        """Generate execution summary"""
        total_sources = len(merged_results["all_sources"])
        
        summary = f"Research execution completed with {total_sources} sources. "
        summary += f"Signal score: {signal_score:.2f}, "
        summary += f"Confidence: {confidence_score:.2f}, "
        summary += f"Coverage: {coverage_completeness:.2f}. "
        
        if signal_score > 0.8:
            summary += "High-quality research results achieved."
        elif signal_score > 0.6:
            summary += "Good research quality with room for improvement."
        else:
            summary += "Research quality may need enhancement."
        
        return summary
