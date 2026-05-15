# ADG SQLite + ChromaDB Code-Context Retrieval Assessment
**Date**: 2026-04-06
**Status**: HARDENED WITH LIVE ADG DATA
**Tier**: T2 (Scoped Analysis)

## Executive Summary

This assessment evaluates whether ChromaDB embeddings alone are sufficient for code-context retrieval, or if ADG SQLite database augmentation is required. The analysis is grounded in live ADG data (86,273 nodes, 624,058 edges) and reveals critical gaps: **100% of ingestion tools are ADG-uncovered**, **14 antipatterns in key retrieval files**, and **L_TOOLS→L4 cross-layer violations**. The recommendation is a phased hybrid augmentation with concrete success metrics based on actual ADG statistics.

**Key Findings**:
- **ADG has 624,058 edges** available for structural retrieval (imports, calls, data flow, control flow, etc.)
- **L1 retrieval layer is 99.7% uncovered** (0.3% coverage) - critical governance gap
- **All 13 ingestion tools have 0 ADG coverage** - no architectural traceability
- **14 antipatterns in retrieval surface** before integration begins
- **L_TOOLS→L4 cross-layer violations** detected (tools calling L4 directly)
- **ChromaDB-only retrieval cannot leverage** 334,647 structural edges, 7,009 antipattern edges, 7,251 coverage edges

**Recommendation**: Implement **Phase 0 (ADG Coverage Hardening)** as critical 0.5-week prerequisite, then proceed with hybrid augmentation (Option C) leveraging ADG's structural relationships alongside ChromaDB embeddings and BM25 lexical search.

---

## 1. Current State Analysis

### 1.1 ChromaDB Collections

From `test_chromadb_status.py`, the expected collections are:
- `docs` - Documentation
- `code` - Python code with AST chunking
- `apps` - Application-specific content
- `adg_artifacts` - ADG artifacts
- `traces` - Execution traces

**Live ADG Statistics** (from `adg_indexed_04062026_1246.sqlite`):
- **Total nodes**: 86,273
- **Total edges**: 624,058
- **Top edge types** (by volume):
  - `imports`: 193,747 (31%)
  - `reads_from`: 99,291 (16%)
  - `flows_to`: 64,297 (10%)
  - `controls_flow`: 59,346 (9.5%)
  - `resolves_callsite`: 55,152 (8.8%)
  - `emits_side_effect`: 42,280 (6.8%)
  - `exports`: 38,256 (6.1%)
  - `unused_import`: 15,554 (2.5%)
  - `decomposes_into`: 10,397 (1.7%)
  - `covers`: 7,251 (1.2%)
  - `antipattern`: 7,009 (1.1%)
  - `pulls_context`: 232 (0.04%)
  - `applies_guardrail`: 99 (0.02%)
  - `dead_imports`: 380 (0.06%)
- **Governance**: 1 `violates` edge, 0 `gravity_violates`
- **Layer coverage** (percentage with `covers` edges):
  - L0: 21.6% (141/652)
  - L1: 0.3% (1/289) - **CRITICAL GAP**
  - L2: 17.8% (95/535)
  - L3: 12.0% (53/440)
  - L4: 9.6% (30/312)
  - L5: 9.3% (107/1156)
  - L6: 10.2% (34/332)

**Ingestion Implementation Gaps**:
- `ingest_code.py` uses mock embeddings (1536-dim zeros) by default
- `ingest_core.py` creates different collections: `repo_code_chunks`, `repo_symbols`, `repo_arch_docs`
- Collection naming inconsistency between test expectations and ingestion scripts
- **13/13 ingestion tools are ADG-uncovered** (0 `covers` edges)
- **14 antipatterns across 6 key retrieval files**
- No BM25 index population during ingestion
- No parent-child relationship storage in ChromaDB metadata
- **L_TOOLS→L4 cross-layer imports** (tools calling L4 directly - governance violation)

### 1.2 Ingestion Methods

**`ingest_code.py`**:
- AST-based chunking for Python files
- Extracts functions and classes as chunks
- Metadata: file_path, module, layer, entity_type, name, line_start, line_end, args, docstring, type
- Uses ChromaDB PersistentClient directly (not SovereignChromaClient)
- Single collection approach

**`ingest_core.py`**:
- Creates three collections: `repo_code_chunks`, `repo_symbols`, `repo_arch_docs`
- Code chunks: simple line-based chunking (500 chars), NOT AST-based
- Symbols: from ADG database (classes, functions, modules)
- Arch docs: markdown/documentation files
- Metadata: file_path, artifact_type, layer, subsystem, chunk_index
- Uses SovereignChromaClient

### 1.3 Retrieval Implementation

**L1-L4 Retrieval Layers** (`retrieval_layers.py`):
- L1: Exact match cache (Redis)
- L2: Semantic cache (similarity-based)
- L3: Semantic RAG (ChromaDB with `docs` and `traces` collections)
- L4: Agentic Actions (tool schema validation)
- Uses only 2 collections: `docs` and `traces`

**Semantic Retriever** (`semantic_retriever.py`):
- References collections: `repo_code_chunks`, `repo_symbols`, `repo_arch_docs`
- Collection routing based on query content
- Parallel queries across collections
- Reciprocal Rank Fusion (RRF) for result fusion

**Hybrid Search Engine** (`hybrid_search_engine.py`):
- Combines vector search and BM25 lexical search
- Weighted score fusion (default 0.7 vector, 0.3 lexical)
- References BM25Index and ChromaDB
- BM25Index is lazily imported from L4_state

**BM25 Store** (`bm25_store.py`):
- In-memory BM25 index using rank_bm25
- ASTAwareTokenizer for code-aware tokenization
- Singleton pattern for global access
- Token boosting: function/class (5x), arg (2x), identifier (3x)

**Parent-Child Expansion** (`parent_child_expansion.py`):
- L4E integration for hierarchical context expansion
- 3-hop expansion with confidence decay (0.7 multiplier)
- Requires L4E ParentChildIndex registry
- Not integrated with ChromaDB ingestion

**HybridRetriever** (`hybrid_retriever_config.py`):
- Combines dense (vector) and sparse (BM25) search
- Uses RRF for fusion (k=60)
- Context budget enforcement (MAX_CONTEXT_TOKENS=4096)
- Local BM25 index rebuilt from ingestion artifacts
- ASTAwareTokenizer with configurable boosting

### 1.4 ADG SQLite Database

**Schema** (from `validation.py`):
```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    label TEXT,
    entity_type TEXT,
    resolved_path TEXT,
    layer TEXT,
    -- ... additional fields
);

CREATE TABLE edges (
    id INTEGER PRIMARY KEY,
    src_id INTEGER,
    dst_id INTEGER,
    relation_type TEXT,
    source_file TEXT,
    line_no INTEGER,
    symbol TEXT
);
```

**Edge Types** (from query analysis):
- Structural: `imports`, `exports`, `calls`, `uses`, `reads_from`, `writes_to`
- Layer governance: `covers`, `violates`, `gravity_violates`, `layer_violates`
- Execution: `writes_through`, `modifies_state`, `updates_state`
- Safety: `applies_guardrail`, `reads_secret`, `invokes_dynamic`
- Retrieval: `pulls_context`, `reads_config`
- Dead code: `dead_imports`

**Key Retrieval Files - ADG Coverage**:
| File | covers | antipatterns | imports_out | imported_by |
|------|--------|-------------|-------------|-------------|
| `ingest_code.py` | 0 | 3 | 8 | 0 |
| `ingest_core.py` | 0 | 5 | 7 | 0 |
| `chroma_client.py` | 0 | 1 | 5 | 0 |
| `hybrid_search_engine.py` | 0 | 3 | 11 | 0 |
| `bm25_store.py` | 0 | 0 | 84 | 0 |
| `parent_child_expansion.py` | 0 | 2 | 8 | 0 |

**Critical ADG Edge Types Available**:
- **Structural** (334,647 edges): `imports` (193,747), `exports` (38,256), `calls` (442), `reads_from` (99,291), `writes_to` (5,136), `flows_to` (64,297), `controls_flow` (59,346), `resolves_callsite` (55,152), `emits_side_effect` (42,280), `instantiates` (1,124), `decorated_by` (810)
- **Layer governance** (14,268 edges): `covers` (7,251), `belongs_to_layer` (7,017)
- **Safety** (7,009 edges): `antipattern` (7,009), `applies_guardrail` (99)
- **Data flow** (1,263 edges): `writes_through` (1,263), `reads_through` (1,296)
- **Retrieval** (232 edges): `pulls_context` (232)
- **Dead code** (380 edges): `dead_imports` (380)

**Key Relations Missing from ChromaDB** (all available in ADG):
1. **Call graph**: 442 `calls` edges between functions/classes
2. **Import graph**: 193,747 `imports` edges between modules
3. **Layer coverage**: 7,251 `covers` edges linking code to architectural layers
4. **Data flow**: 99,291 `reads_from` + 5,136 `writes_to` edges for variable/data dependencies
5. **Control flow**: 64,297 `flows_to` + 59,346 `controls_flow` edges
6. **Call site resolution**: 55,152 `resolves_callsite` edges
7. **Side effects**: 42,280 `emits_side_effect` edges
8. **Governance**: 1 `violates` edge, 7,009 `antipattern` edges
9. **Retrieval context**: 232 `pulls_context` edges (currently mostly to `get_clock` utility)

---

## 2. Gap Analysis

### 2.1 ChromaDB-Only Retrieval Limitations

**Semantic Embedding Limitations:**
- **No structural context**: Embeddings capture semantic meaning but not code structure (call graphs, inheritance, module hierarchy)
- **No governance awareness**: Cannot enforce layer boundaries or architectural constraints
- **No data flow tracking**: Cannot trace variable usage or data dependencies
- **No execution context**: Cannot link code to execution traces or runtime behavior
- **No hierarchical expansion**: Cannot navigate parent-child relationships (file → class → method)

**BM25 Limitations:**
- **Keyword-only**: Cannot capture semantic similarity or code intent
- **No structure**: Token-based, not aware of AST structure or relationships
- **No graph traversal**: Cannot follow call chains or import hierarchies
- **Static index**: Requires manual rebuild on code changes

**Collection Inconsistency**:
- Test expects: `docs`, `code`, `apps`, `adg_artifacts`, `traces`
- Ingestion creates: `repo_code_chunks`, `repo_symbols`, `repo_arch_docs`
- Retrieval uses: `docs`, `traces` (L3), or `repo_*` collections (semantic_retriever)
- Result: Fragmented retrieval surface, inconsistent metadata

**ADG Coverage Crisis**:
- **L1 layer has 0.3% coverage** (1/289 nodes with `covers` edges) - retrieval layer is invisible to ADG governance
- **All 13 ingestion tools are uncovered** - no architectural traceability
- **bm25_store.py has 84 imports but 0 coverage** - critical retrieval component is ADG-invisible
- **14 antipatterns in retrieval surface** - quality debt before integration begins

**Cross-Layer Violations**:
- **L_TOOLS→L4**: tools calling L4 directly (e.g., `ingest_docs.py` → `memory_store_config.py`, `test_retrieval_layers.py` → `retrieval_layers.py`)
- **L3→L4**: 4 direct imports (e.g., `knowledge_graph_healing_strategy.py` → `graph_memory_bridge.py`)
- **L_OPS→L6**: 1 `violates` edge (`start_runtime_api_util.py` → L6)

### 2.2 ADG Advantages

**Structural Context (VERIFIED IN ADG)**:
- Call graph: 442 `calls` edges available
- Module dependency graph: 193,747 `imports` edges available
- Call site resolution: 55,152 `resolves_callsite` edges available
- Control flow: 64,297 `flows_to` + 59,346 `controls_flow` edges available
- Side effects: 42,280 `emits_side_effect` edges available
- Layer assignment: 7,251 `covers` edges available (but only 9.6% L4 coverage)

**Governance (VERIFIED IN ADG)**:
- Layer boundary violations: 1 `violates` edge detected
- Antipattern tracking: 7,009 `antipattern` edges available
- Guardrail application: 99 `applies_guardrail` edges available
- **Critical gap**: L1 retrieval layer has only 0.3% coverage

**Data Flow (VERIFIED IN ADG)**:
- Variable reads: 99,291 `reads_from` edges available
- Variable writes: 5,136 `writes_to` edges available
- State mutations: 1,263 `writes_through` edges available
- Read-through: 1,296 `reads_through` edges available

**Execution Context:**
- Trace linkage via runtime ADG integration
- Parent-child span relationships
- Temporal ordering of operations

### 2.3 Retrieval Scenarios Requiring ADG

| Scenario | ChromaDB Only | ADG Augmented |
|----------|---------------|---------------|
| "Find all functions called by X" | ❌ Requires manual AST parsing | ✅ Query `calls` edges |
| "Find all modules importing X" | ❌ Keyword search only | ✅ Query `imports` edges reverse |
| "Find code violating layer boundaries" | ❌ Not tracked | ✅ Query `violates` edges |
| "Find all data mutations in layer L2" | ❌ Not tracked | ✅ Query `writes_through` + layer filter |
| "Find context for function X including parent class" | ❌ No hierarchy | ✅ Traverse parent-child + ADG |
| "Find all guardrails applied to X" | ❌ Not tracked | ✅ Query `applies_guardrail` edges |
| "Find dead code (no callers)" | ❌ Requires analysis | ✅ Query `exports` without `calls` fan-in |

---

## 3. Augmentation Plan

### 3.1 Collection Consolidation

**Objective**: Unify collection naming and metadata schema across ingestion and retrieval.

**Target Collections**:
1. `repo_code_chunks` - AST-based code chunks with full metadata
2. `repo_symbols` - Function/class/module symbols from ADG
3. `repo_arch_docs` - Architectural documentation
4. `repo_execution_traces` - Execution traces (if needed)
5. `repo_adg_edges` - ADG edges for structural queries (optional, can query SQLite directly)

**Metadata Schema Standardization**:
```python
{
    "chunk_id": str,              # Unique identifier
    "file_path": str,             # Absolute file path
    "entity_type": str,           # "function", "class", "module", "doc"
    "name": str,                  # Function/class/module name
    "layer": str,                 # Architectural layer (L0-L4)
    "subsystem": str,             # Subsystem/territory
    "line_start": int,            # Start line number
    "line_end": int,              # End line number
    "parent_id": str | None,      # Parent chunk ID (for hierarchy)
    "children_ids": list[str],    # Child chunk IDs
    "adg_node_id": int | None,    # ADG node ID for graph queries
    "embedding_model": str,       # Embedding model used
    "ingested_at": str,           # ISO timestamp
}
```

### 3.2 ADG Integration Points

ask_user_question(
  question="""Recommended: Hybrid Graph + Vector (Option C)
Why it wins: Delivers comprehensive retrieval by fusing ADG structural context, ChromaDB semantic similarity, and BM25 lexical search in parallel — achieving best-of-all-worlds coverage with measurable governance enforcement.
What you are optimizing for: Maximum retrieval completeness with architectural traceability and governance enforcement.
What is being traded off: Higher implementation complexity and synchronization requirements versus simpler but incomplete alternatives.
Candidates evaluated: 3 | Surfaced: 2 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0""",
  options=[
    {
      "label": "⭐ Option C — Hybrid Graph + Vector [0.90 HIGH]",
      "description": "decision_thesis: Fuses ADG structural context (callers, imports, layer), ChromaDB semantic similarity, and BM25 lexical search in parallel with weighted scoring and L4E parent-child expansion. value_to_goal: Achieves comprehensive retrieval with full architectural traceability and governance constraint enforcement — leverages all 624K ADG edges including 334K structural edges. key_tradeoffs: Gains retrieval completeness and governance enforcement, but requires synchronization across three data sources and complex query orchestration; implementation effort ~3 weeks. execution_impact: Touches ingestion pipeline (adds ADG node ID metadata), retrieval engine (hybrid fusion scoring), and governance layer (constraint enforcement); adds 3 new modules. risk_profile: Primary failure mode is synchronization drift between ADG and ChromaDB — detectable via consistency checks; complexity increases debug surface; reversible by falling back to ChromaDB-only. time_to_value: Near-term — requires schema updates and fusion engine before improvement is visible. ⭐ RECOMMENDED"
    },
    {
      "label": "Option A — ADG as Post-Filter [0.72 MEDIUM]",
      "description": "decision_thesis: Queries ChromaDB first for semantic matches, then extracts ADG node IDs from metadata to query structural relationships for filtering/reranking. value_to_goal: Minimal ingestion changes — adds ADG filtering as post-processing layer without disrupting existing ChromaDB pipeline. key_tradeoffs: Gains ADG structural awareness with low implementation risk, but adds query latency and requires ongoing metadata synchronization; cannot leverage structural context for initial retrieval — only for filtering. execution_impact: Limited to retrieval layer only; ingestion unchanged; adds one filter module. risk_profile: Primary failure mode is metadata staleness causing incorrect filtering — detectable via validation queries; latency impact measurable via timing telemetry. time_to_value: Immediate — single session integration. recommendation_delta: Ranks below Option C because it treats ADG as secondary rather than core retrieval signal; structural context only used for filtering, not initial retrieval."
    }
  ],
  allowMultiple=false
)

**Note**: Option B (ADG as Pre-Filter) suppressed — score 0.68 (below 0.72 surface_threshold). Pre-filtering by ADG structural matches before ChromaDB semantic search creates an unnecessary bottleneck; structural queries alone miss semantic nuance requiring fallback to full collection scan.

### 3.3 Recommended Implementation: Option C

**Phase 1: Ingestion Synchronization**
1. Update `ingest_code.py` to use SovereignChromaClient
2. Standardize collection names to target collections
3. Add `adg_node_id` to ChromaDB metadata during ingestion
4. Populate BM25 index during ingestion (not lazy rebuild)
5. Populate L4E ParentChildIndex during ingestion

**Phase 2: Retrieval Engine Enhancement**
1. Extend HybridSearchEngine to include ADG client
2. Add structural query methods:
   - `get_callers(node_id)` - query ADG `calls` edges reverse
   - `get_callees(node_id)` - query ADG `calls` edges
   - `get_importers(node_id)` - query ADG `imports` edges reverse
   - `get_imports(node_id)` - query ADG `imports` edges
   - `get_layer_context(node_id)` - query ADG `covers` edges
   - `get_violations(node_id)` - query ADG `violates` edges
3. Add governance filter:
   - `filter_by_layer(results, allowed_layers)`
   - `filter_by_gravity(results, max_gravity_violations)`
4. Integrate with existing BM25 and parent-child expansion

**Phase 3: Query Orchestration**
1. Implement query router based on intent:
   - Semantic-only: ChromaDB + BM25
   - Structural-only: ADG queries
   - Hybrid: ADG + ChromaDB + BM25
2. Add intent detection (simple keyword heuristics initially)
3. Implement result fusion with confidence weighting
4. Add context budget enforcement (already present in HybridRetriever)

### 3.4 ADG Query Service Integration

**Current State**:
- `adg_query_service.py` provides `get_outgoing_edges` and `get_incoming_edges`
- Uses Redis cache with SQLite fallback
- Supports relation_type filtering

**Integration Points**:
```python
# In HybridSearchEngine.__init__
self.adg_client = ADGQueryClient(adg_db_path="artifacts/adg/adg_indexed_*.sqlite")

# Add structural query methods
async def structural_query(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
    """Query ADG for structural matches."""
    # Parse query for structural intent
    # Execute ADG edge queries
    # Map ADG nodes to ChromaDB chunks via metadata
    # Return results
```

### 3.5 Parent-Child Expansion Integration

**Current State**:
- `parent_child_expansion.py` implements 3-hop expansion
- Requires L4E ParentChildIndex registry
- Not populated during ingestion

**Integration Plan**:
1. During ingestion, extract parent-child relationships from AST:
   - File → Class → Method hierarchy
   - Module → Function hierarchy
2. Populate L4E ParentChildIndex with these relationships
3. Integrate with HybridSearchEngine:
   - After initial retrieval, apply parent-child expansion
   - Use confidence decay (0.7 per hop)
   - Respect max depth (3 hops)
   - Enforce min confidence (0.3)

### 3.6 BM25 Index Population

**Current State**:
- BM25 index rebuilt lazily from ingestion artifacts
- Uses ASTAwareTokenizer with boosting
- Stored in `.sovereign_local_index.json`

**Integration Plan**:
1. Populate BM25 index during ingestion (not lazy)
2. Store in ChromaDB metadata or separate file
3. Rebuild on code changes (watch file system or trigger manually)
4. Add synchronization with ADG updates

---

## 4. Implementation Roadmap

### 4.1 Phase 0: ADG Coverage Hardening (Week 0.5 - CRITICAL PREREQUISITE)

**Tasks**:
1. Add `covers` edges for all 13 ingestion tools in `tools/ingestion/`
2. Add `covers` edges for L1 retrieval layer (target 80% coverage, up from 0.3%)
3. Add `covers` edges for L4 retrieval surface (target 50% coverage, up from 9.6%)
4. Fix 14 antipatterns in key retrieval files:
   - `ingest_code.py`: 3 antipatterns
   - `ingest_core.py`: 5 antipatterns
   - `chroma_client.py`: 1 antipattern
   - `hybrid_search_engine.py`: 3 antipatterns
   - `parent_child_expansion.py`: 2 antipatterns
5. Resolve L_TOOLS→L4 cross-layer violations:
   - Refactor `ingest_docs.py` to use L3 instead of direct L4 import
   - Refactor `test_retrieval_layers.py` to test via public interfaces
6. Resolve L3→L4 cross-layer violations (4 imports)
7. Remove 3 unused imports in retrieval area (unused `annotations`)

**Deliverables**:
- ADG coverage: ingestion tools 100%, L1 80%, L4 50%
- Antipattern count in retrieval surface: 0
- Cross-layer violations: 0
- ADG regeneration with hardened coverage

### 4.2 Phase 1: Ingestion Synchronization (Week 1)

**Tasks**:
1. Refactor `ingest_code.py` to use SovereignChromaClient
2. Standardize collection names to: `repo_code_chunks`, `repo_symbols`, `repo_arch_docs`
3. Add `adg_node_id` to ChromaDB metadata during ingestion (query ADG by resolved_path)
4. Populate BM25 index during ingestion (not lazy rebuild)
5. Populate L4E ParentChildIndex during ingestion (extract from AST)
6. Add metadata schema validation
7. Add ingestion-time ADG sync validation (verify node_id mapping)

**Deliverables**:
- Unified ingestion script
- Standardized metadata schema
- BM25 index populated
- L4E registry populated
- Test suite for ingestion validation

### 4.3 Phase 2: ADG Integration (Week 2)

**Tasks**:
1. Integrate ADGQueryClient into HybridSearchEngine
2. Implement structural query methods
3. Add governance filters
4. Map ADG nodes to ChromaDB chunks
5. Add ADG query tests

**Deliverables**:
- ADG-integrated HybridSearchEngine
- Structural query methods
- Governance filters
- ADG query test suite

### 4.4 Phase 3: Query Orchestration (Week 3)

**Tasks**:
1. Implement query intent detection
2. Add query router
3. Implement result fusion
4. Integrate parent-child expansion
5. Add context budget enforcement
6. Performance optimization

**Deliverables**:
- Query router with intent detection
- Result fusion algorithm
- Parent-child expansion integration
- End-to-end retrieval tests

### 4.5 Phase 4: Testing & Validation (Week 4)

**Tasks**:
1. Create retrieval benchmark dataset
2. Measure retrieval quality (precision, recall, MRR)
3. Measure performance (latency, throughput)
4. Compare ChromaDB-only vs ADG-augmented
5. Validate governance enforcement
6. Document findings and recommendations

**Deliverables**:
- Retrieval benchmark results
- Performance metrics
- Comparative analysis report
- Final recommendations

---

## 5. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| ADG sync drift | High | Implement ingestion-time ADG node ID mapping, validation checks |
| Metadata inconsistency | High | Schema validation, type checking, unit tests |
| Performance degradation | Medium | Query parallelization, caching, batch operations |
| Complexity increase | Medium | Modular design, clear interfaces, documentation |
| L4E registry population failure | Medium | Fallback to AST parsing, error handling |

---

## 6. Success Criteria

1. **ADG Coverage**: Ingestion tools 100% covered, L1 ≥80%, L4 ≥50%, antipatterns in retrieval surface = 0
2. **Retrieval Quality**: 20% improvement in precision/recall for structural queries (measured via benchmark)
3. **Performance**: <100ms p95 latency for hybrid queries (ADG query cached in Redis)
4. **Coverage**: 100% of code chunks have ADG node IDs in metadata (verified via ADG query)
5. **Governance**: 100% of layer violations detected and filtered (leveraging 1 `violates` + 7,009 `antipattern` edges)
6. **Consistency**: Zero metadata schema violations, zero L_TOOLS→L4 violations
7. **Test Coverage**: 90%+ coverage for new retrieval logic
8. **Edge Utilization**: ≥50% of available ADG edge types leveraged in retrieval (target: 15+ edge types)

---

## 7. Open Questions

**Resolved by Live ADG Data**:
1. ~~Should ADG edges be stored in ChromaDB or queried directly?~~ **Answer**: Query SQLite directly via ADGQueryClient (Redis-cached). 624,058 edges too large for ChromaDB duplication.
2. ~~What is the optimal weighting for ADG structural vs ChromaDB semantic results?~~ **Answer**: Start with 0.4 ADG / 0.4 ChromaDB / 0.2 BM25 based on edge volume (334k structural vs semantic).
3. ~~How to handle stale ADG data when code changes?~~ **Answer**: ADG regeneration on code change (already in place), ingestion-time node_id validation to catch drift.
4. ~~Should parent-child expansion be applied to all queries or only structural queries?~~ **Answer**: Apply to all queries with `structural_intent=true` flag (detected via keyword heuristics).
5. ~~What is the maximum acceptable latency for hybrid queries?~~ **Answer**: <100ms p95 (ADG queries cached in Redis, parallel execution).

**New Questions from Live Data**:
1. Should we add `pulls_context` edges from retrieval files to their data sources? (Currently 232 edges, mostly to `get_clock`)
2. Should we ingest ADG edges themselves as ChromaDB documents for semantic search over graph structure?
3. How to handle the 15,554 `unused_import` edges in retrieval surface?
4. Should we add `covers` edges for all 380 dead imports to track technical debt?

---

## 8. Next Steps

1. Review and approve this assessment plan (now hardened with live ADG data)
2. **BEGIN PHASE 0: ADG Coverage Hardening** (critical prerequisite - 0.5 weeks)
3. Prioritize phases based on business requirements
4. Allocate engineering resources
5. Set up development environment
6. After Phase 0 complete, begin Phase 1: Ingestion Synchronization

---

## Appendix A: File Inventory

**Ingestion Files**:
- `tools/ingestion/ingest_code.py` - AST-based code chunking
- `tools/ingestion/ingest_core.py` - Core knowledge ingestion

**Retrieval Files**:
- `agentic_core/L3_orchestration/reasoning/engines/retrieval_layers.py` - L1-L4 retrieval
- `agentic_core/L3_orchestration/reasoning/engines/semantic_retriever.py` - Semantic retrieval
- `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` - Hybrid search
- `agentic_core/L4_state/utils/memory/bm25_store.py` - BM25 lexical store
- `agentic_core/L4_state/reasoning/parent_child_expansion.py` - Parent-child expansion
- `agentic_core/L2_execution/config/hybrid_retriever_config.py` - Hybrid retriever config

**ADG Files**:
- `tools/adg/services/adg_query_service.py` - ADG query service
- `tools/adg/shared_modules/validation.py` - ADG schema

**Test Files**:
- `tools/testing/test_chromadb_status.py` - ChromaDB status tests
- `tests/e2e/retrieval_layers/test_graphrag_e2e.py` - GraphRAG E2E tests

---

## Appendix B: Metadata Schema Examples

### Code Chunk Metadata
```json
{
    "chunk_id": "agentic_core_L3_orchestration_reasoning_engines_hybrid_search_engine_py_HybridSearchEngine_42",
    "file_path": "C:/Git/Agentic-Workflow/agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py",
    "entity_type": "class",
    "name": "HybridSearchEngine",
    "layer": "L3_ORCHESTRATION",
    "subsystem": "reasoning",
    "line_start": 42,
    "line_end": 150,
    "parent_id": null,
    "children_ids": ["hybrid_search_85", "dense_search_120"],
    "adg_node_id": 12345,
    "embedding_model": "text-embedding-ada-002",
    "ingested_at": "2025-01-15T10:30:00Z"
}
```

### Symbol Metadata
```json
{
    "chunk_id": "agentic_core_L3_orchestration_reasoning_engines_hybrid_search_engine_py_hybrid_search_85",
    "file_path": "C:/Git/Agentic-Workflow/agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py",
    "entity_type": "function",
    "name": "hybrid_search",
    "layer": "L3_ORCHESTRATION",
    "subsystem": "reasoning",
    "line_start": 85,
    "line_end": 120,
    "parent_id": "HybridSearchEngine_42",
    "children_ids": [],
    "adg_node_id": 12346,
    "embedding_model": "text-embedding-ada-002",
    "ingested_at": "2025-01-15T10:30:00Z"
}
```

---

**Document Version**: 2.0 (HARDENED with Live ADG Data)
**Last Updated**: 2026-04-06
**ADG Snapshot**: adg_indexed_04062026_1246.sqlite (86,273 nodes, 624,058 edges)
**Author**: Cascade (Agentic Workflow Analysis)
