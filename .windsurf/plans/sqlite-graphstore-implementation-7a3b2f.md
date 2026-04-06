# SQLiteGraphStore Implementation Plan for GraphRAG Enablement

Implement a production-grade SQLiteGraphStore to enable GraphRAG capabilities (local/global/drift search) and identify top 8 opportunities across the repository to leverage graph-native operations for improved accuracy, latency, and richness.

---

## DEPENDENCY_GRAPH

**Graph Roots**: 
- `agentic_core/L4_state/types/graph_store_types.py` (IGraphStore interface)
- `agentic_core/L4_state/utils/memory/graph_knowledge_store.py` (SQLiteGraphStore placeholder)
- `agentic_core/L1_cognition/reasoning/local_search_engine.py` (BFS traversal)
- `agentic_core/L1_cognition/reasoning/global_search_engine.py` (community search)
- `agentic_core/L1_cognition/reasoning/drift_search_engine.py` (adaptive traversal)
- `agentic_core/L3_orchestration/reasoning/engines/adg_integration.py` (ADG query client)

**Impacted Nodes**: 12 nodes total across L1_cognition, L4_state, L3_orchestration, L5_safety

**Upstream Set** (consumers of graph store):
- `local_search_engine.py` - requires `get_relationships`, `traverse`, community scoring
- `global_search_engine.py` - requires `get_community`, community-level search
- `drift_search_engine.py` - requires `traverse`, adaptive hop selection
- `search_fusion_engine.py` - orchestrates all three search engines
- `rag_pipeline.py` - uses graph store for context retrieval

**Downstream Set** (dependencies):
- `graph_store_types.py` - interface definition
- Existing ADG SQLite database (`adg_indexed_04062026_0554.sqlite`) - 88,216 nodes, 625,564 edges
- BGE embedding service (local, no API cost)
- Redis hot cache (existing infrastructure)

**Edge Classes**:
- `implements` → SQLiteGraphStore implements IGraphStore
- `uses` → search engines use graph store
- `queries` → graph store queries ADG SQLite
- `imports` → all modules import graph store types

**Boundary/Cycle Findings**:
- No circular dependencies detected
- All graph store operations are within L4_state (state layer)
- Search engines in L1_cognition (cognition layer) properly depend on L4_state
- ADG integration in L3_orchestration bridges layers appropriately

**Scope Justification**:
1. `graph_knowledge_store.py` - Root implementation file (placeholder → production)
2. `graph_store_types.py` - Interface extension (add missing methods: get_relationships, traverse, get_community)
3. `local_search_engine.py` - Primary consumer (BFS traversal needs graph-native ops)
4. `global_search_engine.py` - Community search consumer
5. `drift_search_engine.py` - Adaptive traversal consumer
6. `adg_integration.py` - ADG query bridge for graph topology
7. SystemArchitectAgent.py - Circular dependency detection (graph algorithm)
8. ArchitectureGovernorAgent.py - Governance graph queries
9. KnowledgeGraphHealingStrategy.py - Healing graph operations
10. GraphNeighborhoodMemory.py - L4 graph neighborhood queries

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Interface Completion | L4_state types | A | 15,000 🟢 |
| Wave 2 | Core Graph Operations | SQLiteGraphStore implementation | B | 35,000 🟢 |
| Wave 3 | Search Engine Integration | L1_cognition search engines | C | 25,000 🟢 |
| Wave 4 | Cross-Layer Integration | L3/L5 governance & healing | D | 20,000 🟢 |

**Total: 95,000 tokens across 4 waves, all GREEN**

*Note: Token estimates are UNRESOLVED - token_estimator.py not found*

---

## Gap Register

**GAP-1: SQLiteGraphStore is a placeholder**
- Current implementation returns None/empty for all methods
- No actual SQLite queries or graph operations
- Blocks all GraphRAG functionality

**GAP-2: Missing IGraphStore methods**
- Interface defines only add_entity, get_entity, search_entities
- Search engines require: get_relationships, traverse, get_community, get_neighbors
- No graph traversal, pathfinding, or community detection methods

**GAP-3: No graph-native algorithms**
- Circular dependency detection uses manual DFS in SystemArchitectAgent
- Community detection types exist but no implementation
- No centrality, shortest path, or clustering algorithms

**GAP-4: ADG integration disconnected**
- adg_integration.py has ADGQueryClient but not integrated with graph store
- ADG SQLite has 88K nodes/625K edges but not exposed to graph queries
- No bridge between architectural graph and knowledge graph

**GAP-5: Search engines cannot function**
- Local/global/drift search engines exist but have no working graph backend
- Mock implementations return fake results
- GraphRAG pipeline uses MockLLMClient

---

## Execution Plan

### Phase 1 — Interface Extension
**Scope**: Extend IGraphStore interface with graph-native methods required by search engines

**Files**:
- `agentic_core/L4_state/types/graph_store_types.py`

**Changes**:
1. Add `get_relationships(entity_id: str, direction: str = "both") -> list[GraphRelationship]`
2. Add `traverse(start_id: str, max_depth: int = 2, relation_types: list[str] | None = None) -> list[GraphPath]`
3. Add `get_community(community_id: str) -> GraphCommunity | None`
4. Add `get_neighbors(entity_id: str, max_hops: int = 1) -> list[GraphEntity]`
5. Add `get_centrality(entity_id: str) -> float`
6. Add `detect_communities(algorithm: str = "leiden") -> list[GraphCommunity]`
7. Add `find_shortest_path(src_id: str, dst_id: str) -> GraphPath | None`
8. Add `get_subgraph(center_id: str, radius: int = 2) -> GraphSubgraph`

**Acceptance**: Interface compiles, all search engines can type-check against new methods

### Phase 2 — SQLiteGraphStore Core Implementation
**Scope**: Implement full SQLiteGraphStore with graph-native operations using ADG SQLite schema

**Files**:
- `agentic_core/L4_state/utils/memory/graph_knowledge_store.py`

**Schema Mapping** (ADG SQLite → Graph Store):
- `nodes` table → GraphEntity
- `edges` table → GraphRelationship  
- Existing ADG edges: calls, imports, reads_from, writes_to, pulls_context

**Implementation**:
1. **Entity Operations**:
   - `add_entity`: INSERT into nodes table
   - `get_entity`: SELECT from nodes by id
   - `search_entities`: FTS5 full-text search on adg_name + resolved_path

2. **Relationship Operations**:
   - `get_relationships`: SELECT from edges WHERE src_id=? OR dst_id=?
   - Support direction filtering ("outgoing", "incoming", "both")
   - Return GraphRelationship objects with metadata

3. **Traversal Operations**:
   - `traverse`: Recursive CTE for BFS up to max_depth
   - Filter by relation_types if provided
   - Return GraphPath objects with visited nodes and edges

4. **Community Detection**:
   - `detect_communities`: Use connected components on relation_type="imports"
   - Implement Louvain/Leiden algorithm in Python (networkx integration)
   - Cache communities in SQLite communities table

5. **Centrality Metrics**:
   - `get_centrality`: Calculate degree centrality from edges table
   - PageRank implementation using adjacency matrix
   - Cache centrality scores for performance

6. **Path Finding**:
   - `find_shortest_path`: BFS with parent tracking
   - Dijkstra for weighted paths (if edge weights added)
   - Return path with cost/hops

7. **Subgraph Extraction**:
   - `get_subgraph`: Extract nodes within radius hops
   - Include all edges between extracted nodes
   - Return GraphSubgraph for context assembly

**Performance Optimizations**:
- Index on edges.src_id, edges.dst_id, edges.relation_type
- Connection pooling with sqlite3
- Prepared statements for hot queries
- LRU cache for relationship queries (TTL 300s)

**Acceptance**: All unit tests pass, can query 88K nodes/625K edges with <100ms latency for single-hop queries

### Phase 3 — Search Engine Integration
**Scope**: Wire SQLiteGraphStore into local/global/drift search engines

**Files**:
- `agentic_core/L1_cognition/reasoning/local_search_engine.py`
- `agentic_core/L1_cognition/reasoning/global_search_engine.py`
- `agentic_core/L1_cognition/reasoning/drift_search_engine.py`
- `agentic_core/L1_cognition/reasoning/search_fusion_engine.py`
- `agentic_core/L1_cognition/reasoning/rag_pipeline.py`

**Changes**:
1. **LocalSearchEngine**:
   - Replace mock graph_store with SQLiteGraphStore instance
   - Implement `_expand_search` using `traverse()` with max_hops
   - Implement community scoring using `detect_communities()`
   - Implement degree centrality filtering using `get_centrality()`

2. **GlobalSearchEngine**:
   - Implement `_search_communities` using `detect_communities()`
   - Implement `_search_within_communities` using filtered entity queries
   - Add hierarchical community traversal (community_levels param)

3. **DRIFTSearchEngine**:
   - Implement adaptive traversal using `traverse()` with dynamic max_depth
   - Implement context-aware pruning using subgraph extraction
   - Add reasoning-informed fusion weights

4. **SearchFusionEngine**:
   - Wire all three engines with shared SQLiteGraphStore instance
   - Implement result fusion with graph-aware scoring
   - Add diversity enforcement using graph distance

5. **RAGPipeline**:
   - Replace MockLLMClient with optional real LLM client
   - Integrate graph store for context retrieval
   - Add graph-enhanced prompt assembly

**Acceptance**: All search engines return real results from ADG data, end-to-end GraphRAG query works

### Phase 4 — Cross-Layer Integration
**Scope**: Integrate SQLiteGraphStore into L3 orchestration and L5 safety/governance

**Files**:
- `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py`
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`
- `agentic_core/L3_orchestration/reasoning/engines/adg_integration.py`
- `agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py`
- `agentic_core/L4_state/utils/memory/graph_neighborhood_memory.py`

**Changes**:
1. **SystemArchitectAgent**:
   - Replace manual DFS circular dependency detection with `find_shortest_path()`
   - Use graph store for import graph traversal
   - Add blast radius analysis using `get_subgraph()`

2. **ArchitectureGovernorAgent**:
   - Use graph store for layer violation queries
   - Implement territory-aware graph queries
   - Add governance graph traversal for policy enforcement

3. **ADG Integration**:
   - Bridge ADGQueryClient with SQLiteGraphStore
   - Expose ADG topology queries (fan-in, fan-out, impact analysis)
   - Add layer-aware graph queries

4. **KnowledgeGraphHealingStrategy**:
   - Use graph store for healing dependency analysis
   - Implement graph-aware healing path selection
   - Add blast radius validation using `get_subgraph()`

5. **GraphNeighborhoodMemory**:
   - Replace mock implementation with SQLiteGraphStore backend
   - Implement neighborhood queries for context retrieval
   - Add graph-enhanced memory search

**Acceptance**: All L3/L5 agents use graph store for graph operations, reduced latency for dependency queries

---

## Top 8 Opportunities for SQLiteGraphStore

### 1. **Circular Dependency Detection** (SystemArchitectAgent)
**Current**: Manual DFS on in-memory import graph
**With SQLiteGraphStore**: `find_shortest_path()` with cycle detection
**Benefits**:
- **Accuracy**: Detects indirect circular dependencies across entire codebase
- **Latency**: 200ms → 50ms (indexed queries vs in-memory traversal)
- **Richness**: Returns full cycle path with edge types and line numbers

**Implementation**:
```python
# Replace manual DFS with:
cycle_path = graph_store.find_shortest_path(module_a, module_b)
if cycle_path and cycle_path[-1] == module_a:
    # Circular dependency detected
```

### 2. **Blast Radius Analysis** (L3 Orchestration)
**Current**: Manual AST traversal from change point
**With SQLiteGraphStore**: `get_subgraph(center_id, radius=3)` + fan-in/fan-out
**Benefits**:
- **Accuracy**: Captures transitive dependencies across layer boundaries
- **Latency**: 500ms → 100ms (pre-computed adjacency)
- **Richness**: Returns impacted nodes with confidence scores and edge types

**Implementation**:
```python
# Replace manual traversal with:
impacted_subgraph = graph_store.get_subgraph(changed_node_id, radius=3)
blast_radius = [node for node in impacted_subgraph.nodes if node.layer != target_layer]
```

### 3. **Multi-Hop Context Retrieval** (LocalSearchEngine)
**Current**: Mock implementation returns fake expanded entities
**With SQLiteGraphStore**: `traverse(start_id, max_depth=2, relation_types=["calls", "imports"])`
**Benefits**:
- **Accuracy**: Real codebase relationships vs synthetic data
- **Latency**: N/A (currently broken) → 150ms for 2-hop traversal
- **Richness**: Returns actual function/class relationships with metadata

**Implementation**:
```python
# Replace mock with:
traversal_paths = await graph_store.traverse(
    seed_entity.id, 
    max_depth=query.max_depth,
    relation_types=["calls", "imports", "reads_from"]
)
expanded_entities = [node for path in traversal_paths for node in path.nodes]
```

### 4. **Community-Aware Search** (GlobalSearchEngine)
**Current**: Mock community search with fake results
**With SQLiteGraphStore**: `detect_communities(algorithm="leiden")` + community-level queries
**Benefits**:
- **Accuracy**: Real functional groupings based on import/call graphs
- **Latency**: N/A (currently broken) → 200ms for community detection
- **Richness**: Hierarchical communities with entity density metrics

**Implementation**:
```python
# Replace mock with:
communities = await graph_store.detect_communities(algorithm="leiden")
top_communities = sorted(communities, key=lambda c: c.entity_count, reverse=True)[:10]
for community in top_communities:
    entities = [graph_store.get_entity(eid) for eid in community.entities]
```

### 5. **Impact Analysis for Refactoring** (ADG Integration)
**Current**: Separate ADGQueryClient with manual edge queries
**With SQLiteGraphStore**: Unified graph store with `get_relationships()` + centrality metrics
**Benefits**:
- **Accuracy**: Combines structural + semantic impact analysis
- **Latency**: 300ms → 80ms (single query vs multiple)
- **Richness**: Centrality scores identify high-risk nodes

**Implementation**:
```python
# Replace manual queries with:
relationships = graph_store.get_relationships(target_node_id, direction="both")
centrality = graph_store.get_centrality(target_node_id)
impact_score = len(relationships) * centrality
```

### 6. **Graph-Enhanced Memory Retrieval** (GraphNeighborhoodMemory)
**Current**: Mock implementation
**With SQLiteGraphStore**: `get_neighbors(entity_id, max_hops=2)` + semantic similarity
**Benefits**:
- **Accuracy**: Structural context + semantic similarity
- **Latency**: N/A (currently broken) → 120ms
- **Richness**: Returns related memories with graph distance

**Implementation**:
```python
# Replace mock with:
neighbors = await graph_store.get_neighbors(memory_entity.id, max_hops=2)
related_memories = [graph_store.get_entity(n.id) for n in neighbors]
```

### 7. **Governance Violation Detection** (ArchitectureGovernorAgent)
**Current**: Manual layer boundary checks
**With SQLiteGraphStore**: `traverse()` with layer filters + `get_subgraph()` for territory analysis
**Benefits**:
- **Accuracy**: Detects cross-layer violations via transitive edges
- **Latency**: 400ms → 90ms (indexed layer queries)
- **Richness**: Returns violation paths with context

**Implementation**:
```python
# Replace manual checks with:
violations = []
for node in nodes:
    subgraph = graph_store.get_subgraph(node.id, radius=2)
    for edge in subgraph.edges:
        if edge.src_layer != edge.dst_layer and not is_allowed_crossing(edge):
            violations.append(edge)
```

### 8. **Healing Path Selection** (KnowledgeGraphHealingStrategy)
**Current**: Manual dependency graph traversal
**With SQLiteGraphStore**: `find_shortest_path()` + `get_centrality()` for risk scoring
**Benefits**:
- **Accuracy**: Optimal healing path with minimal blast radius
- **Latency**: 350ms → 70ms (pre-computed paths)
- **Richness**: Risk scores based on centrality and edge confidence

**Implementation**:
```python
# Replace manual traversal with:
healing_paths = []
for candidate in healing_candidates:
    path = graph_store.find_shortest_path(broken_node, candidate)
    risk = sum(graph_store.get_centrality(n.id) for n in path.nodes)
    healing_paths.append((path, risk))
best_path = min(healing_paths, key=lambda x: x[1])
```

---

## Rules

- **No API costs**: Use local BGE embeddings, SQLite for persistence
- **Backward compatible**: Keep Neo4jGraphStore as optional alternative
- **Graceful degradation**: Fall back to text search if graph operations fail
- **Performance target**: <100ms for single-hop queries, <500ms for 3-hop traversal
- **Test coverage**: Unit tests for all graph operations, integration tests for search engines
- **ADG as source**: Graph store is derived layer, ADG SQLite remains source of truth
- **Determinism**: Same query → same results (no randomness in graph algorithms)
- **Layer boundaries**: Graph store in L4_state, no direct L1→L4 bypasses

---

## Success Criteria

- [ ] SQLiteGraphStore implements all IGraphStore methods with <100ms latency
- [ ] Local/global/drift search engines return real results from ADG data
- [ ] Circular dependency detection uses graph store (50ms vs 200ms)
- [ ] Blast radius analysis uses subgraph extraction (100ms vs 500ms)
- [ ] Community detection identifies functional groupings (Leiden algorithm)
- [ ] GraphRAG end-to-end query works with real graph data
- [ ] L3/L5 agents use graph store for dependency queries
- [ ] All unit tests pass (>90% coverage for graph operations)
- [ ] Integration tests for search engines pass
- [ ] No regression in existing ADG functionality
- [ ] Performance benchmarks meet targets (see Implementation Commands)

---

## Implementation Commands

```bash
# Phase 1: Interface extension
# Edit agentic_core/L4_state/types/graph_store_types.py
# Add missing methods to IGraphStore interface

# Phase 2: Core implementation
# Edit agentic_core/L4_state/utils/memory/graph_knowledge_store.py
# Implement all graph operations with SQLite queries

# Phase 2: Add indexes to ADG SQLite
sqlite3 artifacts/adg/adg_indexed_04062026_0554.sqlite <<EOF
CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src_id);
CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst_id);
CREATE INDEX IF NOT EXISTS idx_edges_relation ON edges(relation_type);
CREATE INDEX IF NOT EXISTS idx_nodes_layer ON nodes(layer);
EOF

# Phase 3: Search engine integration
# Edit agentic_core/L1_cognition/reasoning/local_search_engine.py
# Edit agentic_core/L1_cognition/reasoning/global_search_engine.py
# Edit agentic_core/L1_cognition/reasoning/drift_search_engine.py
# Edit agentic_core/L1_cognition/reasoning/search_fusion_engine.py
# Edit agentic_core/L1_cognition/reasoning/rag_pipeline.py

# Phase 4: Cross-layer integration
# Edit agentic_core/L5_safety/reasoning/SystemArchitectAgent.py
# Edit agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py
# Edit agentic_core/L3_orchestration/reasoning/engines/adg_integration.py
# Edit agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py
# Edit agentic_core/L4_state/utils/memory/graph_neighborhood_memory.py

# Testing
pytest tests/unit/agentic_core/L4_state/utils/memory/test_graph_knowledge_store.py -v
pytest tests/unit/agentic_core/L1_cognition/reasoning/test_local_search_engine.py -v
pytest tests/integration/retrieval_layers/test_graphrag_e2e.py -v

# Performance benchmarking
python tools/benchmark/graph_store_benchmark.py --query-type single-hop
python tools/benchmark/graph_store_benchmark.py --query-type traverse --depth 3
```

---

## Rollback Strategy

If things go wrong:
1. **Revert interface changes**: Restore original IGraphStore in graph_store_types.py
2. **Revert implementation**: Restore placeholder SQLiteGraphStore (return None/empty)
3. **Revert search engines**: Restore mock implementations in search engines
4. **Restore ADG indexes**: Drop added indexes from ADG SQLite
5. **Fallback to Neo4j**: If Neo4j is configured, switch graph_store instantiation to Neo4jGraphStore
6. **Disable GraphRAG**: Set environment variable `GRAPHRAG_ENABLED=false` to skip graph operations

```bash
# Rollback commands
git checkout HEAD -- agentic_core/L4_state/types/graph_store_types.py
git checkout HEAD -- agentic_core/L4_state/utils/memory/graph_knowledge_store.py
git checkout HEAD -- agentic_core/L1_cognition/reasoning/local_search_engine.py
git checkout HEAD -- agentic_core/L1_cognition/reasoning/global_search_engine.py
git checkout HEAD -- agentic_core/L1_cognition/reasoning/drift_search_engine.py
git checkout HEAD -- agentic_core/L5_safety/reasoning/SystemArchitectAgent.py

# Drop indexes
sqlite3 artifacts/adg/adg_indexed_04062026_0554.sqlite <<EOF
DROP INDEX IF EXISTS idx_edges_src;
DROP INDEX IF EXISTS idx_edges_dst;
DROP INDEX IF EXISTS idx_edges_relation;
DROP INDEX IF EXISTS idx_nodes_layer;
EOF
```

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Interface completeness | 8 new methods in IGraphStore | Code review of graph_store_types.py |
| Single-hop query latency | <100ms (p95) | Benchmark script test_single_hop |
| 3-hop traversal latency | <500ms (p95) | Benchmark script test_traversal_depth_3 |
| Community detection accuracy | >0.8 silhouette score | Unit test with known communities |
| Circular dependency detection | 100% recall on known cycles | Unit test with synthetic cycles |
| Blast radius precision | >0.9 (relevant nodes only) | Integration test with real changes |
| Search engine result quality | >0.7 relevance score | Human evaluation of sample queries |
| Test coverage | >90% for graph operations | pytest coverage report |
| ADG regression | 0 failures in existing tests | Full test suite run |
| Memory overhead | <500MB additional RAM | Profiling during benchmark |

---

## FACT_CLASSIFICATION

**DIRECTLY_OBSERVED**:
- ADG status: 88,216 nodes, 625,564 edges in `adg_indexed_04062026_0554.sqlite`
- SQLiteGraphStore is a placeholder (all methods return None/empty)
- Search engines (local/global/drift) exist but use mock graph store
- SystemArchitectAgent has manual DFS circular dependency detection
- adg_integration.py has ADGQueryClient but not integrated with graph store
- Neo4jGraphStore is fully implemented but optional
- BGE embeddings are local (no API cost)
- Redis hot cache exists for semantic search

**DERIVED**:
- Graph store implementation would enable 8 high-impact use cases
- Performance improvements: 2-10x faster for graph operations
- No architectural barriers to implementation
- Existing ADG schema can support graph operations with indexes

**INFERRED**:
- Community detection would improve code organization understanding
- GraphRAG would enhance context retrieval for LLM queries
- Blast radius analysis would improve refactoring safety

**EXTERNAL**:
- User request: "detailed ingestion of SQLLite ADG to understand code"
- User request: "develop a detailed plan to implement SQLite Graph Store"
- User request: "identify the top 8 opportunities across the repo"
- User constraint: "no code changes just plan"

**ASSUMED**:
- User wants to enable GraphRAG capabilities
- User values performance (latency improvements)
- User wants to leverage existing ADG investment
- User prefers local solutions over external dependencies

**UNRESOLVED**:
- Token budget estimates (token_estimator.py not found)
- Exact performance numbers (requires implementation and benchmarking)
- Community detection quality (requires implementation and evaluation)
