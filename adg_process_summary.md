# ADG Process Summary - Static and Runtime Components

## Execution Time: March 25, 2026 04:08 UTC

## 1. Static ADG Generation
**Command**: `python tools/generate_full_adg.py`

### Key Metrics:
- **Modules Discovered**: 6,699
- **Modules Parsed**: 6,556 (97.87% coverage)
- **Syntax Errors Remaining**: 143
- **Edges Generated**: 829,987
- **Cache Hit Rate**: 97.9% (6,556 hits, 143 misses)

### Static Artifacts (stored in `artifacts/adg/`):

#### Core ADG Files:
- `adg_indexed_03252026_0408.sqlite` (269.6 MB) - Primary SQLite database
- `adg_snapshot_03252026_0408.json` (10 KB) - High-level snapshot
- `adg_graphsnap_03252026_0408.json` (141.9 MB) - Complete graph snapshot

#### Graph Visualizations:
- `adg_file_graph_03252026_0408.json` (67.4 MB) - File-level dependency graph
- `adg_symbol_graph_03252026_0408.json` (60.2 MB) - Symbol-level dependency graph
- `adg_governance_graph_03252026_0408.json` (50.3 MB) - Governance and violation graph

#### Validation Reports:
- `closure_validation_report_03252026_0408.json` - Closure validation status
- `layer_coverage_report_03252026_0408.json` - Layer distribution coverage
- `edge_density_report_03252026_0408.json` - Edge density analysis
- `provenance_report_03252026_0408.json` - Data provenance tracking
- `replay_determinism_report_03252026_0408.json` - Determinism verification
- `boundary_report_03252026_0408.json` - Boundary condition analysis
- `mutation_integrity_report_03252026_0408.json` - Mutation integrity checks
- `test_surface_coverage_03252026_0408.json` - Test coverage analysis

## 2. Runtime ADG (Redis Hot Cache)
**Command**: `python tools/adg/adg_redis_ingest.py --force`

### Redis Status:
- **Connection**: localhost:6379
- **Nodes Ingested**: 220,221 (8,995 modules tracked)
- **Edges Ingested**: 836,686 (zero-loss projection)
- **Violations Stored**: 3,606
- **Module Contexts**: 8,983 precomputed
- **Projection Integrity**: PASSED (198/198 spot checks)

### Redis Keys Structure:
- `adg:node:<id>` - Individual node metadata (HASH)
- `adg:edge_detail:<id>` - Individual edge metadata (HASH)
- `adg:violation:<id>` - Violation details (HASH)
- `adg:module_context:<id>` - Precomputed module context (HASH)
- `adg:nodes:by_layer:<layer>` - Layer-specific node sets (SET)
- `adg:edge:<src>:<rel>` - Outgoing edge adjacency sets (SET)
- `adg:edge:in:<tgt>:<rel>` - Incoming edge adjacency sets (SET)
- `adg:status` - System status sentinel (STRING)
- `adg:meta` - Complete metadata (HASH)
- `adg:snapshot` - Full snapshot (STRING)
- `adg:violations` - Violation ID list (LIST)

## 3. Closure Validation Status

### Passed Gates (12/13):
1. GOVERNANCE VISIBILITY: 1.0/1.0 ✅
2. DETERMINISM (ARTIFACT LEVEL): 1.0/1.0 ✅
3. NODE GRANULARITY: 2.58/0.95 ✅
4. EDGE SEMANTIC PRECISION: 1.0/1.0 ✅
5. DATA LINEAGE: 1.0/0.95 ✅
6. CONTROL FLOW: 1.0/0.95 ✅
7. SIDE EFFECT MODELING: 0.99/0.95 ✅
8. TEMPORAL ORDERING: 1.0/0.95 ✅
9. CALLSITE RESOLUTION: 0.96/0.95 ✅
10. TYPE ENRICHMENT: 1.0/0.95 ✅
11. TEST → EXECUTION LINKAGE: 1.0/0.95 ✅
12. VIOLATION TRACE DEPTH: 1.0/0.95 ✅

### Failed Gate (1/13):
- **STRUCTURAL COVERAGE**: 0.9787/0.99 ❌
  - 6,556 parsed / 6,699 discovered modules
  - 143 modules with syntax errors remaining

## 4. Graph Plane Coverage
- **G1_imports**: 250,295 edges
- **G3_implements**: 2,232 edges
- **G4_calls**: 19,133 edges (Gap 1 resolved)
- **GT_covers**: 9,724 edges (Gap 2 resolved)
- **GV_violates**: 10 edges (Gap 3+4 resolved)
- **GG_governance**: 5,167 edges (Gap 5 resolved)

## 5. Enhancement Analysis
- **E5 Impact**: 434 modules impacted, risk=LOW (0.1384)
- **E6 Graph Hash**: 6ea56a018069e996... (nodes=219,748, edges=829,987)
- **E7 Drift**: ADG unchanged (hash stable)
- **E8 Ownership**: 6,699 modules, 1,992 high criticality
- **E9 Confidence**: avg=0.7679 (312,996 high, 440,723 low)
- **E10 Repair Routes**: 19 routes (10 critical, 9 medium)

## 6. Next Steps
To achieve 100% STRUCTURAL COVERAGE:
1. Fix remaining 143 syntax errors
2. Re-run static ADG generation
3. Verify closure validation passes
4. Update Redis hot cache with corrected data
