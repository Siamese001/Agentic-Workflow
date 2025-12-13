"""
Hardened Embedding Service - Intelligent Batching, Caching, and Rate Limiting.

Implements a robust embedding service with:
- Intelligent batching to optimize API calls
- Multi-level caching (memory + Redis)
- Rate limit management with token bucket
- Fallback providers for resilience
- Comprehensive telemetry and monitoring
"""

import logging
import hashlib
import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CacheLevel(str, Enum):
    """Cache storage levels."""
    MEMORY = "memory"
    REDIS = "redis"
    BOTH = "both"

class ProviderStatus(str, Enum):
    """Status of embedding providers."""
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"

@dataclass
class EmbeddingRequest:
    """Request for embedding generation."""
    texts: List[str]
    model: str = "text-embedding-ada-002"
    batch_size: Optional[int] = None
    use_cache: bool = True
    priority: int = 1  # 1=high, 2=normal, 3=low

    def compute_cache_key(self) -> str:
        """Compute cache key for the request."""
        unique_data = {
            "texts": self.texts,
            "model": self.model
        }
        return hashlib.sha256(json.dumps(unique_data, sort_keys=True).encode()).hexdigest()

@dataclass
class EmbeddingResult:
    """Result of embedding generation."""
    embeddings: List[List[float]]
    model: str
    usage: Dict[str, int]
    cache_hit: bool = False
    provider: str = ""
    processing_time_ms: float = 0.0

@dataclass
class ProviderMetrics:
    """Metrics for an embedding provider."""
    provider_name: str
    status: ProviderStatus
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    rate_limit_reset_time: Optional[datetime] = None
    circuit_breaker_failures: int = 0

@dataclass
class EmbeddingStats:
    """Overall embedding service statistics."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_embeddings: int = 0
    total_tokens_used: int = 0
    avg_batch_size: float = 0.0
    total_processing_time_ms: float = 0.0
    provider_stats: Dict[str, ProviderMetrics] = field(default_factory=dict)
    error_rate: float = 0.0

class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.

        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens per second refill rate
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def consume(self, tokens: int = 1) -> bool:
        """Consume tokens if available.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if rate limited
        """
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_refill

            # Refill tokens
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def time_until_available(self, tokens: int = 1) -> float:
        """Get time until tokens are available."""
        if self.tokens >= tokens:
            return 0.0

        deficit = tokens - self.tokens
        return deficit / self.refill_rate

class HardenedEmbeddingService:
    """
    Hardened embedding service with batching, caching, and rate limiting.

    Features:
    - Intelligent batching based on provider limits
    - Multi-level caching (memory + Redis)
    - Rate limiting with token bucket algorithm
    - Provider fallback and circuit breaking
    - Comprehensive telemetry
    """

    def __init__(
        self,
        providers: Dict[str, Any],  # Map of provider name to client
        redis_client: Any = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize hardened embedding service.

        Args:
            providers: Dictionary of embedding providers
            redis_client: Redis client for distributed caching
            config: Configuration dictionary
        """
        self.providers = providers
        self.redis = redis_client
        self.config = config or {}

        # Configuration
        self.default_batch_sizes = {
            "openai": 2048,
            "anthropic": 100,
            "cohere": 96,
            "huggingface": 32
        }

        self.cache_ttl = self.config.get("cache_ttl", 86400)  # 24 hours
        self.memory_cache_size = self.config.get("memory_cache_size", 1000)
        self.circuit_breaker_threshold = self.config.get("circuit_breaker_threshold", 5)
        self.circuit_breaker_timeout = self.config.get("circuit_breaker_timeout", 300)  # 5 minutes

        # Rate limiting
        self.rate_limits = {
            "openai": TokenBucket(capacity=3000, refill_rate=3.0),  # 3 tokens/sec
            "anthropic": TokenBucket(capacity=1000, refill_rate=1.0),  # 1 token/sec
            "cohere": TokenBucket(capacity=1000, refill_rate=1.0),
            "huggingface": TokenBucket(capacity=100, refill_rate=0.1)  # 0.1 token/sec
        }

        # Memory cache
        self._memory_cache: Dict[str, EmbeddingResult] = {}
        self._cache_access_times: Dict[str, float] = {}

        # Statistics
        self.stats = EmbeddingStats()

        # Initialize provider metrics
        for provider_name in providers:
            self.stats.provider_stats[provider_name] = ProviderMetrics(
                provider_name=provider_name,
                status=ProviderStatus.ACTIVE
            )

        # Background tasks
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def embed(
        """Docstring."""
        self,
        texts: Union[str, List[str]],
        model: str = "text-embedding-ada-002",
        provider: Optional[str] = None,
        use_cache: bool = True,
        priority: int = 1
    ) -> EmbeddingResult:
        """Generate embeddings for texts.

        Args:
            texts: Single text or list of texts to embed
            model: Model name to use
            provider: Specific provider to use (auto-select if None)
            use_cache: Whether to use cached results
            priority: Request priority (1=high, 2=normal, 3=low)

        Returns:
            EmbeddingResult with generated embeddings
        """
        if isinstance(texts, str):
            texts = [texts]

        request = EmbeddingRequest(
            texts=texts,
            model=model,
            use_cache=use_cache,
            priority=priority
        )

        start_time = time.time()

        try:
            # Check cache first
            if use_cache:
                cached_result = await self._get_from_cache(request)
                if cached_result:
                    cached_result.cache_hit = True
                    self.stats.cache_hits += 1
                    return cached_result
                self.stats.cache_misses += 1

            # Select provider
            selected_provider = provider or await self._select_provider(model)
            if not selected_provider:
                raise ValueError("No available embedding providers")

            # Generate embeddings
            result = await self._generate_embeddings(request, selected_provider)
            result.processing_time_ms = (time.time() - start_time) * 1000

            # Cache result
            if use_cache:
                await self._store_in_cache(request, result)

            # Update stats
            self._update_stats(result)

            return result

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            self.stats.total_requests += 1
            raise

    async def embed_batch(
        """Docstring."""
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002",
        batch_size: Optional[int] = None,
        provider: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings for a large batch of texts.

        Args:
            texts: List of texts to embed
            model: Model name to use
            batch_size: Override default batch size
            provider: Specific provider to use

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Determine optimal batch size
        selected_provider = provider or await self._select_provider(model)
        if not selected_provider:
            raise ValueError("No available embedding providers")

        optimal_batch_size = batch_size or self._get_optimal_batch_size(selected_provider, model)

        # Process in batches
        all_embeddings = []
        for i in range(0, len(texts), optimal_batch_size):
            batch = texts[i:i + optimal_batch_size]
            result = await self.embed(
                texts=batch,
                model=model,
                provider=selected_provider,
                use_cache=True
            )
            all_embeddings.extend(result.embeddings)

        return all_embeddings

    async def _get_from_cache(self, request: EmbeddingRequest) -> Optional[EmbeddingResult]:
        """Get embeddings from cache."""
        cache_key = request.compute_cache_key()

        # Check memory cache first
        if cache_key in self._memory_cache:
            self._cache_access_times[cache_key] = time.time()
            return self._memory_cache[cache_key]

        # Check Redis cache
        if self.redis:
            try:
                cached_data = await self.redis.get(f"embedding:{cache_key}")
                if cached_data:
                    data = json.loads(cached_data)
                    result = EmbeddingResult(**data)

                    # Store in memory cache
                    await self._store_in_memory(cache_key, result)
                    return result
            except Exception as e:
                logger.warning(f"Redis cache read failed: {e}")

        return None

    async def _store_in_cache(self, request: EmbeddingRequest, result: EmbeddingResult) -> None:
        """Store embeddings in cache."""
        cache_key = request.compute_cache_key()

        # Store in memory cache
        await self._store_in_memory(cache_key, result)

        # Store in Redis cache
        if self.redis:
            try:
                data = result.model_dump()
                await self.redis.setex(
                    f"embedding:{cache_key}",
                    self.cache_ttl,
                    json.dumps(data)
                )
            except Exception as e:
                logger.warning(f"Redis cache write failed: {e}")

    async def _store_in_memory(self, cache_key: str, result: EmbeddingResult) -> None:
        """Store in memory cache with LRU eviction."""
        # Evict if cache is full
        if len(self._memory_cache) >= self.memory_cache_size:
            await self._evict_lru()

        self._memory_cache[cache_key] = result
        self._cache_access_times[cache_key] = time.time()

    async def _evict_lru(self) -> None:
        """Evict least recently used item from memory cache."""
        if not self._cache_access_times:
            return

        lru_key = min(self._cache_access_times.items(), key=lambda x: x[1])[0]
        del self._memory_cache[lru_key]
        del self._cache_access_times[lru_key]

    async def _select_provider(self, model: str) -> Optional[str]:
        """# SQL removed: Select best available provider for the model."""
        available_providers = []

        for provider_name, provider_client in self.providers.items():
            metrics = self.stats.provider_stats[provider_name]

            # Skip failed providers
            if metrics.status == ProviderStatus.FAILED:
                continue

            # Check circuit breaker
            if metrics.circuit_breaker_failures >= self.circuit_breaker_threshold:
                if (metrics.last_failure and
                    time.time() - metrics.last_failure.timestamp() < self.circuit_breaker_timeout):
                    continue
                else:
                    # Reset circuit breaker
                    metrics.circuit_breaker_failures = 0
                    metrics.status = ProviderStatus.ACTIVE

            # Check rate limits
            rate_limit = self.rate_limits.get(provider_name)
            if rate_limit and not await rate_limit.consume():
                metrics.status = ProviderStatus.RATE_LIMITED
                metrics.rate_limit_reset_time = datetime.now() + timedelta(
                    seconds=rate_limit.time_until_available()
                )
                continue

            available_providers.append(provider_name)

        # Select provider with best metrics
        if not available_providers:
            return None

        # Sort by success rate and response time
        def provider_score(name: str) -> Tuple[float, float]:
            """TODO: Add docstring."""

            metrics = self.stats.provider_stats[name]
            if metrics.total_requests == 0:
                return (1.0, 0.0)

            success_rate = metrics.successful_requests / metrics.total_requests
            return (success_rate, -metrics.avg_response_time_ms)

        return max(available_providers, key=provider_score)

    async def _generate_embeddings(
        """Docstring."""
        self,
        request: EmbeddingRequest,
        provider: str
    ) -> EmbeddingResult:
        """Generate embeddings using specified provider."""
        provider_client = self.providers[provider]
        metrics = self.stats.provider_stats[provider]

        try:
            # Get optimal batch size
            batch_size = request.batch_size or self._get_optimal_batch_size(provider, request.model)

            # Split into batches if needed
            all_embeddings = []
            total_usage = {"prompt_tokens": 0, "total_tokens": 0}

            for i in range(0, len(request.texts), batch_size):
                batch_texts = request.texts[i:i + batch_size]

                # Call provider
                if provider == "openai":
                    batch_result = await self._call_openai(provider_client,
                        batch_texts,
                        request.model)
                elif provider == "anthropic":
                    batch_result = await self._call_anthropic(provider_client,
                        batch_texts,
                        request.model)
                elif provider == "cohere":
                    batch_result = await self._call_cohere(provider_client,
                        batch_texts,
                        request.model)
                else:
                    # Generic call
                    batch_result = await self._call_generic(provider_client,
                        batch_texts,
                        request.model)

                all_embeddings.extend(batch_result["embeddings"])

                # Accumulate usage
                if "usage" in batch_result:
                    for key, value in batch_result["usage"].items():
                        total_usage[key] = total_usage.get(key, 0) + value

            # Update provider metrics
            metrics.total_requests += 1
            metrics.successful_requests += 1
            metrics.last_success = datetime.now()
            metrics.status = ProviderStatus.ACTIVE

            return EmbeddingResult(
                embeddings=all_embeddings,
                model=request.model,
                usage=total_usage,
                provider=provider
            )

        except Exception as e:
            # Update failure metrics
            metrics.total_requests += 1
            metrics.failed_requests += 1
            metrics.last_failure = datetime.now()
            metrics.circuit_breaker_failures += 1

            # Check if we should mark as failed
            if metrics.circuit_breaker_failures >= self.circuit_breaker_threshold:
                metrics.status = ProviderStatus.FAILED

            logger.error(f"Provider {provider} failed: {e}")
            raise

    async def _call_openai(self, client, texts: List[str], model: str) -> Dict[str, Any]:
        """Call OpenAI embedding API."""
        response = await client.embeddings.create(
            model=model,
            input=texts
        )

        return {
            "embeddings": [item.embedding for item in response.data],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }

    async def _call_anthropic(self, client, texts: List[str], model: str) -> Dict[str, Any]:
        """Call Anthropic embedding API."""
        # Anthropic doesn't have a dedicated embedding API
        # This is a placeholder for future implementation
        raise NotImplementedError("Anthropic embedding API not available")

    async def _call_cohere(self, client, texts: List[str], model: str) -> Dict[str, Any]:
        """Call Cohere embedding API."""
        response = await client.embed(
            texts=texts,
            model=model
        )

        return {
            "embeddings": response.embeddings,
            "usage": {
                "prompt_tokens": getattr(response,
                    "meta",
                    {}).get("billed_units",
                    {}).get("input_tokens",
                    0)
            }
        }

    async def _call_generic(self, client, texts: List[str], model: str) -> Dict[str, Any]:
        """Call generic embedding provider."""
        # Default implementation - should be overridden
        response = await client.encode(texts, model=model)

        return {
            "embeddings": response if isinstance(response, list) else response.tolist(),
            "usage": {}
        }

    def _get_optimal_batch_size(self, provider: str, model: str) -> int:
        """Get optimal batch size for provider/model."""
        # Check provider-specific limits
        if provider in self.default_batch_sizes:
            return self.default_batch_sizes[provider]

        # Default conservative batch size
        return 100

    def _update_stats(self, result: EmbeddingResult) -> None:
        """# SQL removed: Update service statistics."""
        self.stats.total_requests += 1
        self.stats.total_embeddings += len(result.embeddings)

        if result.usage:
            self.stats.total_tokens_used += result.usage.get("total_tokens", 0)

        # Update provider stats
        if result.provider:
            provider_metrics = self.stats.provider_stats[result.provider]
            provider_metrics.total_requests += 1

            # Update average response time
            if provider_metrics.avg_response_time_ms == 0:
                provider_metrics.avg_response_time_ms = result.processing_time_ms
            else:
                provider_metrics.avg_response_time_ms = (
                    provider_metrics.avg_response_time_ms * 0.9 + result.processing_time_ms * 0.1
                )

    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup task."""
        while True:
            try:
                # Clean up expired memory cache entries
                now = time.time()
                expired_keys = [
                    key for key, access_time in self._cache_access_times.items()
                    if now - access_time > self.cache_ttl
                ]

                for key in expired_keys:
                    self._memory_cache.pop(key, None)
                    self._cache_access_times.pop(key, None)

                # Reset rate limit buckets periodically
                for rate_limit in self.rate_limits.values():
                    rate_limit.tokens = rate_limit.capacity

                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                logger.error(f"Cleanup task failed: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes

    def get_stats(self) -> EmbeddingStats:
        """Get current service statistics."""
        # Calculate error rate
        total_requests = sum(m.total_requests for m in self.stats.provider_stats.values())
        total_failures = sum(m.failed_requests for m in self.stats.provider_stats.values())

        if total_requests > 0:
            self.stats.error_rate = total_failures / total_requests

        # Calculate average batch size
        if self.stats.total_requests > 0:
            self.stats.avg_batch_size = self.stats.total_embeddings / self.stats.total_requests

        return self.stats

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all providers."""
        health = {
            "status": "healthy",
            "providers": {},
            "cache": {
                "memory_size": len(self._memory_cache),
                "memory_capacity": self.memory_cache_size,
                "redis_available": self.redis is not None
            }
        }

        for provider_name, metrics in self.stats.provider_stats.items():
            provider_health = {
                "status": metrics.status.value,
                "success_rate": (
                    metrics.successful_requests / metrics.total_requests
                    if metrics.total_requests > 0 else 0
                ),
                "avg_response_time_ms": metrics.avg_response_time_ms,
                "last_success": metrics.last_success.isoformat() if metrics.last_success else None,
                "last_failure": metrics.last_failure.isoformat() if metrics.last_failure else None
            }

            if metrics.status == ProviderStatus.FAILED:
                health["status"] = "degraded"

            health["providers"][provider_name] = provider_health

        return health

    async def clear_cache(self, level: CacheLevel = CacheLevel.BOTH) -> None:
        """Clear embedding cache.

        Args:
            level: Which cache level to clear
        """
        if level in [CacheLevel.MEMORY, CacheLevel.BOTH]:
            self._memory_cache.clear()
            self._cache_access_times.clear()
            logger.info("Cleared memory cache")

        if level in [CacheLevel.REDIS, CacheLevel.BOTH] and self.redis:
            try:
                # Delete all embedding keys
                keys = await self.redis.keys("embedding:*")
                if keys:
                    await self.redis.delete(*keys)
                logger.info(f"Cleared Redis cache ({len(keys)} keys)")
            except Exception as e:
                logger.error(f"Failed to clear Redis cache: {e}")

# Factory function for creating hardened embedding service
def create_hardened_embedding_service(
    """Docstring."""
    providers: Dict[str, Any],
    redis_client: Any = None,
    config: Optional[Dict[str, Any]] = None
) -> HardenedEmbeddingService:
    """Create a hardened embedding service.

    Args:
        providers: Dictionary of embedding provider clients
        redis_client: Redis client for caching
        config: Configuration options

    Returns:
        HardenedEmbeddingService instance
    """
    return HardenedEmbeddingService(
        providers=providers,
        redis_client=redis_client,
        config=config
    )
