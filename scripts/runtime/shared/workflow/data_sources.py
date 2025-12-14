"""Data source providers for executive agents."""

import logging
from tavily import TavilyClient

try:
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


class DataSourceProvider:
    """Interface for external data sources used by executive agents."""

    def __init__(self, brave_search_tool=None, tavily_api_key=None):
        """Initialize with optional search tools.

        Args:
            brave_search_tool: Optional HardenedBraveSearch instance
            tavily_api_key: Optional Tavily API key for automated search
        """
        self.brave_search = brave_search_tool
        self.tavily_client = None
        if tavily_api_key and TAVILY_AVAILABLE:
            try:
                self.tavily_client = TavilyClient(api_key=tavily_api_key)
                self.logger = logging.getLogger("DataSourceProvider")
                self.logger.info("Tavily client initialized successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize Tavily client: {e}")
        else:
            self.logger = logging.getLogger("DataSourceProvider")

    async def search_engineering_blog(self, company_name: str) -> str:
        """Search for company's engineering blog posts.

        Args:
            company_name: Company to search for

        Returns:
            Aggregated blog content
        """
        if not self.brave_search:
            return f"[MOCK] Engineering blog content for {company_name}: Recent posts mention migration to microservices.
                ..
                ..
                ."

        queries = [
            f"{company_name} engineering blog",
            f"{company_name} technical blog architecture",
            f"{company_name} engineering posts 2023 2024"
        ]

        results = []
        for query in queries:
            try:
                search_result = await self.brave_search.execute_search(query, count=3)
                if search_result.get("results"):
                    for item in search_result["results"][:2]:
                        results.append(f"Title: {item['title']}\nSnippet: {item['description']}")
            except Exception as e:
                self.logger.error(f"Search failed for {query}: {e}")

        return "\n\n".join(results) if results else f"No engineering blog found for {company_name}"

    async def scan_github_organization(self, company_name: str) -> str:
        """Scan company's GitHub for tech insights.

        Args:
            company_name: Company to scan

        Returns:
            Technology insights from GitHub
        """
        if not self.brave_search:
            return f"[MOCK] GitHub scan for {company_name}: Primary repos use Python,
                React,
                Kubernetes..."

        query = f"site:github.com {company_name} organization repositories"

        try:
            search_result = await self.brave_search.execute_search(query, count=5)

            if search_result.get("results"):
                insights = []
                for item in search_result["results"]:
                    insights.append(f"Repo: {item['title']}\n{item['description']}")
                return "\n\n".join(insights)
            else:
                return f"No GitHub organization found for {company_name}"

        except Exception as e:
            self.logger.error(f"GitHub scan failed: {e}")
            return f"Error scanning GitHub for {company_name}"

    async def get_interviewer_profile(self, linkedin_url: str) -> str:
        """Get interviewer's professional background.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Professional background and interests
        """
        if not self.brave_search:
            return "[MOCK] Interviewer profile: 15 years at company,
                technical background,
                loves system design..."

        # Extract name from URL if possible
        name = linkedin_url.split('/')[-1] if linkedin_url else "unknown"

        query = f'"{name}" {linkedin_url} background experience interests'

        try:
            search_result = await self.brave_search.execute_search(query, count=3)

            if search_result.get("results"):
                profiles = []
                for item in search_result["results"]:
                    profiles.append(f"Profile: {item['title']}\n{item['description']}")
                return "\n\n".join(profiles)
            else:
                return f"No profile found for {linkedin_url}"

        except Exception as e:
            self.logger.error(f"Profile search failed: {e}")
            return f"Error finding profile for {linkedin_url}"

    def automated_company_research(self, company_name: str) -> str:
        """Perform automated research using Tavily API.

        Args:
            company_name: Company to research

        Returns:
            Aggregated research findings from multiple sources
        """
        if not self.tavily_client:
            return f"[MOCK] Automated research for {company_name}: Engineering blog mentions microservices migration,
                GitHub shows Python/React/Kubernetes stack..."

        try:
            # Define search queries for different aspects
            queries = [
                f"{company_name} engineering blog technical architecture",
                f"{company_name} technology stack engineering culture",
                f"{company_name} GitHub repositories open source",
                f"{company_name} CTO engineering interview technical challenges",
                f"{company_name} engineering blog scalability performance"
            ]

            research_results = []

            for query in queries:
                try:
                    # Perform advanced search with context
                    result = self.tavily_client.search(
                        query=query,
                        search_depth="advanced",
                        include_raw_content=True,
                        max_results=3
                    )

                    # Extract relevant content
                    for item in result.get("results", []):
                        content = f"Source: {item.get('title', 'Unknown')}\n"
                        content += f"URL: {item.get('url', 'N/A')}\n"
                        content += f"Content: {item.get('content', item.get('snippet', ''))}\n"
                        research_results.append(content)

                except Exception as e:
                    self.logger.warning(f"Search failed for query '{query}': {e}")
                    continue

            if research_results:
                # Join and limit content size
                combined = "\n\n".join(research_results)
                if len(combined) > 10000:  # Limit to 10k chars
                    combined = combined[:10000] + "\n\n[Content truncated...]"
                return combined
            else:
                return f"No research results found for {company_name}"

        except Exception as e:
            self.logger.error(f"Automated research failed: {e}")
            return f"Research error for {company_name}: {str(e)}"
