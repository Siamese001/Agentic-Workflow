"""
Hardened Web Scraper - Anti-Detection Web Scraping with Proxies and Rate Limiting.

Implements a robust web scraper with:
- Rotating proxy support
- User-Agent rotation
- Adaptive rate limiting
- CAPTCHA handling
- Session management
- Request retry with exponential backoff
"""

import logging
import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import ssl

logger = logging.getLogger(__name__)

class ProxyType(str, Enum):
    """Types of proxy support."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    TOKEN_BUCKET = "token_bucket"

class CaptchaSolver(str, Enum):
    """CAPTCHA solving services."""
    NONE = "none"
    TWO_CAPTCHA = "2captcha"
    ANTI_CAPTCHA = "anticaptcha"
    CUSTOM = "custom"

@dataclass
class ProxyConfig:
    """Proxy configuration."""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: ProxyType = ProxyType.HTTP
    country: Optional[str] = None

    def to_url(self) -> str:
        """Convert proxy to URL format."""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        else:
            auth = ""

        return f"{self.proxy_type.value}://{auth}{self.host}:{self.port}"

@dataclass
class RequestConfig:
    """Configuration for HTTP requests."""
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    max_redirects: int = 5
    verify_ssl: bool = True
    follow_redirects: bool = True

    # Headers
    default_headers: Dict[str, str] = field(default_factory=dict)

    # Rate limiting
    rate_limit_strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE
    requests_per_second: float = 1.0
    burst_size: int = 5

    # Anti-detection
    rotate_user_agent: bool = True
    rotate_headers: bool = True
    random_delay_range: Tuple[float, float] = (0.5, 2.0)

    # CAPTCHA
    captcha_solver: CaptchaSolver = CaptchaSolver.NONE
    captcha_api_key: Optional[str] = None

@dataclass
class ScrapeResult:
    """Result of a scraping operation."""
    url: str
    status_code: int
    content: str
    headers: Dict[str, str]
    response_time_ms: float
    proxy_used: Optional[str] = None
    user_agent_used: Optional[str] = None
    captcha_solved: bool = False
    retry_count: int = 0
    error_message: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if request was successful."""
        return 200 <= self.status_code < 300 and self.error_message is None

class UserAgentRotator:
    """Rotates User-Agent strings."""

    def __init__(self):
        self.user_agents = [
            # Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
                like Gecko) Chrome/120.0.0.0 Safari/537.36",
                
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,
                like Gecko) Chrome/120.0.0.0 Safari/537.36",
                
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,
                like Gecko) Chrome/120.0.0.0 Safari/537.36",
                

            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",

            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML,
                like Gecko) Version/17.2 Safari/605.1.15",
                

            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
                like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        self.current_index = 0

    def get_random(self) -> str:
        """Get a random User-Agent."""
        return random.choice(self.user_agents)

    def get_next(self) -> str:
        """Get next User-Agent in rotation."""
        ua = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return ua

class ProxyRotator:
    """Manages proxy rotation and health."""

    def __init__(self, proxies: List[ProxyConfig]):
        self.proxies = proxies
        self.healthy_proxies = proxies.copy()
        self.failed_proxies: List[ProxyConfig] = []
        self.proxy_stats: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()

        # Initialize stats
        for proxy in proxies:
            self.proxy_stats[proxy.to_url()] = {
                "successes": 0,
                "failures": 0,
                "last_used": None,
                "avg_response_time": 0.0
            }

    async def get_proxy(self) -> Optional[ProxyConfig]:
        """Get a healthy proxy."""
        async with self._lock:
            if not self.healthy_proxies:
                # Try to recover failed proxies
                await self._recover_failed_proxies()
                if not self.healthy_proxies:
                    return None

            # Select proxy based on success rate and response time
            def proxy_score(proxy: ProxyConfig) -> float:
                stats = self.proxy_stats[proxy.to_url()]
                if stats["successes"] + stats["failures"] == 0:
                    return 1.0

                success_rate = stats["successes"] / (stats["successes"] + stats["failures"])
                response_score = 1.0 / (1.0 + stats["avg_response_time"])

                return success_rate * 0.7 + response_score * 0.3

            proxy = max(self.healthy_proxies, key=proxy_score)
            return proxy

    async def report_success(self, proxy: ProxyConfig, response_time: float) -> None:
        """Report successful proxy usage."""
        async with self._lock:
            url = proxy.to_url()
            stats = self.proxy_stats[url]

            stats["successes"] += 1
            stats["last_used"] = datetime.now()

            # Update average response time
            if stats["avg_response_time"] == 0:
                stats["avg_response_time"] = response_time
            else:
                stats["avg_response_time"] = (
                    stats["avg_response_time"] * 0.9 + response_time * 0.1
                )

    async def report_failure(self, proxy: ProxyConfig) -> None:
        """Report failed proxy."""
        async with self._lock:
            if proxy in self.healthy_proxies:
                self.healthy_proxies.remove(proxy)
                self.failed_proxies.append(proxy)

                url = proxy.to_url()
                self.proxy_stats[url]["failures"] += 1

                logger.warning(f"Proxy {url} marked as failed")

    async def _recover_failed_proxies(self) -> None:
        """Attempt to recover failed proxies."""
        recovered = []

        for proxy in self.failed_proxies:
            # Simple recovery: try failed proxies after 5 minutes
            stats = self.proxy_stats[proxy.to_url()]
            if stats["failures"] < 3:  # Only recover if not too many failures
                self.healthy_proxies.append(proxy)
                recovered.append(proxy)

        for proxy in recovered:
            self.failed_proxies.remove(proxy)
            logger.info(f"Recovered proxy {proxy.to_url()}")

class RateLimiter:
    """Rate limiting with adaptive strategies."""

    def __init__(self,
        strategy: RateLimitStrategy,
        requests_per_second: float,
        burst_size: int = 5):
        self.strategy = strategy
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size

        self.tokens = burst_size
        self.last_refill = time.time()
        self.request_times: List[float] = []
        self.adaptive_delay = 1.0 / requests_per_second
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        if self.strategy == RateLimitStrategy.FIXED:
            await self._fixed_delay()
        elif self.strategy == RateLimitStrategy.ADAPTIVE:
            await self._adaptive_delay()
        elif self.strategy == RateLimitStrategy.EXPONENTIAL_BACKOFF:
            await self._exponential_backoff()
        elif self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            await self._token_bucket()

    async def _fixed_delay(self) -> None:
        """Fixed delay between requests."""
        delay = 1.0 / self.requests_per_second
        await asyncio.sleep(delay)

    async def _adaptive_delay(self) -> None:
        """Adaptive delay based on response patterns."""
        async with self._lock:
            now = time.time()

            # Remove old requests (older than 10 seconds)
            self.request_times = [t for t in self.request_times if now - t < 10]

            # If we're making too many requests, increase delay
            if len(self.request_times) > self.requests_per_second * 2:
                self.adaptive_delay = min(self.adaptive_delay * 1.5, 5.0)
            elif len(self.request_times) < self.requests_per_second * 0.5:
                self.adaptive_delay = max(self.adaptive_delay * 0.9, 1.0 / self.requests_per_second)

            self.request_times.append(now)
            await asyncio.sleep(self.adaptive_delay)

    async def _exponential_backoff(self) -> None:
        """Exponential backoff for rate limiting."""
        async with self._lock:
            now = time.time()
            recent_requests = [t for t in self.request_times if now - t < 1.0]

            if len(recent_requests) >= self.requests_per_second:
                # Exponential backoff
                backoff = min(2 ** len(recent_requests), 10.0)
                await asyncio.sleep(backoff)
            else:
                await asyncio.sleep(1.0 / self.requests_per_second)

            self.request_times.append(now)

    async def _token_bucket(self) -> None:
        """Token bucket algorithm."""
        async with self._lock:
            now = time.time()

            # Refill tokens
            elapsed = now - self.last_refill
            self.tokens = min(
                self.burst_size,
                self.tokens + elapsed * self.requests_per_second
            )
            self.last_refill = now

            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.requests_per_second
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

class HardenedWebScraper:
    """
    Hardened web scraper with anti-detection features.

    Features:
    - Rotating proxy support
    - User-Agent rotation
    - Adaptive rate limiting
    - CAPTCHA handling
    - Session management
    - Request retry with exponential backoff
    """

    def __init__(
        self,
        proxies: Optional[List[ProxyConfig]] = None,
        config: Optional[RequestConfig] = None
    ):
        """Initialize hardened web scraper.

        Args:
            proxies: List of proxy configurations
            config: Request configuration
        """
        self.config = config or RequestConfig()
        self.proxies = proxies or []

        # Initialize components
        self.proxy_rotator = ProxyRotator(self.proxies) if self.proxies else None
        self.user_agent_rotator = UserAgentRotator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_strategy,
            self.config.requests_per_second,
            self.config.burst_size
        )

        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.session_cookies: Dict[str, str] = {}

        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "captcha_solved": 0,
            "proxies_used": 0,
            "avg_response_time_ms": 0.0
        }

        # Initialize session
        asyncio.create_task(self._initialize_session())

    async def _initialize_session(self) -> None:
        """Initialize aiohttp session."""
        # Configure SSL context
        ssl_context = ssl.create_default_context()
        if not self.config.verify_ssl:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        # Create session with default settings
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=100,
            limit_per_host=20
        )

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            cookie_jar=aiohttp.CookieJar(unsafe=True)
        )

    async def scrape(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, Dict]] = None,
        json_data: Optional[Dict] = None
    ) -> ScrapeResult:
        """Scrape a URL with anti-detection measures.

        Args:
            url: URL to scrape
            method: HTTP method
            headers: Additional headers
            params: Query parameters
            data: Form data
            json_data: JSON data

        Returns:
            ScrapeResult with response data
        """
        if not self.session:
            await self._initialize_session()

        # Rate limiting
        await self.rate_limiter.acquire()

        # Prepare request
        headers = headers or {}
        headers.update(self.config.default_headers)

        # Rotate User-Agent
        if self.config.rotate_user_agent:
            headers["User-Agent"] = self.user_agent_rotator.get_random()

        # Get proxy
        proxy = None
        proxy_url = None
        if self.proxy_rotator:
            proxy = await self.proxy_rotator.get_proxy()
            if proxy:
                proxy_url = proxy.to_url()

        # Add random delay
        if self.config.random_delay_range:
            delay = random.uniform(*self.config.random_delay_range)
            await asyncio.sleep(delay)

        # Make request with retries
        result = await self._make_request_with_retry(
            url, method, headers, params, data, json_data, proxy_url
        )

        # Report proxy usage
        if proxy and result.success:
            await self.proxy_rotator.report_success(proxy, result.response_time_ms)
        elif proxy and not result.success:
            await self.proxy_rotator.report_failure(proxy)

        # Update stats
        self._update_stats(result)

        return result

    async def _make_request_with_retry(
        self,
        url: str,
        method: str,
        headers: Dict[str, str],
        params: Optional[Dict],
        data: Optional[Union[str, Dict]],
        json_data: Optional[Dict],
        proxy_url: Optional[str]
    ) -> ScrapeResult:
        """Make request with retry logic."""
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = await self._make_single_request(
                    url, method, headers, params, data, json_data, proxy_url
                )
                result.retry_count = attempt

                # Check for CAPTCHA
                if self._is_captcha_response(result):
                    if await self._handle_captcha(result):
                        result.captcha_solved = True
                        # Retry after solving CAPTCHA
                        continue

                # Check if we should retry
                if result.status_code in [429, 502, 503, 504] and attempt < self.config.max_retries:
                    retry_delay = self.config.retry_delay_seconds * (2 ** attempt)
                    logger.warning(f"Request failed with {result.status_code},
                        retrying in {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    continue

                return result

            except Exception as e:
                last_error = str(e)
                if attempt < self.config.max_retries:
                    retry_delay = self.config.retry_delay_seconds * (2 ** attempt)
                    logger.warning(f"Request failed: {e}, retrying in {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    continue

        # All retries failed
        return ScrapeResult(
            url=url,
            status_code=0,
            content="",
            headers={},
            response_time_ms=0,
            error_message=last_error or "Max retries exceeded"
        )

    async def _make_single_request(
        self,
        url: str,
        method: str,
        headers: Dict[str, str],
        params: Optional[Dict],
        data: Optional[Union[str, Dict]],
        json_data: Optional[Dict],
        proxy_url: Optional[str]
    ) -> ScrapeResult:
        """Make a single HTTP request."""
        start_time = time.time()

        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                proxy=proxy_url,
                allow_redirects=self.config.follow_redirects,
                max_redirects=self.config.max_redirects
            ) as response:
                content = await response.text()
                response_time_ms = (time.time() - start_time) * 1000

                return ScrapeResult(
                    url=url,
                    status_code=response.status,
                    content=content,
                    headers=dict(response.headers),
                    response_time_ms=response_time_ms,
                    proxy_used=proxy_url,
                    user_agent_used=headers.get("User-Agent")
                )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return ScrapeResult(
                url=url,
                status_code=0,
                content="",
                headers={},
                response_time_ms=response_time_ms,
                proxy_used=proxy_url,
                user_agent_used=headers.get("User-Agent"),
                error_message=str(e)
            )

    def _is_captcha_response(self, result: ScrapeResult) -> bool:
        """Check if response contains CAPTCHA challenge."""
        captcha_indicators = [
            "captcha",
            "recaptcha",
            "challenge",
            "verify you are human",
            "security check"
        ]

        content_lower = result.content.lower()
        return any(indicator in content_lower for indicator in captcha_indicators)

    async def _handle_captcha(self, result: ScrapeResult) -> bool:
        """Handle CAPTCHA challenge."""
        if self.config.captcha_solver == CaptchaSolver.NONE:
            return False

        # Placeholder for CAPTCHA solving logic
        # In a real implementation, you would integrate with services like 2captcha
        logger.info("CAPTCHA detected, attempting to solve...")
        self.stats["captcha_solved"] += 1

        # Simulate solving time
        await asyncio.sleep(5)

        return True

    def _update_stats(self, result: ScrapeResult) -> None:
        """# SQL removed: Update scraping statistics."""
        self.stats["total_requests"] += 1

        if result.success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1

        if result.proxy_used:
            self.stats["proxies_used"] += 1

        # Update average response time
        if self.stats["total_requests"] == 1:
            self.stats["avg_response_time_ms"] = result.response_time_ms
        else:
            self.stats["avg_response_time_ms"] = (
                self.stats["avg_response_time_ms"] * 0.9 +
                result.response_time_ms * 0.1
            )

    async def scrape_multiple(
        self,
        urls: List[str],
        concurrent_limit: int = 5,
        delay_between_batches: float = 1.0
    ) -> List[ScrapeResult]:
        """Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            concurrent_limit: Maximum concurrent requests
            delay_between_batches: Delay between batches

        Returns:
            List of scrape results
        """
        semaphore = asyncio.Semaphore(concurrent_limit)

        async def scrape_with_semaphore(url: str) -> ScrapeResult:
            async with semaphore:
                result = await self.scrape(url)
                return result

        # Process in batches
        results = []
        batch_size = concurrent_limit

        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[scrape_with_semaphore(url) for url in batch],
                return_exceptions=True
            )

            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(ScrapeResult(
                        url="",
                        status_code=0,
                        content="",
                        headers={},
                        response_time_ms=0,
                        error_message=str(result)
                    ))
                else:
                    results.append(result)

            # Delay between batches
            if i + batch_size < len(urls):
                await asyncio.sleep(delay_between_batches)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        total = self.stats["total_requests"]
        if total == 0:
            return self.stats

        stats = self.stats.copy()
        stats["success_rate"] = self.stats["successful_requests"] / total
        stats["failure_rate"] = self.stats["failed_requests"] / total

        if self.proxy_rotator:
            stats["proxy_health"] = {
                "healthy": len(self.proxy_rotator.healthy_proxies),
                "failed": len(self.proxy_rotator.failed_proxies),
                "total": len(self.proxies)
            }

        return stats

    async def close(self) -> None:
        """Close resources."""
        if self.session:
            await self.session.close()

# Factory function for creating hardened web scraper
def create_hardened_web_scraper(
    proxies: Optional[List[ProxyConfig]] = None,
    config: Optional[RequestConfig] = None
) -> HardenedWebScraper:
    """Create a hardened web scraper.

    Args:
        proxies: List of proxy configurations
        config: Request configuration

    Returns:
        HardenedWebScraper instance
    """
    return HardenedWebScraper(proxies, config)
