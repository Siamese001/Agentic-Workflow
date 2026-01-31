"""
EmbeddingSovereignAgent - Unified Embedding Gateway

[PHASE 4 MIGRATION] Consolidates all embedding operations:
- Gemini embeddings
- OpenAI embeddings
- Dimension validation
- Batch processing
- Redis caching integration (via mixin)
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    pass

from agentic_core.base_agents.timeout_decorator import timeout
from agentic_core.config.SovereignConfigManager import get_sovereign_config
from agentic_core.L5_safety.validators.decorators import standard_heal

Logger = logging.getLogger(__name__)

# Import mixins for functionality
try:
    from agentic_core.base_agents.redis_cache_mixin import RedisCacheMixin
    from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin
except ImportError:
    # Fallback stubs if mixins are not available
    class SubatomicTestingMixin:
        pass

    class RedisCacheMixin:
        def cache_get(self, key):
            return None

        def cache_set(self, key, value, ttl=None):
            pass


EmbeddingProvider = Literal["gemini", "openai"]


@dataclass
class EmbeddingSovereignAgent(SubatomicTestingMixin, RedisCacheMixin, SovereignBaseAgent):
    """
    Unified Embedding Gateway with Redis caching.

    [PHASE 4 MIGRATION] Absorbed from:
    - gemini_embedder.py
    - core_embedder.py
    - PineconeSovereignAgent.get_embedding()

    [PHASE 8] NOT an agent - utility singleton to avoid circular imports.
    """

    _instance: EmbeddingSovereignAgent | None = None

    # [PHASE 6] configuration now managed by SovereignConfigManager

    _cache_prefix: str = "emb"
    _default_ttl: int = 86400  # 24 hours

    operation_stats: dict[str, int] = field(
        default_factory=lambda: {
            "gemini": 0,
            "openai": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total": 0,
        }
    )

    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize the EmbeddingSovereignAgent."""
        super().__post_init__()

    def __new__(cls, *args, **kwargs):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """[TESTING ONLY] Reset the singleton instance."""
        cls._instance = None

    @property
    def config(self):
        """[PHASE 6] Access centralized config."""
        return get_sovereign_config()

    @property
    def EXPECTED_DIMENSIONS(self) -> dict[str, int]:
        """[PHASE 6] Dynamic dimensions from config."""
        return {
            "gemini": self.config.EMBEDDING_DIM_GEMINI,
            "openai": self.config.EMBEDDING_DIM_OPENAI,
        }

    def _audit(self, provider: str, success: bool, cached: bool, latency_ms: float) -> None:
        """
        [PHASE 4] Record embedding operation.
        Includes FIFO rotation to prevent memory leaks.
        """
        # [PHASE 6] Dynamic limit from config
        limit = self.config.max_audit_log_size

        if len(self.audit_log) >= limit:
            # Prune 10% when full
            prune_count = max(1, int(limit * 0.1))
            self.audit_log = self.audit_log[prune_count:]

        self.audit_log.append(
            {
                "provider": provider,
                "success": success,
                "cached": cached,
                "latency_ms": latency_ms,
                "ts": time.time(),
            }
        )
        self.operation_stats["total"] += 1
        if cached:
            self.operation_stats["cache_hits"] += 1
        else:
            self.operation_stats["cache_misses"] += 1
            if success:
                self.operation_stats[provider] = self.operation_stats.get(provider, 0) + 1

    def _content_hash(self, content: str) -> str:
        """Generate deterministic hash for caching."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def get_embedding(
        self, content: str, provider: EmbeddingProvider = "gemini", use_cache: bool = True
    ) -> list[float]:
        """
        Get embedding vector with optional caching.

        [PHASE 4] Unified interface for all embedding providers.
        """
        start = time.time()

        # Check cache first
        cache_key = f"{self._cache_prefix}:{provider}:{self._content_hash(content)}"

        if use_cache:
            try:
                cached = await self.cache_get(cache_key)
                if cached:
                    latency = (time.time() - start) * 1000
                    self._audit(provider, True, True, latency)
                    return cached
            except Exception as e:
                Logger.warning(f"Redis cache lookup failed: {e}")

        # Generate embedding
        try:
            if provider == "gemini":
                embedding = await self._get_gemini_embedding(content)
            elif provider == "openai":
                embedding = await self._get_openai_embedding(content)
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # Validate dimension
            expected_dim = self.EXPECTED_DIMENSIONS.get(provider)
            if expected_dim and len(embedding) != expected_dim:
                Logger.warning(f"Dimension mismatch: got {len(embedding)}, expected {expected_dim}")

            # cache result
            if use_cache:
                try:
                    await self.cache_set(cache_key, embedding, ttl=self._default_ttl)
                except Exception as e:
                    Logger.warning(f"Redis cache set failed: {e}")

            latency = (time.time() - start) * 1000
            self._audit(provider, True, False, latency)
            return embedding

        except Exception as e:
            latency = (time.time() - start) * 1000
            self._audit(provider, False, False, latency)
            Logger.error(f"Embedding failed: {e}")
            raise

    async def get_embeddings_batch(
        self, contents: list[str], provider: EmbeddingProvider = "gemini", use_cache: bool = True
    ) -> list[list[float]]:
        """
        Get embeddings for multiple contents.
        [PHASE 4] Batch processing with caching.
        """
        results = []
        for content in contents:
            # Sequential processing to ensure consistent caching logic and error handling
            # Future optimization: Use provider batch APIs where available
            embedding = await self.get_embedding(content, provider, use_cache)
            results.append(embedding)
        return results

    async def _get_gemini_embedding(self, content: str) -> list[float]:
        """Get embedding from Gemini."""
        import google.generativeai as genai

        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY missing")

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # 'retrieval_document' is generally preferred for storage
        result = genai.embed_content(
            model="models/text-embedding-004", content=content, task_type="retrieval_document"
        )
        return result["embedding"]

    async def _get_openai_embedding(self, content: str) -> list[float]:
        """Get embedding from OpenAI."""
        import openai

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY missing")

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(model="text-embedding-3-small", input=content)
        return response.data[0].embedding

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """
        L2 Execution Agent - Embedding Gateway Healing.

        WIRED CAPABILITIES:
        - Validates embedding provider configurations
        - Checks Redis cache connectivity
        - Verifies API key availability
        """
        if _call_path is None:
            _call_path = set()

        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}

        _call_path.add(agent_name)
        metrics = {"violations": 0, "fixed": 0, "errors": 0, "skipped": 0}

        try:
            # Validate embedding providers
            if not os.getenv("GOOGLE_API_KEY"):
                metrics["violations"] += 1
                Logger.warning("GOOGLE_API_KEY missing for Gemini embeddings")

            if not os.getenv("OPENAI_API_KEY"):
                metrics["violations"] += 1
                Logger.warning("OPENAI_API_KEY missing for OpenAI embeddings")

            # Test Redis cache connectivity
            try:
                test_key = f"{self._cache_prefix}:test"
                if hasattr(self, "cache_set") and hasattr(self, "cache_get"):
                    self.cache_set(test_key, "test_value", ttl=60)
                    cached = self.cache_get(test_key)
                    if cached != "test_value":
                        metrics["violations"] += 1
                        Logger.warning("Redis cache test failed")
                else:
                    metrics["violations"] += 1
                    Logger.warning("Redis cache methods not available")
            except Exception as e:
                metrics["violations"] += 1
                Logger.warning(f"Redis cache connectivity test failed: {e}")

            # Validate expected dimensions
            try:
                expected_dims = self.EXPECTED_DIMENSIONS
                if not expected_dims or not isinstance(expected_dims, dict):
                    metrics["violations"] += 1
                    Logger.warning("Expected dimensions configuration invalid")
            except Exception as e:
                metrics["violations"] += 1
                Logger.warning(f"Dimensions validation failed: {e}")

            if metrics["violations"] == 0:
                metrics["fixed"] = 1
                Logger.info("EmbeddingSovereignAgent validation passed")

        except Exception as e:
            Logger.error(f"EmbeddingSovereignAgent healing failed: {e}")
            metrics["errors"] += 1
        finally:
            _call_path.discard(agent_name)

        return metrics

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by EmbeddingSovereignAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")

        # Default implementation - EmbeddingSovereignAgent handles embeddings
        try:
            return {
                "status": "skipped",
                "details": f"EmbeddingSovereignAgent heal() not yet implemented for {violation_type} - embedding violations require manual review",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"EmbeddingSovereignAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


# Singleton accessor
def get_embedding_gateway() -> EmbeddingSovereignAgent:
    """Get or create the global embedding gateway."""
    return EmbeddingSovereignAgent()
