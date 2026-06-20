# GraphDB CI Hardening

**P0-P3 Aligned CI Gates for GraphDB Projections**

---

## Executive Summary

This document describes the GraphDB CI hardening layer that validates graph projections from canonical ADG SQLite artifacts. The implementation follows a P0-P3 severity taxonomy aligned with existing repository CI conventions.

**Key Principles:**
- Canonical ADG SQLite remains the source of truth
- GraphDB is a derived read/query surface only
- No policy truth exists solely in GraphDB
- CI gates validate projection integrity without replacing core architecture gating

---

## Architecture

```
Canonical ADG SQLite → GraphDB Projection → P0/P1/P2/P3 Gates → Scorecard
                           ↓
                    NetworkX Graph
                           ↓
              Protected Contract Queries
```

### Truth Boundary

| Layer | Responsibility | Source of Truth |
|-------|---------------|-----------------|
| ADG SQLite | Canonical entities, relations, violations | YES |
| ADG JSON/Parquet | Snapshots, metadata, metrics | YES |
| GraphDB Projection | NetworkX graph for analysis | NO (derived) |
| GraphDB Queries | Traversal, blast-radius, diffing | NO (read-only) |

---

## P0-P3 Gate Taxonomy

### P0 — Hard Block

P0 gates block commits when projection integrity is compromised.

| Gate ID | Name | Failure Condition | Source of Truth |
|---------|------|-------------------|-----------------|
| P0-1 | Projection Parity | Missing required node/edge classes or zero counts | ADG SQLite |
| P0-2 | Deterministic Rebuild | Digest mismatch on repeated build | ADG SQLite + Baseline |
| P0-3 | Schema Compatibility | Missing required tables/columns | ADG SQLite Schema |
| P0-4 | Snapshot Integrity | Missing required metadata fields | ADG Snapshot JSON |
| P0-5 | Query Contract | Cannot execute protected contract queries | Graph Projection |
| P0-6 | Graph-Only Truth | Policy logic implemented only in GraphDB | GraphDB Source |

**Exit Codes:**
- 0 = All gates pass
- 1 = Blocking failure (commit forbidden)
- 2 = Missing artifacts (rebuild required)

### P1 — Ratchet

P1 gates track regressions in correctness and usefulness without blocking (unless configured).

| Gate ID | Name | Regression Tracked | Comparison Basis |
|---------|------|-------------------|------------------|
| P1-1 | Projection Coverage | Node/edge count drops vs baseline | Previous baseline |
| P1-2 | Explanation Parity | Graph explanations diverge from canonical | Canonical violations table |
| P1-3 | Snapshot Diff | Large negative diffs between snapshots | Previous snapshot |
| P1-4 | Query Latency | Protected query latency above threshold | LATENCY_THRESHOLDS |
| P1-5 | Findings Drift | Graph summaries diverge from canonical findings | Previous findings |

**Exit Codes:**
- 0 = No regressions or non-blocking mode
- 1 = Blocking regression detected (only with `--blocking` flag)

### P2 — Warning / Managed Debt

P2 gates track non-blocking quality and maintainability issues.

| Gate ID | Name | Issue Type | Debt Score |
|---------|------|-----------|------------|
| P2-1 | Query Coverage Gaps | Missing optional node/edge projections | 0-50 |
| P2-2 | Indexing Debt | Missing recommended indexes | 0-100 |
| P2-3 | Snapshot Bloat | Oversized or redundant artifacts | 0-100 |
| P2-4 | Metadata Enrichment | Missing optional provenance fields | 0-100 |

### P3 — Watch / Trend

P3 gates track experimental features and long-term opportunities.

| Gate ID | Name | Tracking Purpose |
|---------|------|-----------------|
| P3-1 | Experimental Features | Prototype traversal helpers, viz surfaces |
| P3-2 | Query Ergonomics | Naming convention issues, awkward paths |
| P3-3 | Long-term Opportunities | Richer path semantics, centrality analysis |

---

## Protected Contract Queries

The graph layer must support these queries for core explainability:

1. **exact_violating_path** — Complete path from source to violation
2. **first_illegal_hop** — The initial boundary crossing in a violation
3. **blast_radius_traversal** — All nodes within N hops of a target
4. **historical_diff** — Changes between two snapshot states
5. **neighborhood_extraction** — Direct neighbors of a violation target

---

## Implementation

### Gate Modules

| Module | Path | Purpose |
|--------|------|---------|
| P0 Gates | `ops_scripts/ci/graphdb_p0_gate.py` | Hard block gates |
| P1 Ratchets | `ops_scripts/ci/graphdb_p1_ratchet.py` | Regression detection |
| P2/P3 Watch | `ops_scripts/ci/graphdb_p2p3_watch.py` | Debt and trend tracking |
| Scorecard | `ops_scripts/ci/graphdb_scorecard.py` | Integration and reporting |

### Running Gates

```bash
# Run P0 gates (hard block)
python ops_scripts/ci/graphdb_p0_gate.py

# Run P1 ratchets (warning by default)
python ops_scripts/ci/graphdb_p1_ratchet.py

# Run P1 ratchets with blocking
python ops_scripts/ci/graphdb_p1_ratchet.py --blocking

# Run P2/P3 watch gates
python ops_scripts/ci/graphdb_p2p3_watch.py

# Collect all results to scorecard
python ops_scripts/ci/graphdb_scorecard.py --collect

# Print existing scorecard
python ops_scripts/ci/graphdb_scorecard.py --report
```

---

## Scorecard Integration

Gate outputs populate `artifacts/ci_gates/`:

| Artifact | Contents |
|----------|----------|
| `graphdb_gates.json` | P0 results and P1 ratchet data |
| `graphdb_watch.json` | P2/P3 watch results |
| `graphdb_scorecard.json` | Aggregate scorecard with all entries |

### Scorecard Format

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "run_id": "graphdb-2024-01-01T00-00-00Z",
  "overall_status": "PASS",
  "p0_summary": {
    "total": 6,
    "passed": 6,
    "failed": 0,
    "blocking": 0
  },
  "p1_summary": {
    "total": 5,
    "regressions": 0
  },
  "p2_summary": {
    "warnings": 4,
    "total_debt": 75
  },
  "p3_summary": {
    "watches": 3
  },
  "entries": [...]
}
```

---

## Threshold Configuration

### Latency Thresholds (seconds)

```python
LATENCY_THRESHOLDS = {
    "blast_radius": 5.0,
    "historical_diff": 10.0,
    "violation_explanation": 3.0,
}
```

### Minimum Coverage Ratios

```python
MIN_COVERAGE_RATIOS = {
    "node_type_coverage": 0.95,
    "edge_type_coverage": 0.90,
}
```

---

## Testing

Test suite location: `tests/ops_scripts/ci/test_graphdb_gates.py`

### Test Coverage

| Category | Tests |
|----------|-------|
| P0 Projection Parity | `TestP0ProjectionParity` |
| P0 Deterministic Rebuild | `TestP0DeterministicRebuild` |
| P0 Schema Compatibility | `TestP0SchemaCompatibility` |
| P0 Snapshot Integrity | `TestP0SnapshotIntegrity` |
| P0 Truth Boundary | `TestP0GraphOnlyTruth` |
| P0 Integration | `TestP0Integration` |
| P1 Ratchets | `TestP1Ratchets` |
| P2/P3 Watch | `TestP2P3Watch` |
| Scorecard | `TestScorecardIntegration` |

### Running Tests

```bash
# Run all GraphDB gate tests
pytest tests/ops_scripts/ci/test_graphdb_gates.py -v

# Run specific test class
pytest tests/ops_scripts/ci/test_graphdb_gates.py::TestP0ProjectionParity -v

# Run with coverage
pytest tests/ops_scripts/ci/test_graphdb_gates.py --cov=ops_scripts/ci --cov-report=term-missing
```

---

## Non-Goals

The GraphDB CI layer explicitly does NOT:

1. **Replace canonical ADG CI** — Core ADG gates remain authoritative
2. **Move policy truth to GraphDB** — Policy decisions stay in canonical SQLite
3. **Block on P2/P3 issues** — These are informational only
4. **Validate semantic correctness** — GraphDB validates structural integrity, not meaning
5. **Replace human judgment** — GraphDB provides data; humans decide

---

## Truth-Boundary Rules

### Canonical ADG Sovereignty

- ADG SQLite is the source of truth for all structural data
- GraphDB projections must be reproducible from ADG artifacts
- Any data in GraphDB must be traceable to canonical rows

### GraphDB Non-Sovereignty

- GraphDB may not define new policy rules
- GraphDB may not create findings not backed by canonical violations
- GraphDB may not suppress or rewrite canonical truth

### Compliance Verification

The P0-6 gate (`check_p0_6_graph_only_truth`) scans for:
- Comment markers indicating graph-only rules
- Standalone violation detection functions
- Hardcoded policy logic without ADG backing

---

## Maintenance Guide

### Adding New Gates

1. Determine severity (P0/P1/P2/P3)
2. Implement in appropriate module
3. Add to `run_all_*()` method
4. Update tests
5. Update this documentation

### Modifying Thresholds

Edit constants in gate modules:
- `LATENCY_THRESHOLDS` in `graphdb_p1_ratchet.py`
- `MIN_COVERAGE_RATIOS` in `graphdb_p1_ratchet.py`
- `SNAPSHOT_SIZE_THRESHOLD_MB` in `graphdb_p2p3_watch.py`

### CI Integration

Add to `run_contract_gates.py`:

```python
# Gate: GraphDB P0 integrity
returncode, stdout, stderr = run_cmd(
    [sys.executable, str(ROOT / "ops_scripts/ci/graphdb_p0_gate.py")],
    cwd=ROOT,
)
if returncode != 0:
    print("❌ GraphDB P0 gate failed")
    return False
```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| GraphDB becomes de-facto source of truth | P0-6 gate blocks graph-only truth; architecture review |
| Projection performance degrades | P1-4 latency ratchet; baseline tracking |
| Baseline data grows unbounded | P2-3 snapshot bloat tracking; cleanup recommendations |
| Gate execution time excessive | Timeout handling in scorecard collector; async execution |
| False positives from P1 ratchets | Non-blocking by default; human review of regressions |

---

## Acceptance Criteria

This implementation is complete when:

1. ✅ All P0 gates implemented with blocking behavior
2. ✅ All P1 ratchets implemented with baseline comparison
3. ✅ All P2/P3 gates implemented with debt tracking
4. ✅ Scorecard integration populates artifacts/ci_gates/
5. ✅ Tests validate all gate families
6. ✅ Documentation explains architecture and usage
7. ✅ Canonical ADG remains source of truth
8. ✅ GraphDB remains derived and non-sovereign
9. ✅ No policy truth exists solely in GraphDB
10. ✅ Implementation is additive (doesn't destabilize existing CI)

---

## References

- ADG Generation: `tools/generate/generate_full_adg.py`
- GraphDB Projection: `tools/graphdb/projection.py`
- CI Gate Framework: `ops_scripts/ci/run_contract_gates.py`
- Constitutional Rules: `.codex/rules/constitutional.md`

---

*Document Version: 1.0*
*Last Updated: 2024-04-09*
