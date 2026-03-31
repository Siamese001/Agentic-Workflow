from __future__ import annotations

__version__ = "12.0"
import os


class GoogleSearchClient:
    """
    Centralized client for all Google Custom Search API calls with circuit breaker protection
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.cse_id = os.environ.get("GOOGLE_CSE_ID")
        if not (self.api_key and self.cse_id):
            raise ValueError("GOOGLE_API_KEY or GOOGLE_CSE_ID not found in environment")
        self.service = build("customsearch", "v1", developerKey=self.api_key)
        self.circuit_breaker = circuit_breaker

    def _execute_search_call(self, query: str, num_results: int = 5) -> list:
        """Execute the actual search API call"""
        res = self.service.cse().list(q=query, cx=self.cse_id, num=num_results).execute()
        return res.get("items", [])

    def search(self, query: str, num_results: int = 5) -> list:
        """
        Execute search with circuit breaker protection

        Args:
            query: Search query string
            num_results: Number of results to return (default 5)

        Returns:
            List of search result items

        Raises:
            Exception: If API call fails
            CircuitBreakerOpenError: If circuit breaker is OPEN
        """
        try:
            return self.circuit_breaker.call(self._execute_search_call, query, num_results=num_results)
        except Exception as e:
            raise Exception(f"Google Search API call failed: {e}")
