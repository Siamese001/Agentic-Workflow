---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\test-drift-score-impl-7c4f4c.md'
original_relative_path: 'test-drift-score-impl-7c4f4c.md'
source_sha256: 37201a0d2d65cbc0de84ce78f59d6da368446453fe98f8236f875e30196ff3ea
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Test-Code Drift Score — Implementation Plan

Implement a Redis-backed drift score engine (`tools/adg/drift_score.py`) that quantifies the gap between the full production codebase and `tests/` using the ADG hot cache, storing sub-scores and a composite score in Redis under `adg:drift:*` keys.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Real ADG Baseline (from `adg:snapshot`, timestamp 03132026_1424)

| Surface | Count |
|---|---|
| Total modules | 8,141 |
| **Prod modules** (L0–L6 + L_APP + L_OPS + L_SHARED + L_TOOLS + L_RUNTIME + L_SL + L_PG) | **4,817** |
| Test modules (`L_TEST`) | 3,324 |
| `covers` edges (test→prod semantic coverage) | 7,674 |
| `imports` edges (total) | 48,070 |
| `dead_imports` edges (orphan signal, already in ADG) | 4,392 |
| `violates` edges (layer boundary violations) | 2 |
| `unresolved_count` (phantom imports) | 419 |

**Prod by layer**: L0=366, L1=103, L2=310, L3=204, L4=142, L5=608, L6=47, L_APP=1324, L_OPS=420, L_SHARED=371, L_TOOLS=420, L_RUNTIME=154, L_SL=264, L_PG=84

**Top blast-radius prod modules** (from snapshot `top_fan_out_hotspots`):
- `apps_shared/types/sovereign_severity_types.py` (fan_out=1,146)
- `agentic_core/L0_routing/scripts/execute_ssot.py` (fan_out=1,010)
- `agentic_core/adg/extraction/static_scanner.py` (fan_out=798)
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` (fan_out=457)

---

## Scope

- **Production surface**: layers L0–L6, L_APP, L_OPS, L_SHARED, L_TOOLS, L_RUNTIME, L_SL, L_PG (all `entity_type=module` nodes, exclude `__pycache__`, `::` symbol suffixes)
- **Test surface**: `L_TEST` layer (3,324 modules)
- **Data source**: Redis hot cache via `ADGRedisClient` — snapshot STRING key for counts, node HASHes for module enumeration, edge SETs for graph traversal
- **Output**: Redis `adg:drift:*` keys + stdout summary

---

## Hardened Drift Score Formula

```
drift_score = (
    0.40 * D_coverage   +   # uncovered module ratio via `covers` edges (primary signal)
    0.30 * D_blast      +   # blast-radius-weighted gap (fan_out from snapshot hotspots)
    0.20 * D_orphan     +   # dead_imports ratio (already in ADG graph)
    0.10 * D_violation  +   # violates edges without test coverage (currently 2 — low weight)
)
```

All sub-scores normalised to **[0.0, 1.0]** where `1.0 = maximum drift`. Lower = healthier.

> **Weight change from v1**: D_coverage raised 0.35→0.40, D_violation lowered 0.15→0.10 (real data shows `violates=2`, `layer_violation_count=0` — signal is sparse).

---

## Sub-Score Definitions (grounded in real ADG edge types)

### D_coverage — Coverage Gap
- **Correct relation**: `covers` (7,674 edges in graph) — ADG explicitly models test→prod semantic coverage
- **Numerator**: prod module nodes with zero inbound `covers` edges from any `L_TEST` node
- **Denominator**: total prod modules in scope (4,817), excluding `__init__.py`-only stubs and `_shim`/`_compat` modules
- **Redis query**: for each prod node_id → `adg:edge:in:<node_id>:covers`; intersect sources with L_TEST node set
- **Hardening**: use `adg:nodes:by_layer:L_TEST` SET directly as the test node set (no path prefix scan needed)

### D_blast — Blast-Radius Mismatch
- **Signal**: `top_fan_out_hotspots` from `adg:snapshot` gives the top-20 immediately; full blast uses `adg:edge:<node_id>:imports` fan-out count
- **Coverage weight**: `covered_i = 1 if adg:edge:in:<node_id>:covers` has any L_TEST source
- **Formula**: `D_blast = sum(fan_out_i * (1 - covered_i)) / sum(fan_out_i)` over all prod modules
- **Hardening**: cap individual `fan_out_i` at p99 across all prod modules (prevents `sovereign_severity_types.py` fan_out=1,146 from dominating); snapshot hotspots seed the top-20 output list

### D_orphan — Dead Import / Phantom Ratio
- **Signal**: `dead_imports` edges (4,392 already computed in ADG) — these are test or prod nodes with imports to deleted/moved targets
- **Numerator**: count of `L_TEST` module nodes that are sources of ≥1 `dead_imports` edge
- **Denominator**: total `L_TEST` modules (3,324)
- **Formula**: `D_orphan = orphan_test_count / 3324`
- **Phantom sub-signal**: `unresolved_count=419` from snapshot → include as additive term: `D_orphan = min(1.0, (orphan_test_count + unresolved_from_tests) / 3324)`
- **Hardening**: cap at 1.0; separate `dead_imports` (structural) from `unresolved` (parse-time) in Redis payload

### D_violation — Layer Violation Gap
- **Signal**: `violates` edges (2 in current graph) — source nodes are the violating modules
- **Numerator**: `violates`-edge source modules with zero `covers` edges from `L_TEST`
- **Denominator**: `max(total_violates_sources, 1)` — safe divide; if 0 → `D_violation = 0.0`
- **Hardening**: `layer_violation_count=0` in snapshot confirms violations list is empty; `violates` edges are the correct signal. Score stays 0.0 on a clean graph.

---

## Redis Output Schema

| Key | Type | Contents |
|---|---|---|
| `adg:drift:score` | STRING | composite score e.g. `"0.412"` |
| `adg:drift:subscores` | HASH | `{coverage, blast, orphan, violation, prod_total, test_total, timestamp}` |
| `adg:drift:uncovered` | LIST | `resolved_path` of prod modules with zero `covers` edges |
| `adg:drift:orphan_tests` | LIST | `L_TEST` module paths that are `dead_imports` sources |
| `adg:drift:blast_top` | LIST | top-20 uncovered prod modules by fan_out (JSON `{path, fan_out}`) |
| `adg:drift:violation_gaps` | LIST | `violates`-edge source paths with no test coverage |

All keys: **1-hour TTL**, idempotent (re-run resets TTL).

---

## Implementation Plan

### Phase 1 — Core engine (`tools/adg/drift_score.py`)
1. `_load_snapshot(adg)` → parse `adg:snapshot` STRING for counts + hotspots
2. `_load_layer_nodes(adg, layers)` → `dict[node_id, resolved_path]` using `adg:nodes:by_layer:<L>` SETs + `adg:node:<id>` HASHes
   - Prod layers: `{L0,L1,L2,L3,L4,L5,L6,L_APP,L_OPS,L_SHARED,L_TOOLS,L_RUNTIME,L_SL,L_PG}`
   - Test layers: `{L_TEST}`
3. `compute_coverage_gap(adg, prod_nodes, test_node_set)` → `(float, list[str])`
   - Uses `adg:edge:in:<id>:covers` fan-in per prod node
4. `compute_blast_mismatch(adg, prod_nodes, covered_set, snapshot_hotspots)` → `(float, list[dict])`
   - Uses `adg:edge:<id>:imports` fan-out count per prod node; p99 cap
5. `compute_orphan_phantom(adg, test_nodes, snapshot_unresolved)` → `(float, list[str])`
   - Uses `adg:edge:<id>:dead_imports` fan-out per test node; adds snapshot `unresolved_count`
6. `compute_violation_gap(adg, test_node_set)` → `(float, list[str])`
   - Scans `adg:edge:*:violates` keys; checks fan-in covers for each source
7. `composite_score(d_cov, d_blast, d_orphan, d_viol)` → `float` (weights: 0.40/0.30/0.20/0.10)
8. `write_to_redis(r, scores, detail_lists)` — pipeline write all `adg:drift:*` keys with `EXPIRE 3600`
9. `main()` — wire, print aligned summary table to stdout

### Phase 2 — Regression tests (`tests/adg/test_drift_score.py`)
- Synthetic stub dicts (no live Redis); mock `ADGRedisClient`
- One test per sub-score function (4 tests)
- One test for composite formula weights summing to 1.0
- One test for Redis write schema (assert all 6 keys written with TTL)
- Edge cases: zero prod modules, all covered, zero violations, all-orphan tests

### Phase 3 — Wire into existing tooling
- Add one-line drift score read to `redis_health_check.py` summary block
- Update Redis DB Namespace Map memory with `adg:drift:*` entry

---

## File Locations

| Artifact | Path |
|---|---|
| Engine | `tools/adg/drift_score.py` |
| Tests | `tests/adg/test_drift_score.py` |

---

## Key Design Decisions

- **`covers` not `imports`**: ADG explicitly models test→prod semantic coverage via `covers` edges (7,674); `imports` would double-count transitive deps and miss semantic intent
- **`dead_imports` not `os.path.exists`**: orphan detection is already resolved at graph-build time — no filesystem I/O needed at runtime
- **Layer SET lookup**: `adg:nodes:by_layer:L_TEST` is a direct SET in Redis — O(1) membership test, no full scan needed for test node classification
- **Snapshot for blast hotspots**: `top_fan_out_hotspots` in `adg:snapshot` seeds the top-20 blast report for free; full blast scan is only needed for the score formula
- **D_violation weight 0.10**: real data shows `violates=2` edges — signal is sparse; upweighting would make score noisy relative to actual structural risk
- **Idempotent + CI-safe**: all writes go through a Redis pipeline with TTL; safe to call from any CI step after ADG ingest

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

