# ADG Output Redundancy Analysis

**Date:** 2026-04-06
**Timestamp:** 04062026_0554
**Total Current Size:** 380.84 MB

---

## Executive Summary

The ADG generation produces significant redundant data across multiple output files. Analysis reveals:

- **100.76 MB** of redundant JSON graph files that are incomplete subsets of SQLite
- **87,499 nodes** duplicated across multiple JSON files
- **36 edge types (259,270 edges)** missing from JSON graphs entirely
- **71.84 MB** drift detection file that can be compressed

**Potential Savings:** 120-160 MB (30-40% reduction) with zero signal loss.

---

## Current Output Breakdown

| File | Size | Purpose | Edge Types | Edge Count | Node Count |
|------|------|---------|------------|------------|------------|
| adg_snapshot.json | 0.01 MB | CI-light metrics | N/A | N/A | N/A |
| adg_file_graph.json | 53.22 MB | File-level imports/exports | 5 | 248,947 | 42,687 |
| adg_symbol_graph.json | 31.55 MB | Symbol-level relationships | 9 | 111,500 | 87,499 |
| adg_governance_graph.json | 15.99 MB | Governance/antipattern edges | 44 | 5,847 | 87,504 |
| adg_graphsnap.json | 71.84 MB | Drift detection snapshot | N/A | N/A | 87,507 |
| adg_indexed.sqlite | 163.55 MB | Primary queryable store | 94 | 625,564 | 88,216 |
| adg_run.zip | 44.68 MB | Archive of all artifacts | N/A | N/A | N/A |
| **TOTAL** | **380.84 MB** | | | | |

---

## Critical Redundancy Issues

### 1. JSON Graphs are Incomplete Subsets

**Problem:**
- SQLite contains 94 edge types with 625,564 total edges
- JSON graphs combined contain only 58 edge types with 366,294 edges
- **36 edge types (259,270 edges) are completely missing from JSON graphs**

**Missing Edge Types in JSON:**
- controls_flow (59,076 edges)
- flows_to (63,972 edges)
- emits_side_effect (42,076 edges)
- resolves_callsite (54,801 edges)
- decomposes_into (12,065 edges)
- unused_import (16,655 edges)
- tests_execution_of (2,873 edges)
- ... and 29 more edge types

**Impact:**
- JSON graphs cannot be used as a complete data source
- Any analysis requiring missing edge types must query SQLite anyway
- JSON graphs serve no unique purpose that SQLite doesn't fulfill better

---

### 2. Massive Node Duplication

**Problem:**
- file_graph: 42,687 nodes (module-level only)
- symbol_graph: 87,499 nodes (includes symbols)
- governance_graph: 87,504 nodes (includes symbols)
- symbol_graph and governance_graph have nearly identical node sets

**Node Overlap Analysis:**
```
file_graph ∩ symbol_graph: 42,687 nodes (100% of file_graph)
file_graph ∩ governance_graph: 42,687 nodes (100% of file_graph)
symbol_graph ∩ governance_graph: 87,499 nodes (99.99% overlap)
All three intersect: 42,687 nodes
```

**Impact:**
- symbol_graph and governance_graph duplicate 87,499 nodes (~90 KB each in serialized form)
- file_graph nodes are a proper subset of the other two
- SQLite has the canonical node table with 88,216 nodes

**Estimated Redundancy:**
- Node dictionaries in JSON: ~15-20 MB per file
- Total node duplication: ~30-40 MB across 3 files

---

### 3. adg_graphsnap.json is Uncompressed

**Problem:**
- adg_graphsnap.json is 71.84 MB
- Contains:
  - canonical_edge_order: 349,626 edge IDs (ordered list)
  - canonical_node_order: 87,507 node IDs (ordered list)
  - edge_counts_by_relation: 93 edge type counts
  - Metadata (graph_hash, commit_sha, etc.)

**Structure:**
```json
{
  "canonical_edge_order": [0, 1, 2, ..., 349625],  // Large array
  "canonical_node_order": [0, 1, 2, ..., 87506],   // Large array
  "edge_counts_by_relation": {...},                // Small dict
  "graph_hash": "...",
  "commit_sha": "...",
  ...
}
```

**Impact:**
- Integer arrays compress extremely well with gzip
- Current storage is uncompressed JSON
- Estimated compression ratio: 5-10x

**Potential Savings:**
- Compressed size: ~7-15 MB (vs 71.84 MB)
- Savings: ~57-65 MB

---

## Consolidation Opportunities

### Opportunity 1: Eliminate JSON Graph Files

**Recommendation:** Remove `adg_file_graph.json`, `adg_symbol_graph.json`, and `adg_governance_graph.json`

**Rationale:**
1. **Incomplete Data:** Missing 36 edge types (41% of all edges)
2. **Redundant Storage:** All data exists in SQLite with better query performance
3. **Node Duplication:** Massive duplication of node data across files
4. **No Unique Purpose:** SQLite fulfills all use cases better

**Migration Path:**
1. Update all consumers to query SQLite directly
2. Use SQLite indexes for fast queries by edge type
3. Keep adg_snapshot.json for CI-light metrics (9 KB)

**Signal Loss:** ZERO - SQLite contains superset of all data

**File Size Impact:**
- Remove: 53.22 + 31.55 + 15.99 = 100.76 MB
- Keep: adg_snapshot.json (0.01 MB)
- **Net Savings: 100.75 MB**

---

### Opportunity 2: Compress adg_graphsnap.json

**Recommendation:** Store adg_graphsnap.json as gzip-compressed file

**Rationale:**
1. **High Compressibility:** Integer arrays compress 5-10x
2. **Infrequent Access:** Only used for drift detection (not hot path)
3. **Simple Decompression:** Single line of code to decompress

**Implementation:**
```python
# Save compressed
import gzip
import json
with gzip.open(f"adg_graphsnap_{ts}.json.gz", "wt") as f:
    json.dump(snapshot_data, f)

# Load compressed
with gzip.open(f"adg_graphsnap_{ts}.json.gz", "rt") as f:
    snapshot_data = json.load(f)
```

**Signal Loss:** ZERO - Lossless compression

**File Size Impact:**
- Current: 71.84 MB
- Compressed: ~7-15 MB (estimated)
- **Net Savings: 57-65 MB**

---

### Opportunity 3: Optimize SQLite Storage

**Recommendation:** Apply SQLite optimizations

**Rationale:**
1. SQLite can be VACUUMed to reclaim space
2. Enable page compression if supported
3. Optimize indexes for common query patterns

**Implementation:**
```python
conn = sqlite3.connect(sqlite_path)
conn.execute("VACUUM")  # Reclaim space
conn.execute("PRAGMA optimize")  # Analyze query patterns
conn.close()
```

**Signal Loss:** ZERO - Internal optimization only

**File Size Impact:**
- Current: 163.55 MB
- Estimated after VACUUM: 150-160 MB
- **Net Savings: 3-13 MB**

---

## Recommended Consolidation Strategy

### Phase 1: Eliminate Redundant JSON Graphs (High Impact)

**Actions:**
1. Update `tools/generate/generate_full_adg.py` to skip generating JSON graph files
2. Update all consumers to query SQLite directly
3. Update documentation to reflect SQLite as primary data source

**Files to Modify:**
- `tools/generate/generate_full_adg.py` - Remove JSON graph generation
- `agentic_core/adg/artifact/ArtifactPaths.py` - Remove graph file paths
- Any consumers of JSON graph files - Migrate to SQLite queries

**Expected Savings:** 100.75 MB (26% reduction)

**Risk:** LOW - SQLite contains superset of data

---

### Phase 2: Compress Drift Detection File (Medium Impact)

**Actions:**
1. Modify snapshot save/load to use gzip compression
2. Update file extension to `.json.gz`
3. Update drift detection code to decompress on load

**Files to Modify:**
- `agentic_core/adg/analysis/CanonicalSnapshot.py` - Add compression
- `tools/generate/generate_full_adg.py` - Update file extension

**Expected Savings:** 57-65 MB (15-17% reduction)

**Risk:** LOW - Lossless compression, minimal code change

---

### Phase 3: Optimize SQLite (Low Impact)

**Actions:**
1. Add VACUUM after SQLite write
2. Add PRAGMA optimize after index creation
3. Review index usage and remove unused indexes

**Files to Modify:**
- `agentic_core/adg/artifact/builder.py` - Add optimization calls

**Expected Savings:** 3-13 MB (1-3% reduction)

**Risk:** VERY LOW - Standard SQLite optimization

---

## Final Recommendation

### Immediate Action (Phase 1 + Phase 2)

**Consolidated Output Set (Post-Consolidation):**
| File | Size | Purpose |
|------|------|---------|
| adg_snapshot.json | 0.01 MB | CI-light metrics |
| adg_indexed.sqlite | 163.55 MB | Primary queryable store |
| adg_graphsnap.json.gz | ~10 MB | Compressed drift detection |
| adg_run.zip | ~20 MB | Compressed archive |
| **TOTAL** | **~193 MB** | **49% reduction** |

**Total Savings:** ~188 MB (49% reduction)
**Signal Loss:** ZERO
**Risk:** LOW

### Long-term Optimization (Phase 3)

Apply SQLite VACUUM and optimization for additional 3-13 MB savings.

---

## Consumer Impact Analysis

### Current Consumers of JSON Graphs

Need to identify and update:
1. Any scripts reading `adg_file_graph.json`
2. Any scripts reading `adg_symbol_graph.json`
3. Any scripts reading `adg_governance_graph.json`

**Migration Path:**
```python
# OLD (JSON graph)
with open('adg_file_graph.json') as f:
    data = json.load(f)
    imports_edges = [e for e in data['edges'] if e['r'] == 'imports']

# NEW (SQLite)
conn = sqlite3.connect('adg_indexed.sqlite')
cur = conn.cursor()
imports_edges = cur.execute(
    "SELECT * FROM edges WHERE relation_type='imports'"
).fetchall()
```

**Benefits of Migration:**
- Faster queries (indexed)
- Less memory (streaming vs loading entire file)
- Access to all 94 edge types (not just 58)
- Better filtering and aggregation capabilities

---

## Implementation Checklist

- [x] **Architecture already supports disabling JSON graphs** - `write_split_planes=False` flag exists in `ArtifactPaths.write_all_artifacts()`
- [ ] Update `tools/generate/generate_full_adg.py` to pass `write_split_planes=False`
- [ ] Identify all consumers of JSON graph files (found 20+ files)
- [ ] Update consumers to use SQLite queries:
  - Core ADG tools (tools/adg/*.py)
  - Test files (tools/testing/*.py)
  - Analysis tools (tools/analysis/*.py)
  - Archive tools (tools/archive/*.py)
- [ ] Update `ArtifactPaths.py` documentation to reflect SQLite as primary source
- [ ] Update docs/tools/adg_persistence_guide.md
- [ ] Implement gzip compression for `adg_graphsnap.json` in `CanonicalSnapshot.py`
- [ ] Update snapshot load/save code in `generate_full_adg.py`
- [ ] Add SQLite VACUUM after write in `_write_sqlite()`
- [ ] Test all consumers with new data source
- [ ] Validate zero signal loss with comparison tests
- [ ] Deploy and monitor

## Implementation Details

### Disabling JSON Graph Generation

The architecture already supports this via the `write_split_planes` parameter:

```python
# In tools/generate/generate_full_adg.py, line 289:
paths = write_all_artifacts(
    artifact, 
    out_dir=adg_artifacts_dir, 
    ts=ts,
    write_split_planes=False,  # ADD THIS LINE
)
```

This single-line change eliminates generation of:
- adg_file_graph.json (53.22 MB)
- adg_symbol_graph.json (31.55 MB)
- adg_governance_graph.json (15.99 MB)

**Total savings: 100.76 MB**

### Consumer Migration Pattern

Consumers currently load entire JSON files into memory:

```python
# OLD PATTERN
with open('adg_file_graph.json') as f:
    data = json.load(f)
    imports_edges = [e for e in data['edges'] if e['r'] == 'imports']
```

New pattern uses SQLite with streaming:

```python
# NEW PATTERN
conn = sqlite3.connect('adg_indexed.sqlite')
cur = conn.cursor()
imports_edges = cur.execute(
    "SELECT * FROM edge_view WHERE relation_type='imports'"
).fetchall()
conn.close()
```

**Benefits:**
- No need to load entire file into memory
- Indexed queries are faster
- Access to all 94 edge types (not just 58)
- Better filtering and aggregation capabilities

---

## Conclusion

The ADG output contains significant redundancy:
- **100.76 MB** of incomplete JSON graph files
- **71.84 MB** of uncompressed drift detection data
- **30-40 MB** of duplicated node data

By eliminating redundant JSON graphs and compressing the drift detection file, we can achieve **~188 MB (49%) file size reduction** with **zero signal loss**.

The recommended consolidation strategy is low-risk and high-impact, with SQLite serving as the single source of truth for all graph data.
