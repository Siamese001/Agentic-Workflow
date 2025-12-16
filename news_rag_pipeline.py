"""
Dynamic News RAG Pipeline for Hyper-Personalized Outreach
Integrates real-time news context into the outreach engine

Architecture:
- Fetches news via Brave Search API
- Extracts company/industry relevant insights
- Generates contextual talking points
- Caches results for 24 hours per company
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("NewsRAG")


@dataclass
class NewsInsight:
    """Structured news insight for personalization"""
    headline: str
    summary: str
    relevance_score: float
    source: str
    date: str
    talking_points: List[str]


class NewsRAGPipeline:
    """
    Dynamic News RAG Pipeline for real-time context injection
    """

    def __init__(self):
        self.brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.brave_key:
            logger.warning(
                "⚠️ BRAVE_SEARCH_API_KEY not found. News RAG will be disabled.")

        self.cache_ttl = 24 * 60 * 60  # 24 hours in seconds
        self.max_news_items = 3
        self.session_cache = {}  # In-memory LRU for hot leads

    def _get_cache_key(self, company: str, industry: str) -> str:
        """Generate cache key for news lookup"""
        key = f"news:{company}:{industry}"
        return hashlib.md5(key.encode()).hexdigest()

    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached news is still valid"""
        if not cached_data or "timestamp" not in cached_data:
            return False

        cache_age = datetime.now().timestamp() - cached_data["timestamp"]
        return cache_age < self.cache_ttl

    def _extract_insights(self, news_item: Dict[str, Any], company: str, industry: str) -> NewsInsight:
        """Extract structured insight from news item"""
        title = news_item.get("title", "")
        snippet = news_item.get("description", "")
        url = news_item.get("url", "")

        # Calculate relevance score based on company/industry mentions
        relevance = 0.5  # Base score
        if company.lower() in title.lower() or company.lower() in snippet.lower():
            relevance += 0.3
        if industry.lower() in title.lower() or industry.lower() in snippet.lower():
            relevance += 0.2

        # Generate talking points
        talking_points = []

        # Extract key achievement or milestone
        if any(word in title.lower() for word in ["launch", "release", "announce", "unveil"]):
            talking_points.append(f"Recent product launch: {title}")

        # Extract growth or funding news
        if any(word in title.lower() for word in ["raise", "fund", "investment", "growth"]):
            talking_points.append(f"Growth milestone: {title}")

        # Extract partnership or collaboration
        if any(word in title.lower() for word in ["partner", "collaborate", "joint", "alliance"]):
            talking_points.append(f"Strategic partnership: {title}")

        # Default talking point if nothing specific
        if not talking_points:
            talking_points.append(f"Latest development: {title}")

        return NewsInsight(
            headline=title,
            summary=snippet,
            relevance_score=min(relevance, 1.0),
            source=url.split("/")[2] if url else "Unknown",
            date=news_item.get("age", "Recent"),
            talking_points=talking_points[:2]  # Limit to 2 points
        )

    def _search_company_news(self, company: str, industry: str) -> List[NewsInsight]:
        """Search for recent news about the company"""
        if not self.brave_key:
            return []

        # Build search query
        query = f"{company} {industry} news recent"

        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "X-Subscription-Token": self.brave_key,
                "Accept": "application/json"
            }
            params = {
                "q": query,
                "count": self.max_news_items,
                "text_decorations": "false",
                "search_lang": "en",
                "country": "US",
                "safesearch": "moderate"
            }

            response = requests.get(
                url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get("web", {}).get("results", [])

            insights = []
            for result in results[:self.max_news_items]:
                insight = self._extract_insights(result, company, industry)
                if insight.relevance_score > 0.4:  # Filter low relevance
                    insights.append(insight)

            logger.info(
                f"📰 Found {len(insights)} relevant news items for {company}")
            return insights

        except Exception as e:
            logger.error(f"❌ News search failed for {company}: {e}")
            return []

    def _search_industry_trends(self, industry: str) -> List[NewsInsight]:
        """Search for industry trends and insights"""
        if not self.brave_key:
            return []

        # Build trend-focused query
        query = f"{industry} industry trends 2024 2025"

        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "X-Subscription-Token": self.brave_key,
                "Accept": "application/json"
            }
            params = {
                "q": query,
                "count": 2,  # Fewer for trends
                "text_decorations": "false",
                "search_lang": "en",
                "country": "US"
            }

            response = requests.get(
                url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get("web", {}).get("results", [])

            insights = []
            for result in results[:2]:
                insight = self._extract_insights(result, "", industry)
                insight.talking_points = [
                    f"Industry trend: {insight.headline}"]
                insights.append(insight)

            logger.info(
                f"📈 Found {len(insights)} industry trends for {industry}")
            return insights

        except Exception as e:
            logger.error(f"❌ Industry trends search failed: {e}")
            return []

    def _generate_contextual_intro(self, insights: List[NewsInsight], company: str) -> str:
        """Generate personalized intro based on news insights"""
        if not insights:
            return ""

        # Sort by relevance
        insights.sort(key=lambda x: x.relevance_score, reverse=True)

        # Build contextual intro
        top_insight = insights[0]

        intro_templates = [
            f"I noticed {company} recently {top_insight.talking_points[0].lower() if top_insight.talking_points else 'made headlines'}.",
            f"Following {company}'s recent activities, particularly {top_insight.talking_points[0].lower() if top_insight.talking_points else 'their latest developments'}.",
            f"Given {company}'s recent news about {top_insight.talking_points[0].lower() if top_insight.talking_points else 'their current initiatives'}."
        ]

        return intro_templates[0]  # Use first template

    def _generate_personalization_points(self, insights: List[NewsInsight]) -> List[str]:
        """Generate personalization points from insights"""
        points = []

        for insight in insights[:2]:  # Top 2 insights
            for talking_point in insight.talking_points:
                # Convert to personalization point
                if "product launch" in talking_point.lower():
                    points.append(
                        f"Congrats on the recent launch - must be exciting to see it come to fruition!")
                elif "growth milestone" in talking_point.lower():
                    points.append(
                        f"The recent growth milestone is impressive - speaks to the team's execution.")
                elif "strategic partnership" in talking_point.lower():
                    points.append(
                        f"The strategic partnership announcement caught my eye - smart move for expansion.")
                elif "industry trend" in talking_point.lower():
                    points.append(
                        f"The industry trends are fascinating - curious about your perspective on these shifts.")
                else:
                    points.append(
                        f"The recent developments seem promising - would love to learn more.")

        return points[:3]  # Limit to 3 points

    def execute_news_rag(
        self,
        company: str,
        industry: str,
        redis_get: Optional[callable] = None,
        redis_set: Optional[callable] = None,
        logger: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Execute the News RAG pipeline

        Args:
            company: Target company name
            industry: Industry sector
            redis_get: Redis GET function (optional)
            redis_set: Redis SET function (optional)
            logger: Logger instance (optional)

        Returns:
            Dictionary containing news insights and personalization data
        """
        if logger:
            logger.info(f"📰 Starting News RAG for {company} ({industry})")

        # Check session cache first (hot leads)
        cache_key = self._get_cache_key(company, industry)
        if cache_key in self.session_cache:
            if logger:
                logger.info("🔥 News found in session cache")
            return self.session_cache[cache_key]

        # Check Redis cache
        cached_news = None
        if redis_get:
            try:
                cached_data = redis_get(f"news_rag:{cache_key}")
                if cached_data:
                    cached_news = json.loads(cached_data)
                    if self._is_cache_valid(cached_news):
                        if logger:
                            logger.info("💾 News found in Redis cache")
                        result = cached_news["data"]
                        # Add to session cache
                        self.session_cache[cache_key] = result
                        return result
            except Exception as e:
                if logger:
                    logger.warning(f"Redis cache check failed: {e}")

        # Fetch fresh news
        insights = []

        # Search company-specific news
        company_insights = self._search_company_news(company, industry)
        insights.extend(company_insights)

        # Fill with industry trends if needed
        if len(insights) < 2:
            industry_insights = self._search_industry_trends(industry)
            insights.extend(industry_insights)

        # Generate personalization content
        contextual_intro = self._generate_contextual_intro(insights, company)
        personalization_points = self._generate_personalization_points(
            insights)

        # Build result
        result = {
            "status": "success",
            "company": company,
            "industry": industry,
            "insights_count": len(insights),
            "contextual_intro": contextual_intro,
            "personalization_points": personalization_points,
            "news_available": len(insights) > 0,
            "cache_key": cache_key,
            "timestamp": datetime.now().timestamp()
        }

        # Cache the result
        if redis_set:
            try:
                cache_data = {
                    "timestamp": datetime.now().timestamp(),
                    "data": result
                }
                redis_set(f"news_rag:{cache_key}", json.dumps(cache_data))
                if logger:
                    logger.info("💾 News cached in Redis for 24 hours")
            except Exception as e:
                if logger:
                    logger.warning(f"Redis cache set failed: {e}")

        # Add to session cache
        self.session_cache[cache_key] = result

        if logger:
            logger.info(f"✅ News RAG complete: {len(insights)} insights found")

        return result


# Global pipeline instance
_news_pipeline = None


def get_news_rag_pipeline() -> NewsRAGPipeline:
    """Get or create the global News RAG pipeline instance"""
    global _news_pipeline
    if _news_pipeline is None:
        _news_pipeline = NewsRAGPipeline()
    return _news_pipeline


def execute_news_rag(
    company: str,
    industry: str,
    redis_get: Optional[callable] = None,
    redis_set: Optional[callable] = None,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Convenience function to execute News RAG pipeline

    Args:
        company: Target company name
        industry: Industry sector
        redis_get: Redis GET function
        redis_set: Redis SET function
        logger: Logger instance

    Returns:
        Dictionary containing news insights and personalization data
    """
    pipeline = get_news_rag_pipeline()
    return pipeline.execute_news_rag(company, industry, redis_get, redis_set, logger)