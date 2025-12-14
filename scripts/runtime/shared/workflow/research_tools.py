import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from tavily import TavilyClient
import logging


logger = logging.getLogger(__name__)
# Ensure you add `tavily-python` to requirements.txt

class ResearchResult(BaseModel):
    source_url: str
    content_snippet: str
    relevance_score: float

class ResearchContext(BaseModel):
    company_name: str
    raw_results: List[ResearchResult]
    synthesized_summary: str

class TavilyResearcher:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is not set in environment variables.")
        self.client = TavilyClient(api_key=self.api_key)

    def execute_shadow_audit_search(self, company_name: str) -> str:
        """
        Executes a multi-query search strategy to uncover technical details.
        Returns a formatted string ready for LLM context window.
        """
        queries = [
            f"{company_name} engineering blog technical stack architecture",
            f"{company_name} github open source repositories list",
            f"{company_name} CTO interview podcast transcript technical challenges",
            f"{company_name} job description software engineer tech stack requirements"
        ]

        aggregated_results = []

        logger.info(f"🕵️  Autonomous Agent: Searching deeply for {company_name}...")

        for query in queries:
            try:
                # 'advanced' depth gives better crawl data but costs more credits
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=3,
                    include_domains=[], # Optional: Restrict to legitimate tech sites if needed
                    exclude_domains=["glassdoor.com",
                        "comparably.com"] # Exclude generic salary sites
                )

                for res in response.get("results", []):
                    aggregated_results.append(
                        ResearchResult(
                            source_url=res["url"],
                            content_snippet=res["content"],
                            relevance_score=res["score"]
                        )
                    )
            except Exception as e:
                logger.error(f"⚠️  Search query '{query}' failed: {e}")

        return self._format_results_for_llm(aggregated_results)

    def _format_results_for_llm(self, results: List[ResearchResult]) -> str:
        """Deduplicates and formats results into a dense context block."""
        seen_urls = set()
        unique_results = []

        for r in results:
            if r.source_url not in seen_urls:
                seen_urls.add(r.source_url)
                unique_results.append(r)

        # Sort by relevance
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Format string
        context_str = "SEARCH CONTEXT (AUTO-RETRIEVED):\n"
        for i, r in enumerate(unique_results[:8]): # Cap at top 8 to save tokens
            context_str += f"[{i+1}] Source: {r.source_url}\n"
            context_str += f"Content: {r.
                .content_snippet[:800]}.
                ..
                ..
                .\n\n" # Truncate individual snippets

        return context_str
