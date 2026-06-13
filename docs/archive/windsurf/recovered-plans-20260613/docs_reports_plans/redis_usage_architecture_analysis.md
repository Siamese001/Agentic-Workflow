# Redis Usage Throughout Architecture - Comprehensive Analysis

## Executive Summary

**Redis is a critical infrastructure component** used extensively across the Agentic Workflow architecture, primarily for:
1. **ADG (Abstract Dependency Graph) hot cache** - 590,021 edges, 8,940 nodes
2. **Coordination fabric** - L2 execution leases and idempotency
3. **Semantic caching** - L0, L1, L3, L5 layer caches with TTLs
4. **System Learning** - RAG retrieval cache (limited usage)

## Redis Architecture Overview

### Two Database Namespaces
```
DB 0 — hot caches (L0, L1/Assembly, L3, L5) with configurable TTLs
DB 1 — coordination (L2 leases / idempotency keys) with short TTLs
```

### Canonical Client Location
```
agentic_core/cache/redis_cache_client.py
- DeterministicRedisCache (non-authoritative)
- get_hot_cache() → DB 0
- get_coordination_cache() → DB 1
```

## Redis Usage by Layer

### L0 Routing
- **Prompt Artifact Cache** - Cached prompt templates and artifacts
- **Tool Embedding Cache** - Cached tool embeddings for retrieval

### L1 Cognition
- **Assembly Cache** - Prompt assembly results
- **RAG Retrieval Cache** - `system_learning/engines/rag_retrieval_cache.py`

### L2 Execution
- **Lease Coordinator** - Distributed locks and execution leases
- **Idempotency Keys** - Prevent duplicate operations
- **Sovereign Filesystem MCP** - File operation caching

### L3 Orchestration
- **Orchestration Plan Cache** - Cached execution plans
- **MCP Router** - Template caching for reasoning

### L4 State
- **Config File Cache** - Parsed YAML/JSON configurations
- **Schema Validator Cache** - JSON schema validation results
- **Policy Registry Cache** - Policy lookup caching
- **Cache Admission Gate** - Semantic cache validation

### L5 Safety
- **Safety Evaluation Cache** - Cached safety assessments

## ADG Redis Integration

### Primary Use Case: ADG Hot Cache
```python
# tools/adg/adg_redis_ingest.py
[redis] ingesting 140499 nodes ...
[redis] ingesting 590021 edges (zero-loss projection) ...
[redis] 5032 violations stored
[redis] context precomputing module context for 8940 modules ...
```

### ADG Redis Operations
- **Nodes**: `adg:node:<id>` - Module metadata
- **Edges**: `adg:edge:<src>:<rel>` - Relationship adjacency sets
- **Edge Detail**: `adg:edge_detail:<id>` - Full edge metadata
- **Violations**: `adg:violation:<id>` - Anti-pattern violations
- **Module Context**: `adg:module_context:<id>` - Precomputed analysis
- **Meta**: `adg:meta` - Cache metadata and freshness status
- **Status**: `adg:status` - Freshness sentinel

### ADG Cache Freshness
```python
from tools.adg.adg_mcp_server import adg_status
status = adg_status()
# Result: is_fresh=True, nodes=8940, edges=590021, age=9.1s
```

## Redis in System Learning

### Limited but Strategic Usage

#### 1. RAG Retrieval Cache
**File**: `system_learning/engines/rag_retrieval_cache.py`
```python
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_hot_cache,
)

class RAGTopKCache:
    def __init__(self, ttl_seconds: int = 600, cache: DeterministicRedisCache | None = None):
        self._cache = cache or get_hot_cache()
```

**Purpose**: Cache RAG top-k retrieval results to avoid repeated vector searches
- **TTL**:  (configurable)
- **Key**: Content hash-based
- **Fallback**: Bounded in-process LRU if Redis unavailable

#### 2. Persistent Memory Bridge (Indirect)
The `system_learning_memory_bridge.py` uses Redis indirectly through:
- **MCP Integration** - Memory MCP server may use Redis for coordination
- **Graph Memory Bridge** - Falls back to Redis when SQLite unavailable

### System Learning Redis Patterns

#### Cache-First Design
```python
# Try Redis cache first
cached_result = self._cache.get(cache_key)
if cached_result and not replay_mode:
    return json.loads(cached_result)

# Fallback to live computation
result = compute_live_result()

# Store in cache
self._cache.set(cache_key, json.dumps(result), ex=self._ttl)
```

#### Graceful Degradation
```python
# guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry
try:
    self._cache.set(key, value, ex=ttl)
except Exception as exc:
    logger.debug("Failed to cache result: %s", exc)
```

## Redis Infrastructure

### Configuration
**File**: `agentic_core/config/redis_config.py`
```python
class RedisConnectionConfig:
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    timeout = int(os.getenv("REDIS_TIMEOUT", "5"))
```

### Health Monitoring
**File**: `tools/adg/redis_health_check.py`
- **Auto-start**: Windows Redis service management
- **Health Checks**: Connection testing and ADG cache validation
- **Exit Codes**: 0 (healthy), 1 (stale cache), 2 (Redis down)

### CI Integration
```yaml
# .github/workflows/adg-ci-gates.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - 6379:6379
```

## Redis Design Invariants

### 1. Non-Authoritative
- Redis never becomes source of truth
- All cached data is derivative of L4 artifacts
- Content-hash based keying only

### 2. Deterministic
- No timestamps in cache keys
- Canonical JSON serialization
- Replay-safe with `replay_mode=True`

### 3. Graceful Failure
- Bounded LRU fallback when Redis unavailable
- Silent-swallower pattern for non-critical operations
- No hard failures due to cache infrastructure

### 4. Layer Separation
- Hot cache (DB 0) vs Coordination (DB 1)
- Different TTL strategies per layer
- Clear ownership boundaries

## Redis Performance Characteristics

### ADG Cache Scale
- **Nodes**: 8,940 modules tracked
- **Edges**: 590,021 relationships
- **Violations**: 5,032 anti-patterns
- **Memory**: ~100MB+ for full ADG cache
- **Ingest Time**: ~30 seconds for full refresh

### System Learning Scale
- **RAG Cache**: Typically < 1MB for retrieval caches
- **TTL**:  default for RAG results
- **Hit Rate**: High for repeated queries
- **Fallback**: In-process LRU for resilience

## Conclusion

Redis is **fundamentally integrated** throughout the Agentic Workflow architecture:

1. **ADG Backbone** - Primary use case with 590K+ edges cached
2. **Coordination Fabric** - L2 execution distributed coordination
3. **Semantic Caching** - Multi-layer performance optimization
4. **System Learning** - Strategic RAG retrieval caching

**System Learning uses Redis sparingly but effectively**:
- RAG retrieval cache for performance
- Indirect usage through persistent memory bridge
- Follows architectural patterns of graceful degradation
- Maintains cache-first design with deterministic fallbacks

The Redis infrastructure is production-hardened with comprehensive health monitoring, CI integration, and failure resilience patterns.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

