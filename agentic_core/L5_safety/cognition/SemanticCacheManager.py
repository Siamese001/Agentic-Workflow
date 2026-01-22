from __future__ import annotations
"""
[PHASE 17] Semantic Cache Manager - The "Meta-Learning" Brain.

Prevents repetitive LLM calls by storing architectural decisions in:
1. Redis: O(1) exact match lookup (hashing)
2. Pinecone: Semantic similarity lookup (embeddings)

This dramatically reduces token consumption by reusing decisions for similar files.

[SSOT] Integrates with TieredBatchProcessor for intelligent caching.
"""

import hashlib
import json
import logging
import os
import threading
from typing import Any

Logger = logging.getLogger(__name__)


class SemanticCacheManager:
    """
    Dual-layer semantic cache for architectural decisions.
    
    Layer 1 (Redis): Exact content hash matching - O(1) lookup
    Layer 2 (Pinecone): Semantic similarity matching - vector search
    
    Attributes:
        redis_enabled: Whether Redis is available
        pinecone_enabled: Whether Pinecone is available
        similarity_threshold: Minimum score for semantic match (default: 0.95)
    """

    def __init__(
        self,
        api_key: str | None = None,
        similarity_threshold: float = 0.95,
    ):
        """
        Initialize the Semantic Cache Manager.
        
        Args:
            api_key: API key for embedding generation
            similarity_threshold: Minimum similarity score for semantic match
        """
        self.api_key = api_key
        self.similarity_threshold = similarity_threshold

        # Thread safety lock for concurrent access
        self._lock = threading.RLock()

        # Layer 1: Redis (Exact Cache)
        self.redis_client = None
        self.redis_enabled = False
        self._init_redis()

        # Layer 2: Pinecone (Semantic Cache)
        self.pinecone_index = None
        self.pinecone_enabled = False
        self._init_pinecone()

        # Embedding client (lazy-loaded)
        self._embedding_client = None

        # Statistics
        self.stats = {
            "redis_hits": 0,
            "pinecone_hits": 0,
            "cache_misses": 0,
            "cache_stores": 0,
        }

        Logger.info(f"[SEMANTIC] Cache initialized (Redis: {self.redis_enabled}, Pinecone: {self.pinecone_enabled})")

    def _init_redis(self) -> None:
        """Initialize Redis connection for exact matching."""
        try:
            import redis
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.redis_enabled = True
            Logger.info("[SEMANTIC] Redis connected for exact caching")
        except ImportError:
            Logger.debug("[SEMANTIC] redis package not installed")
        except Exception as e:
            Logger.warning(f"[SEMANTIC] Redis unavailable: {e}")

    def _init_pinecone(self) -> None:
        """Initialize Pinecone connection for semantic matching."""
        pinecone_key = os.environ.get("PINECONE_API_KEY")
        if not pinecone_key:
            Logger.debug("[SEMANTIC] PINECONE_API_KEY not set")
            return

        try:
            from pinecone import Pinecone, ServerlessSpec

            pc = Pinecone(api_key=pinecone_key)
            index_name = "architectural-decisions"

            # Check if index exists
            existing_indexes = [idx.name for idx in pc.list_indexes()]

            if index_name not in existing_indexes:
                Logger.info(f"[SEMANTIC] Creating Pinecone index: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=768,  # text-embedding-004 dimension
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )

            self.pinecone_index = pc.Index(index_name)
            self.pinecone_enabled = True
            Logger.info("[SEMANTIC] Pinecone connected for semantic caching")

        except ImportError:
            Logger.debug("[SEMANTIC] pinecone package not installed")
        except Exception as e:
            Logger.warning(f"[SEMANTIC] Pinecone unavailable: {e}")

    def _get_embedding_client(self):
        """Lazy-load the embedding client (thread-safe)."""
        with self._lock:
            if self._embedding_client is None and self.api_key:
                try:
                    from google import genai
                    self._embedding_client = genai.Client(api_key=self.api_key)
                    Logger.debug("[SEMANTIC] Embedding client initialized")
                except Exception as e:
                    Logger.warning(f"[SEMANTIC] Embedding client failed: {e}")
        return self._embedding_client

    def _compute_hash(self, content: str, violation_type: str) -> str:
        """Compute SHA256 hash for exact matching."""
        key = f"{violation_type}:{content}"
        return hashlib.sha256(key.encode()).hexdigest()

    def _get_embedding(self, text: str) -> list[float] | None:
        """
        Generate embedding vector for semantic matching.
        
        Args:
            text: Text to embed (truncated to 2000 chars)
        
        Returns:
            List of floats representing the embedding vector
        """
        client = self._get_embedding_client()
        if not client:
            return None

        try:
            # Truncate to avoid token limits
            truncated = text[:2000]

            result = client.models.embed_content(
                model="text-embedding-004",
                contents=truncated,
            )

            return result.embeddings[0].values

        except Exception as e:
            Logger.debug(f"[SEMANTIC] Embedding failed: {e}")
            return None

    def get_cached_decision(
        self,
        content_snippet: str,
        violation_type: str,
    ) -> dict[str, Any] | None:
        """
        Check caches in tiered order: Exact -> Semantic.
        
        Args:
            content_snippet: File content or snippet
            violation_type: Type of violation (ORPHAN, GRAVITY, etc.)
        
        Returns:
            Cached decision dict or None if not found
        """
        content_hash = self._compute_hash(content_snippet, violation_type)

        # Layer 1: Exact Match (Redis)
        if self.redis_enabled:
            try:
                cached_json = self.redis_client.get(f"decision:{content_hash}")
                if cached_json:
                    Logger.info("  [CACHE] Hit (Exact - Redis)")
                    with self._lock:
                        self.stats["redis_hits"] += 1
                    return json.loads(cached_json)
            except Exception as e:
                Logger.debug(f"[SEMANTIC] Redis get failed: {e}")

        # Layer 2: Semantic Match (Pinecone)
        if self.pinecone_enabled:
            vector = self._get_embedding(content_snippet)
            if vector:
                try:
                    results = self.pinecone_index.query(
                        vector=vector,
                        top_k=1,
                        include_metadata=True,
                        filter={"violation_type": violation_type},
                    )

                    if results.matches and results.matches[0].score >= self.similarity_threshold:
                        score = results.matches[0].score
                        Logger.info(f"  [CACHE] Hit (Semantic - Pinecone: {score:.2f})")
                        with self._lock:
                            self.stats["pinecone_hits"] += 1
                        return json.loads(results.matches[0].metadata["decision_json"])

                except Exception as e:
                    Logger.debug(f"[SEMANTIC] Pinecone query failed: {e}")

        with self._lock:
            self.stats["cache_misses"] += 1
        return None

    def cache_decision(
        self,
        content_snippet: str,
        violation_type: str,
        decision: dict[str, Any],
    ) -> None:
        """
        Store decision in both caches for future meta-learning.
        
        Args:
            content_snippet: File content or snippet
            violation_type: Type of violation
            decision: Decision dict with action, target_path, reason, confidence
        """
        content_hash = self._compute_hash(content_snippet, violation_type)
        decision_json = json.dumps(decision)

        # Layer 1: Store in Redis (7-day TTL)
        if self.redis_enabled:
            try:
                self.redis_client.setex(
                    f"decision:{content_hash}",
                    86400 * 7,  # 7 days
                    decision_json,
                )
            except Exception as e:
                Logger.debug(f"[SEMANTIC] Redis set failed: {e}")

        # Layer 2: Store in Pinecone
        if self.pinecone_enabled:
            vector = self._get_embedding(content_snippet)
            if vector:
                try:
                    self.pinecone_index.upsert(vectors=[{
                        "id": content_hash,
                        "values": vector,
                        "metadata": {
                            "violation_type": violation_type,
                            "decision_json": decision_json,
                        },
                    }])
                except Exception as e:
                    Logger.debug(f"[SEMANTIC] Pinecone upsert failed: {e}")

        with self._lock:
            self.stats["cache_stores"] += 1

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_hits = self.stats["redis_hits"] + self.stats["pinecone_hits"]
        total_lookups = total_hits + self.stats["cache_misses"]

        return {
            **self.stats,
            "total_hits": total_hits,
            "total_lookups": total_lookups,
            "hit_rate": total_hits / total_lookups if total_lookups > 0 else 0.0,
        }

    def clear_cache(self) -> None:
        """Clear all cached decisions."""
        if self.redis_enabled:
            try:
                # Clear only decision keys
                keys = self.redis_client.keys("decision:*")
                if keys:
                    self.redis_client.delete(*keys)
                Logger.info("[SEMANTIC] Redis cache cleared")
            except Exception as e:
                Logger.warning(f"[SEMANTIC] Redis clear failed: {e}")

        # Note: Pinecone clearing requires index deletion/recreation
        # which is expensive, so we skip it for now

        self.stats = {
            "redis_hits": 0,
            "pinecone_hits": 0,
            "cache_misses": 0,
            "cache_stores": 0,
        }
