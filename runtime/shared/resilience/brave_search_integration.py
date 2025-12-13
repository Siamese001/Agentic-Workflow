"""
Example integration of HardenedBraveSearch with HardenedMCPExecutor.

This file demonstrates how to:
1. Configure Brave Search as an MCP tool
2. Register it with the executor
3. Use it in a research workflow
"""

import asyncio
import os
import logging
from typing import Dict, Any

# Import the components
    HardenedBraveSearch,
    create_brave_search_config,
    SearchMissError,
    ToolExecutionError
)
# from .hardened_mcp_executor import HardenedMCPExecutor, ToolConfig

logger = logging.getLogger(__name__)

class BraveSearchIntegration:
    """
    Example integration class for Brave Search with MCP Executor.

    This shows how to properly configure and use the search tool
    within the hardened framework.
    """

    def __init__(self, api_key: str):
        """Initialize the integration.

        Args:
            api_key: Brave Search API key from environment
        """
        self.api_key = api_key
        self.search_tool = HardenedBraveSearch(api_key)
        self.mcp_executor = None  # Will be initialized later

    async def initialize_executor(self):
        """Initialize the MCP executor with Brave Search registered."""
        # Create fallback function
        async def search_fallback(error: str, query: str, **kwargs) -> Dict[str, Any]:
            """Fallback when external search fails."""
            logger.warning(f"External search failed for '{query}': {error}")

            # In a real implementation, you might:
            # 1. Search internal knowledge base
            # 2. Use cached results
            # 3. Return a structured error response

            return {
                "fallback_message": "External search unavailable. Using internal knowledge.",
                "error_context": error,
                "query": query,
                "results": [],
                "total_found": 0,
                "fallback_used": True,
                "suggestion": "Try rephrasing your query or check network connectivity."
            }

        # Create tool configuration
        brave_config = create_brave_search_config(
            api_key=self.api_key,
            timeout_seconds=6.0,
            max_retries=2,
            fallback_function=search_fallback
        )

        # Initialize executor (assuming it's already imported)
        self.mcp_executor = HardenedMCPExecutor()

        # Register the tool
        self.mcp_executor.register_tool(brave_config)

        logger.info("Brave Search tool registered with MCP executor")

    async def research_query(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Execute a research query using the integrated search tool.

        Args:
            query: Research query
            max_results: Maximum number of results

        Returns:
            Search results with metadata
        """
        if not self.mcp_executor:
            raise RuntimeError("Executor not initialized. Call initialize_executor() first.")

        try:
            # Execute search through MCP executor
            results = await self.mcp_executor.execute_tool(
                "brave_web_search",
                query=query,
                count=max_results
            )

            # Add research metadata
            results["research_metadata"] = {
                "query_processed": True,
                "source": "brave_search_api",
                "timestamp": asyncio.get_event_loop().time(),
                "result_count": len(results.get("results", []))
            }

            return results

        except Exception as e:
            logger.error(f"Research query failed: {e}")
            raise

    async def multi_query_research(self, queries: list[str]) -> Dict[str, Any]:
        """
        Execute multiple research queries concurrently.

        Args:
            queries: List of research queries

        Returns:
            Combined results from all queries
        """
        if not self.mcp_executor:
            raise RuntimeError("Executor not initialized. Call initialize_executor() first.")

        # Execute all queries concurrently
        tasks = [
            self.research_query(query, max_results=3)
            for query in queries
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        combined = {
            "queries": queries,
            "results": [],
            "errors": [],
            "total_results": 0
        }

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                combined["errors"].append({
                    "query": queries[i],
                    "error": str(result)
                })
            else:
                combined["results"].append(result)
                combined["total_results"] += len(result.get("results", []))

        return combined

    def get_search_stats(self) -> Dict[str, Any]:
        """Get comprehensive search statistics."""
        search_stats = self.search_tool.get_stats()

        if self.mcp_executor:
            mcp_stats = self.mcp_executor.get_tool_stats("brave_web_search")
            search_stats.update({
                "mcp_executor_stats": mcp_stats
            })

        return search_stats

# Example usage in K.2.5 Deep Research Node
class K25DeepResearchNode:
    """
    Example implementation of K.2.5 Deep Research using Brave Search.

    This demonstrates how the research node would use the hardened search
    to gather external information.
    """

    def __init__(self, brave_api_key: str):
        """Initialize the research node.

        Args:
            brave_api_key: API key for Brave Search
        """
        self.search_integration = BraveSearchIntegration(brave_api_key)
        self.logger = logging.getLogger("K25Research")

    async def initialize(self):
        """Initialize the search integration."""
        await self.search_integration.initialize_executor()
        self.logger.info("K.2.5 Deep Research node initialized")

    async def research_topic(self, topic: str, depth: int = 2) -> Dict[str, Any]:
        """
        Research a topic with configurable depth.

        Args:
            topic: Main topic to research
            depth: Research depth (1=basic, 2=detailed, 3=comprehensive)

        Returns:
            Research findings with citations
        """
        # Generate search queries based on depth
        queries = [topic]

        if depth >= 2:
            queries.extend([
                f"{topic} recent developments",
                f"{topic} key statistics",
                f"{topic} expert opinions"
            ])

        if depth >= 3:
            queries.extend([
                f"{topic} challenges and limitations",
                f"{topic} future trends",
                f"{topic} case studies"
            ])

        # Execute research
        try:
            results = await self.search_integration.multi_query_research(queries)

            # Process and structure findings
            findings = {
                "topic": topic,
                "research_depth": depth,
                "queries_executed": len(queries),
                "total_sources": results["total_results"],
                "findings": self._process_findings(results["results"]),
                "errors": results["errors"],
                "search_stats": self.search_integration.get_search_stats()
            }

            self.logger.info(
                f"Research completed for '{topic}': {findings['total_sources']} sources"
            )

            return findings

        except Exception as e:
            self.logger.error(f"Research failed for topic '{topic}': {e}")
            raise

    def _process_findings(self, results: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """Process and structure search findings."""
        processed = []

        for result in results:
            query = result.get("query", "")
            search_results = result.get("results", [])

            for item in search_results:
                processed.append({
                    "source_query": query,
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "snippet": item.get("description"),
                    "age": item.get("age"),
                    "relevance_score": self._calculate_relevance(query, item)
                })

        # Sort by relevance
        processed.sort(key=lambda x: x["relevance_score"], reverse=True)

        return processed

    def _calculate_relevance(self, query: str, result: Dict[str, Any]) -> float:
        """Calculate relevance score for a result."""
        # Simple relevance calculation based on title and description
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()
        query_terms = query.lower().split()

        score = 0.0
        for term in query_terms:
            if term in title:
                score += 2.0
            if term in description:
                score += 1.0

        # Normalize score
        max_possible = len(query_terms) * 3
        return min(score / max_possible, 1.0) if max_possible > 0 else 0.0

# Example usage
async def main():
    """Example of how to use the Brave Search integration."""

    # Get API key from environment
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        logger.info("Error: BRAVE_API_KEY environment variable not set")
        return

    # Initialize research node
    research_node = K25DeepResearchNode(api_key)
    await research_node.initialize()

    # Perform research
    topic = "artificial intelligence trends 2025"
    findings = await research_node.research_topic(topic, depth=2)

    # Display results
    logger.info(f"\nResearch Results for: {findings['topic']}")
    logger.info(f"Total Sources: {findings['total_sources']}")
    logger.info(f"Queries Executed: {findings['queries_executed']}")

    logger.info("\nTop Findings:")
    for i, finding in enumerate(findings["findings"][:5], 1):
        logger.info(f"\n{i}. {finding['title']}")
        logger.info(f"   URL: {finding['url']}")
        logger.info(f"   Relevance: {finding['relevance_score']:.2f}")
        logger.info(f"   Snippet: {finding['snippet'][:200]}...")

    # Show statistics
    logger.info("\nSearch Statistics:")
    stats = findings["search_stats"]
    logger.info(f"Success Rate: {stats['success_rate']:.2%}")
    logger.info(f"Average Results: {stats['avg_result_count']:.1f}")

if __name__ == "__main__":
    asyncio.run(main())
