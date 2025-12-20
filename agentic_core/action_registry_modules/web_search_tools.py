"""
Web Search Tools - Atomic Module
Extracted from action_registry.py via Atomic Fission Protocol
Tool ID Prefix: ACT-001
"""
import logging
import os
from typing import Dict

import requests

logger = logging.getLogger("ActionRegistry.WebSearch")


class WebSearchTools:
    """
    Encapsulates web search functionality using Brave API.
    Tool ID Prefix: ACT-001
    """

    def __init__(self):
        """Initializes WebSearchTools and checks for the Brave API key."""
        self.brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.brave_key:
            logger.warning(
                "[!] BRAVE_SEARCH_API_KEY not found. Web search will fail."
            )

    def _format_search_result_item(self, item: Dict) -> str:
        """
        Helper to format a single search result item into a readable string.

        Args:
            item (Dict): A dictionary representing a single search result.

        Returns:
            str: A formatted string of the search result.
        """
        title = item.get('title', 'No Title')
        desc = item.get('description', 'No Description')
        link = item.get('url', 'No Link')
        return f"Title: {title}\nSummary: {desc}\nLink: {link}\n---"

    def _process_search_results(self, data: Dict) -> str:
        """
        Helper to process raw search API response data into a formatted string.

        Args:
            data (Dict): The raw JSON response from the Brave Search API.

        Returns:
            str: A concatenated string of formatted search results, or a
                 "No results found" message.
        """
        results = []
        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                results.append(self._format_search_result_item(item))
        return "\n".join(results) if results else "No results found."

    def search_web(self, query: str) -> str:
        """
        Performs a real web search using the Brave API.
        Tool ID: ACT-001

        Args:
            query (str): The search query string.

        Returns:
            str: A formatted string of search results or an error message.
        """
        if not self.brave_key:
            return "Error: No Search API Key configured."

        logger.info(f"🌐 Searching Web: '{query}'")
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "X-Subscription-Token": self.brave_key,
                "Accept": "application/json"
            }
            params = {"q": query, "count": 3}

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return self._process_search_results(data)

        except requests.exceptions.HTTPError as e:
            logger.error(f"Web search HTTP error for query '{query}': {e}")
            return f"Search Error (HTTP): {e}"
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Web search connection error for query '{query}': {e}")
            return f"Search Error (Connection): {e}"
        except requests.exceptions.Timeout as e:
            logger.error(f"Web search timeout error for query '{query}': {e}")
            return f"Search Error (Timeout): {e}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Web search request error for query '{query}': {e}")
            return f"Search Error (Request): {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during web search for query '{query}': {e}")
            return f"Search Error (Unexpected): {str(e)}"


__all__ = ['WebSearchTools']
