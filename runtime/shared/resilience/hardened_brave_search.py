"""
Hardened Brave Search - MCP Tool for External Web Search with Validation.

Implements a robust search tool with:
- Strict schema validation with Pydantic models
- Anti-hallucination filters
- Rate limit governance
- Integration with HardenedMCPExecutor
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel, Field, validator
import httpx

# Import MCP executor components
# from .hardened_mcp_executor import ToolConfig, ToolExecutionError

logger = logging.getLogger(__name__)

class SearchResultItem(BaseModel):
    """Individual search result item."""
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    description: str = Field(..., description="Description/snippet of the result")
    age: Optional[str] = Field(None, description="Age of the result (e.g., '2 days ago')")

    @validator('url')
    def validate_url(cls, v):
        """Basic URL validation."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Invalid URL format')
        return v

    @validator('description')
    def validate_description(cls, v):
        """Ensure description is not empty."""
        if not v or len(v.strip()) < 10:
            raise ValueError('Description too short or empty')
        return v.strip()

class BraveSearchResponse(BaseModel):
    """Complete search response."""
    query: str = Field(..., description="Original search query")
    results: List[SearchResultItem] = Field(..., description="List of search results")
    total_found: int = Field(..., description="Total number of results found")
    search_time_ms: Optional[float] = Field(None, description="Time taken for search")

    @validator('total_found')
    def validate_total(cls, v, values):
        """Ensure total matches results length."""
        if 'results' in values and v != len(values['results']):
            v = len(values['results'])
        return v

class SearchMissError(Exception):
    """Raised when search returns no results or poor quality results."""
    pass

class ToolExecutionError(Exception):
    """General tool execution error."""
    pass

class HardenedBraveSearch:
    """
    Hardened wrapper for Brave Search API.
    Designed to plug into the HardenedMCPExecutor.

    Features:
    - Strict schema validation
    - Anti-hallucination filters
    - Rate limit awareness
    - Result quality scoring
    """

    def __init__(self,
        api_key: str,
        base_url: str = "https://api.search.brave.com/res/v1/web/search"):
        """Initialize Brave Search client.

        Args:
            api_key: Brave Search API key
            base_url: API endpoint URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger("BraveSearch")

        # Statistics
        self.stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "rate_limited": 0,
            "no_results": 0,
            "avg_result_count": 0.0
        }

    async def run_search(
        self,
        query: str,
        count: int = 5,
        safe_search: str = "moderate",
        text_decorations: bool = False,
        text_format: str = "raw"
    ) -> Dict[str, Any]:
        """
        Execute search with validation and error handling.

        Args:
            query: Search query string
            count: Number of results to return (max 10)
            safe_search: Safe search level (off, moderate, strict)
            text_decorations: Whether to include text decorations
            text_format: Text format (raw, markdown)

        Returns:
            Dict containing validated search results

        Raises:
            ValueError: For invalid inputs
            ToolExecutionError: For search failures
            SearchMissError: For no results
        """
        self.stats["total_searches"] += 1
        start_time = asyncio.get_event_loop().time()

        # Input validation
        if not query or not query.strip():
            raise ValueError("Empty search query rejected.")

        if len(query.strip()) < 3:
            raise ValueError("Search query too short (minimum 3 characters).")

        if count < 1 or count > 10:
            raise ValueError("Result count must be between 1 and 10.")

        # Prepare request
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
            "User-Agent": "Agentic-Workflow/1.0"
        }

        # API parameters optimized for RAG
        params = {
            "q": query.strip(),
            "count": min(count, 10),  # Cap at 10 for context window safety
            "text_decorations": 1 if text_decorations else 0,
            "text_format": text_format,
            "safe_search": safe_search,
            "result_filter": "web",
            "freshness": "pd"  # Prefer recent results
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params
                )

                # Handle rate limiting
                if resp.status_code == 429:
                    self.stats["rate_limited"] += 1
                    raise RuntimeError("Rate Limit Exceeded (429) - Too many requests")

                # Handle other HTTP errors
                if resp.status_code == 401:
                    raise ToolExecutionError("Invalid API key for Brave Search")
                elif resp.status_code == 403:
                    raise ToolExecutionError("Access forbidden - Check API permissions")
                elif resp.status_code >= 500:
                    raise ToolExecutionError(f"Brave Search server error: {resp.status_code}")

                resp.raise_for_status()
                data = resp.json()

        except httpx.TimeoutException:
            self.stats["failed_searches"] += 1
            raise ToolExecutionError("Search request timed out")
        except httpx.RequestError as e:
            self.stats["failed_searches"] += 1
            raise ToolExecutionError(f"Network error during search: {str(e)}")

        # Parse and validate results
        web_results = data.get("web", {}).get("results", [])

        if not web_results:
            self.stats["no_results"] += 1
            raise SearchMissError(f"No results found for query: '{query}'")

        # Quality filter - remove low-quality results
        quality_results = []
        for item in web_results:
            try:
                # Skip results with very short descriptions
                description = item.get("description", "")
                if len(description.strip()) < 20:
                    continue

                # Skip results without proper URLs
                url = item.get("url", "")
                if not url.startswith(('http://', 'https://')):
                    continue

                # Create validated result
                result = SearchResultItem(
                    title=item.get("title", "No Title") or "No Title",
                    url=url,
                    description=description,
                    age=item.get("age")
                )

                quality_results.append(result)

            except Exception as e:
                self.logger.warning(f"Skipping invalid result: {e}")
                continue

        if not quality_results:
            self.stats["no_results"] += 1
            raise SearchMissError(f"No quality results found for query: '{query}'")

        # Create response
        search_time = (asyncio.get_event_loop().time() - start_time) * 1000

        response = BraveSearchResponse(
            query=query,
            results=quality_results,
            total_found=len(quality_results),
            search_time_ms=search_time
        )

        # Update statistics
        self.stats["successful_searches"] += 1
        if self.stats["successful_searches"] == 1:
            self.stats["avg_result_count"] = len(quality_results)
        else:
            self.stats["avg_result_count"] = (
                self.stats["avg_result_count"] * 0.9 + len(quality_results) * 0.1
            )

        self.logger.info(
            f"Search successful: '{query}' -> {len(quality_results)} results "
            f"in {search_time:.0f}ms"
        )

        return response.model_dump()

    async def search_with_fallback(
        self,
        query: str,
        count: int = 5,
        fallback_function: Optional[Callable] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute search with fallback support.

        Args:
            query: Search query
            count: Number of results
            fallback_function: Optional fallback function
            **kwargs: Additional search parameters

        Returns:
            Search results or fallback response
        """
        try:
            return await self.run_search(query, count, **kwargs)
        except (SearchMissError, ToolExecutionError, RuntimeError) as e:
            self.logger.warning(f"Search failed: {e}")

            if fallback_function:
                self.logger.info("Executing fallback search strategy")
                try:
                    return await fallback_function(error=str(e), query=query, count=count)
                except Exception as fallback_error:
                    self.logger.error(f"Fallback also failed: {fallback_error}")

            # Return error response
            return {
                "error": str(e),
                "query": query,
                "results": [],
                "total_found": 0,
                "fallback_used": False
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get search statistics."""
        total = self.stats["total_searches"]
        if total == 0:
            return self.stats

        stats = self.stats.copy()
        stats["success_rate"] = self.stats["successful_searches"] / total
        stats["failure_rate"] = self.stats["failed_searches"] / total
        stats["rate_limit_rate"] = self.stats["rate_limited"] / total

        return stats

    def reset_stats(self) -> None:
        """Reset search statistics."""
        for key in self.stats:
            if isinstance(self.stats[key], (int, float)):
                self.stats[key] = 0

# Integration helper functions
def create_brave_search_config(
    api_key: str,
    timeout_seconds: float = 6.0,
    max_retries: int = 2,
    fallback_function: Optional[Callable] = None
) -> 'ToolConfig':
    """
    Create a ToolConfig for Brave Search integration with HardenedMCPExecutor.

    Args:
        api_key: Brave Search API key
        timeout_seconds: Request timeout
        max_retries: Maximum retry attempts
        fallback_function: Optional fallback function

    Returns:
        ToolConfig instance
    """
    # Initialize the search tool
    search_tool = HardenedBraveSearch(api_key)

    # Default fallback function if not provided
    if fallback_function is None:
        async def default_fallback(error: str, query: str, **kwargs) -> Dict[str, Any]:
            """TODO: Add docstring."""

            return {
                "fallback_message": "External search failed. Using internal knowledge only.",
                "error_context": error,
                "query": query,
                "results": [],
                "total_found": 0,
                "fallback_used": True
            }
        fallback_function = default_fallback

    # Create and return configuration
    # Note: ToolConfig should be imported from hardened_mcp_executor
    return ToolConfig(
        name="brave_web_search",
        function=search_tool.run_search,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        fallback_function=fallback_function,
        description="Search the web using Brave Search API",
        parameters={
            "query": {
                "type": "string",
                "description": "Search query",
                "required": True
            },
            "count": {
                "type": "integer",
                "description": "Number of results (1-10)",
                "default": 5
            }
        }
    )

# Factory function
def create_brave_search_tool(api_key: str) -> HardenedBraveSearch:
    """Create a configured Brave Search tool.

    Args:
        api_key: Brave Search API key

    Returns:
        HardenedBraveSearch instance
    """
    return HardenedBraveSearch(api_key)
