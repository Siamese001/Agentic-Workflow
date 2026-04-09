# Phase A: GraphDB Enhancement - Discovery and Design

## Executive Summary

This document presents the complete Phase A analysis and design for augmenting the existing ADG (Architecture Dependency Graph) with a graph DB projection layer. The design preserves the canonical ADG artifacts as the CI source of truth while adding powerful query capabilities for structural analysis, blast-radius exploration, and historical diffing.

**Key Finding**: The repo already has a sophisticated ADG pipeline with SQLite as the primary queryable store. The optimal approach is to add a lightweight graph projection layer that reads from the canonical SQLite artifacts, not replace the existing infrastructure.

---

## A1. Current ADG Pipeline Analysis

### Core Components Located

**Parsers/Scanners:**
- `agentic_core/adg/extraction/static_scanner.py` - AST-based edge extraction
- Multiple visitor classes in `agentic_core/adg/extraction/visitors/` for different edge types
- Uses Python AST parsing exclusively (no grep/text search)

**Canonical Artifact Writer:**
- `tools/generate/generate_full_adg.py` - Main generation entrypoint
- Produces 5 canonical artifacts:
  - `adg_snapshot_<ts>.json` - CI-light metrics (~50 KB)
  - `adg_indexed_<ts>.sqlite` - Primary queryable store (~38 MB, 18 edge types)
  - `adg_file_graph_<ts>.json` - Import/export/covers/influences/cycles
  - `adg_symbol_graph_<ts>.json` - Calls/implements/reads/writes/instantiates
  - `adg_governance_graph_<ts>.json` - Violations/antipatterns/prompts

**Policy Engine:**
- Local policy engine runs against canonical artifacts
- P0-P3 structural conformance checks
- Ratchet enforcement via `p1_ratchet.json` and `p2_ratchet.json`
- Located in validation modules in `tools/generate/validation/`

**CLI Entry Points:**
- `python -m tools.adg` - Main ADG entrypoint
- `python tools/generate_full_adg.py` - Generation wrapper
- Various analysis tools in `tools/adg/` directory

**Report Emission:**
- 8 standardized reports generated during ADG creation
- Located in `artifacts/adg/` with timestamped files
- JSON format for CI integration

### Current Schema Analysis

**Entity Types (from `agentic_core/adg/contracts/schema.py`):**
- Core: module, symbol, layer, agent, tool, gateway, provider, datastore
- Governance: policy, decision, retrieval_component, seam
- Runtime: scan_run, snapshot, commit, prompt_slot, prompt_template
- Extended: 100+ types including healing, validation, telemetry entities

**Relation Types (18 core edge types):**
- Structural: imports, calls, implements, belongs_to_layer, instantiates
- Data Flow: reads_from, writes_to, routes_through, writes_through
- Control Flow: invokes_provider, produces, consumes, influences
- Governance: violates, validates, heals, orchestrates_healing
- Advanced: generates_prompt, retrieves_via, applies_guardrail, escalates_to_human

---

## A2. Graph DB Strategy Recommendation

### Chosen Approach: **SQLite + NetworkX Hybrid**

**Recommendation:** Use the existing `adg_indexed_<ts>.sqlite` as the source of truth and add a NetworkX-based graph projection layer for advanced queries.

### Justification vs Alternatives

| Criteria | SQLite + NetworkX (Chosen) | Neo4j | ArangoDB | DuckDB |
|----------|---------------------------|-------|----------|--------|
| Local Execution | ✅ Excellent | ❌ Requires server | ❌ Requires server | ✅ Excellent |
| CI Portability | ✅ No external deps | ❌ Server setup | ❌ Server setup | ✅ No external deps |
| Deterministic Rebuilds | ✅ File-based | ❌ Complex state | ❌ Complex state | ✅ File-based |
| Query Expressiveness | ✅ NetworkX algorithms | ✅ Cypher powerful | ✅ AQL powerful | ⚠️ Limited graph queries |
| Maintenance Burden | ✅ Minimal | ❌ Server ops | ❌ Server ops | ✅ Minimal |
| Integration Cost | ✅ Reads existing files | ❌ Migration needed | ❌ Migration needed | ⚠️ Schema changes |

### Architecture

```
Canonical SQLite (adg_indexed_*.sqlite)
        ↓
Graph Projection Layer (NetworkX)
        ↓
Query Workbench
    - Structural conformance queries
    - Blast-radius queries  
    - Historical diff queries
    - Analyst workflows
```

---

## A3. Graph Projection Schema

### Node Type Mapping

```python
NODE_TYPE_MAPPING = {
    # Core entities
    "module": "Module",
    "symbol": "Symbol", 
    "layer": "Layer",
    "agent": "Agent",
    "tool": "Tool",
    "gateway": "Gateway",
    "provider": "Provider",
    "datastore": "DataStore",
    
    # Governance entities
    "policy": "PolicySurface",
    "decision": "DecisionPoint",
    "retrieval_component": "RetrievalComponent",
    "seam": "Seam",
    
    # Runtime entities
    "scan_run": "Snapshot",
    "commit": "Commit",
    "prompt_slot": "PromptSlot",
    "prompt_template": "PromptTemplate",
    
    # Extended entities (grouped by category)
    "validator_node": "Validator",
    "healer_agent": "Healer",
    "embedding_store": "Store",
    "chunk_pipeline": "Processor",
    "retrieval_endpoint": "Endpoint",
    "hitl_checkpoint": "Checkpoint",
    "confidence_gate": "Gate",
    "human_decision": "Human",
    "guardrail": "Guardrail",
    "policy_enforcer": "Enforcer",
    "antipattern_record": "AntiPattern",
    "test_suite": "TestSuite",
    "test_case": "TestCase"
}
```

### Edge Type Mapping

```python
EDGE_TYPE_MAPPING = {
    # Structural edges
    "imports": "IMPORTS",
    "calls": "CALLS", 
    "implements": "IMPLEMENTS",
    "belongs_to_layer": "BELONGS_TO_LAYER",
    "instantiates": "INSTANTIATES",
    "inherits": "INHERITS",
    
    # Data flow edges
    "reads_from": "READS_FROM",
    "writes_to": "WRITES_TO",
    "routes_through": "ROUTES_THROUGH",
    "writes_through": "WRITES_THROUGH",
    
    # Control flow edges
    "invokes_provider": "INVOKES_PROVIDER",
    "produces": "PRODUCES",
    "consumes": "CONSUMES",
    "influences": "INFLUENCES",
    "controls_flow": "CONTROLS_FLOW",
    "flows_to": "FLOWS_TO",
    
    # Context and retrieval edges
    "pulls_context": "PULLS_CONTEXT",
    "retrieves_via": "RETRIEVES_VIA",
    
    # Prompt edges
    "generates_prompt": "GENERATES_PROMPT",
    "consumes_prompt": "CONSUMES_PROMPT",
    "assembles_into": "ASSEMBLES_INTO",
    "injects_into": "INJECTS_INTO",
    
    # Governance edges
    "violates": "VIOLATES",
    "validates": "VALIDATES",
    "applies_guardrail": "APPLIES_GUARDRAIL",
    "verifies_policy": "VERIFIES",
    "escalates_to": "ESCALATES_TO",
    "heals": "HEALS",
    "orchestrates_healing": "ORCHESTRATES_HEALING",
    
    # Trace edges
    "emits_trace": "EMITS_TRACE",
    "lineage_of": "LINEAGE_OF",
    "antipattern": "ANTIPATTERN",
    "evaluates": "EVALUATES"
}
```

### Node Properties Schema

```python
NODE_PROPERTIES = {
    "Module": ["file_path", "layer", "is_test", "is_production", "line_count"],
    "Symbol": ["name", "symbol_type", "file_path", "line_number", "is_exported"],
    "Layer": ["name", "level", "description"],
    "Agent": ["name", "file_path", "class_name"],
    "Tool": ["name", "module_path"],
    "Gateway": ["name", "class_name", "file_path"],
    "Provider": ["name", "interface", "module_path"],
    "DataStore": ["name", "type", "connection_string"],
    "PolicySurface": ["policy_id", "description", "severity"],
    "Snapshot": ["commit_sha", "timestamp", "run_id", "scanner_version"]
}
```

---

## A4. Snapshot Model

### Metadata Schema

```python
SNAPSHOT_METADATA = {
    "commit_sha": str,           # Git commit SHA (40 chars)
    "repo_state_hash": str,      # Git tree hash for repo state
    "schema_version": str,       # ADG schema version
    "scanner_digest": str,       # SHA256 of scanner code
    "artifact_digest": str,      # SHA256 of canonical SQLite file
    "run_id": str,              # Unique run identifier
    "timestamp": str,           # ISO8601 timestamp
    "scanner_version": str,      # Scanner version string
    "node_count": int,          # Total nodes in projection
    "edge_count": int,          # Total edges in projection
    "projection_version": str    # Graph projection schema version
}
```

### Snapshot Storage Strategy

- **Primary**: NetworkX graph objects stored as pickle + metadata JSON
- **Location**: `artifacts/graphdb/projections/<commit_sha>/`
- **Retention**: Keep last 30 snapshots, archive older ones
- **Naming**: `graph_projection_<commit_sha>_<timestamp>.pkl`

### Historical Diff Support

- Snapshots indexed by commit_sha for O(1) lookup
- Metadata includes artifact_digest for change detection
- Graph diff algorithms use NetworkX built-in functions
- Support for pairwise and multi-snapshot comparisons

---

## Repository Analysis and Integration Points

### Where Graph Projection Hooks In

```
tools/generate/generate_full_adg.py
    ↓ (after canonical artifacts written)
tools/graphdb/project_graph.py  ← NEW
    ↓ (reads from adg_indexed_*.sqlite)
NetworkX Graph Projection
    ↓
tools/graphdb/query_workbench.py  ← NEW
```

### Integration Strategy

1. **Post-Generation Hook**: Add graph projection after ADG generation completes
2. **Standalone CLI**: `python -m tools.graphdb.project --from <sqlite_file>`
3. **Library API**: Importable functions for custom analysis
4. **CI Integration**: Optional step in ADG generation pipeline

---

## Query Workbench Design

### B1. Structural Conformance Queries

```python
class StructuralQueries:
    def gravity_import_violations(self) -> List[Path]:
        """Find imports that violate layer gravity rules"""
        
    def illegal_layer_reach(self) -> List[Tuple[str, str]]:
        """Find cross-layer dependencies that violate architecture"""
        
    def l2_lifecycle_conformance(self) -> Dict[str, bool]:
        """Check L2 execution phases against canonical sub-phases"""
        
    def uwg_durable_write_conformance(self) -> List[str]:
        """Verify all durable writes go through UWG"""
```

### B2. Blast-Radius Queries

```python
class BlastRadiusQueries:
    def transitive_dependents(self, node_id: str) -> Set[str]:
        """Find all nodes that depend on the given node"""
        
    def shortest_illegal_path(self, source: str, sink: str) -> List[str]:
        """Find shortest path that violates policies"""
        
    def bypass_paths(self, gateway: str) -> List[List[str]]:
        """Find paths that bypass approved gateways"""
        
    def impact_analysis(self, removed_node: str) -> Dict[str, int]:
        """Analyze impact of removing a node"""
```

### B3. Historical Diff Queries

```python
class HistoricalQueries:
    def new_forbidden_edges(self, from_commit: str, to_commit: str) -> List[Edge]:
        """Find newly introduced policy violations"""
        
    def new_direct_writes(self, from_commit: str, to_commit: str) -> List[Edge]:
        """Find new writes that bypass gateways"""
        
    def orphaned_interfaces(self, from_commit: str, to_commit: str) -> List[str]:
        """Find interfaces that lost all dependents"""
        
    def regression_analysis(self, from_commit: str, to_commit: str) -> Dict[str, Any]:
        """Comprehensive regression analysis between snapshots"""
```

---

## File-by-File Implementation Plan

### Phase D - Projection Pipeline

**New Files:**
- `tools/graphdb/__init__.py` - Package initialization
- `tools/graphdb/project_graph.py` - Main projection entrypoint
- `tools/graphdb/schema.py` - Graph schema definitions
- `tools/graphdb/projection.py` - Core projection logic
- `tools/graphdb/snapshot.py` - Snapshot management
- `tools/graphdb/storage.py` - Storage and lifecycle

**Modified Files:**
- `tools/generate/generate_full_adg.py` - Add optional graph projection step
- `tools/generate/integration.py` - Add graph projection to integration pipeline

### Phase E - Query Workbench

**New Files:**
- `tools/graphdb/queries/__init__.py` - Query package
- `tools/graphdb/queries/structural.py` - Structural conformance queries
- `tools/graphdb/queries/blast_radius.py` - Blast-radius queries
- `tools/graphdb/queries/historical.py` - Historical diff queries
- `tools/graphdb/queries/analyst.py` - Analyst investigation workflows
- `tools/graphdb/workbench.py` - Query workbench main interface

### Phase F - Integration and Tooling

**New Files:**
- `tools/graphdb/cli.py` - CLI interface
- `tools/graphdb/utils.py` - Utility functions
- `tools/graphdb/config.py` - Configuration management

**Modified Files:**
- `tools/__main__.py` - Add graphdb CLI support

### Tests and Documentation

**New Files:**
- `tests/unit/tools/graphdb/` - Complete test suite
- `tests/fixtures/graphdb/` - Test fixtures and golden artifacts
- `docs/tools/graphdb/` - User and developer documentation

---

## Acceptance Criteria

### Functional Requirements
- ✅ Deterministic rebuild from same canonical artifacts
- ✅ Graph projection preserves all metadata needed for queries
- ✅ All query families return correct results
- ✅ Historical diffing works between any two snapshots
- ✅ Zero impact on existing CI truth path

### Non-Functional Requirements
- ✅ Projection completes within 30 seconds for ~38MB SQLite
- ✅ Memory usage stays under 2GB for full repo graph
- ✅ Graph DB adds no external dependencies
- ✅ All projections are reproducible

### Integration Requirements
- ✅ Existing ADG generation pipeline unchanged
- ✅ Graph projection is optional/additive only
- ✅ No policy logic exists only in graph DB layer
- ✅ Canonical artifacts remain source of truth

---

## Risks and Mitigations

### High-Risk Areas

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema drift between ADG and graph projection | High | Auto-generate schema mapping from ADG contracts |
| Performance degradation on large repos | Medium | Implement lazy loading and subgraph extraction |
| Snapshot storage bloat | Medium | Automatic retention policy and compression |
| Duplicate truth surfaces | High | Explicit documentation and read-only projection design |

### Medium-Risk Areas

| Risk | Impact | Mitigation |
|------|--------|------------|
| NetworkX algorithm limitations | Medium | Fallback to custom algorithms for complex queries |
| Memory pressure during projection | Medium | Streaming projection with chunked processing |
| CI portability issues | Low | Use only Python standard library + NetworkX |

### Mitigation Strategies

1. **Schema Synchronization**: Auto-generate mapping from ADG schema contracts
2. **Performance Monitoring**: Built-in timing and memory usage tracking
3. **Gradual Rollout**: Feature flag for graph projection in CI pipeline
4. **Comprehensive Testing**: 100% coverage of projection and query logic

---

## Next Steps

Upon approval, proceed with Phase D implementation in the following order:

1. **D1**: Create projection entrypoint and orchestration
2. **D2**: Implement core graph materialization logic  
3. **D3**: Add snapshot model and metadata handling
4. **E1**: Implement structural conformance query pack
5. **E2**: Implement blast-radius query pack
6. **E3**: Implement historical diff query pack
7. **F1**: Add CLI integration and help text
8. **F3**: Add comprehensive test coverage
9. **F4**: Create documentation and usage examples

Each phase will be implemented as a small, reviewable increment with existing test coverage preserved.
