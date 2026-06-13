# Memory MCP & Redis Optimization Plan

Comprehensive plan to optimize memory MCP storage and Redis usage based on ADG dependency analysis — **Phase 1 & 2 implemented** (20260311T194341Z ADG: 3,329 modules, 152,269 edges, 220 violations, 711 repair routes).

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

**ADG Refresh: 20260311T193725Z** (artifact digest: `47c5fac0fe420863a316dbd4b77458374061d9707484213ef65c00953364e92a`)

**ADG Analysis Findings:**
- **Total dependency edges**: 152,131 (+198 vs prev 151,933; +266 added, -124 removed)
- **Modules**: 3,325 | **Entities**: 43,762 | **Symbols**: 40,437
- **Layer violations**: 220 (all critical) — L0→L5: 32, L_SHARED→L5: 20, L_SHARED→L4: 14
- **Repair routes**: 711 (220 critical, 491 medium)
- **High-criticality modules**: 960 | **Avg confidence**: 0.8856
- **Dead imports**: 2,756 (worst: `L5_safety/config/structure_blueprint/__init__.py`: 103)
- **SSOT violations**: 1,543 hardcoded path hits across 574 files
- **Orphan modules**: 129 | **Unresolved imports**: 443
- **Top hotspot**: `apps_shared/types/sovereign_severity_types.py` (fan-out 1,149)
- **Redis references**: 2,548 across 704 files
- **Bug fixed**: `tools/generate_full_adg.py:253` — `edge.target_module` → `edge.to_name`

**Graph Plane Coverage:**
| Plane | Count |
|-------|-------|
| G1 imports | 22,869 |
| G3 implements | 1,857 |
| G4 calls | 13,990 |
| GT covers (tests) | 3,668 |
| GV violates | 220 |
| GG governance | 110 |

**Critical Gaps Identified:**
1. **No centralized ADG metadata storage** in Memory MCP
2. **Fragmented cache layers** (Redis hot/coordination, in-memory vector, semantic cache)
3. **Missing dependency graph queries** for impact analysis
4. **No Redis key namespace governance** for multi-tenant isolation
5. **Duplicate memory stores** (5+ vector store implementations)
6. **`generate_full_adg.py`** had bug in memory persistence (now fixed)

---

## Part 1: What to Store in Memory MCP

### 1.1 ADG Core Metadata (High Priority)

**Entity Types:**
- `ADGSnapshot` - Full graph snapshots with commit SHA and timestamp
- `Module` - Python modules with file paths and layer assignments
- `Symbol` - Classes, functions, constants with canonical names
- `Layer` - L0-L6 + L_APP/L_SL/L_TOOLS/L_RUNTIME layers
- `Violation` - Layer boundary violations, dead imports, SSOT violations

**Relations:**
- `IMPORTS` - Module A imports Symbol from Module B
- `VIOLATES` - Module violates layer boundary (e.g., L0→L5)
- `DEAD_IMPORT` - Unused import statement
- `SSOT_VIOLATION` - Hardcoded path instead of SSOT constant
- `DEPENDS_ON` - Transitive dependency chain
- `OWNS` - Layer owns module (governance)

**Observations:**
- Import line numbers and symbol names
- Violation severity and remediation status
- File modification timestamps
- Dependency depth and fan-out metrics

**Storage Schema:**
```python
# Entity: ADGSnapshot
{
    "name": "adg_20260311T185727Z",
    "entityType": "ADGSnapshot",
    "observations": [
        "Total edges: 151933",
        "Artifact digest: cf5e8969cd8bfbc77ff7efd8583eb98c8081bc0a2326b329ab7f3d92f6d64b92",
        "Commit SHA: <git-sha>",
        "Layer violations: 220",
        "Dead imports: 2756"
    ]
}

# Entity: Module
{
    "name": "agentic_core.L4_state.memory.semantic_cache_manager",
    "entityType": "Module",
    "observations": [
        "Layer: L4",
        "File: agentic_core/L4_state/memory/semantic_cache_manager.py",
        "Lines: 823",
        "Classes: SemanticCacheManager, PII_Sanitizer",
        "Redis references: 47"
    ]
}

# Relation: IMPORTS
{
    "from": "agentic_core.L4_state.memory.semantic_cache_manager",
    "to": "agentic_core.cache.redis_cache_client",
    "relationType": "IMPORTS"
}
```

### 1.2 Architecture Knowledge (Medium Priority)

**Entity Types:**
- `Agent` - Agentic reasoning components
- `Mixin` - Reusable behavior mixins
- `Strategy` - Enforcement strategies
- `Config` - Configuration modules

**Relations:**
- `INHERITS_FROM` - Class inheritance
- `USES_MIXIN` - Agent uses mixin
- `ENFORCES` - Strategy enforces policy
- `CONFIGURES` - Config applies to component

**Use Cases:**
- Agent discovery and capability mapping
- Mixin usage tracking (prevent duplication)
- Strategy application verification
- Config propagation analysis

### 1.3 Operational Metrics (Low Priority)

**Entity Types:**
- `CacheHit` - Redis cache hit/miss events
- `MemoryPromotion` - Short-term → Long-term DNA promotions
- `HealingOutcome` - Agent healing success/failure

**Relations:**
- `CACHED_BY` - Data cached by agent
- `PROMOTED_TO` - Memory promoted to DNA
- `HEALED_BY` - Violation healed by agent

**Use Cases:**
- Cache effectiveness monitoring
- Memory lifecycle tracking
- Healing pattern analysis

---

## Part 2: Processes Using Memory MCP

### 2.1 ADG Analysis & Impact Assessment

**Process**: `ADGDependencyAnalyzer`
- **Input**: File path or module name
- **Query**: `MATCH (m:Module {name: $module})-[:IMPORTS*1..3]->(dep:Module) RETURN dep`
- **Output**: Dependency tree with blast radius
- **Storage**: Create `DependencyAnalysis` entity with timestamp

**Process**: `LayerViolationDetector`
- **Input**: ADG snapshot
- **Query**: `MATCH (m:Module)-[v:VIOLATES]->(l:Layer) RETURN m, v, l`
- **Output**: Violation report with remediation suggestions
- **Storage**: Update `Violation` entities with status

**Process**: `DeadImportCleaner`
- **Input**: Module path
- **Query**: `MATCH (m:Module)-[d:DEAD_IMPORT]->(s:Symbol) RETURN d`
- **Output**: List of safe-to-remove imports
- **Storage**: Mark `DEAD_IMPORT` relations as `remediated`

### 2.2 Agent Registration & Discovery

**Process**: `AgentRegistrar` (via `GraphMemoryBridge`)
- **Trigger**: Agent instantiation with `MetaLearningMixin`
- **Action**: Create `Agent` entity with capabilities
- **Storage**: `mcp11_create_entities([{name: agent_name, entityType: "Agent", observations: [...]}])`

**Process**: `CapabilityMatcher`
- **Input**: Task description
- **Query**: `MATCH (a:Agent)-[:MASTERED_TASK]->(t:Task) WHERE t.description CONTAINS $keywords RETURN a`
- **Output**: Ranked list of capable agents
- **Storage**: Create `TaskMatch` observation

### 2.3 Memory Lifecycle Management

**Process**: `MemoryPromotionEngine` (via `SemanticCacheManager`)
- **Trigger**: Feedback score >= 0.8
- **Action**: Create `MASTERED_TASK` relation
- **Storage**: `bridge.create_mastered_task_relation(agent_name, task_desc, score)`

**Process**: `DNARetrieval`
- **Input**: Agent name + task context
- **Query**: `MATCH (a:Agent)-[:MASTERED_TASK]->(t:Task) WHERE a.name = $agent RETURN t ORDER BY t.score DESC LIMIT 5`
- **Output**: Top 5 mastered tasks for context injection
- **Storage**: Add observation to agent entity

### 2.4 SSOT Compliance Monitoring

**Process**: `SSOTViolationScanner`
- **Input**: ADG snapshot
- **Query**: `MATCH (m:Module)-[v:SSOT_VIOLATION]->(c:Constant) RETURN m, v, c ORDER BY v.count DESC`
- **Output**: Prioritized remediation list
- **Storage**: Create `SSOTReport` entity with fix suggestions

**Process**: `SSOTHealingTracker`
- **Input**: File path + constant name
- **Action**: Update violation status after fix
- **Storage**: Update `SSOT_VIOLATION` relation with `fixed: true, fixed_at: timestamp`

---

## Part 3: Redis Optimization Strategy

### 3.1 Current Redis Architecture

**Database Namespaces:**
- **DB 0 (HOT)**: L0/L1/L3/L5 caches with configurable TTLs (max 24h)
- **DB 1 (COORDINATION)**: L2 leases, idempotency keys with short TTLs

**Key Patterns Identified:**
```
semantic:{mission_id}:{path_hash}              # L4 semantic cache
rag_topk:{u0_hash}:{embedder}:{manifest}:{k}   # RAG retrieval cache
cache:{content_hash}                            # Generic content cache
lease:{resource_id}                             # L2 coordination leases
```

**Problems:**
1. **No namespace isolation** - Mission IDs mixed with global keys
2. **Inconsistent TTL policies** - Some caches use , others 
3. **No eviction strategy** - LRU not configured, risk of memory bloat
4. **Missing monitoring** - No hit/miss rate tracking per namespace

### 3.2 Redis Key Namespace Governance

**Proposed Namespace Hierarchy:**
```
{layer}:{component}:{mission_id}:{entity_type}:{content_hash}

Examples:
L4:semantic:mission_abc123:file:e3b0c44298fc  # Semantic cache entry
L1:assembly:mission_abc123:thought:a1b2c3d4   # Thought assembly cache
L3:orchestration:global:workflow:def456789    # Global workflow state
L2:coordination:global:lease:resource_xyz     # Coordination lease
```

**Benefits:**
- **Multi-tenant isolation**: Mission-scoped keys prevent cross-contamination
- **Layer-aware eviction**: Different TTL policies per layer
- **Monitoring granularity**: Track hit rates by layer/component
- **Audit trail**: Key pattern reveals data lineage

### 3.3 Redis Performance Optimizations

**3.3.1 Connection Pooling**
```python
# Current: New connection per request (inefficient)
# Proposed: Singleton connection pool

from redis import ConnectionPool, Redis

_redis_pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    socket_timeout=0.3,
    socket_connect_timeout=0.3,
    decode_responses=False  # Binary mode for determinism
)

def get_redis_client(db: int = 0) -> Redis:
    return Redis(connection_pool=_redis_pool, db=db)
```

**3.3.2 Pipeline Batching**
```python
# Current: Individual SET/GET calls
# Proposed: Pipeline batching for bulk operations

def batch_cache_files(entries: list[tuple[str, bytes]]) -> None:
    client = get_redis_client(db=0)
    pipe = client.pipeline()
    for key, value in entries:
        pipe.set(key, value, ex=3600)
    pipe.execute()  # Single round-trip
```

**3.3.3 Compression for Large Values**
```python
import zlib

def set_compressed(key: str, value: bytes, ttl: int) -> None:
    if len(value) > 1024:  # Compress if > 1KB
        compressed = zlib.compress(value, level=6)
        client.set(f"{key}:z", compressed, ex=ttl)
    else:
        client.set(key, value, ex=ttl)
```

**3.3.4 LRU Eviction Policy**
```redis
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 5
```

### 3.4 Redis Monitoring & Metrics

**Key Metrics to Track:**
```python
class RedisCacheMetrics:
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def record_hit(self, namespace: str) -> None:
        self.hits += 1
        # Emit to L6 observability

    def record_miss(self, namespace: str) -> None:
        self.misses += 1
```

**Integration with L6 Observability:**
- Emit cache metrics to `SovereignHealthMonitor`
- Dashboard visualization of hit rates by layer
- Alerts on hit rate < 50% or error rate > 1%

---

## Part 4: Implementation Roadmap

### Phase 1: Memory MCP ADG Integration (Week 1)

**Tasks:**
1. Create `ADGMemoryAdapter` to bridge ADG artifacts → Memory MCP
2. Define entity/relation schemas for ADG metadata
3. Implement bulk upsert for ADG snapshots (151K edges)
4. Add query helpers for dependency analysis
5. Write tests for idempotency and determinism

**Deliverables:**
- `agentic_core/adg/adapters/memory_mcp_adapter.py`
- `agentic_core/adg/queries/dependency_queries.py`
- `tests/adg/test_memory_mcp_integration.py`

### Phase 2: Redis Namespace Governance (Week 2)

**Tasks:**
1. Implement namespace key builder with layer/component/mission isolation
2. Migrate existing cache keys to new namespace pattern
3. Configure LRU eviction and maxmemory policies
4. Add connection pooling to `redis_cache_client.py`
5. Implement pipeline batching for bulk operations

**Deliverables:**
- `agentic_core/cache/namespace_builder.py`
- `agentic_core/cache/redis_cache_client.py` (updated)
- Migration script: `ops_scripts/ci/migrate_redis_namespaces.py`

### Phase 3: Cache Consolidation (Week 3)

**Tasks:**
1. Audit 5+ vector store implementations, identify canonical version
2. Deprecate duplicate stores: mark with `@deprecated` decorator
3. Consolidate to `InMemoryVectorStore` (FAISS-backed) as SSOT
4. Update all consumers to use canonical store
5. Remove deprecated stores after 1-week grace period

**Deliverables:**
- `agentic_core/L4_state/memory/in_memory_vector_store.py` (canonical)
- Deprecation notices in duplicate stores
- `docs/architecture/cache_consolidation_plan.md`

### Phase 4: Monitoring & Observability (Week 4)

**Tasks:**
1. Implement `RedisCacheMetrics` with hit/miss tracking
2. Integrate metrics emission to L6 observability
3. Create Grafana dashboard for cache performance
4. Add alerting rules for degraded cache performance
5. Document cache usage patterns and best practices

**Deliverables:**
- `agentic_core/cache/metrics.py`
- `agentic_core/L6_observability/dashboards/cache_dashboard.json`
- `docs/operations/redis_monitoring.md`

---

## Part 5: Success Metrics

### Memory MCP Metrics
- **ADG query latency**: < 100ms for dependency lookups (p95)
- **Storage efficiency**: < 50MB for full ADG snapshot (151K edges)
- **Query coverage**: 100% of layer violations queryable
- **Idempotency**: 0 duplicate entities/relations after bulk upsert

### Redis Metrics
- **Cache hit rate**: > 70% for semantic cache, > 90% for RAG retrieval
- **Connection pool efficiency**: < 10ms connection acquisition (p95)
- **Memory usage**: < 2GB with LRU eviction active
- **Pipeline speedup**: 5-10x faster for bulk operations (>100 keys)

### Code Quality Metrics
- **Dead import reduction**: 2,756 → < 500 (80% reduction)
- **Layer violations**: 220 → < 50 (77% reduction)
- **SSOT compliance**: 1,543 violations → < 200 (87% compliance)
- **Cache consolidation**: 5+ stores → 1 canonical store

---

## Part 6: Risk Mitigation

### Risk 1: Memory MCP Unavailable in CI
**Mitigation**: `GraphMemoryBridge` already has fallback to `_InMemoryStore`
**Action**: Ensure all ADG queries gracefully degrade to in-memory mode

### Risk 2: Redis Connection Failures
**Mitigation**: `DeterministicRedisCache` has bounded LRU fallback
**Action**: Add circuit breaker pattern to prevent cascade failures

### Risk 3: Migration Downtime
**Mitigation**: Blue-green deployment with dual-write period
**Action**: Run old + new namespaces in parallel for , then cutover

### Risk 4: Performance Regression
**Mitigation**: Benchmark before/after with realistic workloads
**Action**: Rollback plan if cache hit rate drops > 10% or latency increases > 20%

---

## Appendix A: Current Memory/Cache Inventory

### L4_state/memory (15 components)
1. `semantic_cache_manager.py` - Hive Mind with Redis + vector store
2. `sovereign_semantic_cache.py` - Mission-isolated semantic cache
3. `sovereign_memory_store.py` - MCP knowledge graph wrapper
4. `in_memory_vector_store.py` - FAISS-backed vector search
5. `in_memory_vector_cache.py` - Ephemeral vector cache
6. `blackboard_store.py` - Shared state blackboard
7. `bm25_store.py` - BM25 text search index
8. `reasoning_memory.py` - Agent reasoning traces
9. `sovereign_reasoning_memory_ledger.py` - Reasoning audit log
10. `blob_storage_provider.py` - Large artifact storage
11. `prompt_version_store.py` - Prompt template versioning
12. `runtime_models.py` - Runtime model registry
13. `runtime_state_guard.py` - State mutation guard
14. `verifiable_checkpoint_manager.py` - Checkpoint persistence

### Redis Usage (2,548 references across 704 files)
- **Top consumers**: `redis_cache_client.py` (65), `semantic_cache_manager.py` (47), `redis_cache_mixin.py` (46)
- **Integration points**: L1 (meta_client), L2 (RedisSovereignAgent), L3 (sovereign_redis_orchestrator), L4 (semantic cache)

### System Learning (57 files)
- **Stores**: `audit_store.py`, `telemetry_store.py`, `version_store.py`, `config_provider.py`
- **Caches**: `rag_retrieval_cache.py` (RAG top-k memoization)
- **Engines**: 40+ engines for healing, embedding, replay, arbitration

---

## Appendix B: ADG Query Examples

### Query 1: Find All Importers of a Module
```python
# Memory MCP query
bridge = GraphMemoryBridge.get_instance()
results = bridge.search_entities("IMPORTS agentic_core.cache.redis_cache_client")

# Expected: List of all modules importing redis_cache_client
# Use case: Impact analysis before refactoring
```

### Query 2: Detect Layer Violation Chains
```python
# Find transitive violations (L0 → L2 → L5)
query = """
MATCH path = (m1:Module)-[:VIOLATES*2..3]->(l:Layer)
WHERE m1.layer = 'L0' AND l.name = 'L5'
RETURN path
"""
# Use case: Identify indirect layer boundary violations
```

### Query 3: Dead Import Cleanup Candidates
```python
# Find modules with >10 dead imports
query = """
MATCH (m:Module)-[d:DEAD_IMPORT]->(s:Symbol)
WITH m, count(d) as dead_count
WHERE dead_count > 10
RETURN m.name, dead_count
ORDER BY dead_count DESC
"""
# Use case: Prioritize cleanup efforts
```

---

## Phase 3: System Learning Persistent Memory Upgrades - IMPLEMENTED 20260311

### Problem Statement

All `system_learning` engines were **stateless across process restarts**:
- `HealingSuccessRateStore` — EMA rates reset to neutral 0.50 on every restart (cold-start)
- `RCAEngine` — findings discarded after each run; no failure pattern library
- `ShadowDriftAnalyzer` — drift summaries ephemeral (DriftRegistry only)
- `PolicyRecommendationEngine` — recommendations never stored; no feedback loop
- `HealingOutcomeAggregator` — aggregate snapshots lost on restart
- `PatternAnalysisEngine` — clusters recomputed from scratch each run

### Solution: SystemLearningMemoryBridge

**File**: `system_learning/adapters/system_learning_memory_bridge.py`
- Singleton `SystemLearningMemoryBridge` accessed via `get_sl_memory_bridge()`
- MCP unavailability caught and logged, never raises
- Non-authoritative: local in-memory state always wins over MCP-restored data
- Persists only when count >= `_MIN_SAMPLE_SIZE` (statistically meaningful)

### Entity Types Added to Memory MCP

| Entity Type | Source | Captures |
|---|---|---|
| `SLHealingSuccessRate` | `HealingSuccessRateStore` | EMA rate + count per error signature |
| `SLRCAReport` | `rca_engine` | Finding summary per snapshot/window |
| `SLRCAFinding` | `rca_engine` | Pattern (category, signature, count) |
| `SLDriftSummary` | `ShadowDriftAnalyzer` | p95_cosine, drift_flag per profile |
| `SLPolicyRecommendation` | `PolicyRecommendationEngine` | Changes, confidence, applied status |
| `SLHealingAggregate` | `HealingOutcomeAggregator` | Per-snapshot aggregate stats |
| `SLFailurePattern` | `PatternAnalysisEngine` | Cluster centroid + member count |

### Files Modified / Created

| File | Change |
|---|---|
| `system_learning/adapters/system_learning_memory_bridge.py` | NEW - canonical bridge |
| `system_learning/engines/healing_success_rate_store.py` | `_maybe_persist_to_mcp()` + `restore_from_memory()` |
| `system_learning/engines/rca_engine.py` | `analyze_failures_and_persist()` wrapper |
| `system_learning/engines/shadow_drift_analyzer.py` | MCP persist in `_emit_to_registry()` |
| `system_learning/engines/policy_recommendation_engine.py` | `MemoryAwarePolicyRecommendationEngine` subclass |
| `tests/system_learning/test_system_learning_memory_bridge.py` | NEW - 36 tests, all passing |

### Key Capabilities Unlocked

1. **No cold-start for healing priors** — `restore_from_memory()` warm-starts EMA rates from MCP on process startup
2. **Accumulated failure pattern library** — `query_rca_pattern_frequency(category='IMPORT')` returns cross-session pattern history
3. **Cross-session drift trend tracking** — `query_drift_history(profile_id=...)` enables inflection detection
4. **Policy recommendation feedback loop** — `mark_recommendation_applied()` + `query_policy_recommendations(applied_only=True)`
5. **Aggregate snapshot history** — queryable across restarts for meta-learning pipeline replay

---

## Implementation Status Summary

| Phase | Status | Deliverable |
|---|---|---|
| Phase 1: ADGMemoryAdapter | DONE | `agentic_core/adg/adapters/memory_mcp_adapter.py` |
| Phase 2: Redis namespace governance | DONE | `agentic_core/cache/namespace_builder.py` |
| Phase 3: System Learning MCP upgrades | DONE | `system_learning/adapters/system_learning_memory_bridge.py` |
| ADG bug fix | DONE | `generate_full_adg.py:253` edge.to_name fix |
| ADG wiring | DONE | `_persist_adg_to_memory` delegates to `ADGMemoryAdapter` |
| Memory MCP populated | DONE | ADG snapshot + layers + violations + SL upgrades stored |
| Tests | DONE | 40 ADG tests + 36 SL bridge tests = 76 total passing |

---

## Next Steps

1. **Wire `MemoryAwarePolicyRecommendationEngine`** as default in pipeline startup
2. **Wire `restore_from_memory()`** into `get_default_store()` startup path for zero-config warm-start
3. **Wire `analyze_failures_and_persist`** as default in meta-learning pipeline orchestrator
4. **Phase 4** (future): Consolidate 5+ vector store implementations to canonical `InMemoryVectorStore`
5. **Phase 5** (future): Redis connection pooling + pipeline batching in `DeterministicRedisCache`

**Estimated Effort**: Phases 1-3 complete
**Dependencies**: Memory MCP server availability, Redis 6.0+

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

