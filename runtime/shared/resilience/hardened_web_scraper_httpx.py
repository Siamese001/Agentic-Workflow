"""
Hardened Web Scraper - Ghost Protocol Implementation with httpx and HardeningMixin.

Implements an adversarial-resistant web scraper with:
- Identity rotation (User-Agents/Proxies)
- Adaptive rate limiting
- Integration with HardeningMixin for resilience
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import httpx

# Import HardeningMixin (assuming it exists)
# from .hardening_mixin import HardeningMixin, HardeningConfig

class ScraperConfig(BaseModel):
    """Tactical configuration for web operations."""
    proxy_pool: List[str] = Field(default_factory=list,
        description="List of Proxy URLs (http://user:pass@host:port).")
    base_delay: float = Field(1.0, description="Minimum sleep between requests (seconds).")
    jitter: float = Field(0.5, description="Randomized delay factor to avoid robotic patterns.")
    max_adaptive_delay: float = Field(30.0, description="Cap for adaptive backoff.")

class ScrapeResult(BaseModel):
    """Result of a scraping operation."""
    url: str
    status_code: int
    content: str
    metadata: Dict[str, str]

# Pre-defined pool of common valid user agents to avoid library dependencies
COMMON_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
        like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML,
        like Gecko) Version/17.2 Safari/605.1.15",
        
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,
        like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
        like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,
        like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"
]

class HardenedWebScraper(HardeningMixin):
    """
    Adversarial-resistant web scraper.
    Features: User-Agent rotation, Proxy support, and Adaptive throttling.
    """

    def __init__(self, hardening_config: 'HardeningConfig', scraper_config: ScraperConfig):
        super().__init__(hardening_config)
        self.scraper_config = scraper_config
        self.logger = logging.getLogger("WebScraper")
        self.current_delay = scraper_config.base_delay

        # Statistics tracking
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "blocked_requests": 0,
            "adaptive_delays": 0
        }

    def _get_tactical_headers(self) -> Dict[str, str]:
        """Generates a random browser fingerprint."""
        return {
            "User-Agent": random.choice(COMMON_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",  # Do Not Track
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }

    def _get_proxy(self) -> Optional[str]:
        """Selects a proxy from the pool if available."""
        if self.scraper_config.proxy_pool:
            return random.choice(self.scraper_config.proxy_pool)
        return None

    async def _raw_fetch(self, url: str) -> httpx.Response:
        """Low-level fetch wrapped by HardeningMixin."""

        # 1. Apply Tactical Delay (Sleep + Jitter)
        jitter_val = random.uniform(0, self.scraper_config.jitter)
        sleep_time = self.current_delay + jitter_val
        self.logger.debug(f"Sleeping for {sleep_time:.2f}s before request")
        await asyncio.sleep(sleep_time)

        headers = self._get_tactical_headers()
        proxy = self._get_proxy()

        # Log current identity
        self.logger.debug(f"Requesting {url} with UA: {headers['User-Agent'][:50]}...")
        if proxy:
            self.logger.debug(f"Using proxy: {proxy.split('@')[-1] if '@' in proxy else proxy}")

        # 2. Execute Request
        timeout = httpx.Timeout(10.0, connect=5.0)

        async with httpx.AsyncClient(
            proxies=proxy,
            verify=False,
            timeout=timeout,
            follow_redirects=True,
            max_redirects=5
        ) as client:
            response = await client.get(url, headers=headers)

            # Raise for standard errors so Mixin can retry (500s, etc.)
            response.raise_for_status()

            # 3. Check for "Soft Blocks" (Captchas, 403s that pass verify but are empty)
            content_lower = response.text.lower()

            # Check for CAPTCHA indicators
            captcha_indicators = [
                "captcha",
                "recaptcha",
                "challenge",
                "verify you are human",
                "security check",
                "unusual traffic",
                "automated requests"
            ]

            if any(indicator in content_lower for indicator in captcha_indicators):
                raise PermissionError("Soft Block detected (Captcha/Challenge)")

            # Check for empty response on 403
            if response.status_code == 403 and len(response.text.strip()) < 100:
                raise PermissionError("Soft Block detected (Empty 403)")

            # Check for rate limiting headers
            if "x-ratelimit-remaining" in response.headers:
                remaining = int(response.headers["x-ratelimit-remaining"])
                if remaining == 0:
                    raise PermissionError("Rate limit exceeded")

            return response

    async def scrape_url(self, url: str) -> ScrapeResult:
        """
        The Hardened Scraping Pipeline.
        """
        self.stats["total_requests"] += 1

        try:
            # Execute with full hardening (Circuit Breaker + Retry)
            # Note: The Mixin handles the retry loop. If _raw_fetch fails (e.g., 403),
            # the retry will kick in, which calls _raw_fetch again.
            # CRITICAL: _raw_fetch re-rolls User-Agent/Proxy every time it's called!

            response = await self.execute_with_hardening(
                self._raw_fetch,
                url=url,
                tokens_used=0
            )

            # Success: Reduce delay slowly (Heal)
            old_delay = self.current_delay
            self.current_delay = max(
                self.scraper_config.base_delay,
                self.current_delay * 0.9
            )

            if old_delay != self.current_delay:
                self.logger.info(f"Reduced delay from {old_delay:.2f}s to {self.current_delay:.2f}s")

            self.stats["successful_requests"] += 1

            return ScrapeResult(
                url=url,
                status_code=response.status_code,
                content=response.text[:50000],  # Truncate for safety
                metadata=dict(response.headers)
            )

        except PermissionError as e:
            # Soft block detected - increase delay
            old_delay = self.current_delay
            self.current_delay = min(
                self.scraper_config.max_adaptive_delay,
                self.current_delay * 2.0
            )

            self.stats["blocked_requests"] += 1
            self.stats["adaptive_delays"] += 1

            self.logger.warning(f"🚫 Soft block detected: {e}")
            self.logger.warning(f"Increased delay from {old_delay:.2f}s to {self.current_delay:.2f}s")
            raise

        except Exception as e:
            # Other failure - increase delay
            old_delay = self.current_delay
            self.current_delay = min(
                self.scraper_config.max_adaptive_delay,
                self.current_delay * 1.5
            )

            self.logger.error(f"❌ Scraping failed for {url} after retries. Backing off to {self.current_delay:.2f}s")
            self.logger.error(f"Error: {e}")
            raise

    async def scrape_multiple(self,
        urls: List[str],
        delay_between_requests: Optional[float] = None) -> List[ScrapeResult]:
        """
        Scrape multiple URLs with adaptive delays.

        Args:
            urls: List of URLs to scrape
            delay_between_requests: Override current delay between requests

        Returns:
            List of ScrapeResult objects
        """
        results = []

        for i, url in enumerate(urls):
            try:

                if delay_between_requests is not None:
                    old_delay = self.current_delay
                    self.current_delay = delay_between_requests

                result = await self.scrape_url(url)
                results.append(result)

                self.logger.info(f"✅ Successfully scraped {url} ({len(result.content)} bytes)")

            except Exception as e:
                self.logger.error(f"❌ Failed to scrape {url}: {e}")
                # Create a failed result
                failed_result = ScrapeResult(
                    url=url,
                    status_code=0,
                    content="",
                    metadata={"error": str(e)}
                )
                results.append(failed_result)

            # Restore original delay if we overrode it
            if delay_between_requests is not None:
                self.current_delay = old_delay

        return results

    def get_stats(self) -> Dict[str, any]:
        """Get scraping statistics."""
        total = self.stats["total_requests"]
        if total == 0:
            return self.stats

        stats = self.stats.copy()
        stats["success_rate"] = self.stats["successful_requests"] / total
        stats["block_rate"] = self.stats["blocked_requests"] / total
        stats["current_delay"] = self.current_delay

        return stats

    def reset_delay(self) -> None:
        """Reset the adaptive delay to base value."""
        self.current_delay = self.scraper_config.base_delay
        self.logger.info(f"Reset delay to {self.current_delay:.2f}s")

    def add_proxy(self, proxy_url: str) -> None:
        """Add a new proxy to the pool."""
        if proxy_url not in self.scraper_config.proxy_pool:
            self.scraper_config.proxy_pool.append(proxy_url)
            self.logger.info(f"Added proxy to pool: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")

    def remove_proxy(self, proxy_url: str) -> None:
        """Remove a proxy from the pool."""
        if proxy_url in self.scraper_config.proxy_pool:
            self.scraper_config.proxy_pool.remove(proxy_url)
            self.logger.info(f"Removed proxy from pool: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")

# Factory function for creating hardened web scraper
def create_hardened_web_scraper(
    hardening_config: 'HardeningConfig',
    proxy_pool: Optional[List[str]] = None,
    base_delay: float = 1.0,
    jitter: float = 0.5,
    max_adaptive_delay: float = 30.0
) -> HardenedWebScraper:
    """Create a hardened web scraper with default configuration.

    Args:
        hardening_config: HardeningMixin configuration
        proxy_pool: List of proxy URLs
        base_delay: Base delay between requests
        jitter: Random jitter factor
        max_adaptive_delay: Maximum adaptive delay

    Returns:
        HardenedWebScraper instance
    """
    scraper_config = ScraperConfig(
        proxy_pool=proxy_pool or [],
        base_delay=base_delay,
        jitter=jitter,
        max_adaptive_delay=max_adaptive_delay
    )

    return HardenedWebScraper(hardening_config, scraper_config)
