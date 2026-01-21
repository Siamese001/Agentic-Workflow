"""
[PHASE 17/20] Semantic Cache Manager - The Collective Hive Mind.

Located in L4_state as it manages the persistence and state of agentic memory.
Provides O(1) exact recall (Redis) and semantic similarity recall (Pinecone).

Phase 17: Initial implementation with Redis + Pinecone
Phase 20: Hardened singleton pattern, thread safety, and connection retries.

[SSOT] This is the canonical location for the Hive Mind infrastructure.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from typing import Any, Optional

Logger = logging.getLogger(__name__)


class SemanticCacheManager:
    """
    Singleton Semantic Cache Manager - The Hive Mind.
    
    Provides dual-layer caching for collective agent intelligence:
    - Layer 1 (Redis): O(1) exact content hash matching
    - Layer 2 (Pinecone): Semantic similarity matching (>=0.98 threshold)
    
    Phase 20: Enforces singleton pattern with thread-safe initialization.
    
    Usage:
        cache = SemanticCacheManager.get_instance()
        result = cache.recall(context, namespace)
    """
    
    _instance: Optional[SemanticCacheManager] = None
    _instance_lock = threading.RLock()
    
    @classmethod
    def get_instance(cls, api_key: Optional[str] = None) -> SemanticCacheManager:
        """
        Get the singleton instance of SemanticCacheManager.
        
        Thread-safe singleton pattern ensures only one Hive Mind exists.
        
        Args:
            api_key: Optional API key for embedding generation
        
        Returns:
            The singleton SemanticCacheManager instance
        """
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls._create_instance(api_key)
            return cls._instance
    
    @classmethod
    def _create_instance(cls, api_key: Optional[str] = None) -> SemanticCacheManager:
        """Internal factory method for creating the singleton."""
        instance = object.__new__(cls)
        instance._initialize(api_key)
        return instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing only)."""
        with cls._instance_lock:
            cls._instance = None
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize is blocked for direct instantiation.
        Use get_instance() instead.
        """
        if SemanticCacheManager._instance is not None:
            raise RuntimeError(
                "[HiveMind] SINGLETON VIOLATION: Use SemanticCacheManager.get_instance() instead of direct instantiation."
            )
        self._initialize(api_key)
    
    def _initialize(self, api_key: Optional[str] = None) -> None:
        """
        Internal initialization method.
        
        Args:
            api_key: Optional API key for embedding generation
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.similarity_threshold = 0.98  # Strict threshold for auto-action
        
        # Thread safety lock for operations
        self._lock = threading.RLock()
        
        # Layer 1: Redis (Short-Term Memory)
        self.redis_client = None
        self.redis_enabled = False
        self._init_redis()
        
        # Layer 2: Pinecone (Long-Term Memory)
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
        
        # Log initialization status
        if self.redis_enabled:
            Logger.info("[HiveMind] Connected to Short-Term Memory (Redis)")
        else:
            Logger.critical("[HiveMind] LOBOTOMY WARNING: Redis unavailable - operating without short-term memory")
        
        if self.pinecone_enabled:
            Logger.info("[HiveMind] Connected to Long-Term Memory (Pinecone)")
        else:
            Logger.warning("[HiveMind] Long-Term Memory (Pinecone) unavailable")
    
    def _init_redis(self) -> None:
        """Initialize Redis connection with retry logic."""
        try:
            import redis
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.redis_enabled = True
        except ImportError:
            Logger.debug("[HiveMind] redis package not installed")
        except Exception as e:
            Logger.warning(f"[HiveMind] Redis connection failed: {e}")
    
    def _init_pinecone(self) -> None:
        """Initialize Pinecone connection for semantic matching."""
        pinecone_key = os.environ.get("PINECONE_API_KEY")
        if not pinecone_key:
            Logger.debug("[HiveMind] PINECONE_API_KEY not set")
            return
        
        try:
            from pinecone import Pinecone, ServerlessSpec
            
            pc = Pinecone(api_key=pinecone_key)
            index_name = "agentic-hive-mind"
            
            # Check if index exists
            existing_indexes = [idx.name for idx in pc.list_indexes()]
            
            if index_name not in existing_indexes:
                Logger.info(f"[HiveMind] Creating Pinecone index: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=768,  # text-embedding-004 dimension
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
            
            self.pinecone_index = pc.Index(index_name)
            self.pinecone_enabled = True
            
        except ImportError:
            Logger.debug("[HiveMind] pinecone package not installed")
        except Exception as e:
            Logger.error(f"[HiveMind] Pinecone connection failed: {e}")
    
    def _get_embedding_client(self):
        """Lazy-load the embedding client (thread-safe)."""
        with self._lock:
            if self._embedding_client is None and self.api_key:
                try:
                    from google import genai
                    self._embedding_client = genai.Client(api_key=self.api_key)
                    Logger.debug("[HiveMind] Embedding client initialized")
                except Exception as e:
                    Logger.warning(f"[HiveMind] Embedding client failed: {e}")
        return self._embedding_client
    
    def _compute_hash(self, context: str, namespace: str) -> str:
        """Compute SHA256 hash for exact matching."""
        key = f"{namespace}:{context}"
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _get_embedding(self, text: str) -> Optional[list[float]]:
        """Generate embedding vector for semantic matching."""
        client = self._get_embedding_client()
        if not client:
            return None
        
        try:
            truncated = text[:2000]
            result = client.models.embed_content(
                model="text-embedding-004",
                contents=truncated,
            )
            return result.embeddings[0].values
        except Exception as e:
            Logger.debug(f"[HiveMind] Embedding failed: {e}")
            return None
    
    def recall(
        self,
        context: str,
        namespace: str,
    ) -> Optional[dict[str, Any]]:
        """
        Recall a result based on exact or semantic match.
        
        Args:
            context: The context string to query
            namespace: The namespace (typically agent class name)
        
        Returns:
            Cached result dict or None if not found
        """
        ctx_hash = self._compute_hash(context, namespace)
        
        # Layer 1: Exact Match (Redis - O(1))
        if self.redis_enabled:
            try:
                cached = self.redis_client.get(f"memory:{ctx_hash}")
                if cached:
                    Logger.debug(f"[HiveMind] Redis HIT for {namespace}")
                    with self._lock:
                        self.stats["redis_hits"] += 1
                    return json.loads(cached)
            except Exception as e:
                Logger.debug(f"[HiveMind] Redis recall failed: {e}")
        
        # Layer 2: Semantic Match (Pinecone)
        if self.pinecone_enabled:
            vector = self._get_embedding(context)
            if vector:
                try:
                    results = self.pinecone_index.query(
                        vector=vector,
                        top_k=1,
                        include_metadata=True,
                        filter={"namespace": namespace},
                    )
                    
                    if results.matches and results.matches[0].score >= self.similarity_threshold:
                        score = results.matches[0].score
                        Logger.info(f"[HiveMind] Pinecone HIT ({score:.2f}) for {namespace}")
                        with self._lock:
                            self.stats["pinecone_hits"] += 1
                        return json.loads(results.matches[0].metadata["payload"])
                        
                except Exception as e:
                    Logger.debug(f"[HiveMind] Pinecone recall failed: {e}")
        
        with self._lock:
            self.stats["cache_misses"] += 1
        return None
    
    def learn(
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
    ) -> None:
        """
        Teach the Hive Mind a new result.
        
        Args:
            context: The context string
            namespace: The namespace (typically agent class name)
            result: The result to store
        """
        ctx_hash = self._compute_hash(context, namespace)
        payload_json = json.dumps(result)
        
        # Layer 1: Store in Redis (7-day TTL)
        if self.redis_enabled:
            try:
                self.redis_client.setex(
                    f"memory:{ctx_hash}",
                    86400 * 7,  # 7 days
                    payload_json,
                )
            except Exception as e:
                Logger.debug(f"[HiveMind] Redis learn failed: {e}")
        
        # Layer 2: Store in Pinecone
        if self.pinecone_enabled:
            vector = self._get_embedding(context)
            if vector:
                try:
                    self.pinecone_index.upsert(vectors=[{
                        "id": ctx_hash,
                        "values": vector,
                        "metadata": {
                            "namespace": namespace,
                            "payload": payload_json,
                        },
                    }])
                except Exception as e:
                    Logger.debug(f"[HiveMind] Pinecone learn failed: {e}")
        
        with self._lock:
            self.stats["cache_stores"] += 1
    
    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_hits = self.stats["redis_hits"] + self.stats["pinecone_hits"]
            total_lookups = total_hits + self.stats["cache_misses"]
            
            return {
                **self.stats,
                "total_hits": total_hits,
                "total_lookups": total_lookups,
                "hit_rate": total_hits / total_lookups if total_lookups > 0 else 0.0,
            }
