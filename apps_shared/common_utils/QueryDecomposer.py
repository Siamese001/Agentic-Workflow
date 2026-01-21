"""Query Decomposer - Reasoning Layer for Complex Queries.

This component breaks complex multi-hop questions into atomic sub-queries
that can be answered by the retrieval system.
"""

import asyncio
import logging
import re
from typing import Any

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class DecomposedQuery(BaseModel):
    """Result of query decomposition."""

    original_query: str = Field(..., description="Original complex query")
    sub_queries: list[str] = Field(..., description="Decomposed atomic sub-queries")
    reasoning: str = Field(..., description="Reasoning for decomposition")
    complexity_score: int = Field(..., ge=1, le=10, description="Complexity score (1-10)")

    @validator('sub_queries')
    def validate_sub_queries(cls, v):
        """Ensure sub-queries are valid."""
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

    def __init__(self, model_name: str = "gpt-4", max_sub_queries: int = 4):
        """Initialize the Query Decomposer.

        Args:
            model_name: LLM model to use for decomposition
            max_sub_queries: Maximum number of sub-queries to generate
        """
        super().__init__(name="Query Decomposer", model_name=model_name)
        self.max_sub_queries = max_sub_queries

        # Import AdaptiveRetrievalGate for heuristic check
        try:
            from .adaptive_retrieval_gate import AdaptiveRetrievalGate
            self.gate = AdaptiveRetrievalGate()
        except ImportError:
            logger.warning("AdaptiveRetrievalGate not available, skipping heuristic check")
            self.gate = None

        # Simple patterns to detect complex queries
        self.complexity_indicators = {
            'comparison': re.compile(r'\b(compare|vs|versus|against|difference|contrast)\b', re.IGNORECASE),
            'causation': re.compile(r'\b(why|cause|reason|impact|effect)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|during|when|timeline|history)\b', re.IGNORECASE),
            'aggregation': re.compile(r'\b(sum|total|average|count|aggregate|combine)\b', re.IGNORECASE),
            'relationship': re.compile(r'\b(relationship|correlation|between|and)\b', re.IGNORECASE)
        }

    def _calculate_complexity_score(self, query: str) -> int:
        """Calculate complexity score for a query (1-10).

        Args:
            query: Query to analyze

        Returns:
            Complexity score from 1 (simple) to 10 (very complex)
        """
        score = 1  # Base score

        # Check for complexity indicators
        for indicator_type, pattern in self.complexity_indicators.items():
            if pattern.search(query):
                score += 2

        # Word count contributes to complexity
        word_count = len(query.split())
        if word_count > 15:
            score += 2
        elif word_count > 10:
            score += 1

        # Question words increase complexity
        question_words = ['what', 'how', 'why', 'where', 'when', 'which', 'who']
        question_count = sum(1 for word in question_words if word in query.lower())
        score += min(question_count, 2)

        # Cap at 10
        return min(score, 10)

    async def _call_llm(self, prompt: str, temperature: float = 0.3) -> Any:
        """Call the LLM with the given prompt.

        Args:
            prompt: Prompt to send to LLM
            temperature: Sampling temperature

        Returns:
            LLM response
        """
        try:
            # Import here to avoid circular imports
            from .multi_provider_clients import Provider, get_client

            # Get Anthropic client
            client = get_client(Provider.ANTHROPIC)

            # Call LLM with token limit
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,  # Strict token limit for cost control
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content

            return LLMResponseImpl(response.content[0].text)

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            # Return fallback response
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
        # Heuristic check: if gate says simple, skip LLM
        if self.gate:
            decision = self.gate.should_retrieve(query)
            if decision.query_type in ["CONVERSATIONAL", "FACTUAL"] and not decision.should_retrieve:
                logger.info(f"Simple query detected, skipping decomposition: {query}")
                return DecomposedQuery(
                    original_query=query,
                    sub_queries=[query],
                    reasoning="Query is simple, no decomposition needed",
                    complexity_score=1
                )

        # Calculate complexity score
        complexity = self._calculate_complexity_score(query)

        # If complexity is low, return as-is
        if complexity <= 3:
            logger.info(f"Low complexity ({complexity}), returning original query")
            return DecomposedQuery(
                original_query=query,
                sub_queries=[query],
                reasoning="Query complexity is low, no decomposition needed",
                complexity_score=complexity
            )

        # Build decomposition prompt
        prompt = f"""You are an Expert Research Assistant. Break the following complex user query into 2-4 atomic, factual sub-queries that a search engine can answer.

Rules:
- If the query is simple, return it as the single sub-query
- Each sub-query must be self-contained and answerable
- Maximum 4 sub-queries
- Focus on extracting the core information needs

Query: "{query}"

Return in JSON format:
{{
    "sub_queries": ["sub-query 1", "sub-query 2", ...],
    "reasoning": "brief explanation of the decomposition"
}}

Example:
Input: "Compare AWS vs. Azure pricing for financial services"
Output: {{
    "sub_queries": ["AWS pricing model for financial services", "Azure pricing model for financial services", "AWS vs Azure cost comparison"],
    "reasoning": "Decomposed into individual pricing queries and a comparison"
}}"""

        try:
            # Call LLM
            response = await self._call_llm(prompt, temperature=0.1)

            # Parse JSON response
            import json
            result = json.loads(response.content.strip())

            # Validate and limit sub-queries
            sub_queries = result.get("sub_queries", [query])
            if len(sub_queries) > self.max_sub_queries:
                logger.warning(f"LLM generated too many sub-queries ({len(sub_queries)}), truncating")
                sub_queries = sub_queries[:self.max_sub_queries]

            # Ensure at least one sub-query
            if not sub_queries:
                sub_queries = [query]

            reasoning = result.get("reasoning", "Decomposed using LLM analysis")

            return DecomposedQuery(
                original_query=query,
                sub_queries=sub_queries,
                reasoning=reasoning,
                complexity_score=complexity
            )

        except Exception as e:
            logger.error(f"Failed to decompose query: {e}")
            # Fallback to original query
            return DecomposedQuery(
                original_query=query,
                sub_queries=[query],
                reasoning="Decomposition failed, using original query",
                complexity_score=complexity
            )

    async def execute_plan(
        self,
        decomposed_query: DecomposedQuery,
        search_function: callable,
        **kwargs
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

        # Create tasks for parallel execution
        tasks = []
        for sub_query in decomposed_query.sub_queries:
            task = search_function(sub_query, **kwargs)
            tasks.append(task)

        # Execute all tasks concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Sub-query {i} failed: {result}")
                    processed_results.append([])
                else:
                    processed_results.append(result)

            logger.info(f"Completed execution: {sum(len(r) for r in processed_results)} total results")
            return processed_results

        except Exception as e:
            logger.error(f"Failed to execute sub-queries: {e}")
            return [[] for _ in decomposed_query.sub_queries]


# Convenience function for direct usage
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
