from __future__ import annotations

__version__ = "12.0"
import os
from typing import Any, Protocol


class CircuitBreakerProtocol(Protocol):
    def call(self, func: Any, *args: Any, **kwargs: Any) -> Any: ...


class GoogleSearchClient:
    """
    Centralized client for all Google Custom Search API calls with circuit breaker protection
    """

    def __init__(self, circuit_breaker: CircuitBreakerProtocol):
        try:
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError("google-api-python-client is required for GoogleSearchClient") from exc

        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.cse_id = os.environ.get("GOOGLE_CSE_ID")
        if not (self.api_key and self.cse_id):
            raise ValueError("GOOGLE_API_KEY or GOOGLE_CSE_ID not found in environment")
        if not hasattr(circuit_breaker, "call"):
            raise TypeError("circuit_breaker must expose a call() method")
        self.service = build("customsearch", "v1", developerKey=self.api_key, cache_discovery=False)
        self.circuit_breaker = circuit_breaker

    def _execute_search_call(self, query: str, num_results: int = 5) -> list:
        """Execute the actual search API call"""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        num_results = max(1, min(int(num_results), 10))
        res = self.service.cse().list(q=query.strip(), cx=self.cse_id, num=num_results).execute()
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
            return list(
                self.circuit_breaker.call(
                    self._execute_search_call,
                    query,
                    num_results=num_results,
                ),
            )
        except (
            Exception
        ) as e:  # guardian: allow-broad-exception -- circuit breaker may raise any provider error
            raise RuntimeError("Google Search API call failed") from e
