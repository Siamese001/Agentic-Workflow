"""Python-native MCP tool implementations.

Provides direct Python implementations of MCP capabilities without requiring
Node.js MCP servers. These tools integrate seamlessly with the agentic framework.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import praw


@dataclass
class MCPToolResult:
    """Result from an MCP tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    source: str = ""


class PlaywrightMCPTool:
    """Python-native Playwright tool for web scraping and automation."""

    def __init__(self):
        """Initialize Playwright tool."""
        self.logger = logging.getLogger("PlaywrightMCPTool")

    async def scrape_url(self, url: str, selectors: Optional[Dict[str, str]] = None) -> MCPToolResult:
        """Scrape a URL and extract data using CSS selectors.

        Args:
            url: URL to scrape
            selectors: Optional dict of {key: css_selector} for data extraction

        Returns:
            MCPToolResult with extracted data
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until="networkidle")

                data = {"url": url, "title": await page.title()}

                if selectors:
                    for key, selector in selectors.items():
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                data[key] = await element.text_content()
                        except Exception as e:
                            self.logger.warning(f"Failed to extract {key}: {e}")
                            data[key] = None
                else:
                    # Get full page text if no selectors provided
                    data["content"] = await page.content()

                await browser.close()

                return MCPToolResult(
                    success=True,
                    data=data,
                    source="playwright"
                )

        except Exception as e:
            self.logger.error(f"Playwright scraping failed: {e}")
            return MCPToolResult(
                success=False,
                data={},
                error=str(e),
                source="playwright"
            )

    async def screenshot_url(self, url: str, output_path: str) -> MCPToolResult:
        """Take a screenshot of a URL.

        Args:
            url: URL to screenshot
            output_path: Path to save screenshot

        Returns:
            MCPToolResult with screenshot path
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until="networkidle")
                await page.screenshot(path=output_path, full_page=True)

                await browser.close()

                return MCPToolResult(
                    success=True,
                    data={"screenshot_path": output_path, "url": url},
                    source="playwright"
                )

        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return MCPToolResult(
                success=False,
                data={},
                error=str(e),
                source="playwright"
            )


class RedditMCPTool:
    """Python-native Reddit tool using PRAW."""

    def __init__(self):
        """Initialize Reddit tool with credentials from environment."""
        self.logger = logging.getLogger("RedditMCPTool")

        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "AgenticFramework/1.0")

        if client_id and client_secret:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            self.enabled = True
        else:
            self.reddit = None
            self.enabled = False
            self.logger.warning("Reddit credentials not set - tool disabled")

    def search_posts(self, query: str, subreddit: Optional[str] = None, limit: int = 10) -> MCPToolResult:
        """Search Reddit posts.

        Args:
            query: Search query
            subreddit: Optional subreddit to search in
            limit: Maximum number of results

        Returns:
            MCPToolResult with posts
        """
        if not self.enabled:
            return MCPToolResult(
                success=False,
                data=[],
                error="Reddit credentials not configured",
                source="reddit"
            )

        try:
            posts = []

            if subreddit:
                sub = self.reddit.subreddit(subreddit)
                results = sub.search(query, limit=limit)
            else:
                results = self.reddit.subreddit("all").search(query, limit=limit)

            for post in results:
                posts.append({
                    "title": post.title,
                    "score": post.score,
                    "url": post.url,
                    "author": str(post.author),
                    "created_utc": post.created_utc,
                    "num_comments": post.num_comments,
                    "selftext": post.selftext[:500] if post.selftext else ""
                })

            return MCPToolResult(
                success=True,
                data=posts,
                source="reddit"
            )

        except Exception as e:
            self.logger.error(f"Reddit search failed: {e}")
            return MCPToolResult(
                success=False,
                data=[],
                error=str(e),
                source="reddit"
            )

    def get_subreddit_info(self, subreddit_name: str) -> MCPToolResult:
        """Get information about a subreddit.

        Args:
            subreddit_name: Name of subreddit

        Returns:
            MCPToolResult with subreddit info
        """
        if not self.enabled:
            return MCPToolResult(
                success=False,
                data={},
                error="Reddit credentials not configured",
                source="reddit"
            )

        try:
            sub = self.reddit.subreddit(subreddit_name)

            info = {
                "name": sub.display_name,
                "title": sub.title,
                "description": sub.public_description,
                "subscribers": sub.subscribers,
                "active_users": sub.active_user_count,
                "created_utc": sub.created_utc
            }

            return MCPToolResult(
                success=True,
                data=info,
                source="reddit"
            )

        except Exception as e:
            self.logger.error(f"Subreddit info failed: {e}")
            return MCPToolResult(
                success=False,
                data={},
                error=str(e),
                source="reddit"
            )


class DockerHubMCPTool:
    """Python-native DockerHub tool using public API."""

    def __init__(self):
        """Initialize DockerHub tool."""
        self.logger = logging.getLogger("DockerHubMCPTool")
        self.base_url = "https://hub.docker.com/v2"

    def search_images(self, query: str, limit: int = 10) -> MCPToolResult:
        """Search DockerHub for images.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            MCPToolResult with images
        """
        try:
            response = requests.get(
                f"{self.base_url}/search/repositories/",
                params={"query": query, "page_size": limit}
            )
            response.raise_for_status()

            data = response.json()
            images = []

            for result in data.get("results", []):
                images.append({
                    "name": result.get("repo_name"),
                    "description": result.get("short_description"),
                    "stars": result.get("star_count"),
                    "pulls": result.get("pull_count"),
                    "is_official": result.get("is_official"),
                    "is_automated": result.get("is_automated")
                })

            return MCPToolResult(
                success=True,
                data=images,
                source="dockerhub"
            )

        except Exception as e:
            self.logger.error(f"DockerHub search failed: {e}")
            return MCPToolResult(
                success=False,
                data=[],
                error=str(e),
                source="dockerhub"
            )


class PythonMCPToolkit:
    """Unified toolkit for all Python-native MCP tools."""

    def __init__(self):
        """Initialize all MCP tools."""
        self.playwright = PlaywrightMCPTool()
        self.reddit = RedditMCPTool()
        self.dockerhub = DockerHubMCPTool()
        self.logger = logging.getLogger("PythonMCPToolkit")

    async def scrape_web(self, url: str, selectors: Optional[Dict[str, str]] = None) -> MCPToolResult:
        """Scrape web content using Playwright."""
        return await self.playwright.scrape_url(url, selectors)

    def search_reddit(self, query: str, subreddit: Optional[str] = None, limit: int = 10) -> MCPToolResult:
        """Search Reddit posts."""
        return self.reddit.search_posts(query, subreddit, limit)

    def search_dockerhub(self, query: str, limit: int = 10) -> MCPToolResult:
        """Search DockerHub images."""
        return self.dockerhub.search_images(query, limit)

    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        tools = ["playwright", "dockerhub"]
        if self.reddit.enabled:
            tools.append("reddit")
        return tools
