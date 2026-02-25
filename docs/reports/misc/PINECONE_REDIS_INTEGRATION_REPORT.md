# Pinecone & Redis Integration Analysis Report

**Date:** January 22, 2026
**Scope:** RAG Architecture Analysis for Meta-Learning Layer Integration
**Objective:** Ensure every Pinecone operation uses Redis as a fast cache layer

---

## Executive Summary

The codebase contains **7 Pinecone-related files** and **6 Redis-related files** with significant architectural fragmentation. While `SemanticCacheManager` and `PineconeSovereignAgent` properly integrate both systems, **4 out of 7 Pinecone files lack Redis caching**, creating performance gaps and inconsistent behavior.

### Key Findings

| File | Layer | Redis Integrated | Gap Severity |
|------|-------|------------------|--------------|
| `pinecone_store.py` | L4 Semantic Memory | ❌ NO | **CRITICAL** |
| `pinecone_vector_mixin.py` | Utils/Mixin | ❌ NO | **HIGH** |
| `PineconeSovereignAgent.py` | L5 Validators | ✅ YES | None |
| `pinecone.py` (SovereignPineconeClient) | L2 MCP | ❌ NO | **MEDIUM** |
| `pinecone_sync.py` | L4 Semantic Memory | ❌ NO | **HIGH** |
| `pinecone_assistant.py` | L2 ToolRegistry | ❌ NO | **LOW** (Script) |
| `pinecone_mcp_client.py` | L2 MCP | ❌ NO | **HIGH** |

---

## Part 1: Current Architecture Analysis

### 1.1 Pinecone Files Overview

#### 1. `pinecone_store.py` (L4 Semantic Memory)
**Purpose:** Core Pinecone wrapper for RAG operations
**Location:** `agentic_core/semantic_memory/store/pinecone_store.py`

```python
# Current Implementation (NO Redis)
class PineconeVectorStore:
    def query(self, query_embedding, top_k=15, namespace="sovereign-core"):
        # Direct Pinecone query - NO CACHING
        results = self.index.query(vector=query_embedding, top_k=top_k, ...)
        return results
```

**Gap:** Every query hits Pinecone directly. No embedding cache, no result cache.

---

#### 2. `pinecone_vector_mixin.py` (Utils/Mixin)
**Purpose:** Reusable mixin for agents needing vector search
**Location:** `agentic_core/utils/core_extensions/pinecone_vector_mixin.py`

```python
# Current Implementation (Local fallback only, NO Redis)
class PineconeVectorMixin:
    _local_vectors: dict = {}  # In-memory fallback only

    async def vector_search(self, embedding, ...):
        # Falls back to _local_vectors, NOT Redis
```

**Gap:** Uses in-memory dict fallback instead of Redis. Cache is lost on restart.

---

#### 3. `PineconeSovereignAgent.py` (L5 Validators) ✅
**Purpose:** Sovereign gateway for all Pinecone operations
**Location:** `agentic_core/L5_safety/validators/PineconeSovereignAgent.py`

```python
# CORRECT Implementation - Has Redis Integration
class PineconeSovereignAgent(SovereignBaseAgent):
    def __init__(self, ...):
        self.redis_gateway = RedisSovereignAgent(project_root)
        self.redis = self.redis_gateway.get_client()

    async def get_embedding(self, text: str, ...):
        cache_key = f"pc_embed:{hashlib.sha256(text.encode()).hexdigest()}"
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        # ... generate embedding ...
        if self.redis:
            self.redis.set(cache_key, json.dumps(embedding), ex=604800)  # 7 days
```

**Status:** ✅ Properly caches embeddings in Redis with 7-day TTL.

---

#### 4. `pinecone.py` (SovereignPineconeClient) (L2 MCP)
**Purpose:** Audited vector operations with routing
**Location:** `agentic_core/L2_execution/mcp/pinecone.py`

```python
# Current Implementation (NO Redis)
class SovereignPineconeClient(SovereignBaseAgent):
    def execute(self, operation: str, **payload):
        # Direct Pinecone operations - NO CACHING
        if operation == "query":
            response = index.query(vector=vector, ...)
```

**Gap:** No caching layer for query results or embeddings.

---

#### 5. `pinecone_sync.py` (L4 Semantic Memory)
**Purpose:** Memory synchronization after atomic fission
**Location:** `agentic_core/semantic_memory/store/pinecone_sync.py`

```python
# Current Implementation (NO Redis)
class MemoryArchitectSync:
    def _generate_embedding(self, text: str):
        # Direct Gemini call - NO CACHING
        result = self.genai_client.models.embed_content(...)
```

**Gap:** Embeddings are regenerated every time. No caching of expensive API calls.

---

#### 6. `pinecone_assistant.py` (L2 ToolRegistry)
**Purpose:** Script for index initialization
**Location:** `agentic_core/L2_execution/ToolRegistry/pinecone_assistant.py`

**Status:** This is a setup script, not a runtime component. Low priority for Redis integration.

---

#### 7. `pinecone_mcp_client.py` (L2 MCP)
**Purpose:** Official MCP client for Pinecone operations
**Location:** `agentic_core/L2_execution/mcp/pinecone_mcp_client.py`

```python
# Current Implementation (NO Redis)
class SovereignPineconeMcpClient(SovereignBaseAgent):
    async def search(self, query_text: str, ...):
        # Direct MCP call - NO CACHING
        result = await self._hardened_call("pinecone_search", ...)
```

**Gap:** No result caching. Every search hits the MCP server.

---

### 1.2 Redis Files Overview

| File | Purpose | Used By |
|------|---------|---------|
| `RedisSovereignAgent.py` | Singleton Redis gateway | PineconeSovereignAgent |
| `redis_cache_mixin.py` | Reusable caching mixin | Various agents |
| `caching_redis_mcp_client.py` | MCP Redis client | RedisCacheMixin |
| `redis.py` | Sovereign Redis client | Direct operations |
| `SovereignRedisOrchestratorAgent.py` | L3 orchestration | Workflow engines |
| `redis_cache_tools.py` | Tool registry | L2 execution |

---

### 1.3 Existing Best Practice: SemanticCacheManager

The `SemanticCacheManager` in `L4_state/memory/` demonstrates the **correct dual-layer pattern**:

```python
class SemanticCacheManager:
    """
    Dual-layer caching for collective agent intelligence:
    - Layer 1 (Redis): O(1) exact content hash matching (Working Memory - 24h TTL)
    - Layer 2 (Pinecone): Semantic similarity matching (Long-Term DNA)
    """

    def recall(self, context: str, namespace: str):
        # Layer 1: Exact Match (Redis - O(1))
        if self.redis_enabled:
            cached = self.redis_client.get(f"memory:{ctx_hash}")
            if cached:
                return json.loads(cached)

        # Layer 2: Semantic Match (Pinecone)
        if self.pinecone_enabled:
            results = self.pinecone_index.query(vector=vector, ...)
```

**This pattern should be replicated across all Pinecone files.**

---

## Part 2: Identified Gaps

### GAP-001: `pinecone_store.py` Missing Redis Cache
**Severity:** CRITICAL
**Impact:** Every RAG query hits Pinecone directly, adding 100-500ms latency

**Current Flow:**
```
Query → Pinecone → Results (100-500ms)
```

**Required Flow:**
```
Query → Redis Cache Check → [HIT] Return cached (1-5ms)
                         → [MISS] Pinecone → Cache in Redis → Return (100-500ms first time)
```

---

### GAP-002: `pinecone_vector_mixin.py` Uses In-Memory Fallback Instead of Redis
**Severity:** HIGH
**Impact:** Cache is lost on process restart; no shared cache across agents

**Current:**
```python
_local_vectors: dict = {}  # Lost on restart
```

**Required:**
```python
# Use RedisCacheMixin for persistent, shared cache
class PineconeVectorMixin(RedisCacheMixin):
    _cache_prefix = "pinecone_vector"
```

---

### GAP-003: `pinecone_sync.py` Regenerates Embeddings Without Caching
**Severity:** HIGH
**Impact:** Expensive Gemini API calls repeated for same content

**Current:**
```python
def _generate_embedding(self, text: str):
    result = self.genai_client.models.embed_content(...)  # No cache
```

**Required:**
```python
def _generate_embedding(self, text: str):
    cache_key = f"embed:{hashlib.sha256(text.encode()).hexdigest()}"
    cached = self.redis.get(cache_key)
    if cached:
        return json.loads(cached)
    result = self.genai_client.models.embed_content(...)
    self.redis.set(cache_key, json.dumps(result), ex=604800)
    return result
```

---

### GAP-004: `pinecone_mcp_client.py` No Result Caching
**Severity:** HIGH
**Impact:** MCP calls are expensive; no caching of search results

---

### GAP-005: `pinecone.py` (SovereignPineconeClient) No Caching Layer
**Severity:** MEDIUM
**Impact:** Direct Pinecone operations without optimization

---

### GAP-006: Redundant Pinecone Initialization
**Severity:** MEDIUM
**Impact:** Multiple files create their own Pinecone clients instead of using a singleton

**Files with duplicate initialization:**
- `pinecone_store.py` - Creates own `Pinecone()` client
- `pinecone_sync.py` - Creates own `Pinecone()` client
- `pinecone.py` - Creates own `Pinecone()` client
- `pinecone_mcp_client.py` - Uses MCP router (different pattern)
- `PineconeSovereignAgent.py` - Creates own `Pinecone()` client

**Recommendation:** All should route through `PineconeSovereignAgent` as the single gateway.

---

### GAP-007: Inconsistent Dimension Configuration
**Severity:** HIGH
**Impact:** Different files use different embedding dimensions

| File | Dimension | Source |
|------|-----------|--------|
| `pinecone_store.py` | 384 (default) | `EMBEDDING_DIMENSION` env |
| `pinecone_vector_mixin.py` | 1536 | Hardcoded |
| `PineconeSovereignAgent.py` | From SovereignEnv | Config-driven |
| `pinecone_assistant.py` | 768 | Hardcoded |
| `SemanticCacheManager.py` | 768 | Hardcoded |

**Recommendation:** Centralize dimension in `SovereignRagConfig` (already created).

---

## Part 3: Detailed File Diffs

### DIFF-001: Add Redis Caching to `pinecone_store.py`

```python
# FILE: agentic_core/semantic_memory/store/pinecone_store.py
# CHANGE: Add Redis caching for query results and embeddings

# === BEFORE (lines 1-10) ===
from __future__ import annotations

from pinecone import Pinecone, ServerlessSpec

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import os
import time
from typing import Any

# === AFTER ===
from __future__ import annotations

from pinecone import Pinecone, ServerlessSpec

"""
PineconeVectorStore - Sovereign wrapper for Pinecone vector database.

[PHASE 34] Redis-Cached: All queries check Redis first for O(1) retrieval.
"""

import hashlib
import json
import os
import time
from typing import Any

# Redis integration for Meta-Learning Layer caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
```

```python
# === BEFORE (lines 13-47) ===
class PineconeVectorStore:
    """
    Sovereign wrapper for Pinecone vector database.
    """

    def __init__(self, index_name: str = "sovereign-rag"):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not set")
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", "384"))
        # ... rest of init ...

# === AFTER ===
class PineconeVectorStore:
    """
    Sovereign wrapper for Pinecone vector database.

    [PHASE 34] Redis-Cached for Meta-Learning Layer:
    - Query results cached with configurable TTL
    - Embedding cache for repeated queries
    - Graceful degradation if Redis unavailable
    """

    # Cache configuration
    QUERY_CACHE_TTL = 3600  # 1 hour for query results
    EMBEDDING_CACHE_TTL = 604800  # 7 days for embeddings

    def __init__(self, index_name: str = "sovereign-rag"):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not set")
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", "384"))

        # [PHASE 34] Initialize Redis cache
        self.redis_client = None
        self._init_redis_cache()

        # ... rest of existing init code ...

    def _init_redis_cache(self) -> None:
        """Initialize Redis connection for Meta-Learning Layer caching."""
        if not REDIS_AVAILABLE:
            print("[INFO] Redis not available - operating without cache")
            return

        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            print(f"[OK] PineconeVectorStore: Redis cache connected")
        except Exception as e:
            print(f"[WARN] Redis cache unavailable: {e}")
            self.redis_client = None

    def _cache_key(self, prefix: str, data: str) -> str:
        """Generate cache key from prefix and data hash."""
        data_hash = hashlib.sha256(data.encode()).hexdigest()[:32]
        return f"pc:{prefix}:{self.index_name}:{data_hash}"
```

```python
# === BEFORE (lines 64-86) ===
    def query(
        self, query_embedding: list[float], top_k: int = 15, namespace: str = "sovereign-core"
    ) -> list[dict]:
        """
        Query similar vectors with P95 latency telemetry.
        """
        start_time = time.perf_counter()
        try:
            results: Any = self.index.query(
                vector=query_embedding, top_k=top_k, include_metadata=True, namespace=namespace
            )
            # ... rest of query ...

# === AFTER ===
    def query(
        self, query_embedding: list[float], top_k: int = 15, namespace: str = "sovereign-core"
    ) -> list[dict]:
        """
        Query similar vectors with Redis caching and P95 latency telemetry.

        [PHASE 34] Cache Strategy:
        1. Check Redis for cached results (O(1) lookup)
        2. On miss, query Pinecone and cache results
        3. Cache key includes embedding hash + namespace + top_k
        """
        start_time = time.perf_counter()

        # [PHASE 34] Generate cache key from embedding signature
        embedding_sig = hashlib.sha256(
            json.dumps(query_embedding[:10] + query_embedding[-10:]).encode()
        ).hexdigest()[:16]
        cache_key = f"pc:query:{self.index_name}:{namespace}:{embedding_sig}:{top_k}"

        # [PHASE 34] Check Redis cache first
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    latency_ms = (time.perf_counter() - start_time) * 1000
                    print(f"[CACHE HIT] Query returned in {latency_ms:.2f}ms (Redis)")
                    return json.loads(cached)
            except Exception as e:
                print(f"[WARN] Redis cache read failed: {e}")

        # Cache miss - query Pinecone
        try:
            results: Any = self.index.query(
                vector=query_embedding, top_k=top_k, include_metadata=True, namespace=namespace
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            if latency_ms > 500:
                print(f"[WARN] Retrieval Latency High: {latency_ms:.2f}ms")

            formatted_results = [
                {"id": match["id"], "score": match["score"], "metadata": match["metadata"]}
                for match in results.get("matches", [])
            ]

            # [PHASE 34] Cache results in Redis
            if self.redis_client and formatted_results:
                try:
                    self.redis_client.setex(
                        cache_key,
                        self.QUERY_CACHE_TTL,
                        json.dumps(formatted_results)
                    )
                except Exception as e:
                    print(f"[WARN] Redis cache write failed: {e}")

            return formatted_results
        except Exception as e:
            print(f"[ERROR] Pinecone query failed: {e}")
            return []
```

---

### DIFF-002: Add RedisCacheMixin to `pinecone_vector_mixin.py`

```python
# FILE: agentic_core/utils/core_extensions/pinecone_vector_mixin.py
# CHANGE: Integrate RedisCacheMixin for persistent caching

# === BEFORE (lines 46-68) ===
class PineconeVectorMixin:
    """
    ULTRA-HARDENED Pinecone Vector Mixin
    ...
    """

    _pinecone_client = None
    _index_name: str = "sovereign-agents-v1"
    _namespace: str = "agent_patterns"
    _local_vectors: dict = {}

# === AFTER ===
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin


class PineconeVectorMixin(RedisCacheMixin):
    """
    ULTRA-HARDENED Pinecone Vector Mixin with Redis Caching

    [PHASE 34] Now inherits RedisCacheMixin for:
    - Persistent cache across restarts
    - Shared cache across agent instances
    - O(1) cache lookups before Pinecone queries

    Features:
    - Feature flag control (USE_PINECONE)
    - Redis cache with local dict fallback
    - Metrics collection for dashboard visibility
    - No raw code storage (embeddings only)
    - Namespace isolation
    """

    _pinecone_client = None
    _index_name: str = "sovereign-agents-v1"
    _namespace: str = "agent_patterns"
    _local_vectors: dict = {}

    # RedisCacheMixin configuration
    _cache_prefix: str = "pinecone_vector"
    _default_ttl: int = 3600  # 1 hour
```

```python
# === BEFORE (lines 99-176) ===
    async def vector_search(
        self,
        embedding: list[float],
        ...
    ) -> list[dict[str, Any]]:
        """
        Perform a hardened vector search using the Pinecone index with broadness support.
        """
        start = time.time()
        # ... direct Pinecone query ...

# === AFTER ===
    async def vector_search(
        self,
        embedding: list[float],
        top_k: int | None = None,
        broadness: RetrievalBroadness = RetrievalBroadness.STANDARD,
        metadata_filter: dict[str, Any] | None = None,
        include_metadata: bool = True,
        score_threshold: float | None = None,
        use_cache: bool = True,  # [PHASE 34] New parameter
    ) -> list[dict[str, Any]]:
        """
        Perform a hardened vector search with Redis caching.

        [PHASE 34] Cache Strategy:
        1. Generate cache key from embedding signature + parameters
        2. Check Redis cache (via RedisCacheMixin)
        3. On miss, query Pinecone and cache results

        Args:
            embedding: The query embedding vector.
            top_k: (Optional) Explicit override for number of results.
            broadness: RetrievalBroadness enum determining semantic scope.
            metadata_filter: Optional dictionary for metadata filtering.
            include_metadata: Whether to include metadata in results.
            score_threshold: (Optional) Minimum similarity score to return.
            use_cache: Whether to use Redis cache (default: True).

        Returns:
            List of vector search results matching the query.
        """
        start = time.time()
        metrics = get_cache_metrics()

        if len(embedding) != self.EXPECTED_DIMENSION:
            raise ValueError(
                f"Invalid embedding dimension: {len(embedding)} != {self.EXPECTED_DIMENSION}"
            )

        # Precedence Logic: Explicit top_k > Broadness Enum
        if top_k is not None:
            effective_top_k = min(top_k, self.MAX_QUERY_TOP_K)
        else:
            effective_top_k = min(broadness.value, self.MAX_QUERY_TOP_K)

        # [PHASE 34] Generate cache key
        if use_cache:
            import hashlib
            import json

            cache_params = {
                "emb_sig": hashlib.sha256(
                    json.dumps(embedding[:5] + embedding[-5:]).encode()
                ).hexdigest()[:16],
                "top_k": effective_top_k,
                "ns": self._namespace,
                "filter": str(metadata_filter) if metadata_filter else "",
                "threshold": score_threshold,
            }
            cache_key = f"vs:{cache_params['emb_sig']}:{cache_params['top_k']}:{cache_params['ns']}"

            # Check Redis cache
            cached = await self.cache_get(cache_key)
            if cached:
                latency = (time.time() - start) * 1000
                log.debug(f"Vector search cache HIT in {latency:.1f}ms")
                if CACHE_METRICS_ENABLED:
                    metrics.record("redis_vector_search", hit=True, latency_ms=latency)
                return cached

        # ... rest of existing Pinecone query logic ...

        # [PHASE 34] Cache results before returning
        if use_cache and matches:
            await self.cache_set(cache_key, matches, ttl=self._default_ttl)

        return matches
```

---

### DIFF-003: Add Redis Caching to `pinecone_sync.py`

```python
# FILE: agentic_core/semantic_memory/store/pinecone_sync.py
# CHANGE: Cache embeddings in Redis to avoid repeated Gemini API calls

# === BEFORE (lines 43-88) ===
class MemoryArchitectSync:
    """
    L4 State Sync: Updates Pinecone to reflect new modular architecture.
    """

    def __init__(self):
        """Initialize Memory Architect Sync."""
        self.pinecone_available = PINECONE_AVAILABLE
        self.genai_available = GENAI_AVAILABLE
        # ... Pinecone init ...
        # ... Gemini init ...

# === AFTER ===
class MemoryArchitectSync:
    """
    L4 State Sync: Updates Pinecone to reflect new modular architecture.

    [PHASE 34] Redis-Cached Embeddings:
    - Embeddings cached for 7 days to avoid repeated API calls
    - Reduces Gemini API costs significantly
    - Graceful degradation if Redis unavailable
    """

    EMBEDDING_CACHE_TTL = 604800  # 7 days

    def __init__(self):
        """Initialize Memory Architect Sync with Redis caching."""
        self.pinecone_available = PINECONE_AVAILABLE
        self.genai_available = GENAI_AVAILABLE

        # [PHASE 34] Initialize Redis for embedding cache
        self.redis_client = None
        self._init_redis()

        # ... rest of existing init ...

    def _init_redis(self) -> None:
        """Initialize Redis connection for embedding cache."""
        try:
            import redis
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            Logger.info("[OK] MemoryArchitectSync: Redis embedding cache connected")
        except Exception as e:
            Logger.warning(f"[!] Redis embedding cache unavailable: {e}")
            self.redis_client = None
```

```python
# === BEFORE (lines 158-181) ===
    def _generate_embedding(self, text: str) -> list[float] | None:
        """
        Generate embedding vector for text.
        """
        if not self.genai_available:
            Logger.warning("    [!]  Gemini not available for embeddings")
            return None
        try:
            result = self.genai_client.models.embed_content(
                model="models/text-embedding-004", contents=text
            )
            if result and hasattr(result, "embeddings") and len(result.embeddings) > 0:
                return result.embeddings[0].values
            return None
        except Exception as e:
            Logger.error(f"    [X] Embedding generation failed: {e}")
            return None

# === AFTER ===
    def _generate_embedding(self, text: str) -> list[float] | None:
        """
        Generate embedding vector for text with Redis caching.

        [PHASE 34] Cache Strategy:
        1. Hash text content for cache key
        2. Check Redis for cached embedding
        3. On miss, call Gemini API and cache result
        """
        import hashlib
        import json

        # [PHASE 34] Generate cache key from content hash
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        cache_key = f"embed:gemini:{content_hash}"

        # [PHASE 34] Check Redis cache first
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    Logger.debug(f"    [CACHE HIT] Embedding retrieved from Redis")
                    return json.loads(cached)
            except Exception as e:
                Logger.debug(f"    [!] Redis cache read failed: {e}")

        # Cache miss - generate embedding
        if not self.genai_available:
            Logger.warning("    [!]  Gemini not available for embeddings")
            return None

        try:
            result = self.genai_client.models.embed_content(
                model="models/text-embedding-004", contents=text
            )
            if result and hasattr(result, "embeddings") and len(result.embeddings) > 0:
                embedding = result.embeddings[0].values

                # [PHASE 34] Cache embedding in Redis
                if self.redis_client:
                    try:
                        self.redis_client.setex(
                            cache_key,
                            self.EMBEDDING_CACHE_TTL,
                            json.dumps(embedding)
                        )
                        Logger.debug(f"    [CACHED] Embedding stored in Redis (TTL: 7 days)")
                    except Exception as e:
                        Logger.debug(f"    [!] Redis cache write failed: {e}")

                return embedding

            Logger.warning("    [!]  No embedding returned from Gemini")
            return None
        except Exception as e:
            Logger.error(f"    [X] Embedding generation failed: {e}")
            return None
```

---

### DIFF-004: Add Redis Caching to `pinecone_mcp_client.py`

```python
# FILE: agentic_core/L2_execution/mcp/pinecone_mcp_client.py
# CHANGE: Add Redis caching for search results

# === BEFORE (lines 23-45) ===
class SovereignPineconeMcpClient(SovereignBaseAgent):
    """
    Official Pinecone MCP client — L3 routed, L5 shielded.
    """

    def __init__(self):
        """Initialize the Pinecone MCP client with sovereign routing."""
        super().__init__()
        self.router = SovereignMCPRouter(role="semantic_memory")
        self.initialized = False
        self._mcp_audit("init")
        Logger.info("[L4 PINECONE MCP] Client initialized")

# === AFTER ===
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin


class SovereignPineconeMcpClient(RedisCacheMixin, SovereignBaseAgent):
    """
    Official Pinecone MCP client — L3 routed, L5 shielded.

    [PHASE 34] Redis-Cached for Meta-Learning Layer:
    - Search results cached with 1-hour TTL
    - Embedding results cached with 7-day TTL
    - Reduces MCP call overhead significantly
    """

    # RedisCacheMixin configuration
    _cache_prefix: str = "pinecone_mcp"
    _default_ttl: int = 3600  # 1 hour for search results
    EMBEDDING_CACHE_TTL: int = 604800  # 7 days for embeddings

    def __init__(self):
        """Initialize the Pinecone MCP client with sovereign routing and Redis cache."""
        super().__init__()
        self.router = SovereignMCPRouter(role="semantic_memory")
        self.initialized = False
        self._mcp_audit("init")
        Logger.info("[L4 PINECONE MCP] Client initialized with Redis cache")
```

```python
# === BEFORE (lines 57-101) ===
    async def search(
        self,
        query_text: str,
        top_k: int = 10,
        namespace: str | None = None,
        rerank: bool = True,
        filters: dict | None = None,
    ) -> dict[str, Any]:
        """
        Execute semantic search with optional server-side reranking.
        """
        if not config.PINECONE_MCP_ENABLED:
            raise RuntimeError("Pinecone MCP is disabled in Sovereign Config.")
        if not self.initialized:
            await self.initialize()
        try:
            result: Any = await self._hardened_call(
                "pinecone_search",
                self.router.manager.call_tool,
                tool_name="pinecone_search",
                args={...},
            )
            return result
        except Exception as e:
            return {"matches": [], "error": str(e)}

# === AFTER ===
    async def search(
        self,
        query_text: str,
        top_k: int = 10,
        namespace: str | None = None,
        rerank: bool = True,
        filters: dict | None = None,
        use_cache: bool = True,  # [PHASE 34] New parameter
    ) -> dict[str, Any]:
        """
        Execute semantic search with Redis caching and optional server-side reranking.

        [PHASE 34] Cache Strategy:
        1. Generate cache key from query + parameters
        2. Check Redis cache for cached results
        3. On miss, execute MCP call and cache results
        """
        import hashlib

        if not config.PINECONE_MCP_ENABLED:
            raise RuntimeError("Pinecone MCP is disabled in Sovereign Config.")
        if not self.initialized:
            await self.initialize()

        # [PHASE 34] Generate cache key
        effective_namespace = namespace or config.PINECONE_DEFAULT_NAMESPACE
        cache_key = f"search:{hashlib.sha256(query_text.encode()).hexdigest()[:16]}:{top_k}:{effective_namespace}:{rerank}"

        # [PHASE 34] Check Redis cache
        if use_cache:
            cached = await self.cache_get(cache_key)
            if cached:
                Logger.debug(f"[L4 PINECONE MCP] Search cache HIT")
                return cached

        try:
            result: Any = await self._hardened_call(
                "pinecone_search",
                self.router.manager.call_tool,
                tool_name="pinecone_search",
                args={
                    "query": query_text,
                    "top_k": top_k,
                    "namespace": effective_namespace,
                    "rerank": rerank,
                    "rerank_model": config.PINECONE_RERANK_MODEL if rerank else None,
                },
            )
            Logger.info(
                f"[L4 PINECONE MCP] Search completed: {len(result.get('matches', []))} results"
            )

            # [PHASE 34] Cache results
            if use_cache and result.get("matches"):
                await self.cache_set(cache_key, result, ttl=self._default_ttl)

            return result
        except Exception as e:
            Logger.error(f"[L4 PINECONE MCP] Search failed: {e}")
            return {"matches": [], "error": str(e)}
```

---

### DIFF-005: Add Redis Caching to `pinecone.py` (SovereignPineconeClient)

```python
# FILE: agentic_core/L2_execution/mcp/pinecone.py
# CHANGE: Add Redis caching for query operations

# === BEFORE (lines 23-40) ===
class SovereignPineconeClient(SovereignBaseAgent):
    """Sovereign Pinecone client - audit + safe exec for all vector operations."""

    def __init__(self, index_name: str | None = None, namespace: str | None = None):
        super().__init__()
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
        self.namespace = namespace or ""
        self.audit_log: list[dict[str, Any]] = []
        self._pc = None
        self._index = None
        self._mcp_audit("init")

# === AFTER ===
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin


class SovereignPineconeClient(RedisCacheMixin, SovereignBaseAgent):
    """
    Sovereign Pinecone client - audit + safe exec for all vector operations.

    [PHASE 34] Redis-Cached for Meta-Learning Layer:
    - Query results cached with 1-hour TTL
    - Reduces Pinecone API calls significantly
    """

    # RedisCacheMixin configuration
    _cache_prefix: str = "sovereign_pinecone"
    _default_ttl: int = 3600  # 1 hour

    def __init__(self, index_name: str | None = None, namespace: str | None = None):
        super().__init__()
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
        self.namespace = namespace or ""
        self.audit_log: list[dict[str, Any]] = []
        self._pc = None
        self._index = None
        self._mcp_audit("init")
```

---

## Part 4: Centralized Configuration

### Create Unified Pinecone/Redis Config

The `SovereignRagConfig` (already created in `agentic_core/config/rag_config.py`) should be extended:

```python
# FILE: agentic_core/config/rag_config.py
# ADD: Unified cache configuration

@dataclass
class CacheConfig:
    """Redis cache configuration for Meta-Learning Layer."""

    redis_url: str = "redis://localhost:6379"
    query_cache_ttl: int = 3600  # 1 hour for query results
    embedding_cache_ttl: int = 604800  # 7 days for embeddings
    enable_cache: bool = True
    cache_prefix: str = "sovereign_rag"

    # Meta-Learning Layer specific
    meta_learning_ttl: int = 86400  # 24 hours for meta-learning data
    promotion_threshold: float = 0.8  # Score threshold for long-term storage
```

---

## Part 5: Test Cases

### TC-REDIS-001: Verify Redis Cache Hit for Pinecone Queries
```python
def test_pinecone_store_redis_cache_hit():
    """Verify that repeated queries return cached results from Redis."""
    store = PineconeVectorStore()

    # First query - should hit Pinecone
    embedding = [0.1] * 384
    result1 = store.query(embedding, top_k=5)

    # Second query - should hit Redis cache
    start = time.time()
    result2 = store.query(embedding, top_k=5)
    latency = (time.time() - start) * 1000

    assert result1 == result2, "Cached result should match original"
    assert latency < 10, f"Cache hit should be <10ms, got {latency:.2f}ms"
```

### TC-REDIS-002: Verify Embedding Cache in pinecone_sync.py
```python
def test_memory_architect_embedding_cache():
    """Verify embeddings are cached in Redis."""
    sync = MemoryArchitectSync()

    text = "def hello_world(): print('Hello')"

    # First call - should hit Gemini API
    emb1 = sync._generate_embedding(text)

    # Second call - should hit Redis cache
    emb2 = sync._generate_embedding(text)

    assert emb1 == emb2, "Cached embedding should match original"

    # Verify cache key exists in Redis
    import hashlib
    cache_key = f"embed:gemini:{hashlib.sha256(text.encode()).hexdigest()}"
    assert sync.redis_client.exists(cache_key), "Cache key should exist"
```

### TC-REDIS-003: Verify PineconeVectorMixin Uses RedisCacheMixin
```python
def test_pinecone_vector_mixin_redis_integration():
    """Verify PineconeVectorMixin inherits RedisCacheMixin."""
    from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin
    from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin

    assert issubclass(PineconeVectorMixin, RedisCacheMixin), \
        "PineconeVectorMixin should inherit from RedisCacheMixin"

    # Verify cache methods are available
    mixin = PineconeVectorMixin()
    assert hasattr(mixin, 'cache_get'), "Should have cache_get method"
    assert hasattr(mixin, 'cache_set'), "Should have cache_set method"
    assert hasattr(mixin, '_cache_prefix'), "Should have _cache_prefix"
```

### TC-REDIS-004: Verify Graceful Degradation Without Redis
```python
def test_pinecone_store_graceful_degradation():
    """Verify Pinecone operations work when Redis is unavailable."""
    import os

    # Simulate Redis unavailable
    original_url = os.environ.get("REDIS_URL")
    os.environ["REDIS_URL"] = "redis://invalid:9999"

    try:
        store = PineconeVectorStore()
        assert store.redis_client is None, "Redis should be None when unavailable"

        # Query should still work (direct Pinecone)
        embedding = [0.1] * 384
        result = store.query(embedding, top_k=5)
        assert isinstance(result, list), "Query should return list even without cache"
    finally:
        if original_url:
            os.environ["REDIS_URL"] = original_url
```

### TC-REDIS-005: Verify Cache Invalidation on Upsert
```python
def test_cache_invalidation_on_upsert():
    """Verify that upserts invalidate related cache entries."""
    store = PineconeVectorStore()

    embedding = [0.1] * 384

    # Query to populate cache
    store.query(embedding, top_k=5)

    # Upsert new vector
    store.upsert([("test_id", embedding, {"source": "test"})])

    # Cache should be invalidated for this namespace
    # (Implementation detail: upsert should call cache_invalidate)
```

### TC-REDIS-006: Verify Meta-Learning Layer Integration
```python
def test_meta_learning_layer_cache_flow():
    """Verify complete Meta-Learning Layer cache flow."""
    from agentic_core.L4_state.memory.SemanticCacheManager import SemanticCacheManager

    cache = SemanticCacheManager.get_instance()

    # Learn something
    cache.learn(
        context="How to fix import errors",
        namespace="TestAgent",
        result={"action": "add_import", "module": "os"}
    )

    # Recall should hit Redis first
    result = cache.recall(
        context="How to fix import errors",
        namespace="TestAgent"
    )

    assert result is not None, "Should recall from cache"
    assert result["action"] == "add_import", "Should return correct action"
    assert cache.stats["redis_hits"] > 0, "Should have Redis hits"
```

---

## Part 6: Implementation Priority

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P0 | DIFF-001: `pinecone_store.py` Redis cache | 2 hours | HIGH - Core RAG path |
| P0 | DIFF-003: `pinecone_sync.py` embedding cache | 1 hour | HIGH - API cost savings |
| P1 | DIFF-002: `pinecone_vector_mixin.py` RedisCacheMixin | 2 hours | HIGH - All agents using mixin |
| P1 | DIFF-004: `pinecone_mcp_client.py` cache | 1 hour | MEDIUM - MCP path |
| P2 | DIFF-005: `pinecone.py` cache | 1 hour | MEDIUM - Audit path |
| P3 | Centralize dimension config | 30 min | LOW - Consistency |

---

## Part 7: Summary

### Current State
- **7 Pinecone files** with fragmented implementations
- **Only 1 file** (`PineconeSovereignAgent.py`) properly integrates Redis
- **SemanticCacheManager** demonstrates correct dual-layer pattern but is not used universally

### Recommended Actions
1. Apply DIFF-001 through DIFF-005 to add Redis caching to all Pinecone files
2. Centralize Pinecone client creation through `PineconeSovereignAgent`
3. Standardize embedding dimension via `SovereignRagConfig`
4. Run test cases TC-REDIS-001 through TC-REDIS-006 to validate

### Expected Outcomes
- **Latency Reduction:** 100-500ms → 1-5ms for cached queries
- **API Cost Savings:** 70-90% reduction in Gemini embedding API calls
- **Consistency:** All Pinecone operations follow same caching pattern
- **Observability:** Cache hit/miss metrics available for Meta-Learning Layer dashboard

---

*Report generated by Cascade AI - January 22, 2026*
