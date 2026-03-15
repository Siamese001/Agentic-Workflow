"""Query Decomposer - Reasoning Layer for Complex Queries.

This component breaks complex multi-hop questions into atomic sub-queries
that can be answered by the retrieval system.
"""

import asyncio
import logging
import re
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class DecomposedQuery(BaseModel):
    """Result of query decomposition."""

    original_query: str = Field(..., description="Original complex query")
    sub_queries: list[str] = Field(..., description="Decomposed atomic sub-queries")
    reasoning: str = Field(..., description="Reasoning for decomposition")
    complexity_score: int = Field(..., ge=1, le=10, description="Complexity score (1-10)")

    @validator("sub_queries")
    def validate_sub_queries(cls, v):
        """Ensure sub-queries are valid."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DecomposedQuery.validate_sub_queries")

        if not v:
            raise ValueError("At least one sub-query is required")
        if len(v) > 4:
            raise ValueError("Maximum 4 sub-queries allowed")
        return v


class SimpleAgentBase:
    """Simple base class for standalone agents."""

    def __init__(self, name: str, model_name: str = "gpt-4"):
        """Initialize the agent.

        Args:
            name: Agent name for logging
            model_name: LLM model to use
        """
        self.name = name
        self.model_name = model_name
        logger.info(f"Initialized {self.__class__.__name__}: model={model_name}")


class QueryDecomposer(SimpleAgentBase):
    """Decomposes complex queries into atomic sub-queries.

    Uses LLM to break down multi-hop questions into simpler queries
    that can be answered by the retrieval system.
    """

    # guardian: allow-magic-config
    def __init__(self, model_name: str = "gpt-4", max_sub_queries: int = 4):
        """Initialize the Query Decomposer.

        Args:
            model_name: LLM model to use for decomposition
            max_sub_queries: Maximum number of sub-queries to generate
        """
        super().__init__(name="Query Decomposer", model_name=model_name)
        self.max_sub_queries = max_sub_queries
        try:
            self.gate = AdaptiveRetrievalGate()
        except ImportError:
            logger.warning("AdaptiveRetrievalGate not available, skipping heuristic check")
            self.gate = None
        self.complexity_indicators = {
            "comparison": re.compile("\\b(compare|vs|versus|against|difference|contrast)\\b", re.IGNORECASE),
            "causation": re.compile("\\b(why|cause|reason|impact|effect)\\b", re.IGNORECASE),
            "temporal": re.compile("\\b(before|after|during|when|timeline|history)\\b", re.IGNORECASE),
            "aggregation": re.compile("\\b(sum|total|average|count|aggregate|combine)\\b", re.IGNORECASE),
            "relationship": re.compile("\\b(relationship|correlation|between|and)\\b", re.IGNORECASE),
        }

    def _calculate_complexity_score(self, query: str) -> int:
        """Calculate complexity score for a query (1-10).

        Args:
            query: Query to analyze

        Returns:
            Complexity score from 1 (simple) to 10 (very complex)
        """
        score = 1
        for _indicator_type, pattern in self.complexity_indicators.items():
            if pattern.search(query):
                score += 2
        word_count = len(query.split())
        if word_count > 15:
            score += 2
        elif word_count > 10:
            score += 1
        question_words = ["what", "how", "why", "where", "when", "which", "who"]
        question_count = sum(1 for word in question_words if word in query.lower())
        score += min(question_count, 2)
        return min(score, 10)

    # guardian: allow-magic-config
    async def _call_llm(self, prompt: str, temperature: float = 0.3) -> Any:
        """Call the LLM with the given prompt.

        Args:
            prompt: Prompt to send to LLM
            temperature: Sampling temperature

        Returns:
            LLM response
        """
        try:
            client = get_client(Provider.ANTHROPIC)
            # guardian: allow-magic-config
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content

            return LLMResponseImpl(response.content[0].text)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"LLM call failed: {e}")

            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content

            return LLMResponseImpl('{"sub_queries": ["query"], "reasoning": "fallback"}')

    async def decompose(self, query: str) -> DecomposedQuery:
        """Decompose a complex query into sub-queries.

        Args:
            query: Complex query to decompose

        Returns:
            DecomposedQuery with sub-queries and reasoning
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "QueryDecomposer.decompose")

        if self.gate:
            decision = self.gate.should_retrieve(query)
            if decision.query_type in ["CONVERSATIONAL", "FACTUAL"] and (not decision.should_retrieve):
                logger.info(f"Simple query detected, skipping decomposition: {query}")
                return DecomposedQuery(
                    original_query=query,
                    sub_queries=[query],
                    reasoning="Query is simple, no decomposition needed",
                    complexity_score=1,
                )
        complexity = self._calculate_complexity_score(query)
        if complexity <= 3:
            logger.info(f"Low complexity ({complexity}), returning original query")
            return DecomposedQuery(
                original_query=query,
                sub_queries=[query],
                reasoning="Query complexity is low, no decomposition needed",
                complexity_score=complexity,
            )
        prompt = f'You are an Expert Research Assistant. Break the following complex user query into 2-4 atomic, factual sub-queries that a search engine can answer.\n\nRules:\n- If the query is simple, return it as the single sub-query\n- Each sub-query must be self-contained and answerable\n- Maximum 4 sub-queries\n- Focus on extracting the core information needs\n\nQuery: "{query}"\n\nReturn in JSON format:\n{{\n    "sub_queries": ["sub-query 1", "sub-query 2", ...],\n    "reasoning": "brief explanation of the decomposition"\n}}\n\nExample:\nInput: "Compare AWS vs. Azure pricing for financial services"\nOutput: {{\n    "sub_queries": ["AWS pricing model for financial services", "Azure pricing model for financial services", "AWS vs Azure cost comparison"],\n    "reasoning": "Decomposed into individual pricing queries and a comparison"\n}}'
        try:
            # guardian: allow-magic-config
            response = await self._call_llm(prompt, temperature=0.1)
            import json

            result = json.loads(response.content.strip())
            sub_queries = result.get("sub_queries", [query])
            if len(sub_queries) > self.max_sub_queries:
                logger.warning(f"LLM generated too many sub-queries ({len(sub_queries)}), truncating")
                sub_queries = sub_queries[: self.max_sub_queries]
            if not sub_queries:
                sub_queries = [query]
            reasoning = result.get("reasoning", "Decomposed using LLM analysis")
            return DecomposedQuery(
                original_query=query,
                sub_queries=sub_queries,
                reasoning=reasoning,
                complexity_score=complexity,
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to decompose query: {e}")
            return DecomposedQuery(
                original_query=query,
                sub_queries=[query],
                reasoning="Decomposition failed, using original query",
                complexity_score=complexity,
            )

    async def execute_plan(
        self, decomposed_query: DecomposedQuery, search_function: callable, **kwargs
    ) -> list[Any]:
        """Execute search for all sub-queries in parallel.

        Args:
            decomposed_query: Result from decompose() method
            search_function: Async function to execute search
            **kwargs: Additional arguments for search function

        Returns:
            List of search results for all sub-queries
        """
        logger.info(f"Executing {len(decomposed_query.sub_queries)} sub-queries in parallel")
        tasks = []
        for sub_query in decomposed_query.sub_queries:
            task = search_function(sub_query, **kwargs)
            tasks.append(task)
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Sub-query {i} failed: {result}")
                    processed_results.append([])
                else:
                    processed_results.append(result)
            logger.info(f"Completed execution: {sum(len(r) for r in processed_results)} total results")
            return processed_results
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to execute sub-queries: {e}")
            return [[] for _ in decomposed_query.sub_queries]


async def decompose_query(query: str, model_name: str = "gpt-4") -> DecomposedQuery:
    """Decompose a query using default settings.

    Args:
        query: Query to decompose
        model_name: LLM model to use

    Returns:
        DecomposedQuery result
    """
    decomposer = QueryDecomposer(model_name=model_name)
    return await decomposer.decompose(query)
